import 'package:hive_flutter/hive_flutter.dart';

/// Hive boxes — metadata + masters only (derived; server wins on pull).
abstract final class HiveBoxNames {
  static const appPrefs = 'app_prefs';
  static const permissions = 'permissions';
  static const syncMeta = 'sync_meta';
  static const cursors = 'cursors';
  static const masters = 'masters';
}

class HiveStorage {
  HiveStorage(this._boxes);

  final Map<String, Box<dynamic>> _boxes;

  static Future<HiveStorage> open() async {
    await Hive.initFlutter();
    final names = [
      HiveBoxNames.appPrefs,
      HiveBoxNames.permissions,
      HiveBoxNames.syncMeta,
      HiveBoxNames.cursors,
      HiveBoxNames.masters,
    ];
    final boxes = <String, Box<dynamic>>{};
    for (final name in names) {
      boxes[name] = await Hive.openBox<dynamic>(name);
    }
    return HiveStorage(boxes);
  }

  Box<dynamic> box(String name) => _boxes[name]!;

  Future<void> setLocale(String locale) async {
    await box(HiveBoxNames.appPrefs).put('locale', locale);
  }

  String? getLocale() => box(HiveBoxNames.appPrefs).get('locale') as String?;

  Future<void> savePermissions(Map<String, dynamic> manifest) async {
    await box(HiveBoxNames.permissions).put('manifest', manifest);
  }

  Map<String, dynamic>? getPermissions() {
    final raw = box(HiveBoxNames.permissions).get('manifest');
    if (raw is Map) return Map<String, dynamic>.from(raw);
    return null;
  }

  List<String> getAllowedBlocks() {
    final manifest = getPermissions();
    final blocks = manifest?['blocks'];
    if (blocks is List) {
      return blocks.map((e) => e.toString()).toList();
    }
    return const [];
  }

  Future<void> setWatermark(String entity, String iso) async {
    await box(HiveBoxNames.syncMeta).put('wm:$entity', iso);
  }

  String? getWatermark(String entity) =>
      box(HiveBoxNames.syncMeta).get('wm:$entity') as String?;

  Future<void> setCursor(String feed, String cursor) async {
    await box(HiveBoxNames.cursors).put(feed, cursor);
  }

  String? getCursor(String feed) =>
      box(HiveBoxNames.cursors).get(feed) as String?;
}
