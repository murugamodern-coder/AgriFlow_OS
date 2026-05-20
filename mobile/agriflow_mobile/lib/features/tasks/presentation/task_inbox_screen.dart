import 'package:agriflow_mobile/app/router/routes.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:go_router/go_router.dart';
import 'package:agriflow_mobile/features/tasks/domain/task_summary.dart';
import 'package:agriflow_mobile/shared/widgets/empty_state.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final taskInboxProvider = StreamProvider<List<TaskSummary>>((ref) {
  return ref.watch(taskRepositoryProvider).watchInbox();
});

class TaskInboxScreen extends ConsumerWidget {
  const TaskInboxScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final inbox = ref.watch(taskInboxProvider);

    return inbox.when(
      loading: () => const LoadingView(),
      error: (e, _) => Center(child: Text(e.toString())),
      data: (tasks) {
        if (tasks.isEmpty) {
          return EmptyState(message: l10n.emptyTasks);
        }
        return RefreshIndicator(
          onRefresh: () async {
            await ref.read(syncOrchestratorProvider).syncNow();
          },
          child: ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: tasks.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final task = tasks[index];
              return Card(
                child: ListTile(
                  onTap: () => context.push(
                    AppRoutes.taskDetail(
                      task.name,
                      project: task.farmerProject,
                    ),
                  ),
                  title: Text(task.subject),
                  subtitle: Text('${task.status} · ${task.farmerProject ?? ''}'),
                  trailing: task.status == 'completed'
                      ? null
                      : TextButton(
                          onPressed: () async {
                            await ref
                                .read(taskRepositoryProvider)
                                .completeTask(task);
                            if (context.mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text(l10n.syncPending(1))),
                              );
                            }
                          },
                          child: Text(l10n.taskComplete),
                        ),
                ),
              );
            },
          ),
        );
      },
    );
  }
}
