import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/core/sync/projection_writer.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final dashboardStatsProvider = FutureProvider<DashboardStats>((ref) async {
  final db = ref.watch(appDatabaseProvider);
  final blocks = ref.watch(hiveStorageProvider).getAllowedBlocks();
  final tasks = await db.readProjections(
    kind: ProjectionKind.task,
    blocks: blocks,
  );
  final projects = await db.readProjections(
    kind: ProjectionKind.farmerProject,
    blocks: blocks,
  );
  final openTasks = tasks.where((t) {
    final status = t.payload['status'] as String? ?? '';
    return status != 'completed' && status != 'cancelled';
  }).length;
  return DashboardStats(
    projectCount: projects.length,
    openTaskCount: openTasks,
  );
});

class DashboardStats {
  const DashboardStats({
    required this.projectCount,
    required this.openTaskCount,
  });

  final int projectCount;
  final int openTaskCount;
}
