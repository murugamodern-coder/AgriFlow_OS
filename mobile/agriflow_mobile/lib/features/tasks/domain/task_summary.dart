import 'package:equatable/equatable.dart';

class TaskSummary extends Equatable {
  const TaskSummary({
    required this.name,
    required this.subject,
    required this.status,
    this.farmerProject,
    this.block,
    this.priority,
    this.dueDate,
    required this.docVersion,
    required this.modified,
  });

  final String name;
  final String subject;
  final String status;
  final String? farmerProject;
  final String? block;
  final String? priority;
  final String? dueDate;
  final int docVersion;
  final String modified;

  factory TaskSummary.fromPayload(Map<String, dynamic> payload) {
    return TaskSummary(
      name: payload['name'] as String? ?? '',
      subject: payload['subject'] as String? ?? '',
      status: payload['status'] as String? ?? 'open',
      farmerProject: payload['farmer_project'] as String?,
      block: payload['block'] as String?,
      priority: payload['priority'] as String?,
      dueDate: payload['due_date'] as String?,
      docVersion: payload['doc_version'] as int? ?? 0,
      modified: payload['modified']?.toString() ?? '',
    );
  }

  @override
  List<Object?> get props => [name, status, modified];
}
