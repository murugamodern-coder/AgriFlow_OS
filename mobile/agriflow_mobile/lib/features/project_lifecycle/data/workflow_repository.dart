import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';
import 'package:agriflow_mobile/features/project_lifecycle/domain/models/workflow_state.dart';

class WorkflowRepository {
  WorkflowRepository({required ApiClient api, required ApiConfig config})
      : _api = api,
        _config = config;

  final ApiClient _api;
  final ApiConfig _config;

  Future<WorkflowStatus> getAvailableActions(String projectName) async {
    final envelope = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl('agriflow.api.v1.workflow.get_available_actions'),
      data: {'project_name': projectName},
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    return WorkflowStatus.fromJson(envelope.data!);
  }

  Future<Map<String, dynamic>> applyAction(String projectName, String action) async {
    final envelope = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl('agriflow.api.v1.workflow.apply_workflow_action'),
      data: {
        'project_name': projectName,
        'action': action,
      },
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    return envelope.data!;
  }
}
