import 'package:agriflow_mobile/core/sync/sync_visual_controller.dart';
import 'package:agriflow_mobile/features/sync/sync_connectivity.dart';
import 'package:flutter/material.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Shows Tamil toasts when sync state transitions (saved offline / synced).
class SyncFeedbackListener extends ConsumerStatefulWidget {
  const SyncFeedbackListener({super.key, required this.child});

  final Widget child;

  @override
  ConsumerState<SyncFeedbackListener> createState() => _SyncFeedbackListenerState();
}

class _SyncFeedbackListenerState extends ConsumerState<SyncFeedbackListener> {
  SyncBarMode? _lastMode;
  bool _wasRunning = false;

  @override
  Widget build(BuildContext context) {
    final visual = ref.watch(syncVisualControllerProvider);
    final l10n = AppLocalizations.of(context)!;

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_wasRunning && !visual.isRunning && visual.barMode == SyncBarMode.justSynced) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.syncToastComplete),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
      if (_lastMode == SyncBarMode.offline &&
          visual.barMode == SyncBarMode.syncing) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.syncToastStarted),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
      _lastMode = visual.barMode;
      _wasRunning = visual.isRunning;
    });

    return widget.child;
  }
}

/// Call after queueing a mutation while offline.
void showSavedOfflineToast(BuildContext context) {
  final l10n = AppLocalizations.of(context)!;
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text(l10n.syncToastSavedOffline),
      behavior: SnackBarBehavior.floating,
    ),
  );
}
