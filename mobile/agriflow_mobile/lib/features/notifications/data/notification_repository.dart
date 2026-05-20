import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/sync/projection_writer.dart';
import 'package:agriflow_mobile/features/notifications/data/notification_remote.dart';
import 'package:agriflow_mobile/features/notifications/domain/notification_item.dart';

class NotificationRepository {
  NotificationRepository({
    required AppDatabase db,
    required NotificationRemote remote,
  })  : _db = db,
        _remote = remote;

  final AppDatabase _db;
  final NotificationRemote _remote;

  Stream<List<NotificationItem>> watchInbox() {
    return _db.watchProjections(kind: ProjectionKind.notification).map(
          (rows) => rows
              .map((r) => NotificationItem.fromPayload(r.payload))
              .toList(),
        );
  }

  Future<List<NotificationItem>> readCachedInbox() async {
    final rows = await _db.readProjections(kind: ProjectionKind.notification);
    return rows.map((r) => NotificationItem.fromPayload(r.payload)).toList();
  }

  Future<int> unreadCountOnline() => _remote.fetchUnreadCount();

  Future<void> markReadOnline(String name) => _remote.markRead(name);
}
