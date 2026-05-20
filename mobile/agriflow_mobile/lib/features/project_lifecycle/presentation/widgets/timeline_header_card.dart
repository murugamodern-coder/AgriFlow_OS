import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class TimelineHeaderCard extends StatelessWidget {
  const TimelineHeaderCard({
    super.key,
    required this.farmerName,
    required this.tags,
    required this.locationLine,
    required this.schemeLine,
    required this.projectLine,
    required this.officerLine,
    this.referralLine,
  });

  final String farmerName;
  final List<String> tags;
  final String locationLine;
  final String schemeLine;
  final String projectLine;
  final String officerLine;
  final String? referralLine;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    return Card(
      elevation: 0,
      color: theme.colorScheme.primaryContainer.withValues(alpha: 0.35),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: theme.colorScheme.outline.withValues(alpha: 0.3)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(AgriFlowSpacing.space16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.agriculture, color: theme.colorScheme.primary, size: 28),
                const SizedBox(width: AgriFlowSpacing.space8),
                Expanded(
                  child: Text(
                    farmerName,
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                ...tags.map((t) => Padding(
                      padding: const EdgeInsets.only(left: 4),
                      child: _TagChip(label: t),
                    )),
              ],
            ),
            const SizedBox(height: AgriFlowSpacing.space12),
            _infoRow(Icons.place_outlined, locationLine),
            _infoRow(Icons.water_drop_outlined, schemeLine),
            _infoRow(Icons.folder_outlined, projectLine),
            _infoRow(Icons.badge_outlined, officerLine),
            if (referralLine != null && referralLine!.isNotEmpty)
              _infoRow(Icons.handshake_outlined, referralLine!),
          ],
        ),
      ),
    );
  }

  Widget _infoRow(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.only(top: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 18),
          const SizedBox(width: 8),
          Expanded(child: Text(text, style: const TextStyle(height: 1.35))),
        ],
      ),
    );
  }
}

class _TagChip extends StatelessWidget {
  const _TagChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    final isVip = label.toUpperCase().contains('VIP');
    return Chip(
      label: Text(label, style: const TextStyle(fontSize: 11)),
      visualDensity: VisualDensity.compact,
      backgroundColor: isVip
          ? Theme.of(context).colorScheme.tertiaryContainer
          : Theme.of(context).colorScheme.secondaryContainer,
      padding: EdgeInsets.zero,
    );
  }
}
