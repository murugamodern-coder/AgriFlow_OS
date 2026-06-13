import 'package:equatable/equatable.dart';

class WorkflowState extends Equatable {
  const WorkflowState({
    required this.order,
    required this.key,
    required this.state,
    required this.labelTa,
    required this.color,
  });

  final int order;
  final String key;
  final String state;
  final String labelTa;
  final String color;

  factory WorkflowState.fromJson(Map<String, dynamic> json) {
    return WorkflowState(
      order: json['order'] as int? ?? 0,
      key: json['key'] as String? ?? '',
      state: json['state'] as String? ?? '',
      labelTa: json['label_ta'] as String? ?? '',
      color: json['color'] as String? ?? 'blue',
    );
  }

  @override
  List<Object?> get props => [order, key, state];
}

class WorkflowAction extends Equatable {
  const WorkflowAction({
    required this.action,
    required this.nextState,
    required this.allowedRole,
  });

  final String action;
  final String nextState;
  final String allowedRole;

  factory WorkflowAction.fromJson(Map<String, dynamic> json) {
    return WorkflowAction(
      action: json['action'] as String? ?? '',
      nextState: json['next_state'] as String? ?? '',
      allowedRole: json['allowed_role'] as String? ?? '',
    );
  }

  @override
  List<Object?> get props => [action, nextState];
}

class WorkflowStatus extends Equatable {
  const WorkflowStatus({
    required this.currentState,
    required this.currentStage,
    required this.stageSequence,
    required this.actions,
    required this.allStages,
    this.docVersion = 1,
    this.status,
    this.error,
  });

  final String currentState;
  final String currentStage;
  final int stageSequence;
  final int docVersion;
  final String? status;
  final String? error;
  final List<WorkflowAction> actions;
  final List<WorkflowState> allStages;

  factory WorkflowStatus.fromJson(Map<String, dynamic> json) {
    return WorkflowStatus(
      currentState: json['current_state'] as String? ?? 'Lead Captured',
      currentStage: json['current_stage'] as String? ?? 'lead_captured',
      stageSequence: json['stage_sequence'] as int? ?? 1,
      docVersion: json['doc_version'] as int? ?? 1,
      status: json['status'] as String?,
      error: json['error'] as String?,
      actions: (json['actions'] as List? ?? [])
          .map((a) => WorkflowAction.fromJson(Map<String, dynamic>.from(a as Map)))
          .toList(),
      allStages: (json['all_stages'] as List? ?? [])
          .map((s) => WorkflowState.fromJson(Map<String, dynamic>.from(s as Map)))
          .toList(),
    );
  }

  @override
  List<Object?> get props => [currentState, currentStage, stageSequence, docVersion];
}
