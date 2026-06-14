import 'package:agriflow_mobile/core/providers/core_providers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/officer_api.dart';
import '../domain/officer_model.dart';

/// Singleton provider for the Officer API layer.
final officerApiProvider = Provider<OfficerApi>((ref) {
  final client = ref.watch(apiClientProvider);
  final config = ref.watch(apiConfigProvider);
  return OfficerApi(api: client, config: config);
});

/// FutureProvider for officer workload list.
final officersListProvider =
    FutureProvider.autoDispose<List<GovernmentOfficer>>((ref) async {
  final api = ref.watch(officerApiProvider);
  return api.officerWorkload();
});