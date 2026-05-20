import 'package:agriflow_mobile/core/config/env.dart';

class ApiConfig {
  const ApiConfig({required this.baseUrl, required this.deviceId});

  final String baseUrl;
  final String deviceId;

  factory ApiConfig.fromEnv() {
    Env.assertConfigured();
    final base = Env.apiBaseUrl.replaceAll(RegExp(r'/+$'), '');
    final device = Env.deviceId.isNotEmpty
        ? Env.deviceId
        : 'agriflow-mobile-dev';
    return ApiConfig(baseUrl: base, deviceId: device);
  }

  String methodUrl(String methodPath) {
    return '$baseUrl/api/method/$methodPath';
  }
}
