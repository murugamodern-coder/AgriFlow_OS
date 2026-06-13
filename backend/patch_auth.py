from pathlib import Path

path = Path('/home/muruga/workspace/frappe-bench/apps/agriflow/agriflow/api/v1/auth_jwt.py')
text = path.read_text()
old = '''def validate_auth_via_header() -> None:
        authorization = frappe.get_request_header("Authorization", "") or frappe.get_request_header("authorization", "")
        if not authorization:
                return
        if authorization.split(" ", 1)[0].lower() != "bearer":
                return
        resolve_bearer(authorization)'''
new = '''def validate_auth_via_header() -> None:
        """Validate JWT bearer token from Authorization header."""
        auth_header = frappe.get_request_header("Authorization", "") or frappe.get_request_header("authorization", "")
        if not auth_header:
                return
        if not auth_header.lower().startswith("bearer "):
                return

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
                return

        try:
                payload = verify_token(token, expected_kind="access")
                user = payload.get("user")
                if user and frappe.db.exists("User", user):
                        frappe.set_user(user)
                        try:
                                frappe.local.login_manager = frappe.auth.LoginManager()
                                frappe.local.login_manager.user = user
                                frappe.local.login_manager.post_login()
                        except Exception as login_exc:
                                frappe.log_error(title="JWT validate_auth_via_header login_manager", message=str(login_exc))
        except Exception as e:
                frappe.log_error(title="JWT validate_auth_via_header", message=str(e))
                return'''
if old not in text:
    raise SystemExit('Old block not found')
path.write_text(text.replace(old, new, 1))
print('patched')
