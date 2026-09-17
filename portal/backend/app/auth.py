from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException
from jwt import PyJWKClient

from .config import get_settings
from .schemas import Actor

_jwks_clients: dict[str, PyJWKClient] = {}


def get_actor(
    authorization: Annotated[str | None, Header()] = None,
    x_portal_actor: Annotated[str | None, Header()] = None,
) -> Actor:
    settings = get_settings()
    mode = (settings.auth_mode or "dev_bypass").strip().lower()
    if mode != "entra":
        name = (x_portal_actor or "").strip() or "Local Developer"
        return Actor(name=name, oid="dev-bypass", auth_mode="dev_bypass")

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Microsoft Entra ID sign-in is required")
    token = authorization.split(" ", 1)[1].strip()
    if not settings.azure_tenant_id or not settings.azure_client_id:
        raise HTTPException(status_code=500, detail="Entra ID is not configured")
    try:
        claims = _validate_entra_token(token, settings.azure_tenant_id, settings.azure_client_id)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid access token: {exc}") from exc
    name = (
        claims.get("name")
        or claims.get("preferred_username")
        or claims.get("upn")
        or claims.get("oid")
        or "Entra user"
    )
    return Actor(name=str(name), oid=str(claims.get("oid") or ""), auth_mode="entra")


def _validate_entra_token(token: str, tenant_id: str, client_id: str) -> dict:
    issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"
    jwks_url = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
    client = _jwks_clients.get(jwks_url)
    if client is None:
        client = PyJWKClient(jwks_url, cache_jwk_set=True)
        _jwks_clients[jwks_url] = client
    signing_key = client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=client_id,
        issuer=issuer,
        options={"require": ["exp", "iss", "aud"]},
    )
