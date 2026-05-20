import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';

/// Shimmer placeholder for hero timeline loading (UI_TOKENS §24).
class TimelineShimmer extends StatelessWidget {
  const TimelineShimmer({super.key});

  @override
  Widget build(BuildContext context) {
    final base = Theme.of(context).colorScheme.surfaceContainerHighest;
    return Shimmer.fromColors(
      baseColor: base.withValues(alpha: 0.5),
      highlightColor: base.withValues(alpha: 0.9),
      child: ListView(
        padding: const EdgeInsets.all(AgriFlowSpacing.space16),
        children: [
          _box(context, height: 140, radius: 16),
          const SizedBox(height: AgriFlowSpacing.space16),
          ...List.generate(
            8,
            (_) => Padding(
              padding: const EdgeInsets.only(bottom: AgriFlowSpacing.space12),
              child: Row(
                children: [
                  _box(context, width: 28, height: 28, radius: 14),
                  const SizedBox(width: AgriFlowSpacing.space12),
                  Expanded(child: _box(context, height: 52, radius: 12)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _box({double? width, required double height, double radius = 8}) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(radius),
      ),
    );
  }
}
