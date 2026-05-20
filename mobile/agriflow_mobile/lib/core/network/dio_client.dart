import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/network/auth_interceptor.dart';
import 'package:agriflow_mobile/core/network/retry_interceptor.dart';
import 'package:agriflow_mobile/core/network/session_auth_interceptor.dart';
import 'package:agriflow_mobile/core/network/tracing_interceptor.dart';
import 'package:cookie_jar/cookie_jar.dart';
import 'package:dio/dio.dart';
import 'package:dio_cookie_manager/dio_cookie_manager.dart';

Dio createDio({
  required ApiConfig config,
  required AccessTokenReader readAccessToken,
  TokenRefresh? onRefresh,
  CookieJar? cookieJar,
  TracingInterceptor? tracing,
}) {
  final dio = Dio(
    BaseOptions(
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 60),
      headers: {'Content-Type': 'application/json'},
    ),
  );
  final jar = cookieJar ?? CookieJar();
  dio.interceptors.addAll([
    if (tracing != null) tracing,
    CookieManager(jar),
    SessionAuthInterceptor(readSessionId: readAccessToken),
    AuthInterceptor(readAccessToken: readAccessToken, onRefresh: onRefresh),
    RetryInterceptor(),
    LogInterceptor(requestBody: false, responseBody: false),
  ]);
  return dio;
}
