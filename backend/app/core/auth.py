"""Validate hub accounts without copying its user database or signing secret."""
import httpx
from fastapi import Depends, HTTPException, Request

from . import config


def hub_request(method, path, **kwargs):
    try:
        with httpx.Client(timeout=10) as client:
            response = client.request(method, f"{config.AUTH_SERVICE_URL}{path}", **kwargs)
    except httpx.RequestError as exc:
        raise HTTPException(503, "Die Anmeldung ist gerade nicht erreichbar.") from exc
    if response.status_code >= 500:
        raise HTTPException(503, "Die Anmeldung ist gerade nicht erreichbar.")
    return response


def optional_user(request: Request):
    token = request.cookies.get(config.COOKIE_NAME)
    if not token:
        return None
    response = hub_request("GET", "/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    if response.status_code in (401, 403):
        return None
    if response.status_code != 200:
        raise HTTPException(503, "Die Anmeldung ist gerade nicht erreichbar.")
    user = response.json()
    return user


def required_user(user=Depends(optional_user)):
    if user is None:
        raise HTTPException(401, "Bitte zuerst anmelden.")
    return user
