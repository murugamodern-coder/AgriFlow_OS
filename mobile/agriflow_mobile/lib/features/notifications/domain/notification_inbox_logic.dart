import 'package:agriflow_mobile/features/notifications/domain/notification_item.dart';

enum NotificationDateGroup { today, yesterday, thisWeek, older }

class NotificationInboxGrouped {
  const NotificationInboxGrouped({
    required this.today,
    required this.yesterday,
    required this.thisWeek,
    required this.older,
  });

  final List<NotificationItem> today;
  final List<NotificationItem> yesterday;
  final List<NotificationItem> thisWeek;
  final List<NotificationItem> older;

  bool get isEmpty =>
      today.isEmpty &&
      yesterday.isEmpty &&
      thisWeek.isEmpty &&
      older.isEmpty;
}

abstract final class NotificationInboxLogic {
  static List<NotificationItem> filter(
    List<NotificationItem> items, {
    String? type,
    bool unreadOnly = false,
  }) {
    var list = items;
    if (unreadOnly) {
      list = list.where((i) => i.isUnread).toList();
    }
    if (type != null && type.isNotEmpty) {
      list = list.where((i) => i.notificationType == type).toList();
    }
    return list;
  }

  static NotificationInboxGrouped groupByDate(List<NotificationItem> items) {
    final now = DateTime.now();
    final todayStart = DateTime(now.year, now.month, now.day);
    final yesterdayStart = todayStart.subtract(const Duration(days: 1));
    final weekStart = todayStart.subtract(const Duration(days: 7));

    final today = <NotificationItem>[];
    final yesterday = <NotificationItem>[];
    final thisWeek = <NotificationItem>[];
    final older = <NotificationItem>[];

    final sorted = [...items]
      ..sort((a, b) {
        final da = _parse(a.createdOn);
        final db = _parse(b.createdOn);
        if (da == null && db == null) return 0;
        if (da == null) return 1;
        if (db == null) return -1;
        return db.compareTo(da);
      });

    for (final item in sorted) {
      final created = _parse(item.createdOn);
      if (created == null) {
        older.add(item);
        continue;
      }
      if (!created.isBefore(todayStart)) {
        today.add(item);
      } else if (!created.isBefore(yesterdayStart)) {
        yesterday.add(item);
      } else if (!created.isBefore(weekStart)) {
        thisWeek.add(item);
      } else {
        older.add(item);
      }
    }

    return NotificationInboxGrouped(
      today: today,
      yesterday: yesterday,
      thisWeek: thisWeek,
      older: older,
    );
  }

  static DateTime? _parse(String? raw) {
    if (raw == null || raw.isEmpty) return null;
    try {
      return DateTime.parse(raw).toLocal();
    } catch (_) {
      return null;
    }
  }

  static String timeAgo(String? createdOn) {
    final dt = _parse(createdOn);
    if (dt == null) return '';
    final diff = DateTime.now().difference(dt);
    if (diff.inMinutes < 60) return '${diff.inMinutes}m';
    if (diff.inHours < 24) return '${diff.inHours}h';
    if (diff.inDays < 7) return '${diff.inDays}d';
    return '${dt.day}/${dt.month}';
  }
}
