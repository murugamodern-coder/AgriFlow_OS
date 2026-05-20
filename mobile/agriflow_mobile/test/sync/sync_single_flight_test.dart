import 'package:agriflow_mobile/core/sync/sync_single_flight.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('sync lock proof — concurrent syncNow shares single flight', () async {
    final lock = SyncSingleFlight();
    var runs = 0;

    Future<int> work() async {
      runs++;
      await Future<void>.delayed(const Duration(milliseconds: 50));
      return runs;
    }

    final a = lock.execute(work);
    final b = lock.execute(work);
    final results = await Future.wait([a, b]);

    expect(runs, 1);
    expect(results[0], 1);
    expect(results[1], 1);
    expect(identical(a, b), isFalse);
    expect(results[0], results[1]);
  });

  test('sync lock proof — isRunning during flight', () async {
    final lock = SyncSingleFlight();
    final completer = Completer<void>();

    final future = lock.execute(() async {
      expect(lock.isRunning, isTrue);
      await completer.future;
      return true;
    });

    await Future<void>.delayed(Duration.zero);
    expect(lock.isRunning, isTrue);
    completer.complete();
    await future;
    expect(lock.isRunning, isFalse);
  });
}
