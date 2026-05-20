import 'package:agriflow_mobile/app/router/routes.dart';

import 'package:agriflow_mobile/core/config/env.dart';

import 'package:agriflow_mobile/core/providers/core_providers.dart';

import 'package:agriflow_mobile/core/sync/sync_orchestrator.dart';
import 'package:agriflow_mobile/features/notifications/presentation/notification_inbox_screen.dart';
import 'package:agriflow_mobile/features/pilot_ops/presentation/onboarding_screen.dart';
import 'package:agriflow_mobile/features/readiness/data/readiness_remote.dart';

import 'package:agriflow_mobile/shared/widgets/offline_banner.dart';

import 'package:agriflow_mobile/features/sync/presentation/widgets/sync_app_bar_status.dart';
import 'package:agriflow_mobile/features/sync/presentation/widgets/sync_feedback_listener.dart';
import 'package:agriflow_mobile/features/sync/presentation/widgets/sync_flying_overlay.dart';
import 'package:agriflow_mobile/features/sync/sync_connectivity.dart';

import 'package:connectivity_plus/connectivity_plus.dart';

import 'package:flutter/material.dart';

import 'package:flutter_gen/gen_l10n/app_localizations.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:go_router/go_router.dart';



class DashboardShell extends ConsumerStatefulWidget {

  const DashboardShell({super.key, required this.navigationShell});



  final StatefulNavigationShell navigationShell;



  @override

  ConsumerState<DashboardShell> createState() => _DashboardShellState();

}



class _DashboardShellState extends ConsumerState<DashboardShell> {

  bool _offline = false;

  bool _pushInit = false;

  String? _lastSyncLabel;



  @override

  void initState() {

    super.initState();

    WidgetsBinding.instance.addPostFrameCallback((_) async {

      if (!_pushInit && mounted) {

        _pushInit = true;

        await ref.read(pushServiceProvider).initialize(

              onNavigate: (loc) => context.go(loc),

            );

        if (!Env.demoMode) {

          try {

            final release = await ref

                .read(readinessRemoteProvider)

                .checkRelease(Env.appVersion);

            if (release.updateRequired && mounted) {

              final title = AppLocalizations.of(context)!.appTitle;

              showDialog<void>(

                context: context,

                builder: (ctx) => AlertDialog(

                  title: Text(title),

                  content: Text(

                    'Update required (min ${release.minVersion})',

                  ),

                  actions: [

                    TextButton(

                      onPressed: () => Navigator.pop(ctx),

                      child: Text(AppLocalizations.of(ctx)!.retry),

                    ),

                  ],

                ),

              );

            }

          } catch (_) {}

        }

      }

      try {

        await ref.read(syncOrchestratorProvider).syncNow(force: false);

        ref.invalidate(syncStatusProvider);
        await ref.read(syncVisualControllerProvider).refresh();

      } catch (_) {

        // offline at launch is acceptable

      }

      if (!Env.demoMode && mounted) {

        final hive = ref.read(hiveStorageProvider);

        if (await shouldShowOnboarding(hive)) {

          await context.push(AppRoutes.onboarding);

        }

      }

    });

    ref.read(connectivityProvider).onConnectivityChanged.listen((results) {

      if (mounted) {

        setState(() {

          _offline = results.contains(ConnectivityResult.none);

        });

      }

    });

  }



  @override

  Widget build(BuildContext context) {

    final l10n = AppLocalizations.of(context)!;

    final syncAsync = ref.watch(syncStatusProvider);
    final visual = ref.watch(syncVisualControllerProvider);
    final unreadNotif = ref.watch(notificationUnreadCountProvider);
    final showOfflineBanner = _offline || visual.simulateOffline;

    return Scaffold(

      appBar: AppBar(

        title: Text(l10n.appTitle),

        actions: [

          if (!Env.demoMode)

            PopupMenuButton<String>(

              onSelected: (value) {

                if (value == 'feedback') context.push(AppRoutes.feedback);

                if (value == 'onboarding') context.push(AppRoutes.onboarding);

              },

              itemBuilder: (context) => [

                PopupMenuItem(

                  value: 'feedback',

                  child: Text(l10n.feedbackTitle),

                ),

                PopupMenuItem(

                  value: 'onboarding',

                  child: Text(l10n.onboardingTitle),

                ),

              ],

            ),

          const SyncAppBarStatus(),

        ],

      ),

      body: SyncFeedbackListener(

        child: SyncFlyingOverlay(

          child: Column(

        children: [

          OfflineBanner(

            visible: showOfflineBanner,

            pendingCount: visual.pendingCount,

            lastSyncLabel: _lastSyncLabel,

            degradedNetwork: !_offline &&

                (syncAsync.valueOrNull?.pendingCount ?? 0) > 5,

          ),

          Expanded(child: widget.navigationShell),

        ],

      ),

        ),

      ),

      bottomNavigationBar: NavigationBar(

        selectedIndex: widget.navigationShell.currentIndex,

        onDestinationSelected: widget.navigationShell.goBranch,

        destinations: [

          NavigationDestination(

            icon: const Icon(Icons.home_outlined),

            label: l10n.navHome,

          ),

          NavigationDestination(

            icon: const Icon(Icons.people_outline),

            label: l10n.navFarmers,

          ),

          NavigationDestination(

            icon: const Icon(Icons.task_alt),

            label: l10n.navTasks,

          ),

          NavigationDestination(

            icon: Badge(
              isLabelVisible: unreadNotif > 0,
              label: Text('$unreadNotif'),
              child: const Icon(Icons.notifications_outlined),
            ),

            label: l10n.navNotifications,

          ),

          NavigationDestination(

            icon: const Icon(Icons.sync),

            label: l10n.navSync,

          ),

        ],

      ),

    );

  }

}

