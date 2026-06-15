import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:agriflow_mobile/core/providers/core_providers.dart';
import '../data/profit_api.dart';

final profitApiProvider = Provider<ProfitApi>((ref) {
  final client = ref.watch(apiClientProvider);
  final config = ref.watch(apiConfigProvider);
  return ProfitApi(client, config);
});

final dashboardSummaryProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final api = ref.watch(profitApiProvider);
  return api.dashboardSummary();
});

final workflowFunnelProvider = FutureProvider.autoDispose<List<dynamic>>((ref) async {
  final api = ref.watch(profitApiProvider);
  return api.workflowFunnel();
});

final schemePerformanceProvider = FutureProvider.autoDispose<List<dynamic>>((ref) async {
  final api = ref.watch(profitApiProvider);
  return api.schemePerformance();
});