import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:agriflow_mobile/core/i18n/agriflow_i18n.dart';
import 'package:agriflow_mobile/features/tasks/domain/task_summary.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

Future<void> showTaskDetailSheet(
  BuildContext context,
  WidgetRef ref,
  TaskSummary task, {
  required Future<void> Function() onComplete,
}) {
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    showDragHandle: true,
    builder: (ctx) => _TaskDetailSheetBody(
      task: task,
      onComplete: onComplete,
    ),
  );
}

class _TaskDetailSheetBody extends ConsumerStatefulWidget {
  const _TaskDetailSheetBody({
    required this.task,
    required this.onComplete,
  });

  final TaskSummary task;
  final Future<void> Function() onComplete;

  @override
  ConsumerState<_TaskDetailSheetBody> createState() => _TaskDetailSheetBodyState();
}

class _TaskDetailSheetBodyState extends ConsumerState<_TaskDetailSheetBody> {
  bool _checkedIn = false;
  bool _voiceQueued = false;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final task = widget.task;
    final bottom = MediaQuery.paddingOf(context).bottom;

    return Padding(
      padding: EdgeInsets.fromLTRB(
        AgriFlowSpacing.space16,
        0,
        AgriFlowSpacing.space16,
        AgriFlowSpacing.space24 + bottom,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(task.subject, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: AgriFlowSpacing.space8),
          Text(l10n.taskFarmerVillageLine(task.displayFarmer, task.displayVillage)),
          if (task.stageKey != null)
            Text(AgriFlowI18n.stageLabel(context, task.stageKey!)),
          const SizedBox(height: AgriFlowSpacing.space16),
          OutlinedButton.icon(
            onPressed: () async {
              await HapticFeedback.lightImpact();
              setState(() => _checkedIn = true);
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(l10n.taskGpsCheckedIn)),
                );
              }
            },
            icon: Icon(_checkedIn ? Icons.check_circle : Icons.location_on_outlined),
            label: Text(
              _checkedIn ? l10n.taskGpsCheckedIn : l10n.taskGpsCheckIn,
            ),
          ),
          const SizedBox(height: AgriFlowSpacing.space8),
          OutlinedButton.icon(
            onPressed: () async {
              setState(() => _voiceQueued = true);
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(l10n.taskVoiceNoteQueued)),
                );
              }
            },
            icon: Icon(_voiceQueued ? Icons.mic : Icons.mic_none_outlined),
            label: Text(l10n.taskVoiceNoteAttach),
          ),
          const SizedBox(height: AgriFlowSpacing.space16),
          FilledButton(
            onPressed: task.isOpen
                ? () async {
                    await HapticFeedback.mediumImpact();
                    await widget.onComplete();
                    if (context.mounted) Navigator.pop(context);
                  }
                : null,
            child: Text(l10n.taskComplete),
          ),
        ],
      ),
    );
  }
}
