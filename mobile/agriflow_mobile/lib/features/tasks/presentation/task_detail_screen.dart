import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:agriflow_mobile/features/tasks/domain/task_summary.dart';
import 'package:agriflow_mobile/shared/widgets/conflict_sheet.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

class TaskDetailScreen extends ConsumerStatefulWidget {
  const TaskDetailScreen({
    super.key,
    required this.taskName,
    this.farmerProject,
  });

  final String taskName;
  final String? farmerProject;

  @override
  ConsumerState<TaskDetailScreen> createState() => _TaskDetailScreenState();
}

class _TaskDetailScreenState extends ConsumerState<TaskDetailScreen> {
  TaskSummary? _task;
  List<Map<String, dynamic>> _allocations = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final tasks = await ref.read(taskRepositoryProvider).readCachedInbox();
      for (final t in tasks) {
        if (t.name == widget.taskName) {
          _task = t;
          break;
        }
      }
      if (widget.farmerProject != null) {
        _allocations = await ref
            .read(inventoryRemoteProvider)
            .listAllocations(widget.farmerProject!);
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _completeQueued() async {
    final task = _task;
    if (task == null) return;
    final l10n = AppLocalizations.of(context)!;
    await ref.read(taskRepositoryProvider).completeTask(task);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(l10n.syncPending(1))),
      );
      Navigator.pop(context);
    }
  }

  Future<void> _consumePartial(Map<String, dynamic> alloc) async {
    final l10n = AppLocalizations.of(context)!;
    try {
      final connectivity = await ref.read(connectivityProvider).checkConnectivity();
      final offline = connectivity.contains(ConnectivityResult.none);
      if (offline) {
        await ref.read(inventoryQueueProvider).enqueueConsume(
              allocation: alloc['name'] as String,
              qty: 1,
              docVersion: alloc['doc_version'] as int? ?? 1,
              batchNo: alloc['batch_no'] as String?,
              farmerProject: widget.farmerProject,
            );
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(l10n.syncPending(1))),
          );
        }
        return;
      }
      final remote = ref.read(inventoryRemoteProvider);
      await remote.consume(
        allocation: alloc['name'] as String,
        qty: 1,
        docVersion: alloc['doc_version'] as int? ?? 1,
        clientId: const Uuid().v4().replaceAll('-', '').substring(0, 28),
        batchNo: alloc['batch_no'] as String?,
      );
      await _load();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.taskComplete)),
        );
      }
    } catch (e) {
      if (mounted) {
        final msg = e.toString();
        if (msg.contains('SYNC_CONFLICT') || msg.contains('doc_version')) {
          await ConflictSheet.show(
            context,
            clientMutationId: 'inventory-consume',
            onRefresh: _load,
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    if (_loading) return const Scaffold(body: LoadingView());
    if (_task == null) {
      return Scaffold(
        appBar: AppBar(title: Text(widget.taskName)),
        body: Center(child: Text(_error ?? l10n.emptyTasks)),
      );
    }
    final task = _task!;
    final isInstallation = task.subject.toLowerCase().contains('install') ||
        (task.farmerProject?.isNotEmpty ?? false);

    return Scaffold(
      appBar: AppBar(title: Text(task.subject)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text('${task.status} · ${task.farmerProject ?? ''}'),
          const SizedBox(height: 16),
          FilledButton(
            onPressed: task.status == 'completed' ? null : _completeQueued,
            child: Text(l10n.taskComplete),
          ),
          if (isInstallation && _allocations.isNotEmpty) ...[
            const SizedBox(height: 24),
            Text(l10n.taskMaterialsTitle,
                style: Theme.of(context).textTheme.titleMedium),
            ..._allocations.map(
              (a) => ListTile(
                title: Text(a['inventory_item']?.toString() ?? ''),
                subtitle: Text(
                  'Reserved ${a['reserved_qty']} · ${a['status']}',
                ),
                trailing: TextButton(
                  onPressed: () => _consumePartial(a),
                  child: Text(l10n.taskConsumeOne),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
