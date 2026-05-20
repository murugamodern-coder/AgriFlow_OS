import 'dart:async';

/// Generic single-flight helper (tests + optional reuse).
class SyncLock {
  Completer<void>? _inFlight;

  bool get isLocked => _inFlight != null && !_inFlight!.isCompleted;

  Future<T> runExclusive<T>(Future<T> Function() action) async {
    if (_inFlight != null) {
      await _inFlight!.future;
      throw StateError('Already ran while waiting');
    }
    final completer = Completer<void>();
    _inFlight = completer;
    try {
      return await action();
    } finally {
      completer.complete();
      _inFlight = null;
    }
  }
}
