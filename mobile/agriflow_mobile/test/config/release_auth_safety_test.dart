import 'package:agriflow_mobile/core/config/env.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('DEV_AUTH_STUB is false when not in debug', () {
    debugDefaultTargetPlatformOverride = null;
    expect(Env.devAuthStubEnabled, isFalse);
  });
}
