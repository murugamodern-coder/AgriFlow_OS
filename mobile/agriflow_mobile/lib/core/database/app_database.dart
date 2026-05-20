import 'dart:convert';
import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

/// Drift-backed local store — projections + queue (server authoritative).
class AppDatabase extends GeneratedDatabase {
  AppDatabase() : super(_openConnection());

  AppDatabase.forTesting(QueryExecutor executor) : super(executor);

  @override
  int get schemaVersion => 2;

  @override
  Iterable<TableInfo<Table, Object?>> get allTables => const [];

  @override
  MigrationStrategy get migration => MigrationStrategy(
        beforeOpen: (details) async {
          await ensureSchema();
        },
      );

  Future<void> ensureSchema() async {
    await customStatement('''
CREATE TABLE IF NOT EXISTS sync_queue_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  client_mutation_id TEXT NOT NULL UNIQUE,
  entity TEXT NOT NULL,
  op_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  farmer_project TEXT,
  status TEXT NOT NULL,
  retry_count INTEGER NOT NULL DEFAULT 0,
  last_error_code TEXT,
  server_response_json TEXT,
  server_request_id TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
''');
    await customStatement('''
CREATE TABLE IF NOT EXISTS sync_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  phase TEXT NOT NULL,
  success INTEGER NOT NULL,
  error_code TEXT,
  request_id TEXT,
  raw_response_json TEXT,
  started_at TEXT NOT NULL,
  finished_at TEXT
);
''');
    await customStatement('''
CREATE TABLE IF NOT EXISTS idempotency_map (
  client_mutation_id TEXT PRIMARY KEY,
  entity TEXT NOT NULL,
  server_name TEXT,
  result_json TEXT NOT NULL,
  recorded_at TEXT NOT NULL
);
''');
    await customStatement('''
CREATE TABLE IF NOT EXISTS projection_cache (
  kind TEXT NOT NULL,
  name TEXT NOT NULL,
  block TEXT,
  sort_key TEXT,
  payload_json TEXT NOT NULL,
  is_deleted INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (kind, name)
);
''');
    await customStatement('''
CREATE TABLE IF NOT EXISTS inventory_queue_entries (
  client_id TEXT PRIMARY KEY,
  op_type TEXT NOT NULL,
  allocation TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  farmer_project TEXT,
  status TEXT NOT NULL,
  retry_count INTEGER NOT NULL DEFAULT 0,
  last_error_code TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
''');
  }

  // --- Sync queue ---

  Future<List<SyncQueueRow>> pendingQueue({int limit = 50}) async {
    final rows = await customSelect(
      '''
SELECT * FROM sync_queue_entries
WHERE status IN ('pending', 'failed')
ORDER BY created_at ASC
LIMIT ?
''',
      variables: [Variable.withInt(limit)],
      readsFrom: {},
    ).get();
    return rows.map(_mapQueueRow).toList();
  }

  Future<int> pendingCount() async {
    final row = await customSelect(
      '''
SELECT COUNT(*) AS c FROM sync_queue_entries
WHERE status IN ('pending', 'failed', 'conflict')
''',
      readsFrom: {},
    ).getSingle();
    return row.read<int>('c') ?? 0;
  }

  Future<int> conflictCount() async {
    final row = await customSelect(
      "SELECT COUNT(*) AS c FROM sync_queue_entries WHERE status = 'conflict'",
      readsFrom: {},
    ).getSingle();
    return row.read<int>('c') ?? 0;
  }

  Future<int> failedCount() async {
    final row = await customSelect(
      "SELECT COUNT(*) AS c FROM sync_queue_entries WHERE status = 'failed'",
      readsFrom: {},
    ).getSingle();
    return row.read<int>('c') ?? 0;
  }

  Future<int> queuePendingOnlyCount() async {
    final row = await customSelect(
      "SELECT COUNT(*) AS c FROM sync_queue_entries WHERE status = 'pending'",
      readsFrom: {},
    ).getSingle();
    return row.read<int>('c') ?? 0;
  }

  Future<List<SyncQueueRow>> conflictRows({int limit = 20}) async {
    final rows = await customSelect(
      '''
SELECT * FROM sync_queue_entries WHERE status = 'conflict'
ORDER BY updated_at DESC LIMIT ?
''',
      variables: [Variable.withInt(limit)],
      readsFrom: {},
    ).get();
    return rows.map(_mapQueueRow).toList();
  }

  Future<void> enqueueMutation({
    required String clientMutationId,
    required String entity,
    required String opType,
    required String payloadJson,
    String? farmerProject,
  }) async {
    final now = DateTime.now().toUtc().toIso8601String();
    await customInsert(
      '''
INSERT OR REPLACE INTO sync_queue_entries (
  client_mutation_id, entity, op_type, payload_json, farmer_project,
  status, retry_count, created_at, updated_at
) VALUES (?, ?, ?, ?, ?, 'pending', 0, ?, ?)
''',
      variables: [
        Variable.withString(clientMutationId),
        Variable.withString(entity),
        Variable.withString(opType),
        Variable.withString(payloadJson),
        Variable.withString(farmerProject),
        Variable.withString(now),
        Variable.withString(now),
      ],
      updates: {},
    );
  }

  Future<void> markQueueRow({
    required String clientMutationId,
    required String status,
    String? lastErrorCode,
    String? serverResponseJson,
    String? serverRequestId,
    int? retryCount,
  }) async {
    final now = DateTime.now().toUtc().toIso8601String();
    await customUpdate(
      '''
UPDATE sync_queue_entries SET
  status = ?,
  last_error_code = ?,
  server_response_json = ?,
  server_request_id = ?,
  retry_count = COALESCE(?, retry_count),
  updated_at = ?
WHERE client_mutation_id = ?
''',
      variables: [
        Variable.withString(status),
        Variable.withString(lastErrorCode),
        Variable.withString(serverResponseJson),
        Variable.withString(serverRequestId),
        if (retryCount != null) Variable.withInt(retryCount) else const Variable(null),
        Variable.withString(now),
        Variable.withString(clientMutationId),
      ],
      updates: {},
    );
  }

  Future<void> recordIdempotency({
    required String clientMutationId,
    required String entity,
    String? serverName,
    required String resultJson,
  }) async {
    await customInsert(
      '''
INSERT OR REPLACE INTO idempotency_map (
  client_mutation_id, entity, server_name, result_json, recorded_at
) VALUES (?, ?, ?, ?, ?)
''',
      variables: [
        Variable.withString(clientMutationId),
        Variable.withString(entity),
        Variable.withString(serverName),
        Variable.withString(resultJson),
        Variable.withString(DateTime.now().toUtc().toIso8601String()),
      ],
      updates: {},
    );
  }

  Future<Map<String, dynamic>?> findIdempotency(String clientMutationId) async {
    final row = await customSelect(
      'SELECT * FROM idempotency_map WHERE client_mutation_id = ?',
      variables: [Variable.withString(clientMutationId)],
      readsFrom: {},
    ).getSingleOrNull();
    if (row == null) return null;
    return {
      'client_mutation_id': row.read<String>('client_mutation_id'),
      'entity': row.read<String>('entity'),
      'server_name': row.read<String?>('server_name'),
      'result_json': row.read<String>('result_json'),
    };
  }

  Future<void> logSyncRun({
    required String phase,
    required bool success,
    String? errorCode,
    String? requestId,
    String? rawResponseJson,
    required DateTime startedAt,
    DateTime? finishedAt,
  }) async {
    await customInsert(
      '''
INSERT INTO sync_runs (
  phase, success, error_code, request_id, raw_response_json, started_at, finished_at
) VALUES (?, ?, ?, ?, ?, ?, ?)
''',
      variables: [
        Variable.withString(phase),
        Variable.withInt(success ? 1 : 0),
        Variable.withString(errorCode),
        Variable.withString(requestId),
        Variable.withString(rawResponseJson),
        Variable.withString(startedAt.toUtc().toIso8601String()),
        Variable.withString(finishedAt?.toUtc().toIso8601String()),
      ],
      updates: {},
    );
  }

  Future<SyncRunRow?> lastSyncRun() async {
    final row = await customSelect(
      'SELECT * FROM sync_runs ORDER BY started_at DESC LIMIT 1',
      readsFrom: {},
    ).getSingleOrNull();
    if (row == null) return null;
    return _mapSyncRunRow(row);
  }

  Future<List<SyncRunRow>> recentSyncRuns({int limit = 10}) async {
    final rows = await customSelect(
      'SELECT * FROM sync_runs ORDER BY started_at DESC LIMIT ?',
      variables: [Variable.withInt(limit)],
      readsFrom: {},
    ).get();
    return rows.map(_mapSyncRunRow).toList();
  }

  SyncRunRow _mapSyncRunRow(QueryRow row) => SyncRunRow(
        phase: row.read<String>('phase')!,
        success: (row.read<int>('success') ?? 0) == 1,
        errorCode: row.read<String?>('error_code'),
        requestId: row.read<String?>('request_id'),
        startedAt: row.read<String>('started_at')!,
        finishedAt: row.read<String?>('finished_at'),
      );

  Future<void> upsertProjection({
    required String kind,
    required String name,
    required String payloadJson,
    String? block,
    String? sortKey,
    bool isDeleted = false,
  }) async {
    await customInsert(
      '''
INSERT OR REPLACE INTO projection_cache (
  kind, name, block, sort_key, payload_json, is_deleted
) VALUES (?, ?, ?, ?, ?, ?)
''',
      variables: [
        Variable.withString(kind),
        Variable.withString(name),
        Variable.withString(block),
        Variable.withString(sortKey),
        Variable.withString(payloadJson),
        Variable.withInt(isDeleted ? 1 : 0),
      ],
      updates: {},
    );
  }

  Stream<List<ProjectionRow>> watchProjections({
    required String kind,
    List<String>? blocks,
  }) {
    if (blocks != null && blocks.isNotEmpty) {
      final placeholders = List.filled(blocks.length, '?').join(',');
      return customSelect(
        '''
SELECT * FROM projection_cache
WHERE kind = ? AND is_deleted = 0
  AND (block IS NULL OR block IN ($placeholders))
ORDER BY sort_key DESC
''',
        variables: [
          Variable.withString(kind),
          ...blocks.map(Variable.withString),
        ],
        readsFrom: {},
      ).watch().map((rows) => rows.map(_mapProjection).toList());
    }
    return customSelect(
      '''
SELECT * FROM projection_cache
WHERE kind = ? AND is_deleted = 0
ORDER BY sort_key DESC
''',
      variables: [Variable.withString(kind)],
      readsFrom: {},
    ).watch().map((rows) => rows.map(_mapProjection).toList());
  }

  Future<List<ProjectionRow>> readProjections({
    required String kind,
    List<String>? blocks,
    int limit = 100,
  }) async {
    final rows = await watchProjections(kind: kind, blocks: blocks).first;
    return rows.take(limit).toList();
  }

  Future<void> tombstoneProjection({
    required String kind,
    required String name,
  }) async {
    await customUpdate(
      'UPDATE projection_cache SET is_deleted = 1 WHERE kind = ? AND name = ?',
      variables: [
        Variable.withString(kind),
        Variable.withString(name),
      ],
      updates: {},
    );
  }

  SyncQueueRow _mapQueueRow(QueryRow row) => SyncQueueRow(
        id: row.read<int>('id')!,
        clientMutationId: row.read<String>('client_mutation_id')!,
        entity: row.read<String>('entity')!,
        opType: row.read<String>('op_type')!,
        payloadJson: row.read<String>('payload_json')!,
        farmerProject: row.read<String?>('farmer_project'),
        status: row.read<String>('status')!,
        retryCount: row.read<int>('retry_count') ?? 0,
        lastErrorCode: row.read<String?>('last_error_code'),
        serverResponseJson: row.read<String?>('server_response_json'),
        serverRequestId: row.read<String?>('server_request_id'),
      );

  ProjectionRow _mapProjection(QueryRow row) => ProjectionRow(
        kind: row.read<String>('kind')!,
        name: row.read<String>('name')!,
        block: row.read<String?>('block'),
        sortKey: row.read<String?>('sort_key'),
        payloadJson: row.read<String>('payload_json')!,
        payload: jsonDecode(row.read<String>('payload_json')!) as Map<String, dynamic>,
        isDeleted: (row.read<int>('is_deleted') ?? 0) == 1,
      );

  // --- Inventory queue (offline replay via inventory API) ---

  Future<void> enqueueInventoryOp({
    required String clientId,
    required String opType,
    required String allocation,
    required String payloadJson,
    String? farmerProject,
  }) async {
    final now = DateTime.now().toUtc().toIso8601String();
    await customInsert(
      '''
INSERT OR REPLACE INTO inventory_queue_entries (
  client_id, op_type, allocation, payload_json, farmer_project,
  status, retry_count, created_at, updated_at
) VALUES (?, ?, ?, ?, ?, 'pending', 0, ?, ?)
''',
      variables: [
        Variable.withString(clientId),
        Variable.withString(opType),
        Variable.withString(allocation),
        Variable.withString(payloadJson),
        Variable.withString(farmerProject),
        Variable.withString(now),
        Variable.withString(now),
      ],
      updates: {},
    );
  }

  Future<List<InventoryQueueRow>> pendingInventoryOps({int limit = 20}) async {
    final rows = await customSelect(
      '''
SELECT * FROM inventory_queue_entries
WHERE status IN ('pending', 'failed')
ORDER BY created_at ASC LIMIT ?
''',
      variables: [Variable.withInt(limit)],
      readsFrom: {},
    ).get();
    return rows
        .map(
          (r) => InventoryQueueRow(
            clientId: r.read<String>('client_id')!,
            opType: r.read<String>('op_type')!,
            allocation: r.read<String>('allocation')!,
            payloadJson: r.read<String>('payload_json')!,
            farmerProject: r.read<String?>('farmer_project'),
            status: r.read<String>('status')!,
            retryCount: r.read<int>('retry_count') ?? 0,
            lastErrorCode: r.read<String?>('last_error_code'),
          ),
        )
        .toList();
  }

  Future<int> pendingInventoryCount() async {
    final row = await customSelect(
      "SELECT COUNT(*) AS c FROM inventory_queue_entries WHERE status IN ('pending', 'failed')",
      readsFrom: {},
    ).getSingle();
    return row.read<int>('c') ?? 0;
  }

  Future<void> markInventoryOp({
    required String clientId,
    required String status,
    String? lastErrorCode,
    int? retryCount,
  }) async {
    final now = DateTime.now().toUtc().toIso8601String();
    await customUpdate(
      '''
UPDATE inventory_queue_entries SET
  status = ?,
  last_error_code = ?,
  retry_count = COALESCE(?, retry_count),
  updated_at = ?
WHERE client_id = ?
''',
      variables: [
        Variable.withString(status),
        Variable.withString(lastErrorCode),
        if (retryCount != null) Variable.withInt(retryCount) else const Variable(null),
        Variable.withString(now),
        Variable.withString(clientId),
      ],
      updates: {},
    );
  }
}

class SyncQueueRow {
  const SyncQueueRow({
    required this.id,
    required this.clientMutationId,
    required this.entity,
    required this.opType,
    required this.payloadJson,
    this.farmerProject,
    required this.status,
    required this.retryCount,
    this.lastErrorCode,
    this.serverResponseJson,
    this.serverRequestId,
  });

  final int id;
  final String clientMutationId;
  final String entity;
  final String opType;
  final String payloadJson;
  final String? farmerProject;
  final String status;
  final int retryCount;
  final String? lastErrorCode;
  final String? serverResponseJson;
  final String? serverRequestId;
}

class InventoryQueueRow {
  const InventoryQueueRow({
    required this.clientId,
    required this.opType,
    required this.allocation,
    required this.payloadJson,
    this.farmerProject,
    required this.status,
    required this.retryCount,
    this.lastErrorCode,
  });

  final String clientId;
  final String opType;
  final String allocation;
  final String payloadJson;
  final String? farmerProject;
  final String status;
  final int retryCount;
  final String? lastErrorCode;
}

class SyncRunRow {
  const SyncRunRow({
    required this.phase,
    required this.success,
    this.errorCode,
    this.requestId,
    required this.startedAt,
    this.finishedAt,
  });

  final String phase;
  final bool success;
  final String? errorCode;
  final String? requestId;
  final String startedAt;
  final String? finishedAt;
}

class ProjectionRow {
  const ProjectionRow({
    required this.kind,
    required this.name,
    this.block,
    this.sortKey,
    required this.payloadJson,
    required this.payload,
    required this.isDeleted,
  });

  final String kind;
  final String name;
  final String? block;
  final String? sortKey;
  final String payloadJson;
  final Map<String, dynamic> payload;
  final bool isDeleted;
}

LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    final dir = await getApplicationDocumentsDirectory();
    final file = File(p.join(dir.path, 'agriflow_mobile.sqlite'));
    return NativeDatabase.createInBackground(file);
  });
}
