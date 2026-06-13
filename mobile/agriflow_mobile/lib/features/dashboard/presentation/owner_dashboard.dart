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

class OwnerDashboard extends ConsumerWidget {
  const OwnerDashboard({super.key, required this.session});

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
        const SizedBox(height: 4),
        Text(
          l10n.dashboardRoleLine(l10n.roleOwner),
          style: Theme.of(context).textTheme.bodyMedium,
        ),
        const SizedBox(height: 20),
        stats.when(
          loading: () => const LoadingView(),
          error: (_, __) => Text(l10n.errorGeneric),
          data: (s) => LayoutBuilder(
            builder: (context, constraints) {
              final narrow = constraints.maxWidth < 520;
              final kpiRow1 = [
                Expanded(
                  child: DashboardKpiCard(
                    label: l10n.dashboardViewFarmers,
                    value: '—',
                    icon: Icons.people,
                    color: Colors.blue,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: DashboardKpiCard(
                    label: l10n.dashboardProjects,
                    value: '${s.projectCount}',
                    icon: Icons.construction,
                    color: Colors.orange,
                  ),
                ),
              ];
              final kpiRow2 = [
                Expanded(
                  child: DashboardKpiCard(
                    label: l10n.cashAndCarryPos,
                    value: 'POS',
                    icon: Icons.currency_rupee,
                    color: Colors.green,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: DashboardKpiCard(
                    label: l10n.dashboardOpenTasks,
                    value: '${s.openTaskCount}',
                    icon: Icons.task,
                    color: Colors.red,
                  ),
                ),
              ];
              return Column(
                children: [
                  if (narrow) ...[
                    Row(children: kpiRow1),
                    const SizedBox(height: 8),
                    Row(children: kpiRow2),
                  ] else ...[
                    Row(
                      children: [
                        ...kpiRow1,
                        const SizedBox(width: 8),
                        ...kpiRow2,
                      ],
                    ),
                  ],
                ],
              );
            },
          ),
        ),
        const SizedBox(height: 24),
        const DashboardSectionTitle(title: 'Quick Actions'),
        GridView.count(
          crossAxisCount: dashboardActionCrossAxisCount(context),
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 8,
          crossAxisSpacing: 8,
          childAspectRatio: 1.05,
          children: [
            DashboardActionTile(
              label: l10n.farmerCreateTitle,
              icon: Icons.person_add,
              onTap: () => context.go('${AppRoutes.farmers}/new'),
            ),
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
              icon: Icons.timeline,
              onTap: () => context.push(AppRoutes.timeline),
            ),
            DashboardActionTile(
              label: l10n.navTasks,
              icon: Icons.task_alt,
              onTap: () => context.go(AppRoutes.tasks),
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
        const SizedBox(height: 16),
        Card(
          child: ListTile(
            leading: const Icon(Icons.notifications_outlined),
            title: Text(l10n.navNotifications),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => context.go(AppRoutes.notifications),
          ),
        ),
      ],
    );
  }
}
