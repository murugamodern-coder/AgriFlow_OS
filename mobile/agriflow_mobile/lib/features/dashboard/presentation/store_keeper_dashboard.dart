import 'package:agriflow_mobile/app/router/routes.dart';
import 'package:agriflow_mobile/core/auth/user_role_provider.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/widgets/dashboard_widgets.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class StoreKeeperDashboard extends ConsumerWidget {
  const StoreKeeperDashboard({super.key, required this.session});

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
        Text(l10n.dashboardRoleLine('Store Keeper')),
        const SizedBox(height: 8),
        Text(
          'Stock & material movements',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
        ),
        const SizedBox(height: 20),
        Card(
          color: Colors.brown.withValues(alpha: 0.08),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Icon(Icons.inventory_2, size: 36, color: Colors.brown.shade700),
                const SizedBox(width: 16),
                Expanded(
                  child: Text(
                    'Inventory sync keeps warehouse balances up to date offline.',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: DashboardBigButton(
                label: l10n.syncNow,
                icon: Icons.sync,
                color: Colors.brown.shade600,
                onTap: () => context.go(AppRoutes.sync),
              ),
            ),
            Expanded(
              child: DashboardBigButton(
                label: l10n.cashAndCarryPos,
                icon: Icons.point_of_sale,
                onTap: () => context.push(AppRoutes.cashCarryPos),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () async {
            await ref.read(syncOrchestratorProvider).syncNow();
          },
          icon: const Icon(Icons.cloud_download_outlined),
          label: Text(l10n.navSync),
        ),
      ],
    );
  }
}
