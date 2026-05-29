import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:agriflow_mobile/core/i18n/agriflow_i18n.dart';
import 'package:agriflow_mobile/shared/widgets/agriflow_status_icon.dart';
import 'package:agriflow_mobile/features/project_lifecycle/domain/project_timeline_detail.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';

class TimelineStageRow extends StatelessWidget {
  const TimelineStageRow({
    super.key,
    required this.stage,
    required this.expanded,
    required this.onToggleExpand,
  });

  final StageRowModel stage;
  final bool expanded;
  final VoidCallback? onToggleExpand;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final label = AgriFlowI18n.stageLabel(context, stage.stageKey);
    final muted = theme.colorScheme.onSurface.withValues(alpha: 0.45);

    Widget row = InkWell(
      onTap: stage.isDone ? onToggleExpand : null,
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.symmetric(
          vertical: AgriFlowSpacing.space8,
          horizontal: AgriFlowSpacing.space4,
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            AgriFlowStatusIcon(kind: _kindFor(stage.visualState)),
            const SizedBox(width: AgriFlowSpacing.space12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight:
                          stage.isCurrent ? FontWeight.w700 : FontWeight.w500,
                      color: stage.isPending || stage.visualState == StageVisualState.locked
                          ? muted
                          : null,
                    ),
                  ),
                  if (stage.isCurrent)
                    Text(
                      l10n.timelineStageToday,
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: theme.colorScheme.primary,
                        fontWeight: FontWeight.w600,
                      ),
                    )
                  else if (stage.isPending)
                    Text(l10n.timelineStagePending, style: TextStyle(color: muted))
                  else if (stage.visualState == StageVisualState.locked)
                    Text(l10n.timelineStageLocked, style: TextStyle(color: muted)),
                  if (stage.dateLabel != null && stage.isDone)
                    Text(
                      stage.dateLabel!,
                      style: theme.textTheme.bodySmall,
                    ),
                  Builder(
                    builder: (innerCtx) {
                      final localized = AgriFlowI18n.stageSecondary(
                        innerCtx,
                        stage.secondaryI18nKey,
                        arg: stage.secondaryI18nArg,
                      );
                      final text = localized ?? stage.secondaryLabel;
                      if (text == null || text.isEmpty) {
                        return const SizedBox.shrink();
                      }
                      return Text(
                        text,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
            if (stage.isDone)
              Icon(
                expanded ? Icons.expand_less : Icons.expand_more,
                color: theme.colorScheme.onSurfaceVariant,
              ),
          ],
        ),
      ),
    );

    if (stage.isCurrent) {
      row = row
          .animate(onPlay: (c) => c.repeat(reverse: true))
          .shimmer(
            duration: 1800.ms,
            color: theme.colorScheme.primary.withValues(alpha: 0.12),
          )
          .then()
          .scale(
            begin: const Offset(1, 1),
            end: const Offset(1.01, 1.01),
            duration: 1200.ms,
            curve: Curves.easeInOut,
          );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        row,
        if (expanded && stage.isDone)
          Padding(
            padding: const EdgeInsets.only(left: 40, top: 4, bottom: 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (stage.actorLabel != null)
                  Text(
                    l10n.timelineStageBy(stage.actorLabel!),
                    style: theme.textTheme.bodySmall,
                  ),
                if (stage.notes != null && stage.notes!.isNotEmpty)
                  Text(stage.notes!, style: theme.textTheme.bodySmall),
              ],
            ),
          ),
      ],
    );
  }

  AgriFlowStatusKind _kindFor(StageVisualState state) {
    switch (state) {
      case StageVisualState.done:
        return AgriFlowStatusKind.done;
      case StageVisualState.current:
        return AgriFlowStatusKind.active;
      case StageVisualState.pending:
        return AgriFlowStatusKind.pending;
      case StageVisualState.locked:
        return AgriFlowStatusKind.locked;
    }
  }
}
