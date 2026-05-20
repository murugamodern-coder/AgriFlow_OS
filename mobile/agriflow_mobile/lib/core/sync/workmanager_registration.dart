import 'package:agriflow_mobile/core/sync/headless_sync_runner.dart';
import 'package:flutter/foundation.dart';
import 'package:workmanager/workmanager.dart';

const agriflowBackgroundSyncTask = 'agriflowBackgroundSync';

@pragma('vm:entry-point')
void workmanagerCallbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    if (task == agriflowBackgroundSyncTask) {
      final ok = await HeadlessSyncRunner.run();
      return ok;
    }
    return false;
  });
}

abstract final class WorkmanagerRegistration {
  static Future<void> register() async {
    if (kIsWeb) return;
    try {
      await Workmanager().initialize(workmanagerCallbackDispatcher);
      await Workmanager().registerPeriodicTask(
        agriflowBackgroundSyncTask,
        agriflowBackgroundSyncTask,
        frequency: const Duration(minutes: 30),
        constraints: Constraints(
          networkType: NetworkType.connected,
        ),
      );
    } catch (e) {
      debugPrint('Workmanager register skipped: $e');
    }
  }
}
