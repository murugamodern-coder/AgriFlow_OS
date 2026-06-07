import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/features/project_lifecycle/domain/models/workflow_state.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/providers/workflow_provider.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/project_timeline_screen.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/workflow_ui_helpers.dart';
import 'package:flutter/material.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class TimelineWorkflowActions extends ConsumerWidget {
  const TimelineWorkflowActions({
    super.key,
    required this.projectName,
  });

  final String projectName;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final workflowAsync = ref.watch(projectWorkflowProvider(projectName));
    final l10n = AppLocalizations.of(context)!;

    return workflowAsync.when(
      data: (workflow) {
        if (workflow.actions.isEmpty) {
          return Padding(
            padding: const EdgeInsets.only(bottom: AgriFlowSpacing.space12),
            child: Text(
              workflow.stageSequence >= 12
                  ? '✅ ${l10n.stageSubsidyReleased}'
                  : l10n.workflowNoActionsForRole,
              style: TextStyle(color: Colors.grey.shade600),
            ),
          );
        }

        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            for (final action in workflow.actions)
              Padding(
                padding: const EdgeInsets.only(bottom: AgriFlowSpacing.space8),
                child: FilledButton.icon(
                  onPressed: () => _confirmAndApply(context, ref, action),
                  icon: const Icon(Icons.arrow_forward),
                  label: Text(workflowActionLabel(l10n, action.action)),
                  style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
          ],
        );
      },
      loading: () => const Padding(
        padding: EdgeInsets.symmetric(vertical: AgriFlowSpacing.space12),
        child: Center(child: CircularProgressIndicator()),
      ),
      error: (e, _) => Padding(
        padding: const EdgeInsets.only(bottom: AgriFlowSpacing.space12),
        child: Text('${l10n.errorGeneric}: $e'),
      ),
    );
  }

  Future<void> _confirmAndApply(
    BuildContext context,
    WidgetRef ref,
    WorkflowAction action,
  ) async {
    final l10n = AppLocalizations.of(context)!;
    final nextLabel = workflowNextStateLabel(l10n, action);

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.confirmStageTransition),
        content: Text('${l10n.confirmMessageAdvance}\n\n→ $nextLabel'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(l10n.cancel),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: Text(l10n.confirm),
          ),
        ],
      ),
    );

    if (confirmed != true || !context.mounted) return;

    try {
      await ref.read(workflowRepositoryProvider).applyAction(projectName, action.action);
      ref.invalidate(projectWorkflowProvider(projectName));
      ref.invalidate(projectTimelineDetailProvider(projectName));
      await ref.read(syncOrchestratorProvider).syncNow();
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(l10n.transitionSuccess),
          backgroundColor: Colors.green.shade700,
        ),
      );
    } catch (e) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${l10n.transitionFailed}: $e'),
          backgroundColor: Colors.red.shade700,
        ),
      );
    }
  }
}
