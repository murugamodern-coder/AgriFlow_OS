import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final readinessRemoteProvider = Provider<ReadinessRemote>((ref) {
  return ReadinessRemote(
    api: ref.watch(apiClientProvider),
    config: ref.watch(apiConfigProvider),
  );
});

class AppReleaseInfo {
  const AppReleaseInfo({
    required this.updateRequired,
    required this.minVersion,
    required this.apkUrl,
  });

  final bool updateRequired;
  final String minVersion;
  final String apkUrl;
}

class ReadinessRemote {
  ReadinessRemote({required ApiClient api, required ApiConfig config})
      : _api = api,
        _config = config;

  final ApiClient _api;
  final ApiConfig _config;

  Future<AppReleaseInfo> checkRelease(String appVersion) async {
    final env = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl('agriflow.api.v1.readiness.app_release_check'),
      data: {'app_version': appVersion},
      parseData: (j) => Map<String, dynamic>.from(j as Map),
    );
    final d = env.data ?? {};
    return AppReleaseInfo(
      updateRequired: d['update_required'] == true,
      minVersion: d['min_version']?.toString() ?? '',
      apkUrl: d['apk_url']?.toString() ?? '',
    );
  }
}
