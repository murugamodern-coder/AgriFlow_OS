import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

/// Sync conflict UI foundation — server wins; user refreshes.
class ConflictSheet extends StatelessWidget {
  const ConflictSheet({
    super.key,
    required this.clientMutationId,
    this.serverDocVersion,
    this.clientDocVersion,
    required this.onRefresh,
  });

  final String clientMutationId;
  final int? serverDocVersion;
  final int? clientDocVersion;
  final VoidCallback onRefresh;

  static Future<void> show(
    BuildContext context, {
    required String clientMutationId,
    int? serverDocVersion,
    int? clientDocVersion,
    required VoidCallback onRefresh,
  }) {
    return showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (ctx) => ConflictSheet(
        clientMutationId: clientMutationId,
        serverDocVersion: serverDocVersion,
        clientDocVersion: clientDocVersion,
        onRefresh: onRefresh,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(l10n.conflictTitle, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 12),
          Text(l10n.conflictExplanation),
          const SizedBox(height: 12),
          Text(l10n.conflictStepsTitle, style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 4),
          Text('1. ${l10n.conflictStepRefresh}'),
          Text('2. ${l10n.conflictStepReview}'),
          Text('3. ${l10n.conflictStepRetry}'),
          const SizedBox(height: 8),
          Text('Mutation: $clientMutationId', style: Theme.of(context).textTheme.bodySmall),
          if (serverDocVersion != null || clientDocVersion != null)
            Text('Server v$serverDocVersion · Client v$clientDocVersion'),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: () {
              Navigator.pop(context);
              onRefresh();
            },
            child: Text(l10n.conflictRefresh),
          ),
        ],
      ),
    );
  }
}
