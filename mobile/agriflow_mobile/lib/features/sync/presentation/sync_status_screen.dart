import 'package:agriflow_mobile/core/config/env.dart';
import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/features/commercial/data/commercial_remote.dart';
import 'package:agriflow_mobile/core/sync/sync_status.dart';
import 'package:agriflow_mobile/shared/widgets/conflict_sheet.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class SyncStatusScreen extends ConsumerStatefulWidget {
  const SyncStatusScreen({super.key});

  @override
  ConsumerState<SyncStatusScreen> createState() => _SyncStatusScreenState();
}

class _SyncStatusScreenState extends ConsumerState<SyncStatusScreen> {
  SyncStatusSummary? _status;
  List<SyncQueueRow> _conflicts = [];
  bool _loading = false;
  bool _syncLocked = false;
  String? _error;
  String? _syncPhase;
  DeviceHealthSummary? _deviceHealth;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    final db = ref.read(appDatabaseProvider);
    final summary = await ref.read(syncOrchestratorProvider).buildStatusSummary();
    final rows = await db.conflictRows();
    DeviceHealthSummary? health;
    try {
      health = await ref.read(commercialRemoteProvider).fetchDeviceHealth();
    } catch (_) {}
    if (mounted) {
      setState(() {
        _status = summary;
        _conflicts = rows;
        _deviceHealth = health;
      });
    }
  }

  Future<void> _syncNow() async {
    if (_syncLocked) return;
    setState(() {
      _syncLocked = true;
      _loading = true;
      _error = null;
      _syncPhase = 'repair';
    });
    try {
      final summary = await ref.read(syncOrchestratorProvider).syncNow(
            force: true,
            onPhase: (phase) {
              if (mounted) setState(() => _syncPhase = phase);
            },
          );
      await _refresh();
      if (mounted) setState(() => _status = summary);
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
          _syncLocked = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    if (_status == null) return const LoadingView();

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(l10n.syncStatusTitle, style: Theme.of(context).textTheme.titleLarge),
        Text(
          l10n.appVersionLabel(Env.appVersion),
          style: Theme.of(context).textTheme.bodySmall,
        ),
        if (_deviceHealth?.healthScore != null) ...[
          Text(
            l10n.deviceHealthLabel('${_deviceHealth!.healthScore}'),
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          if (_deviceHealth!.stale)
            Text(
              l10n.deviceStaleWarning,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          const SizedBox(height: 8),
        ],
        const SizedBox(height: 16),
        ListTile(
          title: Text(l10n.syncPending(_status!.pendingCount)),
          subtitle: Text(
            'Conflicts: ${_status!.conflictCount} · Phase: ${_status!.lastPhase ?? '-'}',
          ),
        ),
        if (_status!.lastRequestId != null)
          ListTile(
            title: Text(l10n.syncLastRequestId),
            subtitle: Text(_status!.lastRequestId!),
          ),
        if (_error != null)
          Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
        if (_loading && _syncPhase != null) ...[
          const SizedBox(height: 12),
          LinearProgressIndicator(),
          const SizedBox(height: 8),
          Text(l10n.syncPhaseLabel(_syncPhase!)),
        ],
        const SizedBox(height: 16),
        OutlinedButton(
          onPressed: _loading
              ? null
              : () async {
                  final report =
                      await ref.read(syncOrchestratorProvider).repairQueue();
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(
                          l10n.queueRepairResult(
                            report.resetStuck,
                            report.deduped,
                          ),
                        ),
                      ),
                    );
                  }
                  await _refresh();
                },
          child: Text(l10n.syncRepairQueue),
        ),
        const SizedBox(height: 8),
        FilledButton(
          onPressed: _loading ? null : _syncNow,
          child: _loading
              ? const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : Text(l10n.syncNow),
        ),
        if (_conflicts.isNotEmpty) ...[
          const SizedBox(height: 24),
          Text(l10n.conflictTitle, style: Theme.of(context).textTheme.titleMedium),
          ..._conflicts.map((row) {
            return ListTile(
              title: Text(row.clientMutationId),
              subtitle: Text(row.lastErrorCode ?? 'SYNC_CONFLICT_LWW'),
              trailing: IconButton(
                icon: const Icon(Icons.refresh),
                onPressed: () => ConflictSheet.show(
                  context,
                  clientMutationId: row.clientMutationId,
                  onRefresh: _syncNow,
                ),
              ),
            );
          }),
        ],
      ],
    );
  }
}
