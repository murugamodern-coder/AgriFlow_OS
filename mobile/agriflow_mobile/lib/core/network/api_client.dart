import 'package:agriflow_mobile/core/errors/failure.dart';
import 'package:agriflow_mobile/core/network/api_envelope.dart';
import 'package:dio/dio.dart';

typedef JsonMap = Map<String, dynamic>;

class ApiClient {
  ApiClient({required this.dio});

  final Dio dio;

  Future<ApiEnvelope<T>> postMethod<T>({
    required String methodUrl,
    required JsonMap data,
    required T Function(Object? json) parseData,
  }) async {
    try {
      final response = await dio.post<dynamic>(
        methodUrl,
        data: {'data': data},
      );
      final body = _normalizeBody(response.data);
      final envelope = ApiEnvelope.fromJson(body, parseData);
      if (!envelope.ok) {
        throw ApiFailure(
          httpStatus: response.statusCode,
          code: envelope.error?.code,
          messageI18nKey: envelope.error?.messageI18nKey,
          details: envelope.error?.details,
          requestId: envelope.requestId,
        );
      }
      return envelope;
    } on DioException catch (e) {
      final body = e.response?.data;
      if (body is Map<String, dynamic> && body['error'] != null) {
        final err = ApiErrorBody.fromJson(body['error'] as JsonMap);
        throw ApiFailure(
          httpStatus: e.response?.statusCode,
          code: err.code,
          messageI18nKey: err.messageI18nKey,
          details: err.details,
          requestId: body['request_id'] as String?,
        );
      }
      throw NetworkFailure(code: e.type.name);
    }
  }

  JsonMap _normalizeBody(dynamic raw) {
    if (raw is Map<String, dynamic>) return raw;
    if (raw is String) {
      return {};
    }
    return {};
  }
}
