import 'package:agriflow_mobile/app/router/deep_link.dart';
import 'package:agriflow_mobile/core/i18n/agriflow_i18n.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:go_router/go_router.dart';
import 'package:agriflow_mobile/features/notifications/domain/notification_item.dart';
import 'package:agriflow_mobile/shared/widgets/empty_state.dart';
import 'package:agriflow_mobile/shared/widgets/loading_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final notificationInboxProvider = StreamProvider<List<NotificationItem>>((ref) {
  return ref.watch(notificationRepositoryProvider).watchInbox();
});

class NotificationInboxScreen extends ConsumerWidget {
  const NotificationInboxScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final inbox = ref.watch(notificationInboxProvider);

    return inbox.when(
      loading: () => const LoadingView(),
      error: (e, _) => Center(child: Text(e.toString())),
      data: (items) {
        if (items.isEmpty) {
          return EmptyState(message: l10n.emptyNotifications);
        }
        return ListView.separated(
          padding: const EdgeInsets.all(16),
          itemCount: items.length,
          separatorBuilder: (_, __) => const SizedBox(height: 8),
          itemBuilder: (context, index) {
            final item = items[index];
            return Card(
              child: ListTile(
                onTap: () {
                  final loc = DeepLinkParser.toLocation(item.deepLink);
                  if (loc != null) context.push(loc);
                },
                title: Text(
                  AgriFlowI18n.notificationTitle(context, item.titleI18nKey),
                ),
                subtitle: item.bodyPreview != null ? Text(item.bodyPreview!) : null,
                trailing: item.isUnread
                    ? TextButton(
                        onPressed: () async {
                          try {
                            await ref
                                .read(notificationRepositoryProvider)
                                .markReadOnline(item.name);
                          } catch (_) {
                            // offline read-only
                          }
                        },
                        child: Text(l10n.notificationMarkRead),
                      )
                    : null,
              ),
            );
          },
        );
      },
    );
  }
}
