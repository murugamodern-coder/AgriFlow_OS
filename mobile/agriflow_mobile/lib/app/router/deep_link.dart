/// Parses notification / server deep_link paths to go_router locations.
class DeepLinkParser {
  static String? toLocation(String? deepLink) {
    if (deepLink == null || deepLink.isEmpty) return null;
    final path = deepLink.startsWith('/') ? deepLink : '/$deepLink';
    final taskMatch = RegExp(r'^/projects/([^/]+)/tasks/([^/]+)$').firstMatch(path);
    if (taskMatch != null) {
      return '/tasks/${taskMatch.group(2)}?project=${taskMatch.group(1)}';
    }
    final timelineMatch = RegExp(r'^/projects/([^/]+)/timeline$').firstMatch(path);
    if (timelineMatch != null) {
      return '/projects/${timelineMatch.group(1)}/timeline';
    }
    if (path == '/farmers' || path == '/tasks') return path;
    return null;
  }
}
