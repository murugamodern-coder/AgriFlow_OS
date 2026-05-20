import 'package:equatable/equatable.dart';

/// Open task row from sync projection or API payload.
class TaskSummary extends Equatable {
  const TaskSummary({
    required this.name,
    required this.subject,
    required this.status,
    this.farmerProject,
    this.farmer,
    this.farmerName,
    this.villageName,
    this.taskType,
    this.block,
    this.priority,
    this.dueDate,
    this.stageKey,
    this.assignedTo,
    this.assignedOfficer,
    this.isOverdue = false,
    required this.docVersion,
    required this.modified,
  });

  final String name;
  final String subject;
  final String status;
  final String? farmerProject;
  final String? farmer;
  final String? farmerName;
  final String? villageName;
  final String? taskType;
  final String? block;
  final String? priority;
  final String? dueDate;
  final String? stageKey;
  final String? assignedTo;
  final String? assignedOfficer;
  final bool isOverdue;
  final int docVersion;
  final String modified;

  bool get isOpen =>
      status == 'open' || status == 'assigned' || status == 'in_progress';

  String get displayFarmer =>
      farmerName?.isNotEmpty == true ? farmerName! : _farmerFromSubject();

  String get displayVillage => villageName ?? '';

  factory TaskSummary.fromPayload(Map<String, dynamic> payload) {
    return TaskSummary(
      name: payload['name'] as String? ?? '',
      subject: payload['subject'] as String? ?? '',
      status: payload['status'] as String? ?? 'open',
      farmerProject: payload['farmer_project'] as String?,
      farmer: payload['farmer'] as String?,
      farmerName: payload['farmer_name'] as String?,
      villageName: payload['village_name'] as String?,
      taskType: payload['task_type'] as String?,
      block: payload['block'] as String?,
      priority: payload['priority'] as String?,
      dueDate: payload['due_date'] as String?,
      stageKey: payload['stage_key'] as String?,
      assignedTo: payload['assigned_to'] as String?,
      assignedOfficer: payload['assigned_officer'] as String?,
      isOverdue: payload['is_overdue'] as bool? ?? false,
      docVersion: payload['doc_version'] as int? ?? 0,
      modified: payload['modified']?.toString() ?? '',
    );
  }

  String _farmerFromSubject() {
    final parts = subject.split('—');
    if (parts.isNotEmpty) {
      return parts.first.trim();
    }
    final dash = subject.split(' - ');
    if (dash.isNotEmpty) return dash.first.trim();
    return subject;
  }

  @override
  List<Object?> get props => [name, status, modified];
}
