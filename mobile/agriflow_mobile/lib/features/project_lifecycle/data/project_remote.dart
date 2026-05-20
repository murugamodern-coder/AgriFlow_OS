import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';
import 'package:uuid/uuid.dart';

class ProjectRemote {
  ProjectRemote({required ApiClient api, required ApiConfig config})
      : _api = api,
        _config = config;

  final ApiClient _api;
  final ApiConfig _config;
  final _uuid = const Uuid();

  Future<Map<String, dynamic>> fetchTimeline(String projectName) async {
    final envelope = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl('agriflow.api.v1.project.timeline'),
      data: {'name': projectName},
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    return envelope.data!;
  }

  Future<Map<String, dynamic>> transition({
    required String projectName,
    required String targetStage,
    required int docVersion,
    String? notes,
  }) async {
    final envelope = await _api.postMethod<Map<String, dynamic>>(
      methodUrl: _config.methodUrl('agriflow.api.v1.project.transition'),
      data: {
        'name': projectName,
        'target_stage': targetStage,
        'doc_version': docVersion,
        'client_id': _uuid.v4(),
        if (notes != null && notes.isNotEmpty) 'notes': notes,
      },
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    return envelope.data!;
  }
}
