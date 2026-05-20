import 'dart:convert';

/// Structured sync diagnostics persisted to Drift sync_runs.
class SyncDiagnostics {
  const SyncDiagnostics({
    required this.correlationId,
    required this.phase,
    required this.success,
    this.requestId,
    this.errorCode,
    this.pendingCount,
    this.conflictCount,
    this.durationMs,
    this.extra,
  });

  final String correlationId;
  final String phase;
  final bool success;
  final String? requestId;
  final String? errorCode;
  final int? pendingCount;
  final int? conflictCount;
  final int? durationMs;
  final Map<String, Object?>? extra;

  String toJsonString() => jsonEncode({
        'correlation_id': correlationId,
        'phase': phase,
        'success': success,
        if (requestId != null) 'request_id': requestId,
        if (errorCode != null) 'error_code': errorCode,
        if (pendingCount != null) 'pending_count': pendingCount,
        if (conflictCount != null) 'conflict_count': conflictCount,
        if (durationMs != null) 'duration_ms': durationMs,
        if (extra != null) ...extra!,
      });
}
