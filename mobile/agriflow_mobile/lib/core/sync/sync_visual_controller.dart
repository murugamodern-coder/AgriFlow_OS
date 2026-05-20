import 'dart:async';

import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/storage/hive_boxes.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';

enum SyncBarMode { online, offline, syncing, justSynced }

/// Drives demo-visible sync UI (app bar, overlay, toasts).
class SyncVisualController extends ChangeNotifier {
  SyncVisualController({
    required AppDatabase db,
    required HiveStorage hive,
    required Connectivity connectivity,
  })  : _db = db,
        _hive = hive,
        _connectivity = connectivity {
    _simulateOffline = _hive.box(HiveBoxNames.appPrefs).get('simulate_offline') == true;
    _connectivity.onConnectivityChanged.listen((_) => _refreshConnectivity());
    _refreshConnectivity();
    _pollTimer = Timer.periodic(const Duration(seconds: 2), (_) => _refreshCounts());
    _refreshCounts();
  }

  final AppDatabase _db;
  final HiveStorage _hive;
  final Connectivity _connectivity;
  late Timer _pollTimer;

  bool _simulateOffline = false;
  bool _deviceOnline = true;
  int _pendingCount = 0;
  bool _isRunning = false;
  int _syncCurrent = 0;
  int _syncTotal = 0;
  String? _phase;
  DateTime? _lastSuccessAt;
  bool _showFlying = false;
  bool _justSynced = false;
  Timer? _justSyncedTimer;

  bool get simulateOffline => _simulateOffline;
  bool get isEffectivelyOnline => _deviceOnline && !_simulateOffline;
  int get pendingCount => _pendingCount;
  bool get isRunning => _isRunning;
  int get syncCurrent => _syncCurrent;
  int get syncTotal => _syncTotal;
  String? get phase => _phase;
  DateTime? get lastSuccessAt => _lastSuccessAt;
  bool get showFlyingOverlay => _showFlying;

  SyncBarMode get barMode {
    if (_justSynced && !_isRunning) return SyncBarMode.justSynced;
    if (_isRunning) return SyncBarMode.syncing;
    if (!isEffectivelyOnline) return SyncBarMode.offline;
    return SyncBarMode.online;
  }

  Future<void> setSimulateOffline(bool value) async {
    _simulateOffline = value;
    await _hive.box(HiveBoxNames.appPrefs).put('simulate_offline', value);
    notifyListeners();
  }

  void onSyncStarted({required int total}) {
    _isRunning = true;
    _syncTotal = total;
    _syncCurrent = 0;
    _phase = 'repair';
    _showFlying = total > 0;
    _justSynced = false;
    notifyListeners();
  }

  void onSyncPhase(String phase, {int? current, int? total}) {
    _phase = phase;
    if (current != null) _syncCurrent = current;
    if (total != null) _syncTotal = total;
    notifyListeners();
  }

  void onSyncFinished({required bool success}) {
    _isRunning = false;
    _showFlying = false;
    _syncCurrent = 0;
    _syncTotal = 0;
    _phase = null;
    if (success) {
      final raw = _hive.box(HiveBoxNames.syncMeta).get('last_success_at') as String?;
      _lastSuccessAt = raw != null ? DateTime.tryParse(raw) : DateTime.now().toUtc();
      _justSynced = true;
      _justSyncedTimer?.cancel();
      _justSyncedTimer = Timer(const Duration(seconds: 8), () {
        _justSynced = false;
        notifyListeners();
      });
    }
    _refreshCounts();
    notifyListeners();
  }

  Future<void> _refreshConnectivity() async {
    final results = await _connectivity.checkConnectivity();
    _deviceOnline = !results.contains(ConnectivityResult.none);
    notifyListeners();
  }

  Future<void> _refreshCounts() async {
    _pendingCount = await _db.pendingCount();
    final raw = _hive.box(HiveBoxNames.syncMeta).get('last_success_at') as String?;
    if (raw != null) _lastSuccessAt = DateTime.tryParse(raw);
    if (!_isRunning) notifyListeners();
  }

  Future<void> refresh() async {
    await _refreshConnectivity();
    await _refreshCounts();
  }

  @override
  void dispose() {
    _pollTimer.cancel();
    _justSyncedTimer?.cancel();
    super.dispose();
  }
}
