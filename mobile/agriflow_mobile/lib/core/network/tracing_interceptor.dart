import 'package:dio/dio.dart';
import 'package:uuid/uuid.dart';

/// Injects X-Request-Id and X-Sync-Correlation-Id on every API call.
class TracingInterceptor extends Interceptor {
  TracingInterceptor({String? syncCorrelationId})
      : _syncCorrelationId = syncCorrelationId;

  final _uuid = const Uuid();
  String? _syncCorrelationId;

  void setSyncCorrelationId(String id) {
    _syncCorrelationId = id;
  }

  void clearSyncCorrelationId() {
    _syncCorrelationId = null;
  }

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    options.headers['X-Request-Id'] ??= _uuid.v4();
    if (_syncCorrelationId != null) {
      options.headers['X-Sync-Correlation-Id'] = _syncCorrelationId;
    }
    handler.next(options);
  }
}
