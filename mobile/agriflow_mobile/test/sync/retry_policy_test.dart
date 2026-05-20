import 'package:agriflow_mobile/core/sync/retry_policy.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('retry policy backs off and succeeds on third attempt', () async {
    final policy = RetryPolicy(maxAttempts: 3, baseDelayMs: 10, maxDelayMs: 50);
    var calls = 0;
    final result = await policy.run(() async {
      calls++;
      if (calls < 3) throw Exception('connection timeout');
      return 'ok';
    });
    expect(result, 'ok');
    expect(calls, 3);
  });
}
