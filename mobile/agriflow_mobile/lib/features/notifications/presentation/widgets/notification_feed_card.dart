import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:agriflow_mobile/core/design_tokens/status_semantics.dart';
import 'package:agriflow_mobile/shared/widgets/agriflow_status_icon.dart';
import 'package:agriflow_mobile/core/i18n/agriflow_i18n.dart';
import 'package:agriflow_mobile/features/notifications/domain/notification_inbox_logic.dart';
import 'package:agriflow_mobile/features/notifications/domain/notification_item.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

class NotificationFeedCard extends StatelessWidget {
  const NotificationFeedCard({
    super.key,
    required this.item,
    required this.onTap,
    required this.onDismiss,
    this.animateIndex = 0,
  });

  final NotificationItem item;
  final VoidCallback onTap;
  final Future<bool> Function() onDismiss;
  final int animateIndex;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final tone = _toneStyle(theme, item.tone);
    final title = item.bodyPreview?.isNotEmpty == true
        ? item.bodyPreview!
        : AgriFlowI18n.notificationTitle(context, item.titleI18nKey);

    Widget card = Card(
      margin: const EdgeInsets.only(bottom: AgriFlowSpacing.space8),
      color: item.isUnread
          ? tone.foreground.withValues(alpha: 0.08)
          : theme.colorScheme.surface,
      child: ListTile(
        onTap: onTap,
        leading: CircleAvatar(
          backgroundColor: tone.foreground.withValues(alpha: 0.15),
          child: AgriFlowStatusIcon(kind: tone.kind, size: 22),
        ),
        title: Text(
          title,
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: item.isUnread ? FontWeight.w700 : FontWeight.w500,
          ),
        ),
        subtitle: Text(
          AgriFlowI18n.notificationTitle(context, item.titleI18nKey),
          style: theme.textTheme.bodySmall,
        ),
        trailing: Text(
          NotificationInboxLogic.timeAgo(item.createdOn),
          style: theme.textTheme.labelSmall,
        ),
      ),
    );

    card = card
        .animate()
        .fadeIn(duration: 320.ms, delay: (animateIndex * 40).ms)
        .slideX(begin: 0.05, end: 0, duration: 320.ms, delay: (animateIndex * 40).ms);

    return Dismissible(
      key: ValueKey(item.name),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 24),
        margin: const EdgeInsets.only(bottom: AgriFlowSpacing.space8),
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Icon(Icons.close),
      ),
      confirmDismiss: (_) => onDismiss(),
      child: card,
    );
  }

  _ToneStyle _toneStyle(BuildContext context, NotificationTone tone) {
    switch (tone) {
      case NotificationTone.urgent:
        return _ToneStyle(
          AgriFlowStatusSemantics.error(context),
          AgriFlowStatusKind.overdue,
        );
      case NotificationTone.warning:
        return _ToneStyle(
          AgriFlowStatusSemantics.warning(context),
          AgriFlowStatusKind.warning,
        );
      case NotificationTone.orange:
        return _ToneStyle(
          AgriFlowStatusSemantics.alertOrange(context),
          AgriFlowStatusKind.warning,
        );
      case NotificationTone.success:
        return _ToneStyle(
          AgriFlowStatusSemantics.success(context),
          AgriFlowStatusKind.done,
        );
      case NotificationTone.info:
        return _ToneStyle(
          AgriFlowStatusSemantics.info(context),
          AgriFlowStatusKind.info,
        );
    }
  }
}

class _ToneStyle {
  const _ToneStyle(this.foreground, this.kind);
  final Color foreground;
  final AgriFlowStatusKind kind;
}
