from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import recipes, tags
from app.core import database
from app.core.config import API_TITLE, API_VERSION, CORS_ORIGINS

# Initialize the database
database.init_database()

app = FastAPI(title=API_TITLE, version=API_VERSION)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the API under /api for the frontend and keep the legacy routes for
# direct backend access.
api_router = APIRouter(prefix="/api")
api_router.include_router(recipes.router)
api_router.include_router(tags.router)

app.include_router(api_router)
app.include_router(recipes.router, include_in_schema=False)
app.include_router(tags.router, include_in_schema=False)


@app.get("/")
async def root():
    return {"message": "Mama Rezepte API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/health", include_in_schema=False)
async def api_health_check():
    return {"status": "healthy"}
