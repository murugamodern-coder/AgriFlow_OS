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

class OfficeManagerDashboard extends ConsumerWidget {
  const OfficeManagerDashboard({super.key, required this.session});

  final UserSession session;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final stats = ref.watch(dashboardStatsProvider);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          l10n.dashboardWelcome(session.fullName),
          style: Theme.of(context).textTheme.titleLarge,
        ),
        Text(l10n.dashboardRoleLine(l10n.roleOfficeManager)),
        const SizedBox(height: 16),
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
        const SizedBox(height: 20),
        DashboardSectionTitle(title: l10n.navTasks),
        Card(
          child: Column(
            children: [
              ListTile(
                leading: Icon(Icons.approval, color: Colors.blue.shade700),
                title: Text(l10n.navTasks),
                subtitle: Text(l10n.dashboardOpenTasks),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => context.go(AppRoutes.tasks),
              ),
              const Divider(height: 1),
              ListTile(
                leading: Icon(Icons.notifications_active, color: Colors.amber.shade800),
                title: Text(l10n.navNotifications),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => context.go(AppRoutes.notifications),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        DashboardSectionTitle(title: l10n.dashboardViewFarmers),
        GridView.count(
          crossAxisCount: dashboardActionCrossAxisCount(context).clamp(2, 3),
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 8,
          crossAxisSpacing: 8,
          childAspectRatio: 1.1,
          children: [
            DashboardActionTile(
              label: l10n.cashAndCarryPos,
              icon: Icons.point_of_sale,
              onTap: () => context.push(AppRoutes.cashCarryPos),
            ),
            DashboardActionTile(
              label: l10n.dashboardViewFarmers,
              icon: Icons.people,
              onTap: () => context.go(AppRoutes.farmers),
            ),
            DashboardActionTile(
              label: l10n.navTimeline,
              icon: Icons.analytics_outlined,
              onTap: () => context.push(AppRoutes.timeline),
            ),
            DashboardActionTile(
              label: l10n.syncNow,
              icon: Icons.sync,
              onTap: () async {
                await ref.read(syncOrchestratorProvider).syncNow();
                ref.invalidate(dashboardStatsProvider);
              },
            ),
          ],
        ),
      ],
    );
  }
}
