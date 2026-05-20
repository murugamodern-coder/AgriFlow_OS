import 'dart:convert';

import 'package:agriflow_mobile/core/database/app_database.dart';

class PushOpResult {
  const PushOpResult({
    required this.clientMutationId,
    required this.status,
    this.serverName,
    this.conflict,
    this.errorCode,
  });

  final String clientMutationId;
  final String status;
  final String? serverName;
  final Map<String, dynamic>? conflict;
  final String? errorCode;

  factory PushOpResult.fromJson(Map<String, dynamic> json) {
    return PushOpResult(
      clientMutationId: json['client_mutation_id'] as String? ??
          json['op_id'] as String? ??
          '',
      status: json['status'] as String? ?? 'failed',
      serverName: json['name'] as String?,
      conflict: json['conflict'] as Map<String, dynamic>?,
      errorCode: json['error_code'] as String?,
    );
  }
}

/// Applies sync.push results to queue + idempotency (replay-safe).
class PushResultApplier {
  PushResultApplier(this._db);

  final AppDatabase _db;

  Future<void> apply({
    required List<PushOpResult> results,
    required String rawResponseJson,
    required String? requestId,
  }) async {
    for (final result in results) {
      final encoded = jsonEncode({
        'client_mutation_id': result.clientMutationId,
        'status': result.status,
        if (result.serverName != null) 'name': result.serverName,
        if (result.conflict != null) 'conflict': result.conflict,
      });
      switch (result.status) {
        case 'success':
        case 'skipped':
          await _db.markQueueRow(
            clientMutationId: result.clientMutationId,
            status: 'synced',
            serverResponseJson: rawResponseJson,
            serverRequestId: requestId,
          );
          await _db.recordIdempotency(
            clientMutationId: result.clientMutationId,
            entity: 'unknown',
            serverName: result.serverName,
            resultJson: encoded,
          );
        case 'conflict':
          await _db.markQueueRow(
            clientMutationId: result.clientMutationId,
            status: 'conflict',
            lastErrorCode: result.errorCode ?? 'SYNC_CONFLICT_LWW',
            serverResponseJson: rawResponseJson,
            serverRequestId: requestId,
          );
        default:
          await _db.markQueueRow(
            clientMutationId: result.clientMutationId,
            status: 'failed',
            lastErrorCode: result.errorCode ?? 'SYNC_PARTIAL_FAILURE',
            serverResponseJson: rawResponseJson,
            serverRequestId: requestId,
            retryCount: 1,
          );
      }
    }
  }
}
