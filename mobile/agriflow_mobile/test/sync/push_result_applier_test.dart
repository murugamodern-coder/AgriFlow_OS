import 'dart:convert';

import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/sync/push_result_applier.dart';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  late AppDatabase db;
  late PushResultApplier applier;

  setUp(() async {
    db = AppDatabase.forTesting(NativeDatabase.memory());
    await db.ensureSchema();
    applier = PushResultApplier(db);
  });

  tearDown(() async {
    await db.close();
  });

  test('replay queue proof — success marks synced and records idempotency', () async {
    const cmid = '550e8400-e29b-41d4-a716-446655440000';
    await db.enqueueMutation(
      clientMutationId: cmid,
      entity: 'task',
      opType: 'create',
      payloadJson: jsonEncode({'payload': {}}),
    );

    await applier.apply(
      results: [
        PushOpResult(
          clientMutationId: cmid,
          status: 'skipped',
          serverName: 'TSK-2026-00001',
        ),
      ],
      rawResponseJson: '{"ok":true}',
      requestId: 'req-replay-1',
    );

    final rows = await db.pendingQueue();
    expect(rows, isEmpty);

    final idem = await db.findIdempotency(cmid);
    expect(idem, isNotNull);
    expect(idem!['server_name'], 'TSK-2026-00001');
  });

  test('replay queue proof — conflict persists conflict state + server json', () async {
    const cmid = '661e8400-e29b-41d4-a716-446655440001';
    await db.enqueueMutation(
      clientMutationId: cmid,
      entity: 'task',
      opType: 'update',
      payloadJson: jsonEncode({'doc_version': 1}),
    );

    await applier.apply(
      results: [
        PushOpResult(
          clientMutationId: cmid,
          status: 'conflict',
          errorCode: 'SYNC_CONFLICT_LWW',
          conflict: {'server_doc_version': 12},
        ),
      ],
      rawResponseJson: '{"summary":{"conflict":1}}',
      requestId: 'req-conflict-1',
    );

    final pending = await db.pendingQueue();
    expect(pending, isEmpty);
    final all = await db.customSelect(
      'SELECT status, server_request_id, server_response_json FROM sync_queue_entries WHERE client_mutation_id = ?',
      variables: [Variable.withString(cmid)],
      readsFrom: {},
    ).getSingle();
    expect(all.read<String>('status'), 'conflict');
    expect(all.read<String>('server_request_id'), 'req-conflict-1');
    expect(all.read<String>('server_response_json'), contains('conflict'));
  });
}
