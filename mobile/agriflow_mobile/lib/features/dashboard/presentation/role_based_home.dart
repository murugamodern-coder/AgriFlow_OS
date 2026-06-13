import 'package:agriflow_mobile/core/auth/user_role_provider.dart';
import 'package:agriflow_mobile/features/auth/data/auth_repository.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/field_staff_dashboard.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/generic_dashboard.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/installer_dashboard.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/office_manager_dashboard.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/office_staff_dashboard.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/owner_dashboard.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/service_tech_dashboard.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/store_keeper_dashboard.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Routes logged-in users to a role-appropriate home experience.
class RoleBasedHome extends ConsumerWidget {
  const RoleBasedHome({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authSessionProvider);
    final l10n = AppLocalizations.of(context)!;

    return auth.when(
      loading: () => const LoadingView(),
      error: (e, _) => Center(child: Text(l10n.errorGeneric)),
      data: (session) {
        if (session == null) return const SizedBox.shrink();
        final userSession = UserSession.fromAuthSession(session);

        switch (userSession.primaryRole) {
          case AgriflowRole.owner:
            return OwnerDashboard(session: userSession);
          case AgriflowRole.officeManager:
            return OfficeManagerDashboard(session: userSession);
          case AgriflowRole.officeStaff:
            return OfficeStaffDashboard(session: userSession);
          case AgriflowRole.fieldStaff:
            return FieldStaffDashboard(session: userSession);
          case AgriflowRole.installerLead:
          case AgriflowRole.installer:
            return InstallerDashboard(session: userSession);
          case AgriflowRole.serviceTechnician:
            return ServiceTechDashboard(session: userSession);
          case AgriflowRole.storeKeeper:
            return StoreKeeperDashboard(session: userSession);
          case AgriflowRole.unknown:
            return GenericDashboard(session: userSession);
        }
      },
    );
  }
}
