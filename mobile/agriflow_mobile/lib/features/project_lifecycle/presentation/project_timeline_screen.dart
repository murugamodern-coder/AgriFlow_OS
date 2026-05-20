import 'package:agriflow_mobile/core/demo/demo_selection.dart';
import 'package:agriflow_mobile/core/i18n/agriflow_i18n.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/features/project_lifecycle/domain/project_stages.dart';
import 'package:agriflow_mobile/shared/widgets/error_view.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final projectTimelineProvider =
    FutureProvider.family<Map<String, dynamic>, String>((ref, projectName) {
  return ref.read(projectRemoteProvider).fetchTimeline(projectName);
});

class ProjectTimelineScreen extends ConsumerStatefulWidget {
  const ProjectTimelineScreen({super.key, required this.projectName});

  final String projectName;

  @override
  ConsumerState<ProjectTimelineScreen> createState() =>
      _ProjectTimelineScreenState();
}

class _ProjectTimelineScreenState extends ConsumerState<ProjectTimelineScreen> {
  bool _transitioning = false;

  Future<void> _advanceStage(Map<String, dynamic> project, Map workflow) async {
    final l10n = AppLocalizations.of(context)!;
    final nextStage = workflow['next_stage'] as String?;
    if (nextStage == null) return;
    setState(() => _transitioning = true);
    try {
      await ref.read(projectRemoteProvider).transition(
            projectName: widget.projectName,
            targetStage: nextStage,
            docVersion: project['doc_version'] as int? ?? 1,
          );
      await ref.read(syncOrchestratorProvider).syncNow();
      ref.invalidate(projectTimelineProvider(widget.projectName));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.stageTransitionSuccess)),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.errorGeneric)),
        );
      }
    } finally {
      if (mounted) setState(() => _transitioning = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    ref.watch(selectedProjectProvider);
    final data = ref.watch(projectTimelineProvider(widget.projectName));

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(l10n.projectTimelineTitle),
            Text(
              widget.projectName,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
      body: data.when(
        loading: () => const LoadingView(),
        error: (e, _) => ErrorView(
          onRetry: () =>
              ref.invalidate(projectTimelineProvider(widget.projectName)),
        ),
        data: (bundle) {
          final project = Map<String, dynamic>.from(
            bundle['project'] as Map? ?? {},
          );
          final history = (bundle['stage_history'] as List? ?? [])
              .map((e) => Map<String, dynamic>.from(e as Map))
              .toList();
          final workflow = Map<String, dynamic>.from(
            bundle['workflow'] as Map? ?? {},
          );
          final currentStage = project['current_stage'] as String? ?? '';
          final currentIndex = ProjectStages.indexOf(currentStage);

          return RefreshIndicator(
            onRefresh: () async {
              ref.invalidate(projectTimelineProvider(widget.projectName));
              await ref.read(syncOrchestratorProvider).syncNow();
            },
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text(
                  project['project_title'] as String? ?? widget.projectName,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 16),
                ...List.generate(ProjectStages.ordered.length, (index) {
                  final stageKey = ProjectStages.ordered[index];
                  final done = index < currentIndex;
                  final current = index == currentIndex;
                  Map<String, dynamic>? hist;
                  for (final h in history) {
                    if (h['to_stage'] == stageKey) {
                      hist = h;
                      break;
                    }
                  }
                  final transitionedOn = hist?['transitioned_on']?.toString();

                  return _StageTile(
                    sequence: index + 1,
                    label: AgriFlowI18n.stageLabel(context, stageKey),
                    done: done,
                    current: current,
                    dateLabel: transitionedOn,
                  );
                }),
                const SizedBox(height: 24),
                if (workflow['can_transition'] == true) ...[
                  FilledButton(
                    onPressed: _transitioning
                        ? null
                        : () => _advanceStage(project, workflow),
                    child: _transitioning
                        ? const SizedBox(
                            height: 22,
                            width: 22,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : Text(
                            l10n.advanceStage(
                              AgriFlowI18n.stageLabel(
                                context,
                                workflow['next_stage'] as String? ?? '',
                              ),
                            ),
                          ),
                  ),
                ] else if ((workflow['blocking_reasons'] as List?)?.isNotEmpty ??
                    false) ...[
                  Text(
                    (workflow['blocking_reasons'] as List).first.toString(),
                    style: TextStyle(color: Theme.of(context).colorScheme.error),
                  ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }
}

class _StageTile extends StatelessWidget {
  const _StageTile({
    required this.sequence,
    required this.label,
    required this.done,
    required this.current,
    this.dateLabel,
  });

  final int sequence;
  final String label;
  final bool done;
  final bool current;
  final String? dateLabel;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final icon = done
        ? Icons.check_circle
        : current
            ? Icons.radio_button_checked
            : Icons.radio_button_off;
    final iconColor = done
        ? colorScheme.primary
        : current
            ? colorScheme.secondary
            : colorScheme.outline;

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: iconColor),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('$sequence. $label',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight:
                              current ? FontWeight.bold : FontWeight.normal,
                        )),
                if (dateLabel != null && dateLabel!.isNotEmpty)
                  Text(dateLabel!, style: Theme.of(context).textTheme.bodySmall),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
