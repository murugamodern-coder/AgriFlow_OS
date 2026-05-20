import 'package:equatable/equatable.dart';

enum NotificationTone { urgent, warning, orange, info, success }

class NotificationItem extends Equatable {
  const NotificationItem({
    required this.name,
    required this.titleI18nKey,
    this.bodyPreview,
    this.readOn,
    this.deepLink,
    this.notificationType,
    this.createdOn,
    this.priority,
    this.tone = NotificationTone.info,
    this.farmerProject,
    this.farmer,
  });

  final String name;
  final String titleI18nKey;
  final String? bodyPreview;
  final String? readOn;
  final String? deepLink;
  final String? notificationType;
  final String? createdOn;
  final String? priority;
  final NotificationTone tone;
  final String? farmerProject;
  final String? farmer;

  bool get isUnread => readOn == null || readOn!.isEmpty;

  factory NotificationItem.fromPayload(Map<String, dynamic> payload) {
    final nested = payload['payload'] as Map<String, dynamic>?;
    final read = payload['read'] as bool?;
    final readOn = read == true
        ? 'read'
        : payload['read_on']?.toString();
    return NotificationItem(
      name: payload['name'] as String? ?? '',
      titleI18nKey: payload['title_i18n_key'] as String? ?? 'notificationManual',
      bodyPreview: payload['body_preview'] as String?,
      readOn: readOn,
      deepLink: nested?['deep_link'] as String?,
      notificationType: payload['notification_type'] as String?,
      createdOn: payload['created_on']?.toString(),
      priority: payload['priority'] as String?,
      tone: _toneFromPayload(nested, payload),
      farmerProject: payload['farmer_project'] as String?,
      farmer: payload['farmer'] as String?,
    );
  }

  static NotificationTone _toneFromPayload(
    Map<String, dynamic>? nested,
    Map<String, dynamic> payload,
  ) {
    final tone = nested?['tone'] as String?;
    switch (tone) {
      case 'urgent':
        return NotificationTone.urgent;
      case 'warning':
        return NotificationTone.warning;
      case 'orange':
        return NotificationTone.orange;
      case 'success':
        return NotificationTone.success;
      case 'info':
        return NotificationTone.info;
    }
    if (payload['priority'] == 'high') return NotificationTone.urgent;
    return NotificationTone.info;
  }

  @override
  List<Object?> get props => [name, readOn];
}
