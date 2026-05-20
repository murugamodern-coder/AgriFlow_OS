import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/core/sync/sync_visual_controller.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final syncVisualControllerProvider =
    ChangeNotifierProvider<SyncVisualController>((ref) {
  throw UnimplementedError('Initialized in bootstrap');
});

/// True when device is offline or demo simulate-offline is on.
Future<bool> isEffectivelyOffline(WidgetRef ref) async {
  final visual = ref.read(syncVisualControllerProvider);
  if (!visual.isEffectivelyOnline) return true;
  final results = await ref.read(connectivityProvider).checkConnectivity();
  return results.contains(ConnectivityResult.none);
}
