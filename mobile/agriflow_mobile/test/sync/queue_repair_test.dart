import 'dart:convert';

import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/sync/queue_repair.dart';
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('queue repair removes invalid JSON and dedupes cmid', () async {
    final db = AppDatabase.forTesting(NativeDatabase.memory());
    await db.ensureSchema();
    const cmid = '550e8400-e29b-41d4-a716-446655440088';
    await db.enqueueMutation(
      clientMutationId: cmid,
      entity: 'task',
      opType: 'complete',
      payloadJson: jsonEncode({'payload': {'name': 'T', 'doc_version': 1}}),
    );
    await db.enqueueMutation(
      clientMutationId: cmid,
      entity: 'task',
      opType: 'complete',
      payloadJson: jsonEncode({'payload': {'name': 'T', 'doc_version': 1}}),
    );
    await db.customInsert(
      '''
INSERT INTO sync_queue_entries (
  client_mutation_id, entity, op_type, payload_json, status, retry_count, created_at, updated_at
) VALUES ('bad', 'task', 'complete', 'not-json', 'pending', 0, '2026-01-01', '2026-01-01')
''',
      variables: [],
      updates: {},
    );

    final report = await QueueRepair(db).reconcile();
    expect(report.removedInvalid, greaterThanOrEqualTo(1));
    expect(report.deduped, greaterThanOrEqualTo(1));
    final pending = await db.pendingQueue();
    expect(pending.length, 1);
    expect(pending.first.clientMutationId, cmid);
    await db.close();
  });
}
