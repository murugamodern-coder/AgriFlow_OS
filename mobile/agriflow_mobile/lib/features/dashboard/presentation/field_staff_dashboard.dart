import 'package:agriflow_mobile/app/router/routes.dart';
import 'package:agriflow_mobile/core/auth/user_role_provider.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/dashboard_stats.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/widgets/dashboard_widgets.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class FieldStaffDashboard extends ConsumerWidget {
  const FieldStaffDashboard({super.key, required this.session});

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
        Text(l10n.dashboardRoleLine(l10n.roleFieldStaff)),
        const SizedBox(height: 16),
        stats.when(
          loading: () => const LoadingView(),
          error: (_, __) => Text(l10n.errorGeneric),
          data: (s) => Card(
            color: Colors.orange.withValues(alpha: 0.12),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    l10n.dashboardOpenTasks,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${s.openTaskCount}',
                    style: Theme.of(context).textTheme.displaySmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.orange.shade800,
                        ),
                  ),
                ],
              ),
            ),
          ),
        ),
        if (session.blocks.isNotEmpty) ...[
          const SizedBox(height: 8),
          Text(l10n.dashboardBlocksLine(session.blocks.join(', '))),
        ],
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: DashboardBigButton(
                label: l10n.navTasks,
                icon: Icons.task,
                color: Colors.orange.shade700,
                onTap: () => context.go(AppRoutes.tasks),
              ),
            ),
            Expanded(
              child: DashboardBigButton(
                label: l10n.farmerCreateTitle,
                icon: Icons.person_add,
                onTap: () => context.go('${AppRoutes.farmers}/new'),
              ),
            ),
          ],
        ),
        Row(
          children: [
            Expanded(
              child: DashboardBigButton(
                label: l10n.navTimeline,
                icon: Icons.list_alt,
                onTap: () => context.push(AppRoutes.timeline),
              ),
            ),
            Expanded(
              child: DashboardBigButton(
                label: l10n.syncNow,
                icon: Icons.sync,
                onTap: () => context.go(AppRoutes.sync),
              ),
            ),
          ],
        ),
      ],
    );
  }
}
