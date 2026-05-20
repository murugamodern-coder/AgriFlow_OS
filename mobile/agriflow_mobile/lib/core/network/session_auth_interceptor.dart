import 'package:dio/dio.dart';

/// Sends Frappe session id as Cookie (Phase 15 session auth).
class SessionAuthInterceptor extends Interceptor {
  SessionAuthInterceptor({required this.readSessionId});

  final Future<String?> Function() readSessionId;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final sid = await readSessionId();
    if (sid != null && sid.isNotEmpty && !sid.startsWith('dev-stub')) {
      options.headers['Cookie'] = 'sid=$sid';
    }
    handler.next(options);
  }
}
