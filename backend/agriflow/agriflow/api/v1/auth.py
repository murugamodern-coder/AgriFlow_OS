# Copyright (c) 2026, Murugan and contributors
"""Phase 16 auth — JWT pair + session fallback + refresh rotation."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils.password import check_password

from agriflow.api.v1.auth_jwt import issue_token_pair, revoke_refresh, rotate_refresh
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


def _session_login(username: str, password: str) -> str:
    if getattr(frappe.local, "request", None):
        from frappe.auth import LoginManager

        lm = LoginManager()
        lm.authenticate(user=username, pwd=password)
        lm.post_login()
        return frappe.session.sid
    frappe.set_user(username)
    return frappe.generate_hash(length=20)


@frappe.whitelist(allow_guest=True)
def login(**kwargs):
    """Mobile login endpoint - simplified."""
    try:
        # Get payload from request body
        if frappe.request and getattr(frappe.request, "data", None):
            try:
                import json

                payload = json.loads(frappe.request.data)
            except (ValueError, TypeError):
                payload = dict(frappe.form_dict) if frappe.form_dict else kwargs
        else:
            payload = kwargs

        # Extract credentials
        username = (payload.get("username") or payload.get("usr") or "").strip()
        password = payload.get("password") or payload.get("pwd") or ""

        if not username or not password:
            return fail("VAL_REQUIRED_FIELD", _("username and password required"), http_status=400)

        if not check_password(username, password):
            return fail("AUTH_INVALID_CREDENTIALS", _("Invalid login credentials"), http_status=401)

        # Issue tokens
        frappe.set_user(username)
        tokens = issue_token_pair(username)

        return success({
            **tokens,
            "user": _user_payload(),
            "permissions": _permissions_manifest(),
        })

    except frappe.AuthenticationError:
        return fail("AUTH_INVALID_CREDENTIALS", _("Invalid login credentials"), http_status=401)
    except Exception as exc:
        frappe.log_error(title="auth.login", message=str(exc))
        return fail("SRV_INTERNAL", str(exc), http_status=500)


@frappe.whitelist(allow_guest=True)
def refresh(data=None):
    try:
        payload = parse_data(data)
        refresh_token = payload.get("refresh_token") or ""
        if not refresh_token:
            return fail("AUTH_TOKEN_INVALID", _("refresh_token required"), http_status=401)
        if frappe.conf.get("agriflow_auth_mode", "jwt") == "jwt":
            tokens = rotate_refresh(refresh_token)
            return success(tokens)
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
    except frappe.AuthenticationError:
        return fail("AUTH_REFRESH_REUSED", _("Refresh token invalid or reused"), http_status=401)
    except Exception as exc:
        return fail("AUTH_TOKEN_INVALID", str(exc), http_status=401)


@frappe.whitelist()
def logout(data=None):
    try:
        payload = parse_data(data) or {}
        if payload.get("refresh_token"):
            revoke_refresh(payload["refresh_token"])
        if frappe.conf.get("agriflow_auth_mode", "jwt") != "jwt":
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
        from agriflow.api.v1.permissions import ensure_authenticated

        ensure_authenticated()
        return success({"permissions": _permissions_manifest(), "user": _user_payload()})
    except frappe.AuthenticationError as exc:
        return fail("AUTH_TOKEN_INVALID", str(exc), http_status=401)
