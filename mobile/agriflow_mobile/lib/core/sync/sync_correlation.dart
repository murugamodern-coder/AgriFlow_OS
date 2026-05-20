import 'package:uuid/uuid.dart';

/// Per-run sync correlation ID (matches server X-Sync-Correlation-Id).
class SyncCorrelation {
  SyncCorrelation() : _uuid = const Uuid();

  final Uuid _uuid;
  String? _current;

  String get current => _current ??= _uuid.v4();

  void rotate() => _current = _uuid.v4();

  void clear() => _current = null;
}
