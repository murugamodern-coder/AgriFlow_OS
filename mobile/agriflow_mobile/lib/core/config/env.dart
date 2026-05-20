import 'package:flutter/foundation.dart';

/// Runtime configuration via `--dart-define`.
class Env {
  Env._();

  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: '',
  );

  static const String deviceId = String.fromEnvironment(
    'DEVICE_ID',
    defaultValue: '',
  );

  static const String sentryDsn = String.fromEnvironment(
    'SENTRY_DSN',
    defaultValue: '',
  );

  static const String appVersion = String.fromEnvironment(
    'APP_VERSION',
    defaultValue: '0.24.0',
  );

  static const String minAppVersion = String.fromEnvironment(
    'MIN_APP_VERSION',
    defaultValue: '',
  );

  /// When true, registers a stable debug push token (no Firebase required).
  static const bool pushDebugStub = bool.fromEnvironment(
    'PUSH_DEBUG_STUB',
    defaultValue: true,
  );

  /// Real FCM token from Firebase Messaging when integrated.
  static const String fcmToken = String.fromEnvironment(
    'FCM_TOKEN',
    defaultValue: '',
  );

  /// Pilot demo build: hides dev stub, auto-onboarding, pilot menu noise.
  static const bool demoMode = bool.fromEnvironment(
    'DEMO_MODE',
    defaultValue: true,
  );

  /// Dev auth stub: DEBUG/PROFILE only, never release; off when demoMode.
  static bool get devAuthStubEnabled {
    if (demoMode || kReleaseMode || !kDebugMode) return false;
    return const bool.fromEnvironment('DEV_AUTH_STUB', defaultValue: false);
  }

  static void assertConfigured() {
    assert(() {
      if (apiBaseUrl.isEmpty && !devAuthStubEnabled) {
        throw StateError(
          'API_BASE_URL dart-define is required unless DEV_AUTH_STUB=true in debug.',
        );
      }
      return true;
    }());
  }
}
