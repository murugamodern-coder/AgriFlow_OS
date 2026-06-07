import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/features/project_lifecycle/data/workflow_repository.dart';
import 'package:agriflow_mobile/features/project_lifecycle/domain/models/workflow_state.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final workflowRepositoryProvider = Provider<WorkflowRepository>((ref) {
  return WorkflowRepository(
    api: ref.watch(apiClientProvider),
    config: ref.watch(apiConfigProvider),
  );
});

final projectWorkflowProvider =
    FutureProvider.family<WorkflowStatus, String>((ref, projectName) async {
  return ref.watch(workflowRepositoryProvider).getAvailableActions(projectName);
});
