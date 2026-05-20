import 'dart:async';

/// Single-flight: concurrent callers share the same in-flight future.
class SyncSingleFlight {
  Future<dynamic>? _inFlight;

  bool get isRunning => _inFlight != null;

  Future<T> execute<T>(Future<T> Function() work) {
    if (_inFlight != null) {
      return _inFlight! as Future<T>;
    }
    final future = _run(work);
    _inFlight = future;
    return future;
  }

  Future<T> _run<T>(Future<T> Function() work) async {
    try {
      return await work();
    } finally {
      _inFlight = null;
    }
  }
}

class SyncAlreadyRunningException implements Exception {
  @override
  String toString() => 'Sync already running';
}
