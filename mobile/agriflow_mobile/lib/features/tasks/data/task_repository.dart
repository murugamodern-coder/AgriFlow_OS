import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/storage/hive_boxes.dart';
import 'package:agriflow_mobile/core/sync/mutation_queue.dart';
import 'package:agriflow_mobile/core/sync/projection_writer.dart';
import 'package:agriflow_mobile/features/tasks/domain/task_summary.dart';

class TaskRepository {
  TaskRepository({
    required AppDatabase db,
    required HiveStorage hive,
    required MutationQueue queue,
  })  : _db = db,
        _hive = hive,
        _queue = queue;

  final AppDatabase _db;
  final HiveStorage _hive;
  final MutationQueue _queue;

  Stream<List<TaskSummary>> watchInbox() {
    final blocks = _hive.getAllowedBlocks();
    return _db
        .watchProjections(kind: ProjectionKind.task, blocks: blocks)
        .map((rows) => rows.map((r) => TaskSummary.fromPayload(r.payload)).toList());
  }

  Future<List<TaskSummary>> readCachedInbox() async {
    final blocks = _hive.getAllowedBlocks();
    final rows = await _db.readProjections(
      kind: ProjectionKind.task,
      blocks: blocks,
    );
    return rows.map((r) => TaskSummary.fromPayload(r.payload)).toList();
  }

  /// Queue-only complete — no direct task.complete API.
  Future<String> completeTask(TaskSummary task) {
    return _queue.enqueueTaskComplete(
      taskName: task.name,
      docVersion: task.docVersion,
      farmerProject: task.farmerProject,
    );
  }
}
