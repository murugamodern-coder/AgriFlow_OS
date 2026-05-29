import 'package:agriflow_mobile/core/design_tokens/color_tokens.dart';
import 'package:flutter/material.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';

/// Offline / degraded-network indicator with optional sync context.
class OfflineBanner extends StatelessWidget {
  const OfflineBanner({
    super.key,
    required this.visible,
    this.pendingCount,
    this.lastSyncLabel,
    this.degradedNetwork = false,
  });

  final bool visible;
  final int? pendingCount;
  final String? lastSyncLabel;
  final bool degradedNetwork;

  @override
  Widget build(BuildContext context) {
    if (!visible && !degradedNetwork) return const SizedBox.shrink();
    final l10n = AppLocalizations.of(context)!;
    final color = visible ? AgriFlowColors.warning : AgriFlowColors.info;
    final icon = visible ? Icons.cloud_off : Icons.signal_wifi_statusbar_connected_no_internet_4;
    final title = visible
        ? l10n.offlineBanner
        : l10n.degradedNetworkBanner;
    final subtitle = _subtitle(l10n);

    return Material(
      color: color.withOpacity(0.15),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, size: 18, color: color),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: Theme.of(context).textTheme.bodySmall),
                  if (subtitle != null)
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.labelSmall,
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String? _subtitle(AppLocalizations l10n) {
    final parts = <String>[];
    if (pendingCount != null && pendingCount! > 0) {
      parts.add(l10n.offlinePendingHint(pendingCount!));
    }
    if (lastSyncLabel != null && lastSyncLabel!.isNotEmpty) {
      parts.add(l10n.syncLastSuccess(lastSyncLabel!));
    }
    return parts.isEmpty ? null : parts.join(' · ');
  }
}
