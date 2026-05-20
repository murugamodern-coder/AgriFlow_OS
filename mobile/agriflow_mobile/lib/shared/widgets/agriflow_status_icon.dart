import 'package:agriflow_mobile/core/design_tokens/app_dimensions.dart';
import 'package:agriflow_mobile/core/design_tokens/status_semantics.dart';
import 'package:flutter/material.dart';

enum AgriFlowStatusKind {
  done,
  pending,
  active,
  overdue,
  locked,
  warning,
  info,
}

/// Consistent status glyphs across timeline, tasks, and notifications.
class AgriFlowStatusIcon extends StatelessWidget {
  const AgriFlowStatusIcon({
    super.key,
    required this.kind,
    this.size = AppDimensions.statusIconMd,
  });

  final AgriFlowStatusKind kind;
  final double size;

  @override
  Widget build(BuildContext context) {
    final color = _color(context);
    final icon = _icon();
    return Icon(icon, color: color, size: size);
  }

  Color _color(BuildContext context) {
    switch (kind) {
      case AgriFlowStatusKind.done:
        return AgriFlowStatusSemantics.success(context);
      case AgriFlowStatusKind.pending:
      case AgriFlowStatusKind.locked:
        return AgriFlowStatusSemantics.pending(context);
      case AgriFlowStatusKind.active:
        return AgriFlowStatusSemantics.active(context);
      case AgriFlowStatusKind.overdue:
      case AgriFlowStatusKind.warning:
        return AgriFlowStatusSemantics.error(context);
      case AgriFlowStatusKind.info:
        return AgriFlowStatusSemantics.info(context);
    }
  }

  IconData _icon() {
    switch (kind) {
      case AgriFlowStatusKind.done:
        return Icons.check_circle;
      case AgriFlowStatusKind.pending:
        return Icons.radio_button_unchecked;
      case AgriFlowStatusKind.active:
        return Icons.sync;
      case AgriFlowStatusKind.overdue:
        return Icons.warning_amber_rounded;
      case AgriFlowStatusKind.locked:
        return Icons.lock_outline;
      case AgriFlowStatusKind.warning:
        return Icons.schedule;
      case AgriFlowStatusKind.info:
        return Icons.info_outline;
    }
  }
}
