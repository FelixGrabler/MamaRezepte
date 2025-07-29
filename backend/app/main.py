from fastapi import FastAPI
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

# Include routers
app.include_router(recipes.router)
app.include_router(tags.router)


@app.get("/")
async def root():
    return {"message": "Mama Rezepte API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
