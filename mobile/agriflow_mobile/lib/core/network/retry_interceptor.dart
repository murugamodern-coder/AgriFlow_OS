import 'package:dio/dio.dart';

/// Retry-safe networking for idempotent GET-like failures only.
/// POST mutations are not retried here (queue handles replay).
class RetryInterceptor extends Interceptor {
  RetryInterceptor({this.maxRetries = 2});

  final int maxRetries;

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final options = err.requestOptions;
    final isSafe =
        options.method.toUpperCase() == 'GET' ||
        options.extra['retry_safe'] == true;
    final attempt = (options.extra['retry_attempt'] as int?) ?? 0;

    if (!isSafe || attempt >= maxRetries) {
      return handler.next(err);
    }

    final shouldRetry = err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.receiveTimeout ||
        err.type == DioExceptionType.connectionError;

    if (!shouldRetry) {
      return handler.next(err);
    }

    await Future<void>.delayed(Duration(milliseconds: 500 * (attempt + 1)));
    options.extra['retry_attempt'] = attempt + 1;
    try {
      final response = await Dio().fetch<dynamic>(options);
      handler.resolve(response);
    } catch (e) {
      handler.next(err);
    }
  }
}
