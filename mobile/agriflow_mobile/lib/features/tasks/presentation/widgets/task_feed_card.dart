import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:agriflow_mobile/core/i18n/agriflow_i18n.dart';
import 'package:agriflow_mobile/features/tasks/domain/task_inbox_logic.dart';
import 'package:agriflow_mobile/features/tasks/domain/task_summary.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:url_launcher/url_launcher.dart';

class TaskFeedCard extends StatelessWidget {
  const TaskFeedCard({
    super.key,
    required this.task,
    required this.bucket,
    required this.onTap,
    required this.onComplete,
    this.completing = false,
  });

  final TaskSummary task;
  final TaskBucket bucket;
  final VoidCallback onTap;
  final Future<void> Function() onComplete;
  final bool completing;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    Widget card = Card(
      margin: const EdgeInsets.only(bottom: AgriFlowSpacing.space8),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(AgriFlowSpacing.space12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _typeIcon(context, task.taskType),
              const SizedBox(width: AgriFlowSpacing.space12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      task.displayFarmer,
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    if (task.displayVillage.isNotEmpty)
                      Text(
                        task.displayVillage,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    const SizedBox(height: 4),
                    Text(task.subject, style: theme.textTheme.bodyMedium),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        _dueChip(context, l10n),
                        if (task.stageKey != null) ...[
                          const SizedBox(width: 8),
                          Flexible(
                            child: Text(
                              AgriFlowI18n.stageLabel(context, task.stageKey!),
                              style: theme.textTheme.labelSmall,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
              Column(
                children: [
                  IconButton(
                    icon: const Icon(Icons.phone_outlined, size: 20),
                    onPressed: () => _callDemo(context),
                    tooltip: l10n.timelineActionCall,
                  ),
                  IconButton(
                    icon: const Icon(Icons.chat_outlined, size: 20),
                    onPressed: () => _whatsappDemo(context),
                    tooltip: l10n.timelineActionWhatsapp,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );

    if (completing) {
      card = card
          .animate()
          .scale(end: const Offset(0.92, 0.92), duration: 280.ms)
          .fadeOut(duration: 280.ms);
    }

    return Dismissible(
      key: ValueKey(task.name),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        margin: const EdgeInsets.only(bottom: AgriFlowSpacing.space8),
        decoration: BoxDecoration(
          color: theme.colorScheme.primary,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(Icons.check_circle, color: theme.colorScheme.onPrimary),
      ),
      confirmDismiss: (_) async {
        await HapticFeedback.mediumImpact();
        await onComplete();
        return true;
      },
      child: card,
    );
  }

  Widget _dueChip(BuildContext context, AppLocalizations l10n) {
    final theme = Theme.of(context);
    Color color = theme.colorScheme.primary;
    String label;
    switch (bucket) {
      case TaskBucket.overdue:
        color = theme.colorScheme.error;
        label = l10n.taskDueDaysAgo(TaskInboxLogic.daysOverdue(task));
      case TaskBucket.today:
        color = theme.colorScheme.tertiary;
        label = l10n.taskDueToday;
      case TaskBucket.upcoming:
        label = l10n.taskDueInDays(TaskInboxLogic.daysUntil(task));
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(label, style: theme.textTheme.labelSmall?.copyWith(color: color)),
    );
  }

  Widget _typeIcon(BuildContext context, String? type) {
    final scheme = Theme.of(context).colorScheme;
    IconData icon;
    Color color = scheme.primary;
    switch (type) {
      case 'document_collection':
        icon = Icons.description_outlined;
        color = scheme.tertiary;
      case 'verification':
      case 'approval':
        icon = Icons.fact_check_outlined;
      case 'installation':
        icon = Icons.build_outlined;
      case 'follow_up':
        icon = Icons.phone_in_talk_outlined;
      default:
        icon = Icons.agriculture_outlined;
    }
    return CircleAvatar(
      radius: 22,
      backgroundColor: color.withValues(alpha: 0.15),
      child: Icon(icon, color: color, size: 22),
    );
  }

  Future<void> _callDemo(BuildContext context) async {
    final uri = Uri.parse('tel:98765000001');
    if (await canLaunchUrl(uri)) await launchUrl(uri);
  }

  Future<void> _whatsappDemo(BuildContext context) async {
    final uri = Uri.parse('https://wa.me/9198765000001');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }
}
