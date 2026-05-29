import 'package:agriflow_mobile/core/config/env.dart';
import 'package:flutter/foundation.dart';

/// Production-safe telemetry foundation (no crash reporting SDK required).
abstract final class Telemetry {
  static void init() {
    assertReleaseAuthSafe();
    if (Env.sentryDsn.isNotEmpty && kReleaseMode) {
      // Hook point for Sentry/Firebase — wire when DSN provided.
      log('info', 'telemetry', 'Crash reporting DSN configured');
    }
  }

  static void assertReleaseAuthSafe() {
    assert(() {
      if (kReleaseMode && Env.devAuthStubEnabled) {
        throw StateError('DEV_AUTH_STUB must never be enabled in release');
      }
      return true;
    }());
    if (kReleaseMode && Env.devAuthStubEnabled) {
      throw StateError('DEV_AUTH_STUB blocked in release builds');
    }
    if (kReleaseMode && Env.apiBaseUrl.isEmpty) {
      throw StateError('API_BASE_URL required in release builds');
    }
  }

  static void log(
    String level,
    String category,
    String message, {
    Map<String, Object?>? context,
  }) {
    if (kReleaseMode && level == 'debug') return;
    final ctx = context == null ? '' : ' $context';
    debugPrint('[AgriFlow/$level/$category] $message$ctx');
  }

  static void recordError(
    Object error, {
    StackTrace? stack,
    Map<String, Object?>? context,
  }) {
    log('error', 'crash', error.toString(), context: {
      ...?context,
      if (stack != null) 'stack': stack.toString().split('\n').take(5).join(' | '),
    });
  }
}
