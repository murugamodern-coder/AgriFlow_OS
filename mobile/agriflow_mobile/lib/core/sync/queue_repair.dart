import 'dart:convert';

import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:drift/drift.dart';
import 'package:agriflow_mobile/core/observability/telemetry.dart';

/// Repairs corrupted / stuck sync queue rows (server remains authoritative).
class QueueRepairReport {
  const QueueRepairReport({
    required this.resetStuck,
    required this.removedInvalid,
    required this.deduped,
    required this.revalidated,
  });

  final int resetStuck;
  final int removedInvalid;
  final int deduped;
  final int revalidated;
}

class QueueRepair {
  QueueRepair(this._db);

  final AppDatabase _db;

  Future<QueueRepairReport> reconcile() async {
    var resetStuck = 0;
    var removedInvalid = 0;
    var deduped = 0;
    var revalidated = 0;

    final all = await _db.customSelect(
      'SELECT * FROM sync_queue_entries ORDER BY created_at ASC',
      readsFrom: {},
    ).get();

    final seen = <String, int>{};
    for (final row in all) {
      final cmid = row.read<String>('client_mutation_id') ?? '';
      final status = row.read<String>('status') ?? '';
      final payload = row.read<String>('payload_json') ?? '';

      if (cmid.isEmpty || cmid.length != 36) {
        await _db.customUpdate(
          'DELETE FROM sync_queue_entries WHERE id = ?',
          variables: [Variable.withInt(row.read<int>('id')!)],
          updates: {},
        );
        removedInvalid++;
        continue;
      }

      try {
        jsonDecode(payload);
        revalidated++;
      } catch (_) {
        await _db.customUpdate(
          'DELETE FROM sync_queue_entries WHERE id = ?',
          variables: [Variable.withInt(row.read<int>('id')!)],
          updates: {},
        );
        removedInvalid++;
        continue;
      }

      if (status == 'syncing') {
        await _db.markQueueRow(clientMutationId: cmid, status: 'pending');
        resetStuck++;
      }

      if (status == 'failed') {
        final retries = row.read<int>('retry_count') ?? 0;
        // Cap auto-heal retries; prefer manual sync after repeated failures.
        if (retries < 5) {
          await _db.markQueueRow(
            clientMutationId: cmid,
            status: 'pending',
            retryCount: retries + 1,
          );
          resetStuck++;
        } else if (retries == 5) {
          await _db.markQueueRow(
            clientMutationId: cmid,
            status: 'failed',
            lastErrorCode: 'QUEUE_MAX_RETRIES',
          );
        }
      }

      if (seen.containsKey(cmid)) {
        await _db.customUpdate(
          'DELETE FROM sync_queue_entries WHERE id = ?',
          variables: [Variable.withInt(row.read<int>('id')!)],
          updates: {},
        );
        deduped++;
      } else {
        seen[cmid] = row.read<int>('id')!;
      }
    }

    final report = QueueRepairReport(
      resetStuck: resetStuck,
      removedInvalid: removedInvalid,
      deduped: deduped,
      revalidated: revalidated,
    );
    Telemetry.log('info', 'queue_repair', 'reconcile complete', context: {
      'reset_stuck': resetStuck,
      'removed_invalid': removedInvalid,
      'deduped': deduped,
    });
    return report;
  }
}
