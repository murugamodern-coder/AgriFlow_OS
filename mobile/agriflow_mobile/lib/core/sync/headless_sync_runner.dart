import 'package:agriflow_mobile/core/config/env.dart';
import 'package:agriflow_mobile/core/storage/secure_token_store.dart';
import 'package:agriflow_mobile/core/observability/telemetry.dart';
import 'package:dio/dio.dart';

/// Minimal headless ack for Workmanager (JWT when logged in).
abstract final class HeadlessSyncRunner {
  static Future<bool> run() async {
    if (Env.apiBaseUrl.isEmpty) return false;
    final access = await SecureTokenStore().readAccessToken();
    if (access == null || access.isEmpty) return false;

    final base = Env.apiBaseUrl.replaceAll(RegExp(r'/+$'), '');
    final dio = Dio(
      BaseOptions(
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $access',
        },
      ),
    );

    try {
      await dio.post<dynamic>(
        '$base/api/method/agriflow.api.v1.ops.background_sync_ack',
        data: {
          'data': {
            'device_id': Env.deviceId.isNotEmpty ? Env.deviceId : 'headless',
            'success': true,
            'phase': 'workmanager',
            'app_version': Env.appVersion,
          },
        },
      );
      Telemetry.log('info', 'headless_sync', 'ack ok');
      return true;
    } catch (e, st) {
      Telemetry.recordError(e, stack: st, context: {'phase': 'headless_sync'});
      return false;
    }
  }
}
