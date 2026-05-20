import 'package:agriflow_mobile/core/design_tokens/color_tokens.dart';
import 'package:flutter/material.dart';

ThemeData buildAgriFlowTheme({required Brightness brightness}) {
  final isLight = brightness == Brightness.light;
  final scheme = ColorScheme(
    brightness: brightness,
    primary: AgriFlowColors.primary,
    onPrimary: AgriFlowColors.onPrimary,
    primaryContainer: AgriFlowColors.primaryContainer,
    onPrimaryContainer: AgriFlowColors.onPrimaryContainer,
    secondary: AgriFlowColors.secondary,
    onSecondary: AgriFlowColors.onPrimary,
    error: AgriFlowColors.error,
    onError: AgriFlowColors.onPrimary,
    surface: isLight ? AgriFlowColors.surface : const Color(0xFF1E293B),
    onSurface: isLight ? AgriFlowColors.onSurface : AgriFlowColors.surface,
  );

  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor:
        isLight ? AgriFlowColors.background : scheme.surface,
    appBarTheme: const AppBarTheme(
      centerTitle: false,
      elevation: 0,
      scrolledUnderElevation: 1,
    ),
    navigationBarTheme: NavigationBarThemeData(
      indicatorColor: AgriFlowColors.primaryContainer,
      labelTextStyle: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const TextStyle(
            fontWeight: FontWeight.w600,
            color: AgriFlowColors.primary,
          );
        }
        return const TextStyle(color: AgriFlowColors.onSurfaceVariant);
      }),
    ),
    cardTheme: CardThemeData(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: AgriFlowColors.outline),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AgriFlowColors.surface,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
    ),
  );
}
