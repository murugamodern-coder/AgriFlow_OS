import 'package:agriflow_mobile/core/design_tokens/spacing.dart';
import 'package:agriflow_mobile/features/sync/sync_connectivity.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lottie/lottie.dart';

/// Full-screen sync animation: queue items fly toward cloud (demo wow moment).
class SyncFlyingOverlay extends ConsumerWidget {
  const SyncFlyingOverlay({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final visual = ref.watch(syncVisualControllerProvider);
    return Stack(
      children: [
        child,
        if (visual.showFlyingOverlay)
          Positioned.fill(
            child: IgnorePointer(
              child: Container(
                color: Colors.black.withValues(alpha: 0.35),
                child: Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      SizedBox(
                        width: 140,
                        height: 140,
                        child: Lottie.asset(
                          'assets/lottie/sync_cloud.json',
                          repeat: true,
                          fit: BoxFit.contain,
                          errorBuilder: (_, __, ___) => Icon(
                            Icons.cloud_upload,
                            size: 80,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                        ),
                      ),
                      const SizedBox(height: AgriFlowSpacing.space16),
                      ...List.generate(
                        3,
                        (i) => Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: _flyingChip(context, i),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }

  Widget _flyingChip(BuildContext context, int index) {
    return Chip(
      avatar: const Icon(Icons.upload_file, size: 16),
      label: Text('↑ ${index + 1}'),
    )
        .animate(onPlay: (c) => c.repeat())
        .moveY(
          begin: 40,
          end: -80,
          duration: (900 + index * 120).ms,
          curve: Curves.easeInOut,
        )
        .fadeIn(duration: 200.ms)
        .then(delay: 600.ms)
        .fadeOut(duration: 200.ms);
  }
}
