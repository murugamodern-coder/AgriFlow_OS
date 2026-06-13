abstract final class AppRoutes {
  static const login = '/login';
  static const shell = '/';
  static const home = '/home';
  static const farmers = '/farmers';
  static const farmerCreate = '/farmers/new';
  static const timeline = '/timeline';
  static const tasks = '/tasks';

  static String taskDetail(String taskName, {String? project}) {
    final base = '/tasks/$taskName';
    if (project != null) return '$base?project=$project';
    return base;
  }

  static String projectTimeline(String projectName) =>
      '/projects/$projectName/timeline';

  static const notifications = '/notifications';
  static const sync = '/sync';
  static const feedback = '/feedback';
  static const onboarding = '/onboarding';
  static const cashCarryPos = '/billing/cash-carry';

  static String projectSale(String projectName) =>
      '/billing/project-sale/$projectName';
}
