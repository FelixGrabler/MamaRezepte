# Mama Rezepte Backend

A FastAPI backend for the Mama Rezepte recipe management application.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── recipes.py          # Recipe endpoints
│   │   └── tags.py             # Tag endpoints
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration settings
│   │   └── database.py         # Database operations
│   └── models/                 # Pydantic models
│       ├── __init__.py
│       └── schemas.py          # Request/Response models
├── scripts/
│   └── convert_json_to_db.py   # JSON to SQLite conversion script
├── data/                       # Database storage (created at runtime)
├── Dockerfile                  # Production Docker image
├── Dockerfile.dev              # Development Docker image
└── requirements.txt            # Python dependencies
```

## Database Schema

### Tables

- **recipes**: Main recipe information

  - `id` (INTEGER, PK): Unique recipe identifier
  - `title` (TEXT): Recipe name
  - `instructions` (TEXT): Cooking instructions
  - `image_path` (TEXT): Path to recipe image
  - `parent_id` (INTEGER, FK): Reference to parent recipe

- **ingredients**: Recipe ingredients

  - `id` (INTEGER, PK): Unique ingredient identifier
  - `recipe_id` (INTEGER, FK): Reference to recipe
  - `amount` (REAL): Ingredient quantity
  - `unit` (TEXT): Unit of measurement
  - `ingredient` (TEXT): Ingredient name

- **tags**: Recipe tags/categories

  - `id` (INTEGER, PK): Unique tag identifier
  - `name` (TEXT, UNIQUE): Tag name

- **recipe_tags**: Many-to-many relationship between recipes and tags
  - `recipe_id` (INTEGER, FK): Reference to recipe
  - `tag_id` (INTEGER, FK): Reference to tag
  - PRIMARY KEY (recipe_id, tag_id)

## API Endpoints

### Recipes

- `GET /recipes/` - Get all recipes
- `GET /recipes/{recipe_id}` - Get recipe by ID
- `POST /recipes/` - Create new recipe
- `DELETE /recipes/{recipe_id}` - Delete recipe

### Tags

- `GET /tags/` - Get all tags
- `POST /tags/` - Create new tag
- `DELETE /tags/{tag_id}` - Delete tag
- `POST /tags/recipe-tags` - Add tag to recipe
- `DELETE /tags/recipe-tags` - Remove tag from recipe

### General

- `GET /` - API info
- `GET /health` - Health check

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Convert JSON data to SQLite (one time setup)
python scripts/convert_json_to_db.py

# Run the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Using Docker

```bash
# Development
make dev

# Production
make up
```

### Converting JSON Data

The `scripts/convert_json_to_db.py` script converts the existing `recipes.json` file to SQLite database format. It handles:

- Parsing ingredient strings with amounts, units, and names
- Converting Unicode fractions to decimal values
- Creating proper database relationships

## Configuration

Configuration settings are managed in `app/core/config.py`:

- Database path
- API metadata
- CORS settings
