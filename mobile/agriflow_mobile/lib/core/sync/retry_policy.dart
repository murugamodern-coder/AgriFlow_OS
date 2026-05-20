import 'dart:math';

/// Exponential backoff for retry-safe operations (sync phases).
class RetryPolicy {
  RetryPolicy({
    this.maxAttempts = 3,
    this.baseDelayMs = 500,
    this.maxDelayMs = 8000,
  });

  final int maxAttempts;
  final int baseDelayMs;
  final int maxDelayMs;

  Duration delayForAttempt(int attempt) {
    final exp = min(baseDelayMs * pow(2, attempt), maxDelayMs).toInt();
    final jitter = (exp * 0.15 * (attempt % 3)).toInt();
    return Duration(milliseconds: exp + jitter);
  }

  Future<T> run<T>(
    Future<T> Function() action, {
    bool Function(Object error)? shouldRetry,
    Duration? extraDelay,
  }) async {
    Object? lastError;
    for (var attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        return await action();
      } catch (e) {
        lastError = e;
        final retry = shouldRetry?.call(e) ?? _defaultShouldRetry(e);
        if (!retry || attempt >= maxAttempts - 1) rethrow;
        final base = delayForAttempt(attempt);
        await Future<void>.delayed(
          extraDelay != null ? base + extraDelay : base,
        );
      }
    }
    throw lastError ?? StateError('retry exhausted');
  }

  bool _defaultShouldRetry(Object error) {
    final s = error.toString().toLowerCase();
    return s.contains('connection') ||
        s.contains('timeout') ||
        s.contains('offline') ||
        s.contains('socket');
  }
}
