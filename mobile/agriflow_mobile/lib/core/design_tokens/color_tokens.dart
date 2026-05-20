import 'package:flutter/material.dart';

/// Semantic colors from [UI_TOKENS.md] — widgets must use these, not raw hex.
abstract final class AgriFlowColors {
  static const Color primary = Color(0xFF047857);
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color primaryContainer = Color(0xFFD1FAE5);
  static const Color onPrimaryContainer = Color(0xFF065F46);
  static const Color secondary = Color(0xFF4F46E5);
  static const Color background = Color(0xFFF8FAFC);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color onSurface = Color(0xFF1E293B);
  static const Color onSurfaceVariant = Color(0xFF475569);
  static const Color outline = Color(0xFFE2E8F0);
  static const Color success = Color(0xFF059669);
  static const Color warning = Color(0xFFD97706);
  static const Color error = Color(0xFFDC2626);
  static const Color info = Color(0xFF0284C7);
  static const Color alertOrange = Color(0xFFE65100);
  static const Color surfaceDark = Color(0xFF1E293B);
  static const Color backgroundDark = Color(0xFF0F172A);
  static const Color onSurfaceDark = Color(0xFFF1F5F9);
}
