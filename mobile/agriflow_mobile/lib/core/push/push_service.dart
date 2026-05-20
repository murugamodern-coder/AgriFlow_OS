import 'package:agriflow_mobile/app/router/deep_link.dart';
import 'package:agriflow_mobile/core/config/env.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';
import 'package:agriflow_mobile/core/observability/pilot_telemetry_service.dart';
import 'package:agriflow_mobile/core/observability/telemetry.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:go_router/go_router.dart';

/// Push foundation — token registration + local notification deep links.
class PushService {
  PushService({
    required ApiClient api,
    required PilotTelemetryService telemetry,
    FlutterLocalNotificationsPlugin? notifications,
  })  : _api = api,
        _telemetry = telemetry,
        _notifications = notifications ?? FlutterLocalNotificationsPlugin();

  final ApiClient _api;
  final PilotTelemetryService _telemetry;
  final FlutterLocalNotificationsPlugin _notifications;
  static const _channelId = 'agriflow_ops';

  Future<void> initialize({void Function(String location)? onNavigate}) async {
    const android = AndroidInitializationSettings('@mipmap/ic_launcher');
    const ios = DarwinInitializationSettings();
    await _notifications.initialize(
      const InitializationSettings(android: android, iOS: ios),
      onDidReceiveNotificationResponse: (response) {
        final payload = response.payload;
        if (payload != null && payload.isNotEmpty) {
          final loc = DeepLinkParser.toLocation(payload);
          if (loc != null) onNavigate?.call(loc);
        }
      },
    );
    await registerToken();
  }

  Future<void> registerToken() async {
    try {
      final deviceId = await _telemetry.deviceId();
      final fcmToken = Env.fcmToken.trim();
      final token = fcmToken.isNotEmpty
          ? fcmToken
          : (Env.pushDebugStub ? 'debug-push-$deviceId' : deviceId);
      await _api.postMethod<void>(
        methodUrl: '/api/method/agriflow.api.v1.push.register_token',
        data: {
          'device_id': deviceId,
          'push_token': token,
          'platform': 'flutter',
          'app_version': Env.appVersion,
        },
        parseData: (_) {},
      );
    } catch (e, st) {
      Telemetry.recordError(e, stack: st, context: {'phase': 'push_register'});
    }
  }

  Future<void> showLocalDeepLink({
    required String title,
    required String deepLink,
  }) async {
    const android = AndroidNotificationDetails(
      _channelId,
      'AgriFlow',
      channelDescription: 'Task and sync alerts',
      importance: Importance.defaultImportance,
    );
    await _notifications.show(
      DateTime.now().millisecondsSinceEpoch ~/ 1000,
      title,
      null,
      NotificationDetails(android: android),
      payload: deepLink,
    );
  }
}
