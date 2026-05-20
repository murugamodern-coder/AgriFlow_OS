import 'dart:convert';

import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/features/inventory/data/inventory_remote.dart';
import 'package:uuid/uuid.dart';

/// Offline-first inventory mutations — replayed after sync.push (not in sync.push entity set).
class InventoryQueue {
  InventoryQueue(this._db);

  final AppDatabase _db;
  final _uuid = const Uuid();

  Future<String> enqueueConsume({
    required String allocation,
    required double qty,
    required int docVersion,
    String? batchNo,
    String? farmerProject,
  }) async {
    final clientId = _uuid.v4().replaceAll('-', '').substring(0, 28);
    await _db.enqueueInventoryOp(
      clientId: clientId,
      opType: 'consume',
      allocation: allocation,
      payloadJson: jsonEncode({
        'allocation': allocation,
        'qty': qty,
        'doc_version': docVersion,
        'client_id': clientId,
        if (batchNo != null) 'batch_no': batchNo,
      }),
      farmerProject: farmerProject,
    );
    return clientId;
  }

  Future<InventoryReplayReport> replayPending(InventoryRemote remote) async {
    final pending = await _db.pendingInventoryOps();
    var success = 0;
    var failed = 0;
    var conflicts = 0;

    for (final row in pending) {
      await _db.markInventoryOp(clientId: row.clientId, status: 'syncing');
      try {
        final payload = jsonDecode(row.payloadJson) as Map<String, dynamic>;
        if (row.opType == 'consume') {
          await remote.consume(
            allocation: payload['allocation'] as String,
            qty: (payload['qty'] as num).toDouble(),
            docVersion: payload['doc_version'] as int,
            clientId: row.clientId,
            batchNo: payload['batch_no'] as String?,
          );
        }
        await _db.markInventoryOp(clientId: row.clientId, status: 'success');
        success++;
      } catch (e) {
        final msg = e.toString();
        final status = msg.contains('conflict') || msg.contains('doc_version')
            ? 'conflict'
            : 'failed';
        if (status == 'conflict') {
          conflicts++;
        } else {
          failed++;
        }
        await _db.markInventoryOp(
          clientId: row.clientId,
          status: status,
          lastErrorCode: msg.length > 120 ? msg.substring(0, 120) : msg,
        );
      }
    }
    return InventoryReplayReport(
      attempted: pending.length,
      success: success,
      failed: failed,
      conflicts: conflicts,
    );
  }
}

class InventoryReplayReport {
  const InventoryReplayReport({
    required this.attempted,
    required this.success,
    required this.failed,
    required this.conflicts,
  });

  final int attempted;
  final int success;
  final int failed;
  final int conflicts;
}
