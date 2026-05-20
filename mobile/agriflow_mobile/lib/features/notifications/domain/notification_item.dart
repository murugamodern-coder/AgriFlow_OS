import 'package:equatable/equatable.dart';

class NotificationItem extends Equatable {
  const NotificationItem({
    required this.name,
    required this.titleI18nKey,
    this.bodyPreview,
    this.readOn,
    this.deepLink,
  });

  final String name;
  final String titleI18nKey;
  final String? bodyPreview;
  final String? readOn;
  final String? deepLink;

  bool get isUnread => readOn == null || readOn!.isEmpty;

  factory NotificationItem.fromPayload(Map<String, dynamic> payload) {
    final deep = payload['payload'] as Map<String, dynamic>?;
    return NotificationItem(
      name: payload['name'] as String? ?? '',
      titleI18nKey: payload['title_i18n_key'] as String? ?? 'notification.generic',
      bodyPreview: payload['body_preview'] as String?,
      readOn: payload['read_on']?.toString(),
      deepLink: deep?['deep_link'] as String?,
    );
  }

  @override
  List<Object?> get props => [name, readOn];
}
