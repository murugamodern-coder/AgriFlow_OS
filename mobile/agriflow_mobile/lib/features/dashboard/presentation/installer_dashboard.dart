import 'package:agriflow_mobile/app/router/routes.dart';
import 'package:agriflow_mobile/core/auth/user_role_provider.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/dashboard_stats.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/widgets/dashboard_widgets.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class InstallerDashboard extends ConsumerWidget {
  const InstallerDashboard({super.key, required this.session});

  final UserSession session;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final stats = ref.watch(dashboardStatsProvider);
    final isLead = session.hasRole(AgriflowRole.installerLead);
    final roleLabel = isLead ? 'Installer Lead' : 'Installer';

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          l10n.dashboardWelcome(session.fullName),
          style: Theme.of(context).textTheme.titleLarge,
        ),
        Text(l10n.dashboardRoleLine(roleLabel)),
        const SizedBox(height: 16),
        stats.when(
          loading: () => const LoadingView(),
          error: (_, __) => Text(l10n.errorGeneric),
          data: (s) => Card(
            color: Theme.of(context).colorScheme.primaryContainer,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Icon(
                    Icons.build_circle_outlined,
                    size: 40,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Installation queue',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        Text(
                          '${s.projectCount} active projects · ${s.openTaskCount} open tasks',
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: DashboardBigButton(
                label: l10n.navTasks,
                icon: Icons.handyman,
                onTap: () => context.go(AppRoutes.tasks),
              ),
            ),
            Expanded(
              child: DashboardBigButton(
                label: l10n.navTimeline,
                icon: Icons.construction,
                onTap: () => context.push(AppRoutes.timeline),
              ),
            ),
          ],
        ),
        if (isLead) ...[
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: () => context.go(AppRoutes.notifications),
            icon: const Icon(Icons.group_outlined),
            label: Text(l10n.navNotifications),
          ),
        ],
      ],
    );
  }
}
