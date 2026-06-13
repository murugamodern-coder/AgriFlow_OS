import 'package:agriflow_mobile/app/router/routes.dart';
import 'package:agriflow_mobile/core/auth/user_role_provider.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/dashboard_stats.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/widgets/dashboard_widgets.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

/// Fallback when role is unknown or unmapped — same stats as legacy home.
class GenericDashboard extends ConsumerWidget {
  const GenericDashboard({super.key, required this.session});

  final UserSession session;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final stats = ref.watch(dashboardStatsProvider);
    final roleLabel = session.roles.isNotEmpty
        ? session.roles.first.backendName
        : l10n.roleUser;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          l10n.dashboardWelcome(session.fullName),
          style: Theme.of(context).textTheme.titleLarge,
        ),
        Text(l10n.dashboardRoleLine(roleLabel)),
        if (session.blocks.isNotEmpty)
          Text(l10n.dashboardBlocksLine(session.blocks.join(', '))),
        const SizedBox(height: 24),
        stats.when(
          loading: () => const LoadingView(),
          error: (_, __) => Text(l10n.errorGeneric),
          data: (s) => DashboardStatsRow(
            projectCount: s.projectCount,
            openTaskCount: s.openTaskCount,
            projectsLabel: l10n.dashboardProjects,
            tasksLabel: l10n.dashboardOpenTasks,
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
  }
}
