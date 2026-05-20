import 'package:equatable/equatable.dart';

sealed class Failure extends Equatable {
  const Failure({this.code, this.messageI18nKey});

  final String? code;
  final String? messageI18nKey;

  @override
  List<Object?> get props => [code, messageI18nKey];
}

final class NetworkFailure extends Failure {
  const NetworkFailure({super.code, super.messageI18nKey});
}

final class ApiFailure extends Failure {
  const ApiFailure({
    required this.httpStatus,
    super.code,
    super.messageI18nKey,
    this.details,
    this.requestId,
  });

  final int? httpStatus;
  final Map<String, dynamic>? details;
  final String? requestId;

  @override
  List<Object?> get props => [...super.props, httpStatus, details, requestId];
}

final class AuthFailure extends Failure {
  const AuthFailure({super.code, super.messageI18nKey});
}

final class SyncFailure extends Failure {
  const SyncFailure({super.code, super.messageI18nKey, this.partial = false});

  final bool partial;

  @override
  List<Object?> get props => [...super.props, partial];
}

final class CacheFailure extends Failure {
  const CacheFailure({super.messageI18nKey});
}
