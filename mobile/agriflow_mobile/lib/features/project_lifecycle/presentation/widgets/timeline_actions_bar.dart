import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

class TimelineActionsBar extends ConsumerWidget {
  const TimelineActionsBar({
    super.key,
    required this.projectName,
    required this.mobile,
    required this.blockers,
    required this.onNote,
  });

  final String projectName;
  final String? mobile;
  final List<String> blockers;
  final VoidCallback onNote;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (blockers.isNotEmpty) ...[
          ...blockers.map(
            (b) => Card(
              color: theme.colorScheme.errorContainer.withValues(alpha: 0.35),
              margin: const EdgeInsets.only(bottom: AgriFlowSpacing.space8),
              child: ListTile(
                leading: Icon(Icons.warning_amber_rounded,
                    color: theme.colorScheme.error),
                title: Text(l10n.timelineBlockerMissing(b)),
                dense: true,
              ),
            ),
          ),
        ],
        const SizedBox(height: AgriFlowSpacing.space8),
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: mobile != null && mobile!.length >= 10
                    ? () => _dial(mobile!)
                    : null,
                icon: const Icon(Icons.phone_outlined),
                label: Text(l10n.timelineActionCall),
              ),
            ),
            const SizedBox(width: AgriFlowSpacing.space8),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: mobile != null && mobile!.length >= 10
                    ? () => _whatsapp(mobile!)
                    : null,
                icon: const Icon(Icons.chat_outlined),
                label: Text(l10n.timelineActionWhatsapp),
              ),
            ),
            const SizedBox(width: AgriFlowSpacing.space8),
            Expanded(
              child: FilledButton.icon(
                onPressed: onNote,
                icon: const Icon(Icons.edit_note),
                label: Text(l10n.timelineActionNote),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Future<void> _dial(String mobile) async {
    final uri = Uri.parse('tel:$mobile');
    if (await canLaunchUrl(uri)) await launchUrl(uri);
  }

  Future<void> _whatsapp(String mobile) async {
    final digits = mobile.replaceAll(RegExp(r'\D'), '');
    final uri = Uri.parse('https://wa.me/91$digits');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }
}
