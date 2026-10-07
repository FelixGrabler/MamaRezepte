import os
from pathlib import Path

API_TITLE = "Mama Rezepte API"
API_VERSION = "2.0.0"
DATABASE_URL = os.getenv("DATABASE_URL", "")
DATABASE_PASSWORD_FILE = os.getenv("DATABASE_PASSWORD_FILE", "/run/secrets/postgres_password")
LEGACY_DATABASE = Path(os.getenv("LEGACY_DATABASE", "/app/data/recipes.db"))
LEGACY_IMAGES = Path(os.getenv("LEGACY_IMAGES", "/app/legacy-images"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://shared-auth:8000")
SITE_ORIGIN = os.getenv("SITE_ORIGIN", "https://rezepte.grabler.me").rstrip("/")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"
COOKIE_NAME = "mamarezepte_session"
MAX_IMAGE_BYTES = 20 * 1024 * 1024
MAX_IMAGE_EDGE = 1600
