import 'package:equatable/equatable.dart';

/// View model for the hero project timeline screen.
class ProjectTimelineDetail extends Equatable {
  const ProjectTimelineDetail({
    required this.projectName,
    required this.project,
    required this.farmer,
    required this.stages,
    required this.workflow,
    this.blockers = const [],
    this.timelineEvents = const [],
  });

  final String projectName;
  final Map<String, dynamic> project;
  final Map<String, dynamic> farmer;
  final List<StageRowModel> stages;
  final Map<String, dynamic> workflow;
  final List<String> blockers;
  final List<Map<String, dynamic>> timelineEvents;

  int get currentIndex {
    final stage = project['current_stage'] as String? ?? '';
    return stages.indexWhere((s) => s.stageKey == stage);
  }

  @override
  List<Object?> get props => [projectName, project['doc_version']];
}

enum StageVisualState { done, current, pending, locked }

class StageRowModel extends Equatable {
  const StageRowModel({
    required this.stageKey,
    required this.sequence,
    required this.visualState,
    this.dateLabel,
    this.secondaryLabel,
    this.actorLabel,
    this.notes,
    this.isExpanded = false,
  });

  final String stageKey;
  final int sequence;
  final StageVisualState visualState;
  final String? dateLabel;
  final String? secondaryLabel;
  final String? actorLabel;
  final String? notes;
  final bool isExpanded;

  bool get isDone => visualState == StageVisualState.done;
  bool get isCurrent => visualState == StageVisualState.current;
  bool get isPending =>
      visualState == StageVisualState.pending ||
      visualState == StageVisualState.locked;

  @override
  List<Object?> get props => [stageKey, visualState, dateLabel];
}
