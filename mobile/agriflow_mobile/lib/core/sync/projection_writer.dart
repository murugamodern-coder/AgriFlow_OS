import 'dart:convert';

import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/storage/hive_boxes.dart';

abstract final class ProjectionKind {
  static const task = 'task';
  static const timeline = 'timeline';
  static const farmerProject = 'farmer_project';
  static const notification = 'notification';
}

class ProjectionWriter {
  ProjectionWriter(this._db, this._hive);

  final AppDatabase _db;
  final HiveStorage _hive;

  Future<void> applyPull(Map<String, dynamic> data) async {
    final entities = data['entities'] as Map<String, dynamic>? ?? data;
    final blocks = _hive.getAllowedBlocks();

    await _applyEntityBundle(
      kind: ProjectionKind.task,
      bundle: entities['task'] as Map<String, dynamic>?,
      blocks: blocks,
      sortField: 'modified',
    );
    await _applyEntityBundle(
      kind: ProjectionKind.timeline,
      bundle: entities['timeline'] as Map<String, dynamic>?,
      blocks: blocks,
      sortField: 'created_on',
    );
    await _applyEntityBundle(
      kind: ProjectionKind.farmerProject,
      bundle: entities['farmer_project'] as Map<String, dynamic>?,
      blocks: blocks,
      sortField: 'modified',
    );

    final watermarks = data['server_watermark'] as Map<String, dynamic>?;
    if (watermarks != null) {
      for (final entry in watermarks.entries) {
        if (entry.value != null) {
          await _hive.setWatermark(entry.key, entry.value.toString());
        }
      }
    }
  }

  Future<void> _applyEntityBundle({
    required String kind,
    required Map<String, dynamic>? bundle,
    required List<String> blocks,
    required String sortField,
  }) async {
    if (bundle == null) return;
    final items = bundle['items'] as List? ?? [];
    for (final raw in items) {
      final item = Map<String, dynamic>.from(raw as Map);
      final block = item['block'] as String?;
      if (blocks.isNotEmpty && block != null && !blocks.contains(block)) {
        continue;
      }
      final name = item['name'] as String? ?? '';
      if (name.isEmpty) continue;
      await _db.upsertProjection(
        kind: kind,
        name: name,
        block: block,
        sortKey: item[sortField]?.toString(),
        payloadJson: jsonEncode(item),
      );
    }
    final deleted = bundle['deleted'] as List? ?? [];
    for (final raw in deleted) {
      final item = Map<String, dynamic>.from(raw as Map);
      final name = item['name'] as String?;
      if (name != null) {
        await _db.tombstoneProjection(kind: kind, name: name);
      }
    }
    final cursor = bundle['cursor'] as String?;
    if (cursor != null) {
      await _hive.setCursor('pull:$kind', cursor);
    }
  }

  Future<void> cacheNotifications(List<Map<String, dynamic>> items) async {
    for (final item in items) {
      await _db.upsertProjection(
        kind: ProjectionKind.notification,
        name: item['name'] as String? ?? '',
        sortKey: item['modified']?.toString() ?? item['creation']?.toString(),
        payloadJson: jsonEncode(item),
      );
    }
  }
}
