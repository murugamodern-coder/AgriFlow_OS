import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:agriflow_mobile/core/sync/sync_visual_controller.dart';
import 'package:agriflow_mobile/features/sync/sync_connectivity.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class SyncAppBarStatus extends ConsumerWidget {
  const SyncAppBarStatus({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final visual = ref.watch(syncVisualControllerProvider);
    final theme = Theme.of(context);

    final (icon, color, label) = _resolve(l10n, visual, theme);

    return Padding(
      padding: const EdgeInsets.only(right: AgriFlowSpacing.space8),
      child: Material(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
        child: InkWell(
          onTap: () => _showSyncHint(context, visual),
          borderRadius: BorderRadius.circular(20),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                visual.isRunning
                    ? Icon(icon, size: 16, color: color)
                        .animate(onPlay: (c) => c.repeat())
                        .rotate(duration: 1200.ms)
                    : Icon(icon, size: 16, color: color),
                const SizedBox(width: 6),
                Flexible(
                  child: Text(
                    label,
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: color,
                      fontWeight: FontWeight.w600,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  (IconData, Color, String) _resolve(
    AppLocalizations l10n,
    SyncVisualController visual,
    ThemeData theme,
  ) {
    switch (visual.barMode) {
      case SyncBarMode.justSynced:
        return (
          Icons.check_circle_outline,
          theme.colorScheme.primary,
          l10n.syncBarJustSynced,
        );
      case SyncBarMode.syncing:
        final total = visual.syncTotal > 0 ? visual.syncTotal : 1;
        final current = visual.syncCurrent.clamp(0, total);
        return (
          Icons.sync,
          theme.colorScheme.secondary,
          l10n.syncBarSyncing(current, total),
        );
      case SyncBarMode.offline:
        return (
          Icons.wifi_off,
          theme.colorScheme.error,
          l10n.syncBarOffline(visual.pendingCount),
        );
      case SyncBarMode.online:
        return (
          Icons.cloud_done_outlined,
          theme.colorScheme.primary,
          l10n.syncBarOnline(visual.pendingCount),
        );
    }
  }

  void _showSyncHint(BuildContext context, SyncVisualController visual) {
    final l10n = AppLocalizations.of(context)!;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          visual.isEffectivelyOnline
              ? l10n.syncBarTapHintOnline
              : l10n.syncBarTapHintOffline,
        ),
        duration: const Duration(seconds: 2),
      ),
    );
  }
}
