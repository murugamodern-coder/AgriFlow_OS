import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';
import 'package:agriflow_mobile/core/network/dio_client.dart';
import 'package:agriflow_mobile/core/network/tracing_interceptor.dart';
import 'package:agriflow_mobile/core/storage/hive_boxes.dart';
import 'package:agriflow_mobile/core/storage/secure_token_store.dart';
import 'package:agriflow_mobile/core/sync/inventory_queue.dart';
import 'package:agriflow_mobile/core/sync/mutation_queue.dart';
import 'package:agriflow_mobile/core/sync/projection_writer.dart';
import 'package:agriflow_mobile/core/sync/push_result_applier.dart';
import 'package:agriflow_mobile/core/sync/sync_orchestrator.dart';
import 'package:agriflow_mobile/core/sync/sync_status.dart';
import 'package:agriflow_mobile/core/sync/sync_remote.dart';
import 'package:agriflow_mobile/features/auth/data/auth_repository.dart';
import 'package:agriflow_mobile/features/farmer/data/farmer_remote.dart';
import 'package:agriflow_mobile/features/inventory/data/inventory_remote.dart';
import 'package:agriflow_mobile/features/project_lifecycle/data/project_remote.dart';
import 'package:agriflow_mobile/features/notifications/data/notification_remote.dart';
import 'package:agriflow_mobile/features/notifications/data/notification_repository.dart';
import 'package:agriflow_mobile/core/observability/pilot_telemetry_service.dart';
import 'package:agriflow_mobile/core/push/push_service.dart';
import 'package:agriflow_mobile/features/pilot_ops/data/pilot_ops_remote.dart';
import 'package:agriflow_mobile/features/project_lifecycle/data/timeline_repository.dart';
import 'package:agriflow_mobile/features/tasks/data/task_repository.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final appDatabaseProvider = Provider<AppDatabase>((ref) {
  throw UnimplementedError('Initialized in bootstrap');
});

final hiveStorageProvider = Provider<HiveStorage>((ref) {
  throw UnimplementedError('Initialized in bootstrap');
});

final secureTokenStoreProvider = Provider<SecureTokenStore>((ref) {
  return SecureTokenStore();
});

final apiConfigProvider = Provider<ApiConfig>((ref) {
  return ApiConfig.fromEnv();
});

final tracingInterceptorProvider = Provider<TracingInterceptor>((ref) {
  return TracingInterceptor();
});

final dioProvider = Provider<Dio>((ref) {
  final tokens = ref.watch(secureTokenStoreProvider);
  final authRepo = ref.watch(authRepositoryProvider);
  return createDio(
    config: ref.watch(apiConfigProvider),
    readAccessToken: tokens.readAccessToken,
    onRefresh: authRepo.refreshAccessToken,
    tracing: ref.watch(tracingInterceptorProvider),
  );
});

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient(dio: ref.watch(dioProvider));
});

final connectivityProvider = Provider<Connectivity>((ref) => Connectivity());

final mutationQueueProvider = Provider<MutationQueue>((ref) {
  return MutationQueue(ref.watch(appDatabaseProvider));
});

final inventoryQueueProvider = Provider<InventoryQueue>((ref) {
  return InventoryQueue(ref.watch(appDatabaseProvider));
});

final pushServiceProvider = Provider<PushService>((ref) {
  throw UnimplementedError('Initialized in bootstrap');
});

final pilotTelemetryProvider = Provider<PilotTelemetryService>((ref) {
  return PilotTelemetryService(
    remote: ref.watch(pilotOpsRemoteProvider),
    db: ref.watch(appDatabaseProvider),
    hive: ref.watch(hiveStorageProvider),
  );
});

final syncOrchestratorProvider = Provider<SyncOrchestrator>((ref) {
  final db = ref.watch(appDatabaseProvider);
  final hive = ref.watch(hiveStorageProvider);
  final api = ref.watch(apiClientProvider);
  final config = ref.watch(apiConfigProvider);
  return SyncOrchestrator(
    db: db,
    hive: hive,
    remote: SyncRemote(
      api: api,
      config: config,
      db: db,
      applier: PushResultApplier(db),
    ),
    writer: ProjectionWriter(db, hive),
    notificationRemote: ref.watch(notificationRemoteProvider),
    connectivity: ref.watch(connectivityProvider),
    tracing: ref.watch(tracingInterceptorProvider),
    telemetry: ref.watch(pilotTelemetryProvider),
    inventoryQueue: ref.watch(inventoryQueueProvider),
    inventoryRemote: ref.watch(inventoryRemoteProvider),
  );
});

final taskRepositoryProvider = Provider<TaskRepository>((ref) {
  return TaskRepository(
    db: ref.watch(appDatabaseProvider),
    hive: ref.watch(hiveStorageProvider),
    queue: ref.watch(mutationQueueProvider),
  );
});

final timelineRepositoryProvider = Provider<TimelineRepository>((ref) {
  return TimelineRepository(
    db: ref.watch(appDatabaseProvider),
    hive: ref.watch(hiveStorageProvider),
  );
});

final notificationRepositoryProvider = Provider<NotificationRepository>((ref) {
  return NotificationRepository(
    db: ref.watch(appDatabaseProvider),
    remote: ref.watch(notificationRemoteProvider),
  );
});

final inventoryRemoteProvider = Provider<InventoryRemote>((ref) {
  return InventoryRemote(
    api: ref.watch(apiClientProvider),
    config: ref.watch(apiConfigProvider),
  );
});

final notificationRemoteProvider = Provider<NotificationRemote>((ref) {
  return NotificationRemote(
    api: ref.watch(apiClientProvider),
    config: ref.watch(apiConfigProvider),
  );
});

final projectRemoteProvider = Provider<ProjectRemote>((ref) {
  return ProjectRemote(
    api: ref.watch(apiClientProvider),
    config: ref.watch(apiConfigProvider),
  );
});

final farmerRemoteProvider = Provider<FarmerRemote>((ref) {
  return FarmerRemote(
    api: ref.watch(apiClientProvider),
    config: ref.watch(apiConfigProvider),
  );
});

final syncStatusProvider = FutureProvider<SyncStatusSummary>((ref) async {
  return ref.watch(syncOrchestratorProvider).buildStatusSummary();
});
