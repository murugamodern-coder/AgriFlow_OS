import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';

class NotificationRemote {
  NotificationRemote({required this.api, required this.config});

  final ApiClient api;
  final ApiConfig config;

  Future<List<Map<String, dynamic>>> fetchInbox({
    int limit = 50,
    String? cursor,
    bool unreadOnly = false,
  }) async {
    final envelope = await api.postMethod<Map<String, dynamic>>(
      methodUrl: config.methodUrl('agriflow.api.v1.notification.list'),
      data: {
        'limit': limit,
        if (cursor != null) 'cursor': cursor,
        if (unreadOnly) 'unread_only': true,
      },
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    final items = envelope.data?['items'] as List? ?? [];
    return items.map((e) => Map<String, dynamic>.from(e as Map)).toList();
  }

  Future<int> fetchUnreadCount() async {
    final envelope = await api.postMethod<Map<String, dynamic>>(
      methodUrl: config.methodUrl('agriflow.api.v1.notification.unread_count'),
      data: {},
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    return envelope.data?['count'] as int? ?? 0;
  }

  Future<void> markRead(String name) async {
    await api.postMethod<Map<String, dynamic>>(
      methodUrl: config.methodUrl('agriflow.api.v1.notification.mark_read'),
      data: {'name': name},
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
  }

  Future<void> markAllRead() async {
    await api.postMethod<Map<String, dynamic>>(
      methodUrl: config.methodUrl('agriflow.api.v1.notification.mark_all_read'),
      data: {},
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
  }
}
