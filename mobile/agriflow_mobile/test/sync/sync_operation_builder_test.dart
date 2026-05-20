import 'dart:convert';

import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/network/sync_operation_builder.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('sync.push operation shape matches Phase 11 contract', () {
    const row = SyncQueueRow(
      id: 1,
      clientMutationId: 'cmid-1',
      entity: 'task',
      opType: 'complete',
      payloadJson: '{"payload":{"name":"TSK-1","doc_version":3}}',
      farmerProject: 'FP-2026-00007',
      status: 'pending',
      retryCount: 0,
    );
    final op = SyncOperationBuilder.fromQueueRows([row]).single;
    expect(op['client_mutation_id'], 'cmid-1');
    expect(op['entity'], 'task');
    expect(op['op_type'], 'complete');
    expect(op['payload'], jsonDecode('{"name":"TSK-1","doc_version":3}'));
  });
}
