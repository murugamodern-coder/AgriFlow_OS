import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/service_api.dart';
import '../domain/service_visit_model.dart';

/// Singleton provider for the Service API layer.
final serviceApiProvider = Provider<ServiceApi>((ref) {
  final api = ref.watch(apiClientProvider);
  final config = ref.watch(apiConfigProvider);
  return ServiceApi(api: api, config: config);
});

/// FutureProvider for upcoming service visits (next 90 days).
final upcomingVisitsProvider =
    FutureProvider.autoDispose<List<ServiceVisit>>((ref) async {
  final api = ref.watch(serviceApiProvider);
  return api.listUpcomingVisits(daysAhead: 90);
});