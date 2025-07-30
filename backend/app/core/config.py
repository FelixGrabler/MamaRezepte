import os

# Database configuration
DATABASE_PATH = "/app/data/recipes.db"

# Ensure the database directory exists
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# API configuration
API_TITLE = "Mama Rezepte API"
API_VERSION = "1.0.0"

# CORS configuration
CORS_ORIGINS = ["*"]
