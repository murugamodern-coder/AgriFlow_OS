import 'package:agriflow_mobile/app/router/routes.dart';
import 'package:agriflow_mobile/core/auth/user_role_provider.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/dashboard_stats.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/widgets/dashboard_widgets.dart';
import 'package:agriflow_mobile/features/service/presentation/service_visit_list_screen.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class ServiceTechDashboard extends ConsumerWidget {
  const ServiceTechDashboard({super.key, required this.session});

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
        Text(l10n.dashboardRoleLine('Service Technician')),
        const SizedBox(height: 16),
        stats.when(
          loading: () => const LoadingView(),
          error: (_, __) => Text(l10n.errorGeneric),
          data: (s) => Card(
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: Colors.teal.shade100,
                child: Icon(Icons.home_repair_service, color: Colors.teal.shade800),
              ),
              title: const Text('Service visits today'),
              subtitle: Text('${s.openTaskCount} tasks pending'),
              trailing: Text(
                '${s.openTaskCount}',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
            ),
          ),
        ),
        const SizedBox(height: 16),

        // -- Service Visits --
        ListTile(
          leading: Icon(Icons.build, color: Colors.green.shade700),
          title: const Text('Service Visits / பணி பார்வைகள்'),
          subtitle: const Text('Upcoming AMC visits'),
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => const ServiceVisitListScreen(),
              ),
            );
          },
        ),
        const Divider(),

        DashboardSectionTitle(title: l10n.navTasks),
        Row(
          children: [
            Expanded(
              child: DashboardBigButton(
                label: l10n.navTasks,
                icon: Icons.assignment,
                color: Colors.teal.shade600,
                onTap: () => context.go(AppRoutes.tasks),
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
        const SizedBox(height: 8),
        OutlinedButton.icon(
          onPressed: () => context.go(AppRoutes.notifications),
          icon: const Icon(Icons.notifications_outlined),
          label: Text(l10n.navNotifications),
        ),
      ],
    );
  }
}
