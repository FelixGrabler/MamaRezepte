import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import os
from .config import DATABASE_PATH


def init_database():
    """Initialize the database with the required tables."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        # Create recipes table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                instructions TEXT NOT NULL,
                image_path TEXT,
                parent_id INTEGER,
                FOREIGN KEY (parent_id) REFERENCES recipes (id)
            )
        """
        )

        # Create ingredients table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                amount REAL,
                unit TEXT,
                ingredient TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE
            )
        """
        )

        # Create tags table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """
        )

        # Create recipe_tags junction table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recipe_tags (
                recipe_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (recipe_id, tag_id),
                FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            )
        """
        )

        conn.commit()


@contextmanager
def get_db_connection():
    """Get a database connection with context management."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    try:
        yield conn
    finally:
        conn.close()


def get_all_recipes() -> List[Dict[str, Any]]:
    """Get all recipes with their ingredients."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get all recipes
        cursor.execute(
            """
            SELECT id, title, instructions, image_path, parent_id
            FROM recipes
            ORDER BY title
        """
        )

        recipes = []
        for row in cursor.fetchall():
            recipe = dict(row)

            # Get ingredients for this recipe
            cursor.execute(
                """
                SELECT amount, unit, ingredient
                FROM ingredients
                WHERE recipe_id = ?
                ORDER BY id
            """,
                (recipe["id"],),
            )

            ingredients = []
            for ing_row in cursor.fetchall():
                ing_dict = dict(ing_row)
                ingredients.append(ing_dict)

            recipe["ingredients"] = ingredients

            # Get tags for this recipe
            cursor.execute(
                """
                SELECT t.name
                FROM tags t
                JOIN recipe_tags rt ON t.id = rt.tag_id
                WHERE rt.recipe_id = ?
                ORDER BY t.name
            """,
                (recipe["id"],),
            )

            tags = [tag["name"] for tag in cursor.fetchall()]
            recipe["tags"] = tags

            recipes.append(recipe)

        return recipes


def get_recipe_by_id(recipe_id: int) -> Optional[Dict[str, Any]]:
    """Get a single recipe by ID with its ingredients."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get the recipe
        cursor.execute(
            """
            SELECT id, title, instructions, image_path, parent_id
            FROM recipes
            WHERE id = ?
        """,
            (recipe_id,),
        )

        row = cursor.fetchone()
        if not row:
            return None

        recipe = dict(row)

        # Get ingredients for this recipe
        cursor.execute(
            """
            SELECT amount, unit, ingredient
            FROM ingredients
            WHERE recipe_id = ?
            ORDER BY id
        """,
            (recipe_id,),
        )

        ingredients = []
        for ing_row in cursor.fetchall():
            ing_dict = dict(ing_row)
            ingredients.append(ing_dict)

        recipe["ingredients"] = ingredients

        # Get tags for this recipe
        cursor.execute(
            """
            SELECT t.name
            FROM tags t
            JOIN recipe_tags rt ON t.id = rt.tag_id
            WHERE rt.recipe_id = ?
            ORDER BY t.name
        """,
            (recipe_id,),
        )

        tags = [tag["name"] for tag in cursor.fetchall()]
        recipe["tags"] = tags

        return recipe


def create_recipe(
    title: str,
    instructions: str,
    ingredients: List[Dict[str, Any]],
    image_path: Optional[str] = None,
    parent_id: Optional[int] = None,
) -> int:
    """Create a new recipe and return its ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Insert the recipe
        cursor.execute(
            """
            INSERT INTO recipes (title, instructions, image_path, parent_id)
            VALUES (?, ?, ?, ?)
        """,
            (title, instructions, image_path, parent_id),
        )

        recipe_id = cursor.lastrowid

        # Insert ingredients
        for ingredient in ingredients:
            cursor.execute(
                """
                INSERT INTO ingredients (recipe_id, amount, unit, ingredient)
                VALUES (?, ?, ?, ?)
            """,
                (
                    recipe_id,
                    ingredient.get("amount"),
                    ingredient.get("unit"),
                    ingredient["ingredient"],
                ),
            )

        conn.commit()
        return recipe_id


def delete_recipe(recipe_id: int) -> bool:
    """Delete a recipe and its ingredients."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if recipe exists
        cursor.execute("SELECT id FROM recipes WHERE id = ?", (recipe_id,))
        if not cursor.fetchone():
            return False

        # Delete the recipe (ingredients will be deleted due to CASCADE)
        cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        conn.commit()
        return True


def get_all_tags() -> List[Dict[str, Any]]:
    """Get all tags."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM tags ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]


def create_tag(name: str) -> Optional[int]:
    """Create a new tag and return its ID. Returns None if tag already exists."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO tags (name) VALUES (?)", (name,))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None  # Tag already exists


def delete_tag(tag_id: int) -> bool:
    """Delete a tag."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if tag exists
        cursor.execute("SELECT id FROM tags WHERE id = ?", (tag_id,))
        if not cursor.fetchone():
            return False

        cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        conn.commit()
        return True


def add_tag_to_recipe(recipe_id: int, tag_id: int) -> bool:
    """Add a tag to a recipe."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO recipe_tags (recipe_id, tag_id)
                VALUES (?, ?)
            """,
                (recipe_id, tag_id),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Relationship already exists


def remove_tag_from_recipe(recipe_id: int, tag_id: int) -> bool:
    """Remove a tag from a recipe."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM recipe_tags
            WHERE recipe_id = ? AND tag_id = ?
        """,
            (recipe_id, tag_id),
        )
        conn.commit()
        return cursor.rowcount > 0
