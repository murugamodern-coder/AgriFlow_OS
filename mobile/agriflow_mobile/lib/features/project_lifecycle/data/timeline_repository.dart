import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/storage/hive_boxes.dart';
import 'package:agriflow_mobile/core/sync/projection_writer.dart';
import 'package:agriflow_mobile/features/project_lifecycle/domain/timeline_event.dart';

/// Cross-project timeline feed from sync.pull `timeline` entity (block-filtered).
class TimelineRepository {
  TimelineRepository({
    required AppDatabase db,
    required HiveStorage hive,
  })  : _db = db,
        _hive = hive;

  final AppDatabase _db;
  final HiveStorage _hive;

  Stream<List<TimelineEvent>> watchFeed() {
    final blocks = _hive.getAllowedBlocks();
    return _db
        .watchProjections(kind: ProjectionKind.timeline, blocks: blocks)
        .map(
          (rows) => rows
              .map((r) => TimelineEvent.fromPayload(r.payload))
              .toList(),
        );
  }

  Future<List<TimelineEvent>> readCachedFeed() async {
    final blocks = _hive.getAllowedBlocks();
    final rows = await _db.readProjections(
      kind: ProjectionKind.timeline,
      blocks: blocks,
    );
    return rows.map((r) => TimelineEvent.fromPayload(r.payload)).toList();
  }
}
