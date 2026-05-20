import 'dart:convert';

import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/network/sync_operation_builder.dart';
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('queue persistence proof — survives database reopen', () async {
    final executor = NativeDatabase.memory();
    final db1 = AppDatabase.forTesting(executor);
    await db1.ensureSchema();
    const cmid = '550e8400-e29b-41d4-a716-446655440099';
    await db1.enqueueMutation(
      clientMutationId: cmid,
      entity: 'task',
      opType: 'complete',
      payloadJson: jsonEncode({
        'payload': {'name': 'TSK-PERSIST', 'doc_version': 2},
      }),
      farmerProject: 'FP-2026-00007',
    );
    await db1.close();

    final db2 = AppDatabase.forTesting(executor);
    await db2.ensureSchema();
    final pending = await db2.pendingQueue();
    expect(pending.length, 1);
    expect(pending.first.clientMutationId, cmid);

    final ops = SyncOperationBuilder.fromQueueRows(pending);
    expect(ops.first['payload'], isA<Map>());
    expect((ops.first['payload'] as Map)['doc_version'], 2);
    await db2.close();
  });
}
