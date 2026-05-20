import 'package:agriflow_mobile/features/auth/domain/permission_manifest.dart';
import 'package:equatable/equatable.dart';

class AuthSession extends Equatable {
  const AuthSession({
    required this.userName,
    required this.fullName,
    required this.permissions,
    required this.isDevStub,
  });

  final String userName;
  final String fullName;
  final PermissionManifest permissions;
  final bool isDevStub;

  @override
  List<Object?> get props => [userName, fullName, permissions, isDevStub];
}
