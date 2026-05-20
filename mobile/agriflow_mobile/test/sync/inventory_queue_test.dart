import 'package:agriflow_mobile/core/database/app_database.dart';
import 'package:agriflow_mobile/core/sync/inventory_queue.dart';
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('inventory queue persists pending consume', () async {
    final db = AppDatabase.forTesting(NativeDatabase.memory());
    await db.ensureSchema();
    final queue = InventoryQueue(db);
    final id = await queue.enqueueConsume(
      allocation: 'ALLOC-TEST',
      qty: 1,
      docVersion: 1,
    );
    expect(id.length, 28);
    final pending = await db.pendingInventoryOps();
    expect(pending.length, 1);
    expect(pending.first.status, 'pending');
    expect(pending.first.opType, 'consume');
  });
}
