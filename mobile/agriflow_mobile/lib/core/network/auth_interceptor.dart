import 'package:dio/dio.dart';

typedef AccessTokenReader = Future<String?> Function();
typedef TokenRefresh = Future<String?> Function();

class AuthInterceptor extends Interceptor {
  AuthInterceptor({
    required this.readAccessToken,
    this.onRefresh,
  });

  final AccessTokenReader readAccessToken;
  final TokenRefresh? onRefresh;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await readAccessToken();
    if (token != null && token.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    options.headers['X-AgriFlow-Platform'] = 'mobile';
    options.headers['X-AgriFlow-Client-Version'] = '0.14.0';
    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode == 401 && onRefresh != null) {
      final newToken = await onRefresh!();
      if (newToken != null && newToken.isNotEmpty) {
        err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
        try {
          final clone = await Dio().fetch<dynamic>(err.requestOptions);
          return handler.resolve(clone);
        } catch (_) {
          // fall through
        }
      }
    }
    handler.next(err);
  }
}
