import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/errors/failure.dart';
import 'package:agriflow_mobile/core/observability/pilot_telemetry_service.dart';
import 'package:agriflow_mobile/core/observability/sync_diagnostics.dart';
import 'package:agriflow_mobile/core/observability/sync_failure_category.dart';
import 'package:agriflow_mobile/core/observability/telemetry.dart';
import 'package:agriflow_mobile/core/sync/inventory_queue.dart';
import 'package:agriflow_mobile/core/storage/hive_boxes.dart';
import 'package:agriflow_mobile/core/sync/projection_writer.dart';
import 'package:agriflow_mobile/core/sync/queue_repair.dart';
import 'package:agriflow_mobile/core/sync/adaptive_sync_policy.dart';
import 'package:agriflow_mobile/core/sync/retry_policy.dart';
import 'package:agriflow_mobile/core/sync/sync_correlation.dart';
import 'package:agriflow_mobile/core/sync/sync_remote.dart';
import 'package:agriflow_mobile/core/sync/sync_single_flight.dart';
import 'package:agriflow_mobile/core/sync/sync_status.dart';
import 'package:agriflow_mobile/core/network/tracing_interceptor.dart';
import 'package:agriflow_mobile/features/inventory/data/inventory_remote.dart';
import 'package:agriflow_mobile/features/notifications/data/notification_remote.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

class SyncOrchestrator {
  SyncOrchestrator({
    required AppDatabase db,
    required HiveStorage hive,
    required SyncRemote remote,
    required ProjectionWriter writer,
    required NotificationRemote notificationRemote,
    required Connectivity connectivity,
    TracingInterceptor? tracing,
    PilotTelemetryService? telemetry,
    InventoryQueue? inventoryQueue,
    InventoryRemote? inventoryRemote,
  })  : _db = db,
        _hive = hive,
        _remote = remote,
        _writer = writer,
        _notificationRemote = notificationRemote,
        _connectivity = connectivity,
        _tracing = tracing,
        _telemetry = telemetry,
        _inventoryQueue = inventoryQueue,
        _inventoryRemote = inventoryRemote;

  final AppDatabase _db;
  final HiveStorage _hive;
  final SyncRemote _remote;
  final ProjectionWriter _writer;
  final NotificationRemote _notificationRemote;
  final Connectivity _connectivity;
  final TracingInterceptor? _tracing;
  final PilotTelemetryService? _telemetry;
  final InventoryQueue? _inventoryQueue;
  final InventoryRemote? _inventoryRemote;
  final SyncSingleFlight _lock = SyncSingleFlight();

  static const _longOfflineHours = 72;
  final SyncCorrelation _correlation = SyncCorrelation();
  final RetryPolicy _retry = RetryPolicy();
  final AdaptiveSyncPolicy _adaptive = AdaptiveSyncPolicy();

  bool get isSyncing => _lock.isRunning;
  String get correlationId => _correlation.current;

  Future<SyncStatusSummary> syncNow({
    void Function(String phase)? onPhase,
    bool force = false,
  }) async {
    if (!force) {
      final connectivity = await _connectivity.checkConnectivity();
      final summary = await buildStatusSummary();
      final lastRaw = _hive.box(HiveBoxNames.syncMeta).get('last_success_at') as String?;
      final last = lastRaw != null ? DateTime.tryParse(lastRaw) : null;
      if (!_adaptive.shouldSyncNow(
        lastSuccessAt: last,
        connectivity: connectivity,
        pendingCount: summary.pendingCount,
      )) {
        return summary;
      }
    }
    return _lock.execute(() => _runSync(onPhase: onPhase));
  }

  Future<QueueRepairReport> repairQueue() => QueueRepair(_db).reconcile();

  Future<void> _logDiag(SyncDiagnostics d) async {
    await _db.logSyncRun(
      phase: d.phase,
      success: d.success,
      errorCode: d.errorCode,
      requestId: d.requestId,
      rawResponseJson: d.toJsonString(),
      startedAt: DateTime.now().toUtc(),
      finishedAt: DateTime.now().toUtc(),
    );
  }

  Future<SyncStatusSummary> _runSync({void Function(String phase)? onPhase}) async {
    _correlation.rotate();
    _tracing?.setSyncCorrelationId(_correlation.current);
    final runStarted = DateTime.now().toUtc();

    onPhase?.call('repair');
    await repairQueue();

    final connectivity = await _connectivity.checkConnectivity();
    if (connectivity.contains(ConnectivityResult.none)) {
      throw const NetworkFailure(code: 'OFFLINE');
    }
    final networkDelay = _adaptive.retryDelayForConnectivity(connectivity);

    try {
      final pending = await _db.pendingQueue();
      for (final row in pending) {
        await _db.markQueueRow(
          clientMutationId: row.clientMutationId,
          status: 'syncing',
        );
      }

      if (pending.isNotEmpty) {
        onPhase?.call('push');
        final pushStarted = DateTime.now().toUtc();
        final pushEnvelope = await _retry.run(
          () => _remote.pushBatch(pending),
          shouldRetry: (e) => e is! ApiFailure || e.code?.startsWith('SYNC_') != true,
          extraDelay: networkDelay,
        );
        await _logDiag(
          SyncDiagnostics(
            correlationId: _correlation.current,
            phase: 'push',
            success: pushEnvelope.ok,
            requestId: pushEnvelope.requestId,
            pendingCount: pending.length,
          ),
        );
      }

      onPhase?.call('pull');
      final pullStarted = DateTime.now().toUtc();
      final modifiedSince = _resolvePullWatermarks();
      final pullEnvelope = await _retry.run(
        () => _remote.pullEntities(modifiedSince: modifiedSince),
      );
      await _writer.applyPull(pullEnvelope.data ?? {});
      await _logDiag(
        SyncDiagnostics(
          correlationId: _correlation.current,
          phase: 'pull',
          success: pullEnvelope.ok,
          requestId: pullEnvelope.requestId,
          durationMs: DateTime.now().toUtc().difference(pullStarted).inMilliseconds,
        ),
      );

      onPhase?.call('notifications');
      final notifStarted = DateTime.now().toUtc();
      await _retry.run(() async {
        final notifList = await _notificationRemote.fetchInbox(limit: 50);
        await _writer.cacheNotifications(notifList);
      });
      await _logDiag(
        SyncDiagnostics(
          correlationId: _correlation.current,
          phase: 'notifications',
          success: true,
          durationMs: DateTime.now().toUtc().difference(notifStarted).inMilliseconds,
        ),
      );

      if (_inventoryQueue != null && _inventoryRemote != null) {
        onPhase?.call('inventory');
        final invReport = await _inventoryQueue!.replayPending(_inventoryRemote!);
        if (invReport.attempted > 0) {
          await _logDiag(
            SyncDiagnostics(
              correlationId: _correlation.current,
              phase: 'inventory_replay',
              success: invReport.failed == 0,
              extra: {
                'attempted': invReport.attempted,
                'success': invReport.success,
                'failed': invReport.failed,
                'conflicts': invReport.conflicts,
              },
            ),
          );
        }
      }

      final summary = await buildStatusSummary();
      _hive.box(HiveBoxNames.syncMeta).put(
        'last_success_at',
        DateTime.now().toUtc().toIso8601String(),
      );
      Telemetry.log('info', 'sync', 'run complete', context: {
        'correlation_id': _correlation.current,
        'pending': summary.pendingCount,
        'conflicts': summary.conflictCount,
        'duration_ms': DateTime.now().toUtc().difference(runStarted).inMilliseconds,
      });
      await _telemetry?.reportHeartbeat(correlationId: _correlation.current);
      return summary;
    } catch (e, st) {
      final category = SyncFailureCategory.categorize(
        e,
        code: e is Failure ? e.code : null,
      );
      Telemetry.recordError(e, stack: st, context: {
        'correlation_id': _correlation.current,
        'phase': 'sync_error',
        'failure_category': category,
      });
      await _logDiag(
        SyncDiagnostics(
          correlationId: _correlation.current,
          phase: 'error',
          success: false,
          errorCode: e is Failure ? e.code : e.runtimeType.toString(),
          extra: {'failure_category': category},
        ),
      );
      await _telemetry?.uploadDiagnostics(
        kind: 'sync_error',
        error: e,
      );
      await repairQueue();
      rethrow;
    } finally {
      _tracing?.clearSyncCorrelationId();
    }
  }

  Map<String, String?> _resolvePullWatermarks() {
    final lastRaw = _hive.box(HiveBoxNames.syncMeta).get('last_success_at') as String?;
    final last = lastRaw != null ? DateTime.tryParse(lastRaw) : null;
    if (last != null &&
        DateTime.now().toUtc().difference(last).inHours >= _longOfflineHours) {
      return {};
    }
    return {
      'timeline': _hive.getWatermark('timeline'),
      'task': _hive.getWatermark('task'),
      'farmer_project': _hive.getWatermark('farmer_project'),
    };
  }

  Future<SyncStatusSummary> buildStatusSummary() async {
    final pending = await _db.pendingCount();
    final conflicts = await _db.conflictCount();
    final last = await _db.lastSyncRun();
    return SyncStatusSummary(
      pendingCount: pending,
      conflictCount: conflicts,
      lastSuccessAt: last?.success == true
          ? DateTime.tryParse(last!.startedAt)
          : null,
      lastPhase: last?.phase,
      lastRequestId: last?.requestId,
      lastCorrelationId: _correlation.current,
      isRunning: _lock.isRunning,
      lastErrorCode: last?.errorCode,
    );
  }
}
