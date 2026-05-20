import 'package:agriflow_mobile/core/config/env.dart';
import 'package:agriflow_mobile/core/observability/telemetry.dart';
import 'package:flutter/foundation.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

/// Initializes Sentry when DSN is provided (release/staging builds).
abstract final class SentryBootstrap {
  static Future<void> init(Future<void> Function() runApp) async {
    final dsn = Env.sentryDsn.trim();
    if (dsn.isEmpty) {
      await runApp();
      return;
    }
    await SentryFlutter.init(
      (options) {
        options.dsn = dsn;
        options.environment = kReleaseMode ? 'production' : 'development';
        options.tracesSampleRate = kReleaseMode ? 0.2 : 1.0;
        options.sendDefaultPii = false;
      },
      appRunner: () async => runApp(),
    );
  }

  static Future<void> capture(
    Object error, {
    StackTrace? stack,
    Map<String, Object?>? context,
  }) async {
    Telemetry.recordError(error, stack: stack, context: context);
    if (Env.sentryDsn.isEmpty) return;
    await Sentry.captureException(
      error,
      stackTrace: stack,
      withScope: (scope) {
        if (context != null) {
          for (final e in context.entries) {
            scope.setContexts(e.key, e.value);
          }
        }
      },
    );
  }
}
