import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';
import 'package:agriflow_mobile/features/farmer/domain/geo_option.dart';

class GeographyRemote {
  GeographyRemote({required ApiClient api, required ApiConfig config})
      : _api = api,
        _config = config;

  final ApiClient _api;
  final ApiConfig _config;

  Future<List<GeoOption>> getStates() async {
    return _fetchList(
      method: 'agriflow.api.v1.geography.get_states',
      labelKey: 'state_name',
    );
  }

  Future<List<GeoOption>> getDistricts(String state) async {
    return _fetchList(
      method: 'agriflow.api.v1.geography.get_districts',
      data: {'state': state},
      labelKey: 'district_name',
    );
  }

  Future<List<GeoOption>> getBlocks(String district) async {
    return _fetchList(
      method: 'agriflow.api.v1.geography.get_blocks',
      data: {'district': district},
      labelKey: 'block_name',
    );
  }

  Future<List<GeoOption>> searchVillages({
    required String block,
    required String search,
    int limit = 50,
  }) async {
    if (search.trim().length < 2) return const [];
    return _fetchList(
      method: 'agriflow.api.v1.geography.get_villages',
      data: {'block': block, 'search': search.trim(), 'limit': limit},
      labelKey: 'village_name',
    );
  }

  Future<List<GeoOption>> getClusters({String? block}) async {
    return _fetchList(
      method: 'agriflow.api.v1.geography.get_clusters',
      data: block == null ? const {} : {'block': block},
      labelKey: 'cluster_name',
    );
  }

  Future<List<GeoOption>> getOfficers() async {
    return _fetchList(
      method: 'agriflow.api.v1.geography.get_officers',
      labelKey: 'officer_name',
    );
  }

  Future<List<GeoOption>> _fetchList({
    required String method,
    required String labelKey,
    Map<String, dynamic> data = const {},
  }) async {
    final envelope = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl(method),
      data: data,
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    final items = envelope.data!['items'] as List? ?? [];
    return items
        .map(
          (e) => GeoOption.fromJson(
            Map<String, dynamic>.from(e as Map),
            labelKey: labelKey,
          ),
        )
        .toList();
  }
}
