import 'package:agriflow_mobile/core/config/env.dart';
import 'package:flutter/foundation.dart';

/// Temporary debug logging for auth bootstrap (debug builds only).
abstract final class AuthBootstrapLog {
  static void logEnv() {
    if (!kDebugMode) return;
    debugPrint(
      '[AuthBootstrap] devAuthStubEnabled=${Env.devAuthStubEnabled} '
      'demoMode=${Env.demoMode} '
      'API_BASE_URL=${Env.apiBaseUrl.isEmpty ? "(empty)" : Env.apiBaseUrl}',
    );
  }

  static void logRestore({
    required String path,
    String? accessToken,
    bool? hasManifest,
    String? manifestUser,
  }) {
    if (!kDebugMode) return;
    final tokenLabel = accessToken == null
        ? 'null'
        : accessToken.length <= 12
            ? accessToken
            : '${accessToken.substring(0, 8)}…';
    debugPrint(
      '[AuthBootstrap] restoreSession path=$path '
      'accessToken=$tokenLabel '
      'hasManifest=$hasManifest '
      'manifestUser=${manifestUser ?? "—"}',
    );
  }

  static void logPurge(String reason) {
    if (!kDebugMode) return;
    debugPrint('[AuthBootstrap] purging dev-stub persistence: $reason');
  }
}
