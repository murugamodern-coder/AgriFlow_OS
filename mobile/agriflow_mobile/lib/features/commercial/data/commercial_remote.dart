import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final commercialRemoteProvider = Provider<CommercialRemote>((ref) {
  return CommercialRemote(
    api: ref.watch(apiClientProvider),
    config: ref.watch(apiConfigProvider),
  );
});

class DeviceHealthSummary {
  const DeviceHealthSummary({
    required this.healthScore,
    required this.stale,
  });

  final int? healthScore;
  final bool stale;
}

class CommercialRemote {
  CommercialRemote({required ApiClient api, required ApiConfig config})
      : _api = api,
        _config = config;

  final ApiClient _api;
  final ApiConfig _config;

  Future<DeviceHealthSummary?> fetchDeviceHealth() async {
    try {
      final env = await _api.postMethod<Map<String, dynamic>>(
        methodUrl: _config.methodUrl(
          'agriflow.api.v1.commercial.device_health_for_officer',
        ),
        data: {},
        parseData: (j) => Map<String, dynamic>.from(j as Map),
      );
      final d = env.data;
      if (d == null || d['health_score'] == null) return null;
      return DeviceHealthSummary(
        healthScore: (d['health_score'] as num?)?.toInt(),
        stale: d['stale'] == true,
      );
    } catch (_) {
      return null;
    }
  }
}
