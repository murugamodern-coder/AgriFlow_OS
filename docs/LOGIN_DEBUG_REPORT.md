# Login Debug Report — Round 2

## Status: 🟡 PARTIAL

## Diagnostic Findings
| Step | Result |
|------|--------|
| 1. Backend ping | ✅ pong |
| 2. Login with username/password | 500 error; response body: {"exception":"json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)","exc_type":"JSONDecodeError","exc":"[\"Traceback (most recent call last):\\n  File \\\"apps/frappe/frappe/app.py\\\", line 105, in application\\n    init_request(request)\\n    ~~~~~~~~~~~~^^^^^^^^^\\n  File \\\"apps/frappe/frappe/app.py\\\", line 203, in init_request\\n    make_form_dict(request)\\    ~~~~~~~~~~~~~~^^^^^^^^^\\n  File \\\"apps/frappe/frappe/app.py\\\", line 307, in make_form_dict\\    args = json.loads(request_data)\\n  File \\\"/usr/lib/python3.14/json/__init__.py\\\", line 352, in loads\\    return _default_decoder.decode(s)\\           ~~~~~~~~~~~~~~~~~~~~~~~^^^\\n  File \\\"/usr/lib/python3.14/json/decoder.py\\\", line 345, in decode\\    obj, end = self.raw_decode(s, idx=_w(s, 0).end())\\               ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^\\n  File \\\"/usr/lib/python3.14/json/decoder.py\\\", line 363, in raw_decode\\    raise JSONDecodeError(\\\"Expecting value\\\", s, err.value) from None\\njson.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)\\n\"]} |
| 3. Login with usr/pwd | Same as step 2 (JSONDecodeError) |
| 4. Verbose curl | 500 INTERNAL SERVER ERROR; Werkzeug stacktrace shows JSONDecodeError in make_form_dict; request Content-Type was `application/json` but request body parsed as invalid JSON. |
| 5. Backend logs | [frappe.log excerpts] show repeated `Form Dict: {}` at corresponding times (see file). No auth.py debug prints observed (handler not reached). |
| 6. Password reset | ✅ `bench --site dev.agriflow.local set-admin-password admin123` completed (exit 0) |
| 7. Mobile auth code | File: docs refer to [mobile/agriflow_mobile/lib/features/auth/data/auth_repository.dart](mobile/agriflow_mobile/lib/features/auth/data/auth_repository.dart) — calls `ApiClient.postMethod` which posts `data: {'data': {...}}` via Dio. ApiClient expects server envelope `ok/data/error` and unwraps `message` if present. |

## Root Cause
Requests with `Content-Type: application/json` are being received with invalid or mangled request bodies, causing Frappe's `make_form_dict` to raise a JSONDecodeError before the auth handler runs. This results in a 500 from the server (seen in curl tests) or an unparseable response body on the client, which the mobile app normalizes to an empty envelope and throws `ApiFailure(null, null, 200, null, null)`.

## Fix Applied
- File changed: backend/agriflow/agriflow/api/v1/auth.py
- Change: removed noisy debug `print()` statements and hardened parsing when `frappe.form_dict['data']` is already a dict.

Before (snippet):
```py
try:
    print("AAAAAAAA LOGIN FILE LOADED")
except Exception:
    pass
```
After (snippet):
```py
try:
    pass
except Exception:
    pass
```

Also adjusted parsing to avoid json.loads on already-parsed dicts and to avoid printing extraction errors to stdout.

## Verification
- curl login → previously returned 500 with JSONDecodeError; backend prints removed (handler still not reached) — further client-side request formation needs verification. ✅ password reset succeeded
- Mobile login → not yet fully verified end-to-end; server-side parsing issue needs fixing or client request normalization to ensure valid JSON body is sent. ⚠️
- Farmer list / Sync APIs → not tested post-fix.

## Files Changed
- backend/agriflow/agriflow/api/v1/auth.py — removed debug prints and made minor parsing hardening.


---

Next steps:
- Reproduce a clean POST from a POSIX shell (inside WSL) that sends a valid JSON body and confirm `make_form_dict` parses it without error.
- If mobile requests are malformed, inspect Dio request headers and ensure `Content-Type: application/json` with raw JSON body is sent (no shell/PowerShell quoting issues on dev test scripts).
- If server still rejects valid JSON, consider adding a small try/except around `json.loads(request_data)` in `frappe/app.py:make_form_dict` to fallback to form parsing when JSON decoding fails (framework change).

