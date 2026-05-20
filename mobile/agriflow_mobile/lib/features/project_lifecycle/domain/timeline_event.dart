import 'package:equatable/equatable.dart';

class TimelineEvent extends Equatable {
  const TimelineEvent({
    required this.name,
    required this.eventType,
    required this.createdOn,
    this.farmerProject,
    this.block,
    this.title,
  });

  final String name;
  final String eventType;
  final String createdOn;
  final String? farmerProject;
  final String? block;
  final String? title;

  factory TimelineEvent.fromPayload(Map<String, dynamic> payload) {
    return TimelineEvent(
      name: payload['name'] as String? ?? '',
      eventType: payload['event_type'] as String? ?? 'unknown',
      createdOn: payload['created_on']?.toString() ?? '',
      farmerProject: payload['farmer_project'] as String?,
      block: payload['block'] as String?,
      title: payload['title'] as String? ?? payload['body'] as String?,
    );
  }

  @override
  List<Object?> get props => [name, createdOn];
}
