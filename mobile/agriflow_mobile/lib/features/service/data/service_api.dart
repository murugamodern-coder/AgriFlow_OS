import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';
import '../domain/service_visit_model.dart';

/// Remote data layer for Service Visit APIs (M7).
///
/// Uses ApiClient.postMethod to match existing envelope format.
class ServiceApi {
  ServiceApi({required ApiClient api, required ApiConfig config})
      : _api = api,
        _config = config;

  final ApiClient _api;
  final ApiConfig _config;

  /// List upcoming service visits (next N days).
  Future<List<ServiceVisit>> listUpcomingVisits({
    int daysAhead = 90,
    String? technician,
  }) async {
    final envelope = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl('agriflow.api.v1.service.list_upcoming_visits'),
      data: {
        'days_ahead': daysAhead,
        if (technician != null) 'technician': technician,
      },
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    final data = envelope.data!;
    final visits = (data['visits'] as List<dynamic>? ?? [])
        .map((v) => ServiceVisit.fromJson(Map<String, dynamic>.from(v as Map)))
        .toList();
    return visits;
  }

  /// Complete a visit with checklist data.
  Future<Map<String, dynamic>> completeVisit({
    required String visitName,
    bool? dripPipesIntact,
    bool? drippersClogged,
    bool? filterClean,
    bool? valveWorking,
    bool? pumpMotorOk,
    String? issuesFound,
    String? actionsTaken,
    double? farmerSatisfaction,
    bool? followUpRequired,
    String? followUpDate,
  }) async {
    final envelope = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl('agriflow.api.v1.service.complete_visit'),
      data: {
        'visit_name': visitName,
        if (dripPipesIntact != null) 'drip_pipes_intact': dripPipesIntact ? 1 : 0,
        if (drippersClogged != null) 'drippers_clogged': drippersClogged ? 1 : 0,
        if (filterClean != null) 'filter_clean': filterClean ? 1 : 0,
        if (valveWorking != null) 'valve_working': valveWorking ? 1 : 0,
        if (pumpMotorOk != null) 'pump_motor_ok': pumpMotorOk ? 1 : 0,
        if (issuesFound != null) 'issues_found': issuesFound,
        if (actionsTaken != null) 'actions_taken': actionsTaken,
        if (farmerSatisfaction != null) 'farmer_satisfaction': farmerSatisfaction,
        if (followUpRequired != null) 'follow_up_required': followUpRequired ? 1 : 0,
        if (followUpDate != null) 'follow_up_date': followUpDate,
      },
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    return envelope.data!;
  }

  /// Get farmer service history.
  Future<Map<String, dynamic>> farmerServiceHistory(String farmer) async {
    final envelope = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl('agriflow.api.v1.service.farmer_service_history'),
      data: {'farmer': farmer},
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    return envelope.data!;
  }
}