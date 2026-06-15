import 'package:agriflow_mobile/core/network/api_client.dart';
import 'package:agriflow_mobile/core/network/api_config.dart';

class ProfitApi {
  final ApiClient _client;
  final ApiConfig _config;
  
  ProfitApi(this._client, this._config);
  
  Future<Map<String, dynamic>> dashboardSummary() async {
    final result = await _client.postMethod(
      _config.methodUrl('agriflow.api.v1.profit.dashboard_summary'),
      data: {},
    );
    if (result.ok && result.data != null) {
      return result.data as Map<String, dynamic>;
    }
    return {};
  }
  
  Future<Map<String, dynamic>> dailySalesSummary({String? fromDate, String? toDate}) async {
    final result = await _client.postMethod(
      _config.methodUrl('agriflow.api.v1.profit.daily_sales_summary'),
      data: {
        if (fromDate != null) 'from_date': fromDate,
        if (toDate != null) 'to_date': toDate,
      },
    );
    if (result.ok && result.data != null) {
      return result.data as Map<String, dynamic>;
    }
    return {};
  }
  
  Future<List<dynamic>> workflowFunnel() async {
    final result = await _client.postMethod(
      _config.methodUrl('agriflow.api.v1.profit.workflow_funnel'),
      data: {},
    );
    if (result.ok && result.data != null) {
      final data = result.data as Map<String, dynamic>;
      return data['stages'] as List<dynamic>? ?? [];
    }
    return [];
  }
  
  Future<List<dynamic>> schemePerformance() async {
    final result = await _client.postMethod(
      _config.methodUrl('agriflow.api.v1.profit.scheme_performance'),
      data: {},
    );
    if (result.ok && result.data != null) {
      final data = result.data as Map<String, dynamic>;
      return data['schemes'] as List<dynamic>? ?? [];
    }
    return [];
  }
}