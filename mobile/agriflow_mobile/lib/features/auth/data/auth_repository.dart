import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/config/env.dart';
import 'package:agriflow_mobile/core/errors/failure.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';
import 'package:agriflow_mobile/core/storage/hive_boxes.dart';
import 'package:agriflow_mobile/core/storage/secure_token_store.dart';
import 'package:agriflow_mobile/features/auth/data/auth_bootstrap_log.dart';
import 'package:agriflow_mobile/features/auth/data/dev_stub_tokens.dart';
import 'package:agriflow_mobile/features/auth/domain/auth_session.dart';
import 'package:agriflow_mobile/features/auth/domain/permission_manifest.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  throw UnimplementedError('Initialized in bootstrap');
});

final authSessionProvider =
    StateNotifierProvider<AuthSessionNotifier, AsyncValue<AuthSession?>>(
  (ref) => throw UnimplementedError('Initialized in bootstrap'),
);

class AuthSessionNotifier extends StateNotifier<AsyncValue<AuthSession?>> {
  AuthSessionNotifier(this._repo) : super(const AsyncValue.loading()) {
    _restore();
  }

  final AuthRepository _repo;

  Future<void> _restore() async {
    try {
      final session = await _repo.restoreSession();
      state = AsyncValue.data(session);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> login(String username, String password) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(
      () => _repo.login(username: username, password: password),
    );
  }

  Future<void> loginDevStub() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _repo.loginDevStub());
  }

  Future<void> logout() async {
    await _repo.logout();
    state = const AsyncValue.data(null);
  }
}

class AuthRepository {
  AuthRepository({
    required ApiClient api,
    required ApiConfig config,
    required SecureTokenStore tokens,
    required HiveStorage hive,
  })  : _api = api,
        _config = config,
        _tokens = tokens,
        _hive = hive;

  final ApiClient _api;
  final ApiConfig _config;
  final SecureTokenStore _tokens;
  final HiveStorage _hive;

  AuthSession? _cached;

  Future<AuthSession?> restoreSession() async {
    AuthBootstrapLog.logEnv();

    final accessToken = await _tokens.readAccessToken();
    final refreshToken = await _tokens.readRefreshToken();
    final manifest = _hive.getPermissions();
    final hasManifest = manifest != null && manifest.isNotEmpty;

    final stubTokens = DevStubTokens.isStubAccessToken(accessToken) ||
        DevStubTokens.isStubRefreshToken(refreshToken);
    final stubManifest = DevStubTokens.isStubManifest(manifest);

    if (!Env.devAuthStubEnabled && (stubTokens || stubManifest)) {
      AuthBootstrapLog.logRestore(
        path: 'reject_dev_stub_purge',
        accessToken: accessToken,
        hasManifest: hasManifest,
        manifestUser: manifest?['user'] as String?,
      );
      AuthBootstrapLog.logPurge(
        'DEV_AUTH_STUB=false but stub token/manifest found in '
        'SecureTokenStore/Hive (separate from agriflow_mobile cache folders)',
      );
      await _purgeDevStubPersistence();
      return null;
    }

    if (Env.devAuthStubEnabled) {
      if (hasManifest) {
        AuthBootstrapLog.logRestore(
          path: 'dev_stub_manifest',
          accessToken: accessToken,
          hasManifest: true,
          manifestUser: manifest['user'] as String?,
        );
        _cached = AuthSession(
          userName: DevStubTokens.user,
          fullName: DevStubTokens.fullName,
          permissions: PermissionManifest.fromJson(manifest),
          isDevStub: true,
        );
        return _cached;
      }
      AuthBootstrapLog.logRestore(
        path: 'dev_stub_no_manifest',
        accessToken: accessToken,
        hasManifest: false,
      );
      return null;
    }

    if (accessToken == null || accessToken.isEmpty) {
      AuthBootstrapLog.logRestore(
        path: 'no_access_token',
        hasManifest: hasManifest,
        manifestUser: manifest?['user'] as String?,
      );
      return null;
    }
    if (!hasManifest) {
      AuthBootstrapLog.logRestore(
        path: 'no_permissions_manifest',
        accessToken: accessToken,
        hasManifest: false,
      );
      return null;
    }

    AuthBootstrapLog.logRestore(
      path: 'token_and_manifest',
      accessToken: accessToken,
      hasManifest: true,
      manifestUser: manifest['user'] as String?,
    );
    _cached = AuthSession(
      userName: manifest['user'] as String? ?? 'user',
      fullName: manifest['full_name'] as String? ?? 'Officer',
      permissions: PermissionManifest.fromJson(manifest),
      isDevStub: false,
    );
    return _cached;
  }

  Future<void> _purgeDevStubPersistence() async {
    _cached = null;
    await _tokens.clear();
    await _hive.savePermissions({});
  }

  Future<AuthSession> login({
    required String username,
    required String password,
  }) async {
    final envelope = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl('agriflow.api.v1.auth.login'),
      data: {'username': username, 'password': password},
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    final data = envelope.data!;
    await _tokens.saveTokens(
      accessToken: data['access_token'] as String,
      refreshToken: data['refresh_token'] as String,
    );
    final permissions = PermissionManifest.fromJson(
      data['permissions'] as Map<String, dynamic>?,
    );
    await _hive.savePermissions({
      'user': data['user']?['name'] ?? username,
      'full_name': data['user']?['full_name'] ?? username,
      ...permissions.toJson(),
    });
    _cached = AuthSession(
      userName: username,
      fullName: data['user']?['full_name'] as String? ?? username,
      permissions: permissions,
      isDevStub: false,
    );
    return _cached!;
  }

  Future<AuthSession> loginDevStub() async {
    assert(Env.devAuthStubEnabled, 'DEV_AUTH_STUB only in debug');
    if (!Env.devAuthStubEnabled) {
      throw StateError('Dev auth stub disabled');
    }
    await _tokens.saveTokens(
      accessToken: DevStubTokens.access,
      refreshToken: DevStubTokens.refresh,
    );
    const permissions = PermissionManifest(
      roles: ['Field Staff'],
      blocks: [DevStubTokens.block],
      districts: ['TVM'],
    );
    await _hive.savePermissions({
      'user': DevStubTokens.user,
      'full_name': DevStubTokens.fullName,
      ...permissions.toJson(),
    });
    _cached = const AuthSession(
      userName: DevStubTokens.user,
      fullName: DevStubTokens.fullName,
      permissions: permissions,
      isDevStub: true,
    );
    return _cached!;
  }

  Future<String?> refreshAccessToken() async {
    final refresh = await _tokens.readRefreshToken();
    if (refresh == null || refresh.isEmpty) return null;
    if (DevStubTokens.isStubRefreshToken(refresh)) {
      if (Env.devAuthStubEnabled) {
        return DevStubTokens.access;
      }
      AuthBootstrapLog.logPurge('refresh blocked: stub token with DEV_AUTH_STUB=false');
      await _purgeDevStubPersistence();
      return null;
    }
    try {
      final envelope = await _api.postMethod<Map<String, dynamic>>(
        methodUrl: _config.methodUrl('agriflow.api.v1.auth.refresh'),
        data: {'refresh_token': refresh},
        parseData: (json) => Map<String, dynamic>.from(json as Map),
      );
      final access = envelope.data!['access_token'] as String;
      await _tokens.saveTokens(
        accessToken: access,
        refreshToken: envelope.data!['refresh_token'] as String? ?? refresh,
      );
      return access;
    } on ApiFailure catch (e) {
      if (e.code == 'AUTH_REFRESH_REUSED' || e.code == 'AUTH_TOKEN_INVALID') {
        await _tokens.clear();
        _cached = null;
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  Future<void> logout() async {
    final refresh = await _tokens.readRefreshToken();
    if (refresh != null && refresh.isNotEmpty && !Env.devAuthStubEnabled) {
      try {
        await _api.postMethod<Map<String, dynamic>>(
          methodUrl: _config.methodUrl('agriflow.api.v1.auth.logout'),
          data: {'refresh_token': refresh},
          parseData: (json) => Map<String, dynamic>.from(json as Map),
        );
      } catch (_) {
        // best-effort revoke
      }
    }
    _cached = null;
    await _tokens.clear();
    await _hive.savePermissions({});
  }
}
