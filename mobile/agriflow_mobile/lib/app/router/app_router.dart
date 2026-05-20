import 'package:agriflow_mobile/app/router/routes.dart';
import 'package:agriflow_mobile/features/auth/data/auth_repository.dart';
import 'package:agriflow_mobile/features/auth/presentation/login_screen.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/dashboard_shell.dart';
import 'package:agriflow_mobile/features/dashboard/presentation/home_dashboard_screen.dart';
import 'package:agriflow_mobile/features/farmer/presentation/farmer_list_screen.dart';
import 'package:agriflow_mobile/features/notifications/presentation/notification_inbox_screen.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/project_timeline_screen.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/timeline_feed_screen.dart';
import 'package:agriflow_mobile/features/pilot_ops/presentation/feedback_screen.dart';
import 'package:agriflow_mobile/features/pilot_ops/presentation/onboarding_screen.dart';
import 'package:agriflow_mobile/features/sync/presentation/sync_status_screen.dart';
import 'package:agriflow_mobile/features/tasks/presentation/task_detail_screen.dart';
import 'package:agriflow_mobile/features/tasks/presentation/task_inbox_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final auth = ref.watch(authSessionProvider);
  return GoRouter(
    initialLocation: AppRoutes.home,
    redirect: (context, state) {
      if (auth.isLoading) return null;
      final loggedIn = auth.asData?.value != null;
      final onLogin = state.matchedLocation == AppRoutes.login;
      if (!loggedIn && !onLogin) return AppRoutes.login;
      if (loggedIn && onLogin) return AppRoutes.home;
      if (loggedIn && state.matchedLocation == AppRoutes.onboarding) {
        return null;
      }
      return null;
    },
    routes: [
      GoRoute(
        path: AppRoutes.login,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: AppRoutes.onboarding,
        builder: (context, state) => const OnboardingScreen(),
      ),
      GoRoute(
        path: AppRoutes.feedback,
        builder: (context, state) => const FeedbackScreen(),
      ),
      GoRoute(
        path: '/projects/:projectName/timeline',
        builder: (context, state) => ProjectTimelineScreen(
          projectName: state.pathParameters['projectName']!,
        ),
      ),
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) =>
            DashboardShell(navigationShell: navigationShell),
        branches: [
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: AppRoutes.home,
                builder: (context, state) => const HomeDashboardScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: AppRoutes.farmers,
                builder: (context, state) => const FarmerListScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: AppRoutes.tasks,
                builder: (context, state) => const TaskInboxScreen(),
                routes: [
                  GoRoute(
                    path: ':taskName',
                    builder: (context, state) => TaskDetailScreen(
                      taskName: state.pathParameters['taskName']!,
                      farmerProject: state.uri.queryParameters['project'],
                    ),
                  ),
                ],
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: AppRoutes.notifications,
                builder: (context, state) => const NotificationInboxScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: AppRoutes.sync,
                builder: (context, state) => const SyncStatusScreen(),
              ),
            ],
          ),
        ],
      ),
      GoRoute(
        path: AppRoutes.timeline,
        builder: (context, state) => const TimelineFeedScreen(),
      ),
    ],
  );
});
