import 'package:agriflow_mobile/app/router/app_router.dart';
import 'package:agriflow_mobile/core/design_tokens/agriflow_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class AgriFlowApp extends ConsumerWidget {
  const AgriFlowApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    return MaterialApp.router(
      onGenerateTitle: (context) => AppLocalizations.of(context)!.appTitle,
      theme: buildAgriFlowTheme(brightness: Brightness.light),
      darkTheme: buildAgriFlowTheme(brightness: Brightness.dark),
      locale: const Locale('ta'),
      supportedLocales: AppLocalizations.supportedLocales,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      localeResolutionCallback: (locale, supported) {
        if (locale != null && supported.contains(locale)) return locale;
        return const Locale('ta');
      },
      routerConfig: router,
    );
  }
}
