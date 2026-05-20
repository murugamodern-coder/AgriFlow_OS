import 'package:agriflow_mobile/core/errors/failure.dart';
import 'package:agriflow_mobile/core/observability/sync_failure_category.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('categorizes offline and auth', () {
    expect(
      SyncFailureCategory.categorize(const NetworkFailure(code: 'OFFLINE')),
      'network',
    );
    expect(
      SyncFailureCategory.categorize(Exception('jwt expired'), code: 'AUTH_EXPIRED'),
      'auth',
    );
  });
}
