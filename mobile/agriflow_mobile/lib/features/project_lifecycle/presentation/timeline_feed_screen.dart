import 'package:agriflow_mobile/app/router/routes.dart';
import 'package:agriflow_mobile/core/demo/demo_selection.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/core/sync/mutation_queue.dart';
import 'package:agriflow_mobile/features/project_lifecycle/domain/timeline_event.dart';
import 'package:agriflow_mobile/shared/widgets/empty_state.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final timelineFeedProvider = StreamProvider<List<TimelineEvent>>((ref) {
  return ref.watch(timelineRepositoryProvider).watchFeed();
});

class TimelineFeedScreen extends ConsumerWidget {
  const TimelineFeedScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final feed = ref.watch(timelineFeedProvider);
    final selected = ref.watch(selectedProjectProvider);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.navTimeline)),
      body: feed.when(
        loading: () => const LoadingView(),
        error: (e, _) => Center(child: Text(l10n.errorGeneric)),
        data: (events) {
          if (events.isEmpty) {
            return EmptyState(message: l10n.emptyTimeline);
          }
          return RefreshIndicator(
            onRefresh: () async {
              await ref.read(syncOrchestratorProvider).syncNow();
            },
            child: ListView.separated(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              itemCount: events.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (context, index) {
                final event = events[index];
                return Card(
                  child: ListTile(
                    title: Text(event.title ?? event.eventType),
                    subtitle: Text(
                      [
                        if (event.farmerProject != null) event.farmerProject!,
                        event.createdOn,
                      ].join(' · '),
                    ),
                    leading: const Icon(Icons.event_note),
                    onTap: event.farmerProject != null
                        ? () => context.push(
                              AppRoutes.projectTimeline(event.farmerProject!),
                            )
                        : null,
                  ),
                );
              },
            ),
          );
        },
      ),
      floatingActionButton: selected != null
          ? FloatingActionButton(
              onPressed: () => showTimelineNoteSheet(context, ref, selected),
              child: const Icon(Icons.add_comment),
            )
          : null,
    );
  }
}

void showTimelineNoteSheet(
  BuildContext context,
  WidgetRef ref,
  String farmerProject,
) {
  final l10n = AppLocalizations.of(context)!;
  final controller = TextEditingController();
  showModalBottomSheet<void>(
    context: context,
    showDragHandle: true,
    builder: (ctx) => Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextField(
            controller: controller,
            maxLines: 3,
            decoration: InputDecoration(labelText: l10n.timelineNoteLabel),
          ),
          const SizedBox(height: 16),
          FilledButton(
            onPressed: () async {
              await ref.read(mutationQueueProvider).enqueueTimelineNote(
                    farmerProject: farmerProject,
                    body: controller.text.trim(),
                  );
              if (ctx.mounted) Navigator.pop(ctx);
            },
            child: Text(l10n.timelineNoteQueue),
          ),
        ],
      ),
    ),
  );
}
