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
      final secondary = _secondaryForStage(
        key,
        project: project,
        farmer: farmer,
        block: block,
        village: village,
        officer: officer,
        hist: hist,
      );
      stages.add(
        StageRowModel(
          stageKey: key,
          sequence: i + 1,
          visualState: visual,
          dateLabel: _formatDate(hist?['transitioned_on']),
          secondaryLabel: secondary.text,
          secondaryI18nKey: secondary.i18nKey,
          secondaryI18nArg: secondary.i18nArg,
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

  static _SecondaryResolution _secondaryForStage(
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
          return _SecondaryResolution.text(
            notes.split('referred_by:').last.trim(),
          );
        }
        return _SecondaryResolution.text(hist?['notes'] as String?);
      case 'documents_collected':
        return const _SecondaryResolution.i18n('docsComplete');
      case 'mimis_registered':
        final mimis = project['mimis_registration_number'];
        if (mimis == null) return const _SecondaryResolution.empty();
        return _SecondaryResolution.i18n('mimisId', mimis.toString());
      case 'field_survey':
        final name = officer?['officer_name'] as String? ??
            project['officer_name'] as String?;
        return _SecondaryResolution.text(name);
      case 'quotation_generated':
        final q = project['quoted_amount'];
        if (q == null) return const _SecondaryResolution.empty();
        return _SecondaryResolution.i18n('quotation', _formatInr(q));
      case 'pre_inspection_approval':
        return const _SecondaryResolution.i18n('aaoApproved');
      case 'work_order_received':
        return const _SecondaryResolution.i18n('stockReserved');
      case 'material_dispatched':
        return _SecondaryResolution.text(
          project['work_order_number'] as String?,
        );
      case 'installation_done':
        return const _SecondaryResolution.i18n('installationTeam');
      default:
        return _SecondaryResolution.text(hist?['notes'] as String?);
    }
  }

  static String _formatInr(dynamic amount) {
    final n = double.tryParse(amount.toString()) ?? 0;
    if (n >= 100000) return '${(n / 100000).toStringAsFixed(1)}L';
    return NumberFormat('#,##,###').format(n.round());
  }
}

/// Resolution carries either a plain text fallback (notes, names) or an
/// i18n key + optional argument the widget should resolve via [AgriFlowI18n].
class _SecondaryResolution {
  const _SecondaryResolution.text(this.text)
      : i18nKey = null,
        i18nArg = null;
  const _SecondaryResolution.i18n(this.i18nKey, [this.i18nArg]) : text = null;
  const _SecondaryResolution.empty()
      : text = null,
        i18nKey = null,
        i18nArg = null;

  final String? text;
  final String? i18nKey;
  final String? i18nArg;
}
