import 'package:agriflow_mobile/core/design_tokens/status_semantics.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/features/sync/presentation/widgets/sync_feedback_listener.dart';
import 'package:agriflow_mobile/features/sync/sync_connectivity.dart';
import 'package:agriflow_mobile/features/auth/data/auth_repository.dart';
import 'package:agriflow_mobile/features/tasks/domain/task_inbox_logic.dart';
import 'package:agriflow_mobile/features/tasks/domain/task_summary.dart';
import 'package:agriflow_mobile/features/tasks/presentation/widgets/task_detail_sheet.dart';
import 'package:agriflow_mobile/features/tasks/presentation/widgets/task_feed_card.dart';
import 'package:agriflow_mobile/features/tasks/presentation/widgets/task_stats_card.dart';
import 'package:agriflow_mobile/shared/widgets/empty_state.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final taskInboxProvider = StreamProvider<List<TaskSummary>>((ref) {
  return ref.watch(taskRepositoryProvider).watchInbox();
});

class TaskInboxScreen extends ConsumerStatefulWidget {
  const TaskInboxScreen({super.key});

  @override
  ConsumerState<TaskInboxScreen> createState() => _TaskInboxScreenState();
}

class _TaskInboxScreenState extends ConsumerState<TaskInboxScreen> {
  TaskFilterScope _scope = TaskFilterScope.all;
  String? _typeFilter;
  final Set<String> _completing = {};

  Future<void> _refresh() async {
    await ref.read(syncOrchestratorProvider).syncNow();
  }

  Future<void> _complete(TaskSummary task) async {
    setState(() => _completing.add(task.name));
    final offline = await isEffectivelyOffline(ref);
    await ref.read(taskRepositoryProvider).completeTask(task);
    if (mounted) {
      if (offline) {
        showSavedOfflineToast(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(AppLocalizations.of(context)!.syncPending(1))),
        );
      }
    }
    await Future<void>.delayed(const Duration(milliseconds: 320));
    if (mounted) setState(() => _completing.remove(task.name));
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final inbox = ref.watch(taskInboxProvider);
    final auth = ref.watch(authSessionProvider).valueOrNull;
    final currentUser = auth?.userName;

    return inbox.when(
      loading: () => const LoadingView(),
      error: (e, _) => Center(child: Text(l10n.errorGeneric)),
      data: (tasks) {
        final filtered = TaskInboxLogic.filterTasks(
          tasks,
          scope: _scope,
          currentUser: currentUser,
          taskType: _typeFilter,
        );
        final grouped = TaskInboxLogic.group(filtered);
        final allEmpty = grouped.overdue.isEmpty &&
            grouped.today.isEmpty &&
            grouped.upcoming.isEmpty;

        if (allEmpty) {
          return RefreshIndicator(
            onRefresh: _refresh,
            child: ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              children: [
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: TaskStatsCard(stats: grouped.stats),
                ),
                _filterBar(l10n),
                SizedBox(
                  height: MediaQuery.sizeOf(context).height * 0.4,
                  child: EmptyState(message: l10n.taskFeedEmptyCelebration),
                ),
              ],
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: _refresh,
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
            children: [
              TaskStatsCard(stats: grouped.stats),
              const SizedBox(height: 12),
              _filterBar(l10n),
              const SizedBox(height: 16),
              if (grouped.overdue.isNotEmpty) ...[
                _sectionTitle(
                  l10n.taskSectionOverdue,
                  grouped.overdue.length,
                  AgriFlowStatusSemantics.error(context),
                ),
                ...grouped.overdue.map(
                  (t) => TaskFeedCard(
                    task: t,
                    bucket: TaskBucket.overdue,
                    completing: _completing.contains(t.name),
                    onTap: () => showTaskDetailSheet(
                      context,
                      ref,
                      t,
                      onComplete: () => _complete(t),
                    ),
                    onComplete: () => _complete(t),
                  ),
                ),
              ],
              if (grouped.today.isNotEmpty) ...[
                _sectionTitle(
                  l10n.taskSectionToday,
                  grouped.today.length,
                  Theme.of(context).colorScheme.tertiary,
                ),
                ...grouped.today.map(
                  (t) => TaskFeedCard(
                    task: t,
                    bucket: TaskBucket.today,
                    completing: _completing.contains(t.name),
                    onTap: () => showTaskDetailSheet(
                      context,
                      ref,
                      t,
                      onComplete: () => _complete(t),
                    ),
                    onComplete: () => _complete(t),
                  ),
                ),
              ],
              if (grouped.upcoming.isNotEmpty) ...[
                _sectionTitle(
                  l10n.taskSectionUpcoming,
                  grouped.upcoming.length,
                  Theme.of(context).colorScheme.primary,
                ),
                ...grouped.upcoming.map(
                  (t) => TaskFeedCard(
                    task: t,
                    bucket: TaskBucket.upcoming,
                    completing: _completing.contains(t.name),
                    onTap: () => showTaskDetailSheet(
                      context,
                      ref,
                      t,
                      onComplete: () => _complete(t),
                    ),
                    onComplete: () => _complete(t),
                  ),
                ),
              ],
            ],
          ),
        );
      },
    );
  }

  Widget _sectionTitle(String label, int count, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, top: 4),
      child: Row(
        children: [
          Icon(Icons.circle, size: 10, color: color),
          const SizedBox(width: 8),
          Text(
            l10n.sectionWithCount(label, count),
            style: const TextStyle(fontWeight: FontWeight.w700),
          ),
        ],
      ),
    );
  }

  Widget _filterBar(AppLocalizations l10n) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          FilterChip(
            label: Text(l10n.taskFilterAll),
            selected: _scope == TaskFilterScope.all && _typeFilter == null,
            onSelected: (_) => setState(() {
              _scope = TaskFilterScope.all;
              _typeFilter = null;
            }),
          ),
          const SizedBox(width: 8),
          FilterChip(
            label: Text(l10n.taskFilterMine),
            selected: _scope == TaskFilterScope.mine,
            onSelected: (_) => setState(() {
              _scope = TaskFilterScope.mine;
              _typeFilter = null;
            }),
          ),
          const SizedBox(width: 8),
          FilterChip(
            label: Text(l10n.taskFilterVisit),
            selected: _typeFilter == 'field_visit',
            onSelected: (_) => setState(() {
              _scope = TaskFilterScope.byType;
              _typeFilter = 'field_visit';
            }),
          ),
          const SizedBox(width: 8),
          FilterChip(
            label: Text(l10n.taskFilterDocument),
            selected: _typeFilter == 'document_collection',
            onSelected: (_) => setState(() {
              _scope = TaskFilterScope.byType;
              _typeFilter = 'document_collection';
            }),
          ),
        ],
      ),
    );
  }
}
