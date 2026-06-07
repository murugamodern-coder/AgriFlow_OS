import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/providers/workflow_provider.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/workflow_ui_helpers.dart';
import 'package:flutter/material.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class TimelineWorkflowProgressCard extends ConsumerWidget {
  const TimelineWorkflowProgressCard({
    super.key,
    required this.projectName,
  });

  final String projectName;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final workflowAsync = ref.watch(projectWorkflowProvider(projectName));
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return workflowAsync.when(
      data: (workflow) {
        final progress = (workflow.stageSequence / 12).clamp(0.0, 1.0);
        var stageColor = 'blue';
        for (final stage in workflow.allStages) {
          if (stage.order == workflow.stageSequence) {
            stageColor = stage.color;
            break;
          }
        }
        final color = workflowColorFromName(stageColor);
        final stateLabel = workflowStageLabel(l10n, workflow.currentStage);

        return Card(
          margin: const EdgeInsets.fromLTRB(
            AgriFlowSpacing.space16,
            0,
            AgriFlowSpacing.space16,
            AgriFlowSpacing.space8,
          ),
          child: Padding(
            padding: const EdgeInsets.all(AgriFlowSpacing.space16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      l10n.currentStageLabel,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    Text(
                      l10n.stageXOf12(workflow.stageSequence),
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AgriFlowSpacing.space8),
                Text(
                  stateLabel,
                  style: theme.textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  workflow.currentState,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: AgriFlowSpacing.space16),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: progress,
                    minHeight: 8,
                    backgroundColor: theme.colorScheme.surfaceContainerHighest,
                    color: color,
                  ),
                ),
              ],
            ),
          ),
        );
      },
      loading: () => Card(
        margin: const EdgeInsets.symmetric(horizontal: AgriFlowSpacing.space16),
        child: const Padding(
          padding: EdgeInsets.all(AgriFlowSpacing.space16),
          child: Center(child: CircularProgressIndicator()),
        ),
      ),
      error: (e, _) => Card(
        margin: const EdgeInsets.symmetric(horizontal: AgriFlowSpacing.space16),
        child: Padding(
          padding: const EdgeInsets.all(AgriFlowSpacing.space16),
          child: Text('${l10n.errorGeneric}: $e'),
        ),
      ),
    );
  }
}
