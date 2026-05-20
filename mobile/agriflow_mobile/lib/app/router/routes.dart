abstract final class AppRoutes {
  static const login = '/login';
  static const shell = '/';
  static const home = '/home';
  static const farmers = '/farmers';
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
}
