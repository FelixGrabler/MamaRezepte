from fastapi import APIRouter, Depends, HTTPException, Response

from app.core import config, database
from app.core.auth import hub_request, optional_user
from app.models.schemas import Credentials

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(credentials: Credentials, response: Response):
    result = hub_request("POST", "/api/auth/login", json=credentials.model_dump())
    if result.status_code in (400, 401, 403):
        raise HTTPException(401, "Benutzername oder Passwort ist falsch.")
    if result.status_code != 200:
        raise HTTPException(503, "Die Anmeldung ist gerade nicht erreichbar.")
    token = result.json()["access_token"]
    profile = hub_request("GET", "/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    if profile.status_code != 200:
        raise HTTPException(503, "Die Anmeldung ist gerade nicht erreichbar.")
    database.bind_legacy_owner(profile.json())
    response.set_cookie(config.COOKIE_NAME, token, max_age=7 * 24 * 3600,
                        httponly=True, secure=config.COOKIE_SECURE, samesite="lax", path="/api")
    return profile.json()


@router.get("/me")
def me(user=Depends(optional_user)):
    return user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(config.COOKIE_NAME, path="/api", secure=config.COOKIE_SECURE,
                           httponly=True, samesite="lax")
    return {"ok": True}
