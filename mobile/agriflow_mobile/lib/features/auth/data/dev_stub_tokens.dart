/// Dev auth stub token values (must match [AuthRepository.loginDevStub]).
abstract final class DevStubTokens {
  static const access = 'dev-stub-access';
  static const refresh = 'dev-stub-refresh';
  static const user = 'dev@agriflow.local';
  static const fullName = 'Dev Officer';
  static const block = 'BLK-DEV-01';

  static bool isStubAccessToken(String? token) =>
      token != null && token == access;

  static bool isStubRefreshToken(String? token) =>
      token != null && token == refresh;

  static bool isStubManifest(Map<String, dynamic>? manifest) {
    if (manifest == null || manifest.isEmpty) return false;
    if (manifest['user'] == user || manifest['full_name'] == fullName) {
      return true;
    }
    final blocks = manifest['blocks'];
    if (blocks is List && blocks.map((e) => e.toString()).contains(block)) {
      return true;
    }
    return false;
  }
}
