import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/config/env.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final pilotOpsRemoteProvider = Provider<PilotOpsRemote>((ref) {
  return PilotOpsRemote(
    api: ref.watch(apiClientProvider),
    config: ref.watch(apiConfigProvider),
  );
});

class PilotOpsRemote {
  PilotOpsRemote({required ApiClient api, required ApiConfig config})
      : _api = api,
        _config = config;

  final ApiClient _api;
  final ApiConfig _config;

  static const _methodPrefix = 'agriflow.api.v1.pilot_ops';

  Future<void> heartbeat(Map<String, dynamic> payload) async {
    await _api.postMethod<void>(
      methodUrl: _config.methodUrl('$_methodPrefix.heartbeat'),
      data: payload,
      parseData: (_) {},
    );
  }

  Future<void> uploadDiagnostics(Map<String, dynamic> payload) async {
    await _api.postMethod<void>(
      methodUrl: _config.methodUrl('$_methodPrefix.diagnostic_upload'),
      data: payload,
      parseData: (_) {},
    );
  }

  Future<String> submitFeedback(Map<String, dynamic> payload) async {
    final env = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl('$_methodPrefix.feedback_submit'),
      data: payload,
      parseData: (j) => Map<String, dynamic>.from(j as Map),
    );
    return (env.data?['feedback_id'] ?? '').toString();
  }

  Future<List<Map<String, dynamic>>> fetchOnboardingSteps() async {
    final env = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl('$_methodPrefix.onboarding_checklist'),
      data: {},
      parseData: (j) => Map<String, dynamic>.from(j as Map),
    );
    final steps = env.data?['steps'];
    if (steps is List) {
      return steps.map((e) => Map<String, dynamic>.from(e as Map)).toList();
    }
    return const [];
  }

  static Map<String, dynamic> devicePayload({
    required String deviceId,
    required int queuePending,
    required int queueConflict,
    required int queueFailed,
    String? lastSyncAt,
    String? lastCorrelationId,
    Map<String, dynamic>? diagnostics,
  }) {
    return {
      'device_id': deviceId,
      'app_version': Env.appVersion,
      'build_number': Env.appVersion,
      'platform': 'flutter',
      'queue_pending': queuePending,
      'queue_conflict': queueConflict,
      'queue_failed': queueFailed,
      if (lastSyncAt != null) 'last_sync_at': lastSyncAt,
      if (lastCorrelationId != null) 'last_correlation_id': lastCorrelationId,
      if (diagnostics != null) 'diagnostics': diagnostics,
    };
  }
}
