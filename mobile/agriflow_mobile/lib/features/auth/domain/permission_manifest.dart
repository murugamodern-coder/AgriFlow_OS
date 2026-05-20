class PermissionManifest {
  const PermissionManifest({
    required this.roles,
    required this.blocks,
    required this.districts,
  });

  final List<String> roles;
  final List<String> blocks;
  final List<String> districts;

  factory PermissionManifest.fromJson(Map<String, dynamic>? json) {
    if (json == null) {
      return const PermissionManifest(roles: [], blocks: [], districts: []);
    }
    return PermissionManifest(
      roles: _stringList(json['roles']),
      blocks: _stringList(json['blocks']),
      districts: _stringList(json['districts']),
    );
  }

  Map<String, dynamic> toJson() => {
        'roles': roles,
        'blocks': blocks,
        'districts': districts,
      };

  static List<String> _stringList(dynamic value) {
    if (value is List) return value.map((e) => e.toString()).toList();
    return const [];
  }
}
