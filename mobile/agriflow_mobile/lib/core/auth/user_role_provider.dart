import 'package:agriflow_mobile/features/auth/data/auth_repository.dart';
import 'package:agriflow_mobile/features/auth/domain/auth_session.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Agriflow roles as defined in backend `fixtures/role.json`.
enum AgriflowRole {
  owner('Agriflow Owner'),
  officeManager('Agriflow Office Manager'),
  officeStaff('Agriflow Office Staff'),
  fieldStaff('Agriflow Field Staff'),
  installerLead('Agriflow Installer Lead'),
  installer('Agriflow Installer'),
  serviceTechnician('Agriflow Service Technician'),
  storeKeeper('Agriflow Store Keeper'),
  unknown('Unknown');

  const AgriflowRole(this.backendName);

  final String backendName;

  static const _aliases = <String, AgriflowRole>{
    'Owner': AgriflowRole.owner,
    'Office Manager': AgriflowRole.officeManager,
    'Office Staff': AgriflowRole.officeStaff,
    'Field Staff': AgriflowRole.fieldStaff,
    'Installer Lead': AgriflowRole.installerLead,
    'Installer': AgriflowRole.installer,
    'Service Technician': AgriflowRole.serviceTechnician,
    'Store Keeper': AgriflowRole.storeKeeper,
  };

  static AgriflowRole fromBackend(String name) {
    final trimmed = name.trim();
    for (final role in AgriflowRole.values) {
      if (role == AgriflowRole.unknown) continue;
      if (role.backendName == trimmed) return role;
    }
    return _aliases[trimmed] ?? AgriflowRole.unknown;
  }

  static List<AgriflowRole> parseAll(Iterable<String> backendRoles) {
    final parsed = <AgriflowRole>{};
    for (final name in backendRoles) {
      final role = fromBackend(name);
      if (role != AgriflowRole.unknown) parsed.add(role);
    }
    return parsed.toList();
  }
}

class UserSession {
  const UserSession({
    required this.userId,
    required this.fullName,
    required this.roles,
    this.blocks = const [],
    this.districts = const [],
  });

  final String userId;
  final String fullName;
  final List<AgriflowRole> roles;
  final List<String> blocks;
  final List<String> districts;

  factory UserSession.fromAuthSession(AuthSession session) {
    return UserSession(
      userId: session.userName,
      fullName: session.fullName,
      roles: AgriflowRole.parseAll(session.permissions.roles),
      blocks: session.permissions.blocks,
      districts: session.permissions.districts,
    );
  }

  bool hasRole(AgriflowRole role) => roles.contains(role);

  AgriflowRole get primaryRole {
    if (hasRole(AgriflowRole.owner)) return AgriflowRole.owner;
    if (hasRole(AgriflowRole.officeManager)) return AgriflowRole.officeManager;
    if (hasRole(AgriflowRole.fieldStaff)) return AgriflowRole.fieldStaff;
    if (hasRole(AgriflowRole.installerLead)) return AgriflowRole.installerLead;
    if (hasRole(AgriflowRole.installer)) return AgriflowRole.installer;
    if (hasRole(AgriflowRole.serviceTechnician)) {
      return AgriflowRole.serviceTechnician;
    }
    if (hasRole(AgriflowRole.storeKeeper)) return AgriflowRole.storeKeeper;
    if (hasRole(AgriflowRole.officeStaff)) return AgriflowRole.officeStaff;
    return AgriflowRole.unknown;
  }
}

/// Derived from [authSessionProvider] permissions manifest (login / restore).
/// Backend source: `agriflow.api.v1.auth.login` → `permissions.roles`.
final userSessionProvider = Provider<UserSession?>((ref) {
  final auth = ref.watch(authSessionProvider);
  final session = auth.valueOrNull;
  if (session == null) return null;
  return UserSession.fromAuthSession(session);
});
