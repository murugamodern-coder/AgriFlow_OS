# Copyright (c) 2026, Murugan and contributors
"""Phase 15 — Session auth for mobile E2E (Frappe session + permissions manifest)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils.password import check_password

from agriflow.api.v1.permissions import get_allowed_blocks
from agriflow.api.v1.response import fail, parse_data, success


def _permissions_manifest() -> dict:
	roles = list(frappe.get_roles())
	blocks = get_allowed_blocks()
	block_list = sorted(blocks) if blocks is not None else []
	districts = frappe.get_all(
		"User Permission",
		filters={"user": frappe.session.user, "allow": "District"},
		pluck="for_value",
	)
	return {
		"roles": roles,
		"blocks": block_list,
		"districts": sorted(set(districts or [])),
	}


def _user_payload() -> dict:
	return {
		"name": frappe.session.user,
		"full_name": frappe.utils.get_fullname(frappe.session.user),
		"email": frappe.db.get_value("User", frappe.session.user, "email"),
	}


def _establish_session(username: str, password: str) -> str:
	"""HTTP login via LoginManager; bench execute falls back to set_user + sid hash."""
	if not check_password(username, password):
		raise frappe.AuthenticationError(_("Invalid login credentials"))

	if getattr(frappe.local, "request", None):
		from frappe.auth import LoginManager

		login_manager = LoginManager()
		login_manager.authenticate(user=username, pwd=password)
		login_manager.post_login()
		return frappe.session.sid

	frappe.set_user(username)
	return frappe.generate_hash(length=20)


@frappe.whitelist(allow_guest=True)
def login(data=None):
	try:
		payload = parse_data(data)
		username = (payload.get("username") or payload.get("usr") or "").strip()
		password = payload.get("password") or payload.get("pwd") or ""
		if not username or not password:
			return fail("VAL_REQUIRED_FIELD", _("username and password required"), http_status=400)

		sid = _establish_session(username, password)
		return success(
			{
				"access_token": sid,
				"refresh_token": sid,
				"expires_in": 3600,
				"token_type": "session",
				"user": _user_payload(),
				"permissions": _permissions_manifest(),
			}
		)
	except frappe.AuthenticationError:
		return fail("AUTH_INVALID_CREDENTIALS", _("Invalid login credentials"), http_status=401)
	except Exception as exc:
		frappe.log_error(title="auth.login")
		return fail("SRV_INTERNAL", str(exc), http_status=500)


@frappe.whitelist()
def refresh(data=None):
	try:
		if frappe.session.user in ("Guest", ""):
			return fail("AUTH_TOKEN_INVALID", _("Not logged in"), http_status=401)
		return success(
			{
				"access_token": frappe.session.sid,
				"refresh_token": frappe.session.sid,
				"expires_in": 3600,
				"token_type": "session",
			}
		)
	except Exception as exc:
		return fail("AUTH_TOKEN_INVALID", str(exc), http_status=401)


@frappe.whitelist()
def logout(data=None):
	try:
		from frappe.sessions import Session

		sid = frappe.session.sid
		if sid:
			Session(sid).delete()
		frappe.local.login_manager.logout()
		return success({"logged_out": True})
	except Exception:
		return success({"logged_out": True})


@frappe.whitelist()
def permissions(data=None):
	try:
		if frappe.session.user in ("Guest", ""):
			return fail("AUTH_TOKEN_INVALID", _("Not logged in"), http_status=401)
		return success({"permissions": _permissions_manifest(), "user": _user_payload()})
	except Exception as exc:
		return fail("AUTH_TOKEN_INVALID", str(exc), http_status=401)
