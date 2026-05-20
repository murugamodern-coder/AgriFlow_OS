import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
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
          ? tone.background.withValues(alpha: 0.08)
          : theme.colorScheme.surface,
      child: ListTile(
        onTap: onTap,
        leading: CircleAvatar(
          backgroundColor: tone.background.withValues(alpha: 0.2),
          child: Icon(tone.icon, color: tone.foreground, size: 22),
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

  _ToneStyle _toneStyle(ThemeData theme, NotificationTone tone) {
    switch (tone) {
      case NotificationTone.urgent:
        return _ToneStyle(theme.colorScheme.error, Icons.warning_amber_rounded);
      case NotificationTone.warning:
        return _ToneStyle(theme.colorScheme.tertiary, Icons.schedule);
      case NotificationTone.orange:
        return _ToneStyle(const Color(0xFFE65100), Icons.inventory_2_outlined);
      case NotificationTone.success:
        return _ToneStyle(theme.colorScheme.primary, Icons.check_circle_outline);
      case NotificationTone.info:
        return _ToneStyle(theme.colorScheme.primary, Icons.info_outline);
    }
  }
}

class _ToneStyle {
  const _ToneStyle(this.foreground, this.icon);
  final Color foreground;
  final IconData icon;

  Color get background => foreground;
}
