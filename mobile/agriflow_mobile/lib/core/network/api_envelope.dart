import 'dart:convert';

/// Standard AgriFlow API envelope (server authoritative).
class ApiEnvelope<T> {
  const ApiEnvelope({
    required this.ok,
    this.data,
    this.error,
    this.serverTime,
    this.requestId,
  });

  final bool ok;
  final T? data;
  final ApiErrorBody? error;
  final String? serverTime;
  final String? requestId;

  factory ApiEnvelope.fromJson(
    Map<String, dynamic> json,
    T Function(Object? json) dataParser,
  ) {
    return ApiEnvelope(
      ok: json['ok'] == true,
      data: json['data'] != null ? dataParser(json['data']) : null,
      error: json['error'] != null
          ? ApiErrorBody.fromJson(json['error'] as Map<String, dynamic>)
          : null,
      serverTime: json['server_time'] as String?,
      requestId: json['request_id'] as String?,
    );
  }

  Map<String, dynamic> toJsonMap() => {
        'ok': ok,
        'data': data,
        'error': error?.toJson(),
        'server_time': serverTime,
        'request_id': requestId,
      };

  String toJsonString() => jsonEncode(toJsonMap());
}

class ApiErrorBody {
  const ApiErrorBody({
    required this.code,
    required this.message,
    this.messageI18nKey,
    this.details,
  });

  final String code;
  final String message;
  final String? messageI18nKey;
  final Map<String, dynamic>? details;

  factory ApiErrorBody.fromJson(Map<String, dynamic> json) {
    return ApiErrorBody(
      code: json['code'] as String? ?? 'SRV_INTERNAL',
      message: json['message'] as String? ?? 'Unknown error',
      messageI18nKey: json['message_i18n_key'] as String?,
      details: json['details'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'code': code,
        'message': message,
        if (messageI18nKey != null) 'message_i18n_key': messageI18nKey,
        if (details != null) 'details': details,
      };
}
