import 'package:agriflow_mobile/core/design_tokens/color_tokens.dart';
import 'package:agriflow_mobile/core/sync/sync_status.dart';
import 'package:flutter/material.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';

class SyncStatusChip extends StatelessWidget {
  const SyncStatusChip({super.key, required this.status});

  final SyncStatusSummary status;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final color = status.pendingCount > 0
        ? AgriFlowColors.warning
        : AgriFlowColors.success;
    final label = status.isRunning
        ? l10n.syncInProgress
        : l10n.syncPending(status.pendingCount);
    return Chip(
      avatar: Icon(
        status.isRunning ? Icons.sync : Icons.cloud_done,
        size: 16,
        color: color,
      ),
      label: Text(label, style: Theme.of(context).textTheme.labelSmall),
      visualDensity: VisualDensity.compact,
    );
  }
}
