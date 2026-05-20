import 'package:agriflow_mobile/core/i18n/agriflow_i18n.dart';
import 'package:agriflow_mobile/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('notification and stage labels resolve in English', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Builder(
          builder: (context) {
            expect(
              AgriFlowI18n.notificationTitle(context, 'notification.task_due'),
              'Task due',
            );
            expect(
              AgriFlowI18n.stageLabel(context, 'field_survey'),
              'Field survey',
            );
            return const SizedBox();
          },
        ),
      ),
    );
    await tester.pumpAndSettle();
  });
}
