import 'dart:convert';

import 'package:agriflow_mobile/core/database/app_database.dart';

/// Builds canonical sync.push operation objects from queue rows.
class SyncOperationBuilder {
  static List<Map<String, dynamic>> fromQueueRows(List<SyncQueueRow> rows) {
    return rows.map(_fromRow).toList();
  }

  static Map<String, dynamic> _fromRow(SyncQueueRow row) {
    final decoded = jsonDecode(row.payloadJson) as Map<String, dynamic>;
    final payload = decoded['payload'] is Map
        ? Map<String, dynamic>.from(decoded['payload'] as Map)
        : decoded;

    return {
      'client_mutation_id': row.clientMutationId,
      'entity': row.entity,
      'op_type': row.opType,
      if (decoded['client_id'] != null) 'client_id': decoded['client_id'],
      if (decoded['doc_version'] != null) 'doc_version': decoded['doc_version'],
      'payload': payload,
      if (row.farmerProject != null) 'farmer_project': row.farmerProject,
    };
  }
}
