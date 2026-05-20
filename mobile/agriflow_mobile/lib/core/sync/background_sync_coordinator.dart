import 'dart:async';

import 'package:agriflow_mobile/core/observability/sentry_bootstrap.dart';
import 'package:agriflow_mobile/core/observability/telemetry.dart';
import 'package:agriflow_mobile/core/sync/sync_orchestrator.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/widgets.dart';

/// Schedules sync on connectivity restore, app resume, and periodic interval.
class BackgroundSyncCoordinator with WidgetsBindingObserver {
  BackgroundSyncCoordinator({
    required SyncOrchestrator orchestrator,
    required Connectivity connectivity,
    Duration interval = const Duration(minutes: 15),
  })  : _orchestrator = orchestrator,
        _connectivity = connectivity,
        _interval = interval;

  final SyncOrchestrator _orchestrator;
  final Connectivity _connectivity;
  final Duration _interval;
  StreamSubscription<List<ConnectivityResult>>? _connSub;
  Timer? _timer;
  bool _disposed = false;

  void start() {
    WidgetsBinding.instance.addObserver(this);
    _connSub = _connectivity.onConnectivityChanged.listen((results) {
      if (!results.contains(ConnectivityResult.none)) {
        unawaited(_safeSync('connectivity'));
      }
    });
    _timer = Timer.periodic(_interval, (_) => unawaited(_safeSync('periodic')));
  }

  void dispose() {
    _disposed = true;
    WidgetsBinding.instance.removeObserver(this);
    _connSub?.cancel();
    _timer?.cancel();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      unawaited(_safeSync('resume'));
    }
  }

  Future<void> _safeSync(String trigger) async {
    if (_disposed || _orchestrator.isSyncing) return;
    try {
      Telemetry.log('info', 'bg_sync', 'trigger', context: {'trigger': trigger});
      await _orchestrator.syncNow();
    } catch (e, st) {
      await SentryBootstrap.capture(e, stack: st, context: {'trigger': trigger});
    }
  }
}
