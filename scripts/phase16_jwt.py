# Copyright (c) 2026, Murugan and contributors
"""HMAC JWT-style tokens for mobile (Phase 16) — no external PyJWT dependency."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

import frappe

ACCESS_TTL = 900  # 15 min
REFRESH_TTL = 604800  # 7 days
REFRESH_CACHE_PREFIX = "agriflow:refresh:"


def _secret() -> str:
	return (
		frappe.conf.get("agriflow_jwt_secret")
		or frappe.local.conf.get("encryption_key")
		or frappe.local.conf.get("secret")
		or "agriflow-dev-secret-change-me"
	)


def _b64url_encode(raw: bytes) -> str:
	return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _b64url_decode(data: str) -> bytes:
	padding = "=" * (-len(data) % 4)
	return base64.urlsafe_b64decode(data + padding)


def sign_token(payload: dict[str, Any], ttl_sec: int, *, kind: str = "access") -> str:
	body_obj = {
		**payload,
		"kind": kind,
		"exp": int(time.time()) + ttl_sec,
		"iat": int(time.time()),
	}
	body = _b64url_encode(json.dumps(body_obj, separators=(",", ":")).encode())
	sig = hmac.new(_secret().encode(), body.encode(), hashlib.sha256).hexdigest()
	return f"{body}.{sig}"


def verify_token(token: str, *, expected_kind: str | None = None) -> dict[str, Any]:
	if not token or "." not in token:
		raise frappe.AuthenticationError("Invalid token")
	body, sig = token.rsplit(".", 1)
	expected_sig = hmac.new(_secret().encode(), body.encode(), hashlib.sha256).hexdigest()
	if not hmac.compare_digest(sig, expected_sig):
		raise frappe.AuthenticationError("Invalid token signature")
	payload = json.loads(_b64url_decode(body))
	if int(payload.get("exp") or 0) < int(time.time()):
		raise frappe.AuthenticationError("Token expired")
	if expected_kind and payload.get("kind") != expected_kind:
		raise frappe.AuthenticationError("Invalid token type")
	return payload


def issue_token_pair(user: str) -> dict[str, Any]:
	refresh_id = frappe.generate_hash(length=24)
	refresh_token = sign_token({"user": user, "rid": refresh_id}, REFRESH_TTL, kind="refresh")
	frappe.cache().set_value(
		f"{REFRESH_CACHE_PREFIX}{refresh_id}",
		{"user": user, "used": False},
		expires_in_sec=REFRESH_TTL,
	)
	access_token = sign_token({"user": user}, ACCESS_TTL, kind="access")
	return {
		"access_token": access_token,
		"refresh_token": refresh_token,
		"expires_in": ACCESS_TTL,
		"token_type": "Bearer",
	}


def rotate_refresh(refresh_token: str) -> dict[str, Any]:
	payload = verify_token(refresh_token, expected_kind="refresh")
	rid = payload.get("rid")
	user = payload.get("user")
	if not rid or not user:
		raise frappe.AuthenticationError("Invalid refresh token")
	cache_key = f"{REFRESH_CACHE_PREFIX}{rid}"
	stored = frappe.cache().get_value(cache_key)
	if not stored or stored.get("used"):
		raise frappe.AuthenticationError("Refresh token reused or revoked")
	frappe.cache().set_value(cache_key, {"user": user, "used": True}, expires_in_sec=REFRESH_TTL)
	return issue_token_pair(user)


def resolve_bearer(authorization: str | None) -> str | None:
	if not authorization:
		return None
	parts = authorization.split(" ", 1)
	if len(parts) != 2 or parts[0].lower() != "bearer":
		return None
	payload = verify_token(parts[1].strip(), expected_kind="access")
	user = payload.get("user")
	if not user:
		raise frappe.AuthenticationError("Invalid access token")
	frappe.set_user(user)
	return user


def revoke_refresh(refresh_token: str) -> None:
	try:
		payload = verify_token(refresh_token, expected_kind="refresh")
		rid = payload.get("rid")
		if rid:
			frappe.cache().delete_value(f"{REFRESH_CACHE_PREFIX}{rid}")
	except Exception:
		pass
