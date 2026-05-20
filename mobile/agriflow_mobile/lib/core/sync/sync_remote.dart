import 'dart:convert';

import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';
import 'package:agriflow_mobile/core/network/api_envelope.dart';
import 'package:agriflow_mobile/core/network/sync_operation_builder.dart';
import 'package:agriflow_mobile/core/sync/push_result_applier.dart';

class SyncRemote {
  SyncRemote({
    required this.api,
    required this.config,
    required this.db,
    required this.applier,
  });

  final ApiClient api;
  final ApiConfig config;
  final AppDatabase db;
  final PushResultApplier applier;

  Future<ApiEnvelope<Map<String, dynamic>>> pushBatch(
    List<SyncQueueRow> pending,
  ) async {
    final operations = SyncOperationBuilder.fromQueueRows(pending);

    final envelope = await api.postMethod<Map<String, dynamic>>(
      methodUrl: config.methodUrl('agriflow.api.v1.sync.push'),
      data: {
        'device_id': config.deviceId,
        'pushed_at': DateTime.now().toUtc().toIso8601String(),
        'operations': operations,
      },
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );

    final data = envelope.data ?? {};
    final results = (data['results'] as List? ?? [])
        .map((e) => PushOpResult.fromJson(Map<String, dynamic>.from(e as Map)))
        .toList();
    await applier.apply(
      results: results,
      rawResponseJson: envelope.toJsonString(),
      requestId: envelope.requestId,
    );
    return envelope;
  }

  Future<ApiEnvelope<Map<String, dynamic>>> pullEntities({
    required Map<String, String?> modifiedSince,
  }) async {
    return api.postMethod(
      methodUrl: config.methodUrl('agriflow.api.v1.sync.pull'),
      data: {
        'device_id': config.deviceId,
        'entities': ['timeline', 'task', 'farmer_project'],
        'modified_since': modifiedSince,
        'include_deleted': true,
      },
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
  }
}
