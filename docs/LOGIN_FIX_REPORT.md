# Login Fix Report

## Status: 🟡 PARTIAL

## Root Cause
The mobile `ApiClient` assumed the backend returned a top-level API envelope. The custom Agriflow auth endpoint returns the envelope nested under a top-level `message` field, so `ApiClient._normalizeBody` failed to extract the actual response body.

## Fix Applied
- `mobile/agriflow_mobile/lib/core/network/api_client.dart`
  - Added `dart:convert` support for parsing raw JSON string responses.
  - Unwrapped `raw['message']` when the backend response envelope is nested under `message`.

## Test Results
- curl login: 200 ✅
- Custom auth endpoint response inspected: nested `message` envelope ✅
- `flutter analyze mobile/agriflow_mobile/lib/core/network/api_client.dart`: 0 issues ✅
- Mobile login: pending app-level verification after hot restart 🔧
- Dashboard loads: pending user verification 🔧
- Farmer list: pending user verification 🔧
- Sync API: pending user verification 🔧

## Files Changed
- `mobile/agriflow_mobile/lib/core/network/api_client.dart`
- `docs/LOGIN_FIX_REPORT.md`

## Commit
fix(auth): login response parsing for ERPNext-enabled backend
