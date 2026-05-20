import 'package:agriflow_mobile/core/config/env.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('demo mode disables dev auth stub', () {
    expect(Env.demoMode, isTrue);
    expect(Env.devAuthStubEnabled, isFalse);
  });
}
