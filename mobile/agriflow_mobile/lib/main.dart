import 'package:agriflow_mobile/app/bootstrap.dart';
import 'package:agriflow_mobile/core/observability/sentry_bootstrap.dart';

Future<void> main() async {
  await SentryBootstrap.init(bootstrap);
}
