import 'package:agriflow_mobile/app/router/routes.dart';
import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/demo/demo_selection.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/core/sync/projection_writer.dart';
import 'package:agriflow_mobile/features/auth/data/auth_repository.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final dashboardStatsProvider = FutureProvider<DashboardStats>((ref) async {
  final db = ref.watch(appDatabaseProvider);
  final blocks = ref.watch(hiveStorageProvider).getAllowedBlocks();
  final tasks = await db.readProjections(
    kind: ProjectionKind.task,
    blocks: blocks,
  );
  final projects = await db.readProjections(
    kind: ProjectionKind.farmerProject,
    blocks: blocks,
  );
  final openTasks = tasks.where((t) {
    final status = t.payload['status'] as String? ?? '';
    return status != 'completed' && status != 'cancelled';
  }).length;
  return DashboardStats(
    projectCount: projects.length,
    openTaskCount: openTasks,
  );
});

class DashboardStats {
  const DashboardStats({
    required this.projectCount,
    required this.openTaskCount,
  });

  final int projectCount;
  final int openTaskCount;
}

class HomeDashboardScreen extends ConsumerWidget {
  const HomeDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final auth = ref.watch(authSessionProvider);
    final stats = ref.watch(dashboardStatsProvider);

    return auth.when(
      loading: () => const LoadingView(),
      error: (e, _) => Center(child: Text(l10n.errorGeneric)),
      data: (session) {
        if (session == null) return const SizedBox.shrink();
        final roles = session.permissions.roles;
        final primaryRole = roles.contains('Owner')
            ? l10n.roleOwner
            : roles.contains('Office Manager')
                ? l10n.roleOfficeManager
                : roles.contains('Field Staff')
                    ? l10n.roleFieldStaff
                    : roles.isNotEmpty
                        ? roles.first
                        : l10n.roleUser;
        final blocks = session.permissions.blocks;

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(l10n.dashboardWelcome(session.fullName), style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text(l10n.dashboardRoleLine(primaryRole)),
            if (blocks.isNotEmpty)
              Text(l10n.dashboardBlocksLine(blocks.join(', '))),
            const SizedBox(height: 24),
            stats.when(
              loading: () => const LoadingView(),
              error: (_, __) => Text(l10n.errorGeneric),
              data: (s) => Row(
                children: [
                  Expanded(
                    child: _StatCard(
                      label: l10n.dashboardProjects,
                      value: '${s.projectCount}',
                      icon: Icons.account_tree_outlined,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _StatCard(
                      label: l10n.dashboardOpenTasks,
                      value: '${s.openTaskCount}',
                      icon: Icons.task_alt,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: () => context.go(AppRoutes.farmers),
              icon: const Icon(Icons.people_outline),
              label: Text(l10n.dashboardViewFarmers),
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: () async {
                await ref.read(syncOrchestratorProvider).syncNow();
                ref.invalidate(dashboardStatsProvider);
              },
              icon: const Icon(Icons.sync),
              label: Text(l10n.syncNow),
            ),
          ],
        );
      },
    );
  }
}

class _StatCard extends StatelessWidget {
  const _StatCard({
    required this.label,
    required this.value,
    required this.icon,
  });

  final String label;
  final String value;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: Theme.of(context).colorScheme.primary),
            const SizedBox(height: 8),
            Text(value, style: Theme.of(context).textTheme.headlineSmall),
            Text(label, style: Theme.of(context).textTheme.bodySmall),
          ],
        ),
      ),
    );
  }
}
