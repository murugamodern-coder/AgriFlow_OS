import 'package:agriflow_mobile/app/app.dart';
import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';
import 'package:agriflow_mobile/core/network/dio_client.dart';
import 'package:agriflow_mobile/core/network/tracing_interceptor.dart';
import 'package:agriflow_mobile/core/observability/pilot_telemetry_service.dart';
import 'package:agriflow_mobile/core/observability/telemetry.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:agriflow_mobile/core/push/push_service.dart';
import 'package:agriflow_mobile/core/storage/hive_boxes.dart';
import 'package:agriflow_mobile/core/storage/secure_token_store.dart';
import 'package:agriflow_mobile/core/sync/background_sync_coordinator.dart';
import 'package:agriflow_mobile/core/sync/workmanager_registration.dart';
import 'package:agriflow_mobile/core/sync/inventory_queue.dart';
import 'package:agriflow_mobile/core/sync/projection_writer.dart';
import 'package:agriflow_mobile/core/sync/push_result_applier.dart';
import 'package:agriflow_mobile/core/sync/queue_repair.dart';
import 'package:agriflow_mobile/core/sync/sync_orchestrator.dart';
import 'package:agriflow_mobile/core/sync/sync_remote.dart';
import 'package:agriflow_mobile/core/sync/sync_visual_controller.dart';
import 'package:agriflow_mobile/features/sync/sync_connectivity.dart';
import 'package:agriflow_mobile/features/auth/data/auth_repository.dart';
import 'package:agriflow_mobile/features/inventory/data/inventory_remote.dart';
import 'package:agriflow_mobile/features/notifications/data/notification_remote.dart';
import 'package:agriflow_mobile/features/pilot_ops/data/pilot_ops_remote.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

Future<void> bootstrap() async {
  WidgetsFlutterBinding.ensureInitialized();
  Telemetry.init();

  final hive = await HiveStorage.open();
  final db = AppDatabase();
  await db.ensureSchema();
  await QueueRepair(db).reconcile();

  final tokens = SecureTokenStore();
  final config = ApiConfig.fromEnv();
  final tracing = TracingInterceptor();

  final authRepo = AuthRepository(
    api: ApiClient(
      dio: createDio(
        config: config,
        readAccessToken: tokens.readAccessToken,
        tracing: tracing,
      ),
    ),
    config: config,
    tokens: tokens,
    hive: hive,
  );
  final dio = createDio(
    config: config,
    readAccessToken: tokens.readAccessToken,
    onRefresh: authRepo.refreshAccessToken,
    tracing: tracing,
  );
  final api = ApiClient(dio: dio);
  final connectivity = Connectivity();
  final notificationRemote = NotificationRemote(api: api, config: config);
  final inventoryRemote = InventoryRemote(api: api, config: config);
  final inventoryQueue = InventoryQueue(db);
  final pilotRemote = PilotOpsRemote(api: api);
  final pilotTelemetry = PilotTelemetryService(
    remote: pilotRemote,
    db: db,
    hive: hive,
  );
  final syncVisualController = SyncVisualController(
    db: db,
    hive: hive,
    connectivity: connectivity,
  );
  final syncOrchestrator = SyncOrchestrator(
    db: db,
    hive: hive,
    remote: SyncRemote(
      api: api,
      config: config,
      db: db,
      applier: PushResultApplier(db),
    ),
    writer: ProjectionWriter(db, hive),
    notificationRemote: notificationRemote,
    connectivity: connectivity,
    tracing: tracing,
    telemetry: pilotTelemetry,
    inventoryQueue: inventoryQueue,
    inventoryRemote: inventoryRemote,
    visual: syncVisualController,
  );
  BackgroundSyncCoordinator(
    orchestrator: syncOrchestrator,
    connectivity: connectivity,
  ).start();
  await WorkmanagerRegistration.register();

  final pushService = PushService(api: api, telemetry: pilotTelemetry);

  runApp(
    ProviderScope(
      overrides: [
        appDatabaseProvider.overrideWithValue(db),
        hiveStorageProvider.overrideWithValue(hive),
        secureTokenStoreProvider.overrideWithValue(tokens),
        apiConfigProvider.overrideWithValue(config),
        tracingInterceptorProvider.overrideWithValue(tracing),
        dioProvider.overrideWithValue(dio),
        apiClientProvider.overrideWithValue(api),
        connectivityProvider.overrideWithValue(connectivity),
        notificationRemoteProvider.overrideWithValue(notificationRemote),
        inventoryRemoteProvider.overrideWithValue(inventoryRemote),
        inventoryQueueProvider.overrideWithValue(inventoryQueue),
        pilotOpsRemoteProvider.overrideWithValue(pilotRemote),
        pilotTelemetryProvider.overrideWithValue(pilotTelemetry),
        pushServiceProvider.overrideWithValue(pushService),
        authRepositoryProvider.overrideWithValue(
          AuthRepository(api: api, config: config, tokens: tokens, hive: hive),
        ),
        authSessionProvider.overrideWith(
          (ref) => AuthSessionNotifier(ref.watch(authRepositoryProvider)),
        ),
        syncOrchestratorProvider.overrideWithValue(syncOrchestrator),
        syncVisualControllerProvider.overrideWithValue(syncVisualController),
      ],
      child: const AgriFlowApp(),
    ),
  );
}
