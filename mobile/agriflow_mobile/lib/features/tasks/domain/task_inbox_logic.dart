import 'package:agriflow_mobile/features/tasks/domain/task_summary.dart';

enum TaskBucket { overdue, today, upcoming }

enum TaskFilterScope { all, mine, byType }

class TaskInboxStats {
  const TaskInboxStats({
    required this.pendingToday,
    required this.overdue,
    required this.today,
    required this.upcoming,
  });

  final int pendingToday;
  final int overdue;
  final int today;
  final int upcoming;
}

class TaskInboxGrouped {
  const TaskInboxGrouped({
    required this.stats,
    required this.overdue,
    required this.today,
    required this.upcoming,
  });

  final TaskInboxStats stats;
  final List<TaskSummary> overdue;
  final List<TaskSummary> today;
  final List<TaskSummary> upcoming;
}

abstract final class TaskInboxLogic {
  static List<TaskSummary> filterTasks(
    List<TaskSummary> tasks, {
    required TaskFilterScope scope,
    required String? currentUser,
    String? taskType,
  }) {
    var open = tasks.where((t) => t.isOpen).toList();
    if (scope == TaskFilterScope.mine && currentUser != null) {
      open = open
          .where(
            (t) =>
                t.assignedTo == currentUser ||
                t.assignedOfficer == currentUser,
          )
          .toList();
    }
    if (scope == TaskFilterScope.byType && taskType != null) {
      open = open.where((t) => t.taskType == taskType).toList();
    }
    return open;
  }

  static TaskInboxGrouped group(List<TaskSummary> open) {
    final now = DateTime.now();
    final todayDate = DateTime(now.year, now.month, now.day);

    final overdue = <TaskSummary>[];
    final today = <TaskSummary>[];
    final upcoming = <TaskSummary>[];

    for (final task in open) {
      final bucket = _bucketFor(task, todayDate);
      switch (bucket) {
        case TaskBucket.overdue:
          overdue.add(task);
        case TaskBucket.today:
          today.add(task);
        case TaskBucket.upcoming:
          upcoming.add(task);
      }
    }

    int compareDue(TaskSummary a, TaskSummary b) {
      final da = _parseDue(a.dueDate);
      final db = _parseDue(b.dueDate);
      if (da == null && db == null) return 0;
      if (da == null) return 1;
      if (db == null) return -1;
      return da.compareTo(db);
    }

    overdue.sort(compareDue);
    today.sort(compareDue);
    upcoming.sort(compareDue);

    return TaskInboxGrouped(
      stats: TaskInboxStats(
        pendingToday: overdue.length + today.length,
        overdue: overdue.length,
        today: today.length,
        upcoming: upcoming.length,
      ),
      overdue: overdue,
      today: today,
      upcoming: upcoming,
    );
  }

  static TaskBucket _bucketFor(TaskSummary task, DateTime todayDate) {
    if (task.isOverdue) return TaskBucket.overdue;
    final due = _parseDue(task.dueDate);
    if (due == null) return TaskBucket.today;
    final dueDay = DateTime(due.year, due.month, due.day);
    if (dueDay.isBefore(todayDate)) return TaskBucket.overdue;
    if (dueDay == todayDate) return TaskBucket.today;
    return TaskBucket.upcoming;
  }

  static DateTime? _parseDue(String? raw) {
    if (raw == null || raw.isEmpty) return null;
    try {
      return DateTime.parse(raw).toLocal();
    } catch (_) {
      return null;
    }
  }

  static int daysOverdue(TaskSummary task) {
    final due = _parseDue(task.dueDate);
    if (due == null) return 0;
    final today = DateTime.now();
    final dueDay = DateTime(due.year, due.month, due.day);
    final todayDay = DateTime(today.year, today.month, today.day);
    return todayDay.difference(dueDay).inDays;
  }

  static int daysUntil(TaskSummary task) {
    final due = _parseDue(task.dueDate);
    if (due == null) return 0;
    final today = DateTime.now();
    final dueDay = DateTime(due.year, due.month, due.day);
    final todayDay = DateTime(today.year, today.month, today.day);
    return dueDay.difference(todayDay).inDays;
  }
}
