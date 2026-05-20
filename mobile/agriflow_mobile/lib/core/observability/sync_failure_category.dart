/// Categorizes sync errors for ops dashboards and Sentry tags.
abstract final class SyncFailureCategory {
  static String categorize(Object error, {String? code}) {
    final c = code ?? error.toString();
    if (c.contains('OFFLINE') || c.contains('Network')) return 'network';
    if (c.contains('AUTH') || c.contains('401') || c.contains('jwt')) return 'auth';
    if (c.contains('SYNC_CONFLICT') || c.contains('conflict')) return 'conflict';
    if (c.contains('PERM') || c.contains('403')) return 'permission';
    if (c.contains('VAL_') || c.contains('validation')) return 'validation';
    if (c.contains('inventory') || c.contains('STOCK')) return 'inventory';
    return 'unknown';
  }
}
