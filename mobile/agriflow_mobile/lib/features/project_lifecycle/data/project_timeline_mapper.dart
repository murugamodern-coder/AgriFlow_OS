import 'package:agriflow_mobile/features/project_lifecycle/domain/project_stages.dart';
import 'package:agriflow_mobile/features/project_lifecycle/domain/project_timeline_detail.dart';
import 'package:intl/intl.dart';

class ProjectTimelineMapper {
  ProjectTimelineMapper._();

  static ProjectTimelineDetail fromApi({
    required String projectName,
    required Map<String, dynamic> bundle,
    required Map<String, dynamic> farmer,
    Map<String, dynamic>? block,
    Map<String, dynamic>? village,
    Map<String, dynamic>? officer,
    Map<String, dynamic>? cluster,
  }) {
    final project = Map<String, dynamic>.from(bundle['project'] as Map? ?? {});
    final history = (bundle['stage_history'] as List? ?? [])
        .map((e) => Map<String, dynamic>.from(e as Map))
        .toList();
    final workflow = Map<String, dynamic>.from(bundle['workflow'] as Map? ?? {});
    final events = (bundle['timeline']?['items'] as List? ?? [])
        .map((e) => Map<String, dynamic>.from(e as Map))
        .toList();

    final currentStage = project['current_stage'] as String? ?? '';
    final currentIndex = ProjectStages.indexOf(currentStage);
    final status = project['status'] as String? ?? 'active';

    final historyByStage = <String, Map<String, dynamic>>{};
    for (final h in history) {
      final to = h['to_stage'] as String?;
      if (to != null) historyByStage[to] = h;
    }

    final blockers = _parseBlockers(project['remarks'] as String?);

    final stages = <StageRowModel>[];
    for (var i = 0; i < ProjectStages.ordered.length; i++) {
      final key = ProjectStages.ordered[i];
      final hist = historyByStage[key];
      final visual = _visualState(i, currentIndex, status);
      stages.add(
        StageRowModel(
          stageKey: key,
          sequence: i + 1,
          visualState: visual,
          dateLabel: _formatDate(hist?['transitioned_on']),
          secondaryLabel: _secondaryForStage(
            key,
            project: project,
            farmer: farmer,
            block: block,
            village: village,
            officer: officer,
            hist: hist,
          ),
          actorLabel: hist?['transitioned_by'] as String?,
          notes: hist?['notes'] as String?,
        ),
      );
    }

    return ProjectTimelineDetail(
      projectName: projectName,
      project: project,
      farmer: {
        ...farmer,
        if (block != null) 'block_name': block['block_name'] ?? block['name'],
        if (village != null) 'village_name': village['village_name'] ?? village['name'],
        if (officer != null) 'officer_name': officer['officer_name'],
        if (cluster != null) 'cluster_name': cluster['cluster_name'] ?? cluster['name'],
      },
      stages: stages,
      workflow: workflow,
      blockers: blockers,
      timelineEvents: events,
    );
  }

  static StageVisualState _visualState(int index, int currentIndex, String status) {
    if (index < currentIndex) return StageVisualState.done;
    if (index == currentIndex) return StageVisualState.current;
    if (status == 'active' && index == currentIndex + 1) {
      return StageVisualState.pending;
    }
    return StageVisualState.locked;
  }

  static List<String> _parseBlockers(String? remarks) {
    if (remarks == null || remarks.isEmpty) return [];
    if (remarks.contains('BLOCKER:')) {
      return remarks
          .split('\n')
          .where((l) => l.trim().startsWith('BLOCKER:'))
          .map((l) => l.replaceFirst('BLOCKER:', '').trim())
          .where((s) => s.isNotEmpty)
          .toList();
    }
    return [];
  }

  static String? _formatDate(dynamic raw) {
    if (raw == null) return null;
    try {
      final dt = DateTime.parse(raw.toString()).toLocal();
      return DateFormat('MMM d').format(dt);
    } catch (_) {
      return raw.toString().length > 10
          ? raw.toString().substring(0, 10)
          : raw.toString();
    }
  }

  static String? _secondaryForStage(
    String key, {
    required Map<String, dynamic> project,
    required Map<String, dynamic> farmer,
    Map<String, dynamic>? block,
    Map<String, dynamic>? village,
    Map<String, dynamic>? officer,
    Map<String, dynamic>? hist,
  }) {
    switch (key) {
      case 'lead_captured':
        final notes = farmer['notes'] as String? ?? '';
        if (notes.contains('referred_by:')) {
          return notes.split('referred_by:').last.trim();
        }
        return hist?['notes'] as String?;
      case 'documents_collected':
        return '4/4 uploaded';
      case 'mimis_registered':
        final mimis = project['mimis_registration_number'];
        return mimis != null ? 'ID: $mimis' : null;
      case 'field_survey':
        return officer?['officer_name'] as String? ??
            project['officer_name'] as String?;
      case 'quotation_generated':
        final q = project['quoted_amount'];
        if (q != null) return '₹${_formatInr(q)}';
        return null;
      case 'pre_inspection_approval':
        return 'AAO approved';
      case 'work_order_received':
        return 'stock reserved';
      case 'material_dispatched':
        return project['work_order_number'] as String?;
      case 'installation_done':
        return 'Murugan team';
      default:
        return hist?['notes'] as String?;
    }
  }

  static String _formatInr(dynamic amount) {
    final n = double.tryParse(amount.toString()) ?? 0;
    if (n >= 100000) return '${(n / 100000).toStringAsFixed(1)}L';
    return NumberFormat('#,##,###').format(n.round());
  }
}
