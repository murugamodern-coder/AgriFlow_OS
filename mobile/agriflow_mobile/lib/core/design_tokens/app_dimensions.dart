import 'package:agriflow_mobile/core/design_tokens/spacing.dart';

/// Layout dimensions — mirrors UI_TOKENS spacing/radius scales.
abstract final class AppDimensions {
  static const double radius8 = 8;
  static const double radius12 = 12;
  static const double radius16 = 16;
  static const double radius20 = 20;

  static const double pagePadding = AgriFlowSpacing.space16;
  static const double pagePaddingLarge = AgriFlowSpacing.space24;
  static const double listGap = AgriFlowSpacing.space8;
  static const double sectionGap = AgriFlowSpacing.space16;
  static const double bottomSafeExtra = AgriFlowSpacing.space24;

  static const double statusIconSm = 20;
  static const double statusIconMd = 26;
  static const double minTouchTarget = 44;
}
