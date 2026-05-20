import 'package:agriflow_mobile/app/router/deep_link.dart';
import 'package:agriflow_mobile/app/router/routes.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/features/notifications/domain/notification_inbox_logic.dart';
import 'package:agriflow_mobile/features/notifications/domain/notification_item.dart';
import 'package:agriflow_mobile/features/notifications/presentation/widgets/notification_feed_card.dart';
import 'package:agriflow_mobile/shared/widgets/empty_state.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final notificationInboxProvider = StreamProvider<List<NotificationItem>>((ref) {
  return ref.watch(notificationRepositoryProvider).watchInbox();
});

final notificationUnreadCountProvider = Provider<int>((ref) {
  final inbox = ref.watch(notificationInboxProvider);
  return inbox.maybeWhen(
    data: (items) => items.where((i) => i.isUnread).length,
    orElse: () => 0,
  );
});

class NotificationInboxScreen extends ConsumerStatefulWidget {
  const NotificationInboxScreen({super.key});

  @override
  ConsumerState<NotificationInboxScreen> createState() =>
      _NotificationInboxScreenState();
}

class _NotificationInboxScreenState extends ConsumerState<NotificationInboxScreen> {
  String? _typeFilter;
  final Set<String> _dismissed = {};

  Future<void> _refresh() async {
    await ref.read(syncOrchestratorProvider).syncNow();
  }

  void _navigate(NotificationItem item) {
    final loc = item.deepLink != null
        ? DeepLinkParser.toLocation(item.deepLink)
        : null;
    if (loc != null) {
      context.push(loc);
      return;
    }
    if (item.farmerProject != null) {
      context.push(AppRoutes.projectTimeline(item.farmerProject!));
      return;
    }
    if (item.notificationType?.contains('task') == true) {
      context.go(AppRoutes.tasks);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final inbox = ref.watch(notificationInboxProvider);

    return inbox.when(
      loading: () => const LoadingView(),
      error: (_, __) => Center(child: Text(l10n.errorGeneric)),
      data: (items) {
        final visible = items.where((i) => !_dismissed.contains(i.name)).toList();
        final filtered = NotificationInboxLogic.filter(
          visible,
          type: _typeFilter,
        );
        final grouped = NotificationInboxLogic.groupByDate(filtered);

        return Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
              child: Row(
                children: [
                  Expanded(
                    child: SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: [
                          FilterChip(
                            label: Text(l10n.notificationFilterAll),
                            selected: _typeFilter == null,
                            onSelected: (_) => setState(() => _typeFilter = null),
                          ),
                          const SizedBox(width: 8),
                          FilterChip(
                            label: Text(l10n.notificationFilterUrgent),
                            selected: _typeFilter == 'system_alert',
                            onSelected: (_) =>
                                setState(() => _typeFilter = 'system_alert'),
                          ),
                          const SizedBox(width: 8),
                          FilterChip(
                            label: Text(l10n.notificationFilterTasks),
                            selected: _typeFilter == 'task_overdue',
                            onSelected: (_) =>
                                setState(() => _typeFilter = 'task_overdue'),
                          ),
                        ],
                      ),
                    ),
                  ),
                  TextButton(
                    onPressed: () async {
                      try {
                        await ref
                            .read(notificationRepositoryProvider)
                            .markAllReadOnline();
                        await _refresh();
                      } catch (_) {}
                    },
                    child: Text(l10n.notificationMarkAllRead),
                  ),
                ],
              ),
            ),
            Expanded(
              child: grouped.isEmpty
                  ? RefreshIndicator(
                      onRefresh: _refresh,
                      child: ListView(
                        physics: const AlwaysScrollableScrollPhysics(),
                        children: [
                          SizedBox(
                            height: MediaQuery.sizeOf(context).height * 0.35,
                            child: EmptyState(message: l10n.notificationEmptyFriendly),
                          ),
                        ],
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh: _refresh,
                      child: ListView(
                        physics: const AlwaysScrollableScrollPhysics(),
                        padding: const EdgeInsets.all(16),
                        children: [
                          ..._buildSections(context, grouped, l10n),
                        ],
                      ),
                    ),
            ),
          ],
        );
      },
    );
  }

  List<Widget> _buildSections(
    BuildContext context,
    NotificationInboxGrouped grouped,
    AppLocalizations l10n,
  ) {
    var index = 0;
    final sections = <Widget>[];

    void addSection(String title, List<NotificationItem> items) {
      if (items.isEmpty) return;
      sections.add(
        Padding(
          padding: const EdgeInsets.only(bottom: 8, top: 4),
          child: Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
        ),
      );
      for (final item in items) {
        sections.add(
          NotificationFeedCard(
            item: item,
            animateIndex: index++,
            onTap: () async {
              if (item.isUnread) {
                try {
                  await ref
                      .read(notificationRepositoryProvider)
                      .markReadOnline(item.name);
                } catch (_) {}
              }
              _navigate(item);
            },
            onDismiss: () async {
              if (item.isUnread) {
                try {
                  await ref
                      .read(notificationRepositoryProvider)
                      .markReadOnline(item.name);
                } catch (_) {}
              }
              setState(() => _dismissed.add(item.name));
              return true;
            },
          ),
        );
      }
    }

    addSection(l10n.notificationGroupToday, grouped.today);
    addSection(l10n.notificationGroupYesterday, grouped.yesterday);
    addSection(l10n.notificationGroupThisWeek, grouped.thisWeek);
    addSection(l10n.notificationGroupOlder, grouped.older);
    return sections;
  }
}
