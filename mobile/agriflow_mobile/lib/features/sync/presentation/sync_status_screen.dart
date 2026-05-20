import 'package:agriflow_mobile/core/config/env.dart';
import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/core/storage/hive_boxes.dart';
import 'package:agriflow_mobile/core/sync/sync_visual_controller.dart';
import 'package:agriflow_mobile/features/sync/sync_connectivity.dart';
import 'package:agriflow_mobile/shared/widgets/conflict_sheet.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

class SyncStatusScreen extends ConsumerStatefulWidget {
  const SyncStatusScreen({super.key});

  @override
  ConsumerState<SyncStatusScreen> createState() => _SyncStatusScreenState();
}

class _SyncStatusScreenState extends ConsumerState<SyncStatusScreen> {
  List<SyncQueueRow> _pending = [];
  List<SyncQueueRow> _conflicts = [];
  List<SyncRunRow> _history = [];
  bool _loading = false;
  String? _error;
  String? _syncPhase;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final db = ref.read(appDatabaseProvider);
    final pending = await db.pendingQueue(limit: 20);
    final conflicts = await db.conflictRows();
    final history = await db.recentSyncRuns(limit: 10);
    if (mounted) {
      setState(() {
        _pending = pending;
        _conflicts = conflicts;
        _history = history;
      });
    }
    await ref.read(syncVisualControllerProvider).refresh();
  }

  Future<void> _syncNow({bool force = true}) async {
    if (_loading) return;
    setState(() {
      _loading = true;
      _error = null;
      _syncPhase = 'repair';
    });
    try {
      await ref.read(syncOrchestratorProvider).syncNow(
            force: force,
            onPhase: (phase) {
              if (mounted) setState(() => _syncPhase = phase);
            },
          );
      ref.invalidate(syncStatusProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(AppLocalizations.of(context)!.syncToastComplete)),
        );
      }
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) {
        setState(() => _loading = false);
        await _load();
      }
    }
  }

  String _timeAgo(DateTime? dt, AppLocalizations l10n) {
    if (dt == null) return l10n.syncNever;
    final diff = DateTime.now().toUtc().difference(dt.toUtc());
    if (diff.inMinutes < 1) return l10n.syncJustNow;
    if (diff.inMinutes < 60) return l10n.syncMinutesAgo(diff.inMinutes);
    if (diff.inHours < 24) return l10n.syncHoursAgo(diff.inHours);
    return DateFormat('MMM d, HH:mm').format(dt.toLocal());
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final visual = ref.watch(syncVisualControllerProvider);
    final theme = Theme.of(context);

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(AgriFlowSpacing.space16),
        children: [
          Text(l10n.syncStatusTitle, style: theme.textTheme.titleLarge),
          const SizedBox(height: AgriFlowSpacing.space12),
          _statusHero(context, visual, l10n),
          const SizedBox(height: AgriFlowSpacing.space16),
          FilledButton.icon(
            onPressed: _loading ? null : () => _syncNow(),
            icon: _loading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.sync),
            label: Text(l10n.syncForceNow),
          ),
          if (_loading && _syncPhase != null) ...[
            const SizedBox(height: 12),
            LinearProgressIndicator(),
            Text(l10n.syncPhaseLabel(_syncPhase!)),
          ],
          if (_error != null)
            Text(_error!, style: TextStyle(color: theme.colorScheme.error)),
          const SizedBox(height: AgriFlowSpacing.space24),
          Text(l10n.syncPendingListTitle, style: theme.textTheme.titleMedium),
          if (_pending.isEmpty)
            ListTile(title: Text(l10n.syncPendingListEmpty))
          else
            ..._pending.map(
              (row) => ListTile(
                leading: Icon(_iconForEntity(row.entity)),
                title: Text('${row.entity} · ${row.opType}'),
                subtitle: Text(
                  row.farmerProject ?? row.clientMutationId,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                dense: true,
              ).animate().fadeIn(duration: 200.ms),
            ),
          const SizedBox(height: AgriFlowSpacing.space24),
          Text(l10n.syncHistoryTitle, style: theme.textTheme.titleMedium),
          if (_history.isEmpty)
            ListTile(title: Text(l10n.syncHistoryEmpty))
          else
            ..._history.map(
              (run) => ListTile(
                leading: Icon(
                  run.success ? Icons.check_circle : Icons.error_outline,
                  color: run.success
                      ? theme.colorScheme.primary
                      : theme.colorScheme.error,
                ),
                title: Text(run.phase),
                subtitle: Text(
                  '${run.success ? l10n.syncHistoryOk : l10n.syncHistoryFail} · ${_formatRunTime(run.startedAt)}',
                ),
                dense: true,
              ),
            ),
          if (Env.demoMode) ...[
            const SizedBox(height: AgriFlowSpacing.space24),
            Text(l10n.syncDeveloperTitle, style: theme.textTheme.titleMedium),
            SwitchListTile(
              title: Text(l10n.syncSimulateOffline),
              subtitle: Text(l10n.syncSimulateOfflineHint),
              value: visual.simulateOffline,
              onChanged: (v) async {
                await visual.setSimulateOffline(v);
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(
                        v ? l10n.syncSimulateOfflineOn : l10n.syncSimulateOfflineOff,
                      ),
                    ),
                  );
                }
              },
            ),
            OutlinedButton.icon(
              onPressed: _loading
                  ? null
                  : () async {
                      await visual.setSimulateOffline(false);
                      await _syncNow(force: true);
                    },
              icon: const Icon(Icons.cloud_upload),
              label: Text(l10n.syncDemoFlowButton),
            ),
          ],
          if (_conflicts.isNotEmpty) ...[
            const SizedBox(height: AgriFlowSpacing.space24),
            Text(l10n.conflictTitle, style: theme.textTheme.titleMedium),
            ..._conflicts.map(
              (row) => ListTile(
                title: Text(row.clientMutationId),
                subtitle: Text(row.lastErrorCode ?? 'SYNC_CONFLICT_LWW'),
                trailing: IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: () => ConflictSheet.show(
                    context,
                    clientMutationId: row.clientMutationId,
                    onRefresh: () => _syncNow(),
                  ),
                ),
              ),
            ),
          ],
          const SizedBox(height: 48),
        ],
      ),
    );
  }

  Widget _statusHero(
    BuildContext context,
    SyncVisualController visual,
    AppLocalizations l10n,
  ) {
    final theme = Theme.of(context);
    final raw = ref
        .read(hiveStorageProvider)
        .box(HiveBoxNames.syncMeta)
        .get('last_success_at') as String?;
    final last = visual.lastSuccessAt ?? DateTime.tryParse(raw ?? '');

    return Card(
      color: theme.colorScheme.primaryContainer.withValues(alpha: 0.35),
      child: Padding(
        padding: const EdgeInsets.all(AgriFlowSpacing.space16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.syncLastSuccessLabel(_timeAgo(last, l10n)),
              style: theme.textTheme.titleSmall,
            ),
            const SizedBox(height: 8),
            Text(
              l10n.syncPendingChanges(visual.pendingCount),
              style: theme.textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600),
            ),
          ],
        ),
      ),
    );
  }

  IconData _iconForEntity(String entity) {
    switch (entity) {
      case 'task':
        return Icons.task_alt;
      case 'timeline':
        return Icons.timeline;
      default:
        return Icons.cloud_upload;
    }
  }

  String _formatRunTime(String iso) {
    final dt = DateTime.tryParse(iso);
    if (dt == null) return iso;
    return DateFormat('MMM d · HH:mm').format(dt.toLocal());
  }
}
