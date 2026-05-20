class SyncStatusSummary {
  const SyncStatusSummary({
    required this.pendingCount,
    required this.conflictCount,
    required this.lastSuccessAt,
    required this.lastPhase,
    required this.lastRequestId,
    required this.isRunning,
    required this.lastErrorCode,
    this.lastCorrelationId,
  });

  final int pendingCount;
  final int conflictCount;
  final DateTime? lastSuccessAt;
  final String? lastPhase;
  final String? lastRequestId;
  final String? lastCorrelationId;
  final bool isRunning;
  final String? lastErrorCode;

  static const empty = SyncStatusSummary(
    pendingCount: 0,
    conflictCount: 0,
    lastSuccessAt: null,
    lastPhase: null,
    lastRequestId: null,
    lastCorrelationId: null,
    isRunning: false,
    lastErrorCode: null,
  );
}
