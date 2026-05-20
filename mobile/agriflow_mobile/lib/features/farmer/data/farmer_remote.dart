import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';
import 'package:agriflow_mobile/features/farmer/domain/farmer_summary.dart';

class FarmerRemote {
  FarmerRemote({required ApiClient api, required ApiConfig config})
      : _api = api,
        _config = config;

  final ApiClient _api;
  final ApiConfig _config;

  Future<List<FarmerSummary>> list({int limit = 50}) async {
    final envelope = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl('agriflow.api.v1.farmer.list'),
      data: {'limit': limit, 'is_active': true},
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    final items = envelope.data!['items'] as List? ?? [];
    return items
        .map((e) => FarmerSummary.fromJson(Map<String, dynamic>.from(e as Map)))
        .toList();
  }
}
