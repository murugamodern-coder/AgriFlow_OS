import 'dart:convert';

import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:uuid/uuid.dart';

/// Queue-only write path — no direct mutation APIs from UI.
class MutationQueue {
  MutationQueue(this._db);

  final AppDatabase _db;
  final _uuid = const Uuid();

  Future<String> enqueueTaskComplete({
    required String taskName,
    required int docVersion,
    String? farmerProject,
    Map<String, dynamic>? extra,
  }) async {
    final clientMutationId = _uuid.v4();
    final payload = {
      'payload': {
        'name': taskName,
        'doc_version': docVersion,
        if (extra != null) ...extra,
      },
    };
    await _db.enqueueMutation(
      clientMutationId: clientMutationId,
      entity: 'task',
      opType: 'complete',
      payloadJson: jsonEncode(payload),
      farmerProject: farmerProject,
    );
    return clientMutationId;
  }

  Future<String> enqueueTimelineNote({
    required String farmerProject,
    required String body,
  }) async {
    final clientMutationId = _uuid.v4();
    final payload = {
      'payload': {
        'farmer_project': farmerProject,
        'body': body,
        'text': body,
      },
    };
    await _db.enqueueMutation(
      clientMutationId: clientMutationId,
      entity: 'timeline',
      opType: 'note',
      payloadJson: jsonEncode(payload),
      farmerProject: farmerProject,
    );
    return clientMutationId;
  }
}
