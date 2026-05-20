import 'package:agriflow_mobile/core/config/api_config.dart';
import 'package:agriflow_mobile/core/network/api_client.dart';

class InventoryRemote {
  InventoryRemote({required this.api, required this.config});

  final ApiClient api;
  final ApiConfig config;

  Future<List<Map<String, dynamic>>> listAllocations(String farmerProject) async {
    final envelope = await api.postMethod<Map<String, dynamic>>(
      methodUrl: config.methodUrl('agriflow.api.v1.inventory.allocation_list'),
      data: {'farmer_project': farmerProject, 'active_only': true},
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    final items = envelope.data?['items'] as List? ?? [];
    return items.map((e) => Map<String, dynamic>.from(e as Map)).toList();
  }

  Future<Map<String, dynamic>> consume({
    required String allocation,
    required double qty,
    required int docVersion,
    required String clientId,
    String? batchNo,
  }) async {
    final envelope = await api.postMethod<Map<String, dynamic>>(
      methodUrl: config.methodUrl('agriflow.api.v1.inventory.allocation_consume'),
      data: {
        'allocation': allocation,
        'qty': qty,
        'doc_version': docVersion,
        'client_id': clientId,
        if (batchNo != null) 'batch_no': batchNo,
      },
      parseData: (json) => Map<String, dynamic>.from(json as Map),
    );
    return envelope.data ?? {};
  }
}
