import 'package:connectivity_plus/connectivity_plus.dart';

/// Adaptive sync intervals — reduces battery/network use in production.
class AdaptiveSyncPolicy {
  AdaptiveSyncPolicy({this.minIntervalMinutes = 15, this.maxIntervalMinutes = 120});

  final int minIntervalMinutes;
  final int maxIntervalMinutes;

  static const _lastSyncKey = 'adaptive_last_sync_at';

  bool shouldSyncNow({
    required DateTime? lastSuccessAt,
    required List<ConnectivityResult> connectivity,
    required int pendingCount,
  }) {
    if (connectivity.contains(ConnectivityResult.none)) {
      return false;
    }
    if (pendingCount > 0) {
      return true;
    }
    final last = lastSuccessAt ?? DateTime.fromMillisecondsSinceEpoch(0);
    final elapsed = DateTime.now().toUtc().difference(last);
    final onWifi = connectivity.contains(ConnectivityResult.wifi);
    final interval = onWifi ? minIntervalMinutes : maxIntervalMinutes;
    return elapsed.inMinutes >= interval;
  }

  Duration retryDelayForConnectivity(List<ConnectivityResult> connectivity) {
    final onWifi = connectivity.contains(ConnectivityResult.wifi);
    final base = onWifi ? 500 : 1500;
    return Duration(milliseconds: base);
  }
}
