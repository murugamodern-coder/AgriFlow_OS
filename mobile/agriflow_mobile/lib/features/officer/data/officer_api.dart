import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';
import '../domain/officer_model.dart';

/// Remote data layer for Officer Network APIs (M8).
class OfficerApi {
  OfficerApi({required ApiClient api, required ApiConfig config})
      : _api = api,
        _config = config;

  final ApiClient _api;
  final ApiConfig _config;

  /// List active officers, optionally filtered.
  Future<List<GovernmentOfficer>> listOfficers({
    String? district,
    String? designation,
  }) async {
    final envelope = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl('agriflow.api.v1.officer.list_officers'),
      data: {
        if (district != null) 'district': district,
        if (designation != null) 'designation': designation,
      },
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    final data = envelope.data!;
    return (data['officers'] as List<dynamic>? ?? [])
        .map((o) => GovernmentOfficer.fromJson(Map<String, dynamic>.from(o as Map)))
        .toList();
  }

  /// Get officer workload (active projects per officer).
  Future<List<GovernmentOfficer>> officerWorkload() async {
    final envelope = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl('agriflow.api.v1.officer.officer_workload'),
      data: <String, dynamic>{},
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    final data = envelope.data!;
    return (data['workload'] as List<dynamic>? ?? [])
        .map((o) => GovernmentOfficer.fromJson(Map<String, dynamic>.from(o as Map)))
        .toList();
  }
}