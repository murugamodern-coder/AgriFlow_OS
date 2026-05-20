# Headless sync — Android setup

Run after `flutter create .` in `agriflow_mobile`.

## 1. Dependencies

Already in `pubspec.yaml`: `workmanager`.

## 2. `android/app/src/main/AndroidManifest.xml`

Inside `<application>`:

```xml
<receiver
    android:name="be.tramckrijte.workmanager.BackgroundWorker"
    android:exported="false" />
```

## 3. Minimum SDK

`android/app/build.gradle`: `minSdkVersion 23` or higher.

## 4. ProGuard (release)

```
-keep class be.tramckrijte.workmanager.** { *; }
```

## 5. Verify

```bash
flutter run --dart-define=API_BASE_URL=https://staging.example \
  --dart-define=APP_VERSION=0.19.0
```

Log in, background the app 30+ minutes, check server **Operational Log** for `headless_sync` events.

See also [BATTERY_OPTIMIZATION.md](../../../docs/BATTERY_OPTIMIZATION.md).
