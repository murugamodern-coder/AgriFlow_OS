import 'dart:convert';

import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/storage/hive_boxes.dart';
import 'package:agriflow_mobile/core/sync/projection_writer.dart';
import 'package:agriflow_mobile/core/sync/mutation_queue.dart';
import 'package:agriflow_mobile/features/project_lifecycle/data/timeline_repository.dart';
import 'package:agriflow_mobile/features/tasks/data/task_repository.dart';
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hive/hive.dart';

void main() {
  test('offline read proof — Drift projections readable without network', () async {
    Hive.init('./test_hive_${DateTime.now().microsecondsSinceEpoch}');
    final hive = await HiveStorage.open();
    await hive.savePermissions({
      'roles': ['Field Staff'],
      'blocks': ['BLK01'],
      'districts': ['TVM'],
    });

    final db = AppDatabase.forTesting(NativeDatabase.memory());
    await db.ensureSchema();

    await db.upsertProjection(
      kind: ProjectionKind.task,
      name: 'TSK-2026-00099',
      block: 'BLK01',
      sortKey: '2026-05-20T10:00:00',
      payloadJson: jsonEncode({
        'name': 'TSK-2026-00099',
        'subject': 'Field visit',
        'status': 'open',
        'block': 'BLK01',
        'doc_version': 1,
        'modified': '2026-05-20T10:00:00',
      }),
    );
    await db.upsertProjection(
      kind: ProjectionKind.timeline,
      name: 'TE-2026-00001',
      block: 'BLK01',
      sortKey: '2026-05-20T09:00:00',
      payloadJson: jsonEncode({
        'name': 'TE-2026-00001',
        'event_type': 'manual_note',
        'created_on': '2026-05-20T09:00:00',
        'farmer_project': 'FP-2026-00007',
        'block': 'BLK01',
        'title': 'Note',
      }),
    );

    final tasks = TaskRepository(db: db, hive: hive, queue: MutationQueue(db));
    final cachedTasks = await tasks.readCachedInbox();
    expect(cachedTasks.length, 1);
    expect(cachedTasks.first.name, 'TSK-2026-00099');

    final timeline = TimelineRepository(db: db, hive: hive);
    final cachedTimeline = await timeline.readCachedFeed();
    expect(cachedTimeline.length, 1);
    expect(cachedTimeline.first.eventType, 'manual_note');

    await db.close();
  });
}
