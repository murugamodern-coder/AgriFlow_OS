import 'dart:io';

import 'package:agriflow_mobile/core/config/env.dart';
import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/observability/sync_diagnostics.dart';
import 'package:agriflow_mobile/core/observability/telemetry.dart';
import 'package:agriflow_mobile/core/storage/hive_boxes.dart';
import 'package:agriflow_mobile/features/pilot_ops/data/pilot_ops_remote.dart';
import 'package:uuid/uuid.dart';

/// Heartbeat + diagnostic upload for pilot deployment (best-effort, non-blocking).
class PilotTelemetryService {
  PilotTelemetryService({
    required PilotOpsRemote remote,
    required AppDatabase db,
    required HiveStorage hive,
  })  : _remote = remote,
        _db = db,
        _hive = hive;

  final PilotOpsRemote _remote;
  final AppDatabase _db;
  final HiveStorage _hive;
  final _uuid = const Uuid();

  static const _deviceKey = 'pilot_device_id';
  static const _lastHeartbeatKey = 'last_heartbeat_at';
  static const _heartbeatMinMinutes = 30;

  Future<String> deviceId() async {
    final fromEnv = Env.deviceId.trim();
    if (fromEnv.isNotEmpty) return fromEnv;
    final box = _hive.box(HiveBoxNames.appPrefs);
    var id = box.get(_deviceKey) as String?;
    if (id == null || id.isEmpty) {
      id = _uuid.v4();
      await box.put(_deviceKey, id);
    }
    return id;
  }

  Future<void> reportHeartbeat({String? correlationId, bool force = false}) async {
    try {
      final prefs = _hive.box(HiveBoxNames.appPrefs);
      final lastRaw = prefs.get(_lastHeartbeatKey) as String?;
      final last = lastRaw != null ? DateTime.tryParse(lastRaw) : null;
      if (!force &&
          last != null &&
          DateTime.now().toUtc().difference(last).inMinutes < _heartbeatMinMinutes) {
        return;
      }
      final pending = await _db.queuePendingOnlyCount();
      final conflicts = await _db.conflictCount();
      final failed = await _db.failedCount();
      final lastRun = await _db.lastSyncRun();
      await _remote.heartbeat(
        PilotOpsRemote.devicePayload(
          deviceId: await deviceId(),
          queuePending: pending,
          queueConflict: conflicts,
          queueFailed: failed,
          lastCorrelationId: correlationId,
          lastSyncAt: lastRun?.finishedAt?.toIso8601String(),
          diagnostics: {
            'platform': Platform.operatingSystem,
            'app_version': Env.appVersion,
            'os': Platform.operatingSystemVersion,
          },
        ),
      );
      await prefs.put(_lastHeartbeatKey, DateTime.now().toUtc().toIso8601String());
    } catch (e, st) {
      Telemetry.recordError(e, stack: st, context: {'phase': 'heartbeat'});
    }
  }

  Future<void> uploadDiagnostics({
    required String kind,
    SyncDiagnostics? lastSync,
    Object? error,
  }) async {
    try {
      final payload = PilotOpsRemote.devicePayload(
        deviceId: await deviceId(),
        queuePending: await _db.queuePendingOnlyCount(),
        queueConflict: await _db.conflictCount(),
        queueFailed: await _db.failedCount(),
        diagnostics: {
          'kind': kind,
          if (lastSync != null) 'last_sync': lastSync.toJson(),
          if (error != null) 'error': error.toString(),
        },
      );
      await _remote.uploadDiagnostics(payload);
    } catch (e, st) {
      Telemetry.recordError(e, stack: st, context: {'phase': 'diagnostic_upload'});
    }
  }
}
