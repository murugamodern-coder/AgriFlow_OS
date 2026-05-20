import 'package:agriflow_mobile/core/design_tokens/color_tokens.dart';
import 'package:flutter/material.dart';

ThemeData buildAgriFlowTheme({required Brightness brightness}) {
  final isLight = brightness == Brightness.light;
  final scheme = ColorScheme(
    brightness: brightness,
    primary: AgriFlowColors.primary,
    onPrimary: AgriFlowColors.onPrimary,
    primaryContainer: isLight
        ? AgriFlowColors.primaryContainer
        : AgriFlowColors.primary.withValues(alpha: 0.25),
    onPrimaryContainer: isLight
        ? AgriFlowColors.onPrimaryContainer
        : AgriFlowColors.primaryContainer,
    secondary: AgriFlowColors.secondary,
    onSecondary: AgriFlowColors.onPrimary,
    tertiary: AgriFlowColors.alertOrange,
    onTertiary: AgriFlowColors.onPrimary,
    error: AgriFlowColors.error,
    onError: AgriFlowColors.onPrimary,
    surface: isLight ? AgriFlowColors.surface : AgriFlowColors.surfaceDark,
    onSurface: isLight ? AgriFlowColors.onSurface : AgriFlowColors.onSurfaceDark,
    onSurfaceVariant: isLight
        ? AgriFlowColors.onSurfaceVariant
        : AgriFlowColors.onSurfaceDark.withValues(alpha: 0.7),
    outline: isLight
        ? AgriFlowColors.outline
        : AgriFlowColors.onSurfaceVariant.withValues(alpha: 0.35),
    surfaceContainerHighest: isLight
        ? AgriFlowColors.background
        : AgriFlowColors.backgroundDark,
  );

  return ThemeData(
    useMaterial3: true,
    brightness: brightness,
    colorScheme: scheme,
    scaffoldBackgroundColor:
        isLight ? AgriFlowColors.background : AgriFlowColors.backgroundDark,
    appBarTheme: AppBarTheme(
      centerTitle: false,
      elevation: 0,
      scrolledUnderElevation: 1,
      backgroundColor: scheme.surface,
      foregroundColor: scheme.onSurface,
    ),
    navigationBarTheme: NavigationBarThemeData(
      indicatorColor: scheme.primaryContainer,
      backgroundColor: scheme.surface,
      labelTextStyle: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return TextStyle(
            fontWeight: FontWeight.w600,
            color: scheme.primary,
          );
        }
        return TextStyle(color: scheme.onSurfaceVariant);
      }),
    ),
    cardTheme: CardThemeData(
      elevation: 0,
      color: scheme.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: scheme.outline),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: scheme.surface,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
    ),
    snackBarTheme: SnackBarThemeData(
      behavior: SnackBarBehavior.floating,
      backgroundColor: scheme.onSurface,
      contentTextStyle: TextStyle(color: scheme.surface),
    ),
  );
}
