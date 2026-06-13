import 'package:agriflow_mobile/core/demo/demo_selection.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:agriflow_mobile/features/project_lifecycle/data/project_timeline_mapper.dart';
import 'package:agriflow_mobile/features/project_lifecycle/domain/project_timeline_detail.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/providers/workflow_provider.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/timeline_feed_screen.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/widgets/timeline_actions_bar.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/widgets/timeline_header_card.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/widgets/timeline_project_sale_button.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/widgets/timeline_workflow_actions.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/widgets/timeline_workflow_progress_card.dart';
import 'package:agriflow_mobile/features/project_lifecycle/presentation/widgets/workflow_timeline_stage_row.dart';
import 'package:agriflow_mobile/shared/widgets/empty_state.dart';
import 'package:agriflow_mobile/shared/widgets/error_view.dart';
import 'package:agriflow_mobile/shared/widgets/timeline_shimmer.dart';
import 'package:flutter/material.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final projectTimelineDetailProvider =
    FutureProvider.family<ProjectTimelineDetail, String>((ref, projectName) async {
  final remote = ref.read(projectRemoteProvider);
  final bundle = await remote.fetchTimelineBundle(projectName);
  final timeline = Map<String, dynamic>.from(bundle['timeline'] as Map);
  final farmer = Map<String, dynamic>.from(bundle['farmer'] as Map? ?? {});
  return ProjectTimelineMapper.fromApi(
    projectName: projectName,
    bundle: timeline,
    farmer: farmer,
  );
});

class ProjectTimelineScreen extends ConsumerStatefulWidget {
  const ProjectTimelineScreen({super.key, required this.projectName});

  final String projectName;

  @override
  ConsumerState<ProjectTimelineScreen> createState() =>
      _ProjectTimelineScreenState();
}

class _ProjectTimelineScreenState extends ConsumerState<ProjectTimelineScreen> {
  Future<void> _refresh() async {
    ref.invalidate(projectTimelineDetailProvider(widget.projectName));
    ref.invalidate(projectWorkflowProvider(widget.projectName));
    await ref.read(syncOrchestratorProvider).syncNow();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    ref.watch(selectedProjectProvider);
    final asyncDetail = ref.watch(projectTimelineDetailProvider(widget.projectName));
    final asyncWorkflow = ref.watch(projectWorkflowProvider(widget.projectName));

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.projectTimelineTitle),
      ),
      body: asyncDetail.when(
        loading: () => const TimelineShimmer(),
        error: (_, __) => ErrorView(onRetry: _refresh),
        data: (detail) {
          return asyncWorkflow.when(
            loading: () => const TimelineShimmer(),
            error: (_, __) => ErrorView(onRetry: _refresh),
            data: (workflow) {
              if (workflow.allStages.isEmpty) {
                return EmptyState(message: l10n.emptyTimeline);
              }
              final farmer = detail.farmer;
              final tags = _parseTags(farmer['tags'] as String?);
              final location = _locationLine(farmer, l10n);
              final scheme = _schemeLine(farmer, l10n);
              final project = detail.project;
              final projectLabel = (project['project_title'] as String?)?.contains('#') == true
                  ? (project['project_title'] as String).split('·').last.trim()
                  : widget.projectName;
              final projectLine = l10n.timelineHeaderProject(projectLabel);
              final officer = l10n.timelineHeaderOfficer(
                project['officer_name'] as String? ??
                    farmer['officer_name'] as String? ??
                    '—',
              );
              final referralRaw = _referralLine(farmer);
              final referral =
                  referralRaw != null ? l10n.timelineHeaderReferral(referralRaw) : null;

              return RefreshIndicator(
                onRefresh: _refresh,
                child: CustomScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  slivers: [
                    SliverPadding(
                      padding: const EdgeInsets.fromLTRB(
                        AgriFlowSpacing.space16,
                        AgriFlowSpacing.space16,
                        AgriFlowSpacing.space16,
                        AgriFlowSpacing.space8,
                      ),
                      sliver: SliverToBoxAdapter(
                        child: TimelineHeaderCard(
                          farmerName: farmer['farmer_name'] as String? ?? '—',
                          tags: tags,
                          locationLine: location,
                          schemeLine: scheme,
                          projectLine: projectLine,
                          officerLine: officer,
                          referralLine: referral,
                        ),
                      ),
                    ),
                    SliverToBoxAdapter(
                      child: TimelineWorkflowProgressCard(
                        projectName: widget.projectName,
                      ),
                    ),
                    SliverList(
                      delegate: SliverChildBuilderDelegate(
                        (context, index) {
                          final stage = workflow.allStages[index];
                          return WorkflowTimelineStageRow(
                            stage: stage,
                            currentStageOrder: workflow.stageSequence,
                          );
                        },
                        childCount: workflow.allStages.length,
                      ),
                    ),
                    SliverPadding(
                      padding: const EdgeInsets.all(AgriFlowSpacing.space16),
                      sliver: SliverToBoxAdapter(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            TimelineWorkflowActions(
                              projectName: widget.projectName,
                            ),
                            TimelineProjectSaleButton(
                              projectName: widget.projectName,
                              farmerDisplayName:
                                  farmer['farmer_name'] as String?,
                            ),
                            const SizedBox(height: AgriFlowSpacing.space16),
                            TimelineActionsBar(
                              projectName: widget.projectName,
                              mobile: farmer['mobile'] as String?,
                              blockers: detail.blockers,
                              onNote: () => showTimelineNoteSheet(
                                context,
                                ref,
                                widget.projectName,
                              ),
                            ),
                            const SizedBox(height: AgriFlowSpacing.space24),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              );
            },
          );
        },
      ),
    );
  }

  List<String> _parseTags(String? raw) {
    if (raw == null || raw.isEmpty) return [];
    return raw
        .split(',')
        .map((s) => s.trim())
        .where((s) => s.isNotEmpty)
        .map((s) {
          if (s.toUpperCase() == 'VIP') return 'VIP ⭐';
          if (s.contains('Friend')) return 'FF';
          return s;
        })
        .toList();
  }

  String _locationLine(Map<String, dynamic> farmer, AppLocalizations l10n) {
    final block = farmer['block_name'] ?? farmer['block'] ?? '';
    final village = farmer['village_name'] ?? farmer['village'] ?? '';
    final acres = farmer['land_extent_acres'];
    final acresStr = acres != null ? ' · $acres ${l10n.timelineAcres}' : '';
    return l10n.timelineHeaderLocation('$block', '$village', acresStr);
  }

  String _schemeLine(Map<String, dynamic> farmer, AppLocalizations l10n) {
    final tags = (farmer['tags'] as String? ?? '').toLowerCase();
    if (tags.contains('drip')) {
      return l10n.timelineHeaderSchemeDrip;
    }
    return l10n.timelineHeaderSchemeSubsidy;
  }

  String? _referralLine(Map<String, dynamic> farmer) {
    final notes = farmer['notes'] as String? ?? '';
    if (!notes.contains('referred_by:')) return null;
    return notes.split('referred_by:').last.trim();
  }
}
