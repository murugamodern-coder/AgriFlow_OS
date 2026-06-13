import 'package:agriflow_mobile/app/router/routes.dart';
import 'package:agriflow_mobile/core/auth/user_role_provider.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/widgets/dashboard_widgets.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class OfficeStaffDashboard extends ConsumerWidget {
  const OfficeStaffDashboard({super.key, required this.session});

  final UserSession session;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          l10n.dashboardWelcome(session.fullName),
          style: Theme.of(context).textTheme.titleLarge,
        ),
        Text(l10n.dashboardRoleLine('Office Staff')),
        const SizedBox(height: 8),
        Text(
          'Data entry & customer records',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
        ),
        const SizedBox(height: 20),
        FilledButton.icon(
          onPressed: () => context.go('${AppRoutes.farmers}/new'),
          icon: const Icon(Icons.person_add),
          label: Text(l10n.farmerCreateTitle),
        ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () => context.go(AppRoutes.farmers),
          icon: const Icon(Icons.people_outline),
          label: Text(l10n.dashboardViewFarmers),
        ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () => context.push(AppRoutes.cashCarryPos),
          icon: const Icon(Icons.receipt_long),
          label: Text(l10n.cashAndCarryPos),
        ),
        const SizedBox(height: 24),
        DashboardSectionTitle(title: l10n.syncNow),
        Card(
          child: ListTile(
            leading: const Icon(Icons.cloud_upload_outlined),
            title: Text(l10n.syncNow),
            subtitle: Text(l10n.navSync),
            onTap: () => context.go(AppRoutes.sync),
          ),
        ),
      ],
    );
  }
}
