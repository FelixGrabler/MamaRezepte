from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api import auth, recipes, tags
from app.core import config, database


@asynccontextmanager
async def lifespan(app):
    database.init_database()
    yield


app = FastAPI(title=config.API_TITLE, version=config.API_VERSION, lifespan=lifespan)


@app.middleware("http")
async def protect_requests(request: Request, call_next):
    # Require a matching browser origin for every state change, including login.
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        if request.headers.get("origin") != config.SITE_ORIGIN:
            return JSONResponse({"detail": "Ungültiger Anfrageursprung."}, status_code=403)
    response = await call_next(request)
    if request.url.path.startswith(("/api/", "/recipes", "/tags")):
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Vary"] = "Cookie"
    return response


api = APIRouter(prefix="/api")
api.include_router(auth.router)
api.include_router(recipes.router)
api.include_router(tags.router)
app.include_router(api)
# Legacy read URLs keep access checks; writes use the same authorization rules.
app.include_router(recipes.router, include_in_schema=False)
app.include_router(tags.router, include_in_schema=False)


@app.get("/health")
@app.get("/api/health", include_in_schema=False)
def health():
    with database.engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "healthy"}
