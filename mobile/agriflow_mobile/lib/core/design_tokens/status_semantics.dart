import 'package:agriflow_mobile/core/design_tokens/color_tokens.dart';
import 'package:flutter/material.dart';

/// Semantic status colors — use instead of raw Colors.* in widgets.
abstract final class AgriFlowStatusSemantics {
  static Color success(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark
          ? AgriFlowColors.success.withValues(alpha: 0.9)
          : AgriFlowColors.success;

  static Color warning(BuildContext context) => AgriFlowColors.warning;

  static Color error(BuildContext context) => Theme.of(context).colorScheme.error;

  static Color info(BuildContext context) => AgriFlowColors.info;

  static Color pending(BuildContext context) =>
      Theme.of(context).colorScheme.outline;

  static Color active(BuildContext context) =>
      Theme.of(context).colorScheme.secondary;

  static Color alertOrange(BuildContext context) => AgriFlowColors.alertOrange;

  static Color onScrim(BuildContext context) =>
      Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.35);
}
