import os

# Database configuration
DATABASE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "recipes.db"
)

# API configuration
API_TITLE = "Mama Rezepte API"
API_VERSION = "1.0.0"

# CORS configuration
CORS_ORIGINS = ["*"]  # In production, replace with specific origins
