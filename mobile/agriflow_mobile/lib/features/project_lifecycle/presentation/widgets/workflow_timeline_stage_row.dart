import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:agriflow_mobile/features/project_lifecycle/domain/models/workflow_state.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/workflow_ui_helpers.dart';
import 'package:flutter/material.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';

/// 12-stage workflow row with completed / current / future visual states.
class WorkflowTimelineStageRow extends StatelessWidget {
  const WorkflowTimelineStageRow({
    super.key,
    required this.stage,
    required this.currentStageOrder,
  });

  final WorkflowState stage;
  final int currentStageOrder;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final isCompleted = stage.order < currentStageOrder;
    final isCurrent = stage.order == currentStageOrder;
    final isFuture = stage.order > currentStageOrder;
    final color = workflowColorFromName(stage.color, muted: isFuture);
    final stateLabel = workflowStageLabel(l10n, stage.key);

    return Container(
      padding: const EdgeInsets.symmetric(
        vertical: AgriFlowSpacing.space12,
        horizontal: AgriFlowSpacing.space16,
      ),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isCompleted || isCurrent ? color : Colors.grey.shade300,
              border: isCurrent ? Border.all(color: color, width: 3) : null,
            ),
            child: Center(
              child: isCompleted
                  ? const Icon(Icons.check, color: Colors.white, size: 18)
                  : Text(
                      '${stage.order}',
                      style: TextStyle(
                        color: isFuture ? Colors.grey.shade600 : Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                    ),
            ),
          ),
          const SizedBox(width: AgriFlowSpacing.space16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  stateLabel,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: isCurrent ? FontWeight.bold : FontWeight.w500,
                    color: isFuture ? Colors.grey.shade600 : Colors.black87,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  stage.state,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ),
          ),
          if (isCurrent)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                l10n.currentStageLabel,
                style: TextStyle(
                  color: color,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
