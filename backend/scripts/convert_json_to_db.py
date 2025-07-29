#!/usr/bin/env python3
"""
Script to convert recipes.json to SQLite database
"""

import json
import sys
import os

# Add the backend directory to the path so we can import database module
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core import database


def parse_ingredient(ingredient_str):
    """
    Parse ingredient string like "30_g_Mehl" into amount, unit, and ingredient.

    Examples:
    - "30_g_Mehl" -> (30.0, "g", "Mehl")
    - "1__Ei" -> (1.0, "", "Ei")
    - "__Salz" -> (None, "", "Salz")
    - "2-3_Löffel_Wasser" -> (2.5, "Löffel", "Wasser")
    - "¼_kg_Mehl" -> (0.25, "kg", "Mehl")
    """

    # Handle fractions
    fractions = {
        "¼": 0.25,
        "½": 0.5,
        "¾": 0.75,
        "⅓": 0.33,
        "⅔": 0.67,
        "⅛": 0.125,
        "⅜": 0.375,
        "⅝": 0.625,
        "⅞": 0.875,
    }

    # Replace fractions with decimal values
    for fraction, decimal in fractions.items():
        ingredient_str = ingredient_str.replace(fraction, str(decimal))

    # Split by underscores
    parts = ingredient_str.split("_")

    if len(parts) < 3:
        # Handle cases like "__Salz" or "Salz"
        if ingredient_str.startswith("__"):
            return None, "", ingredient_str[2:]
        else:
            return None, "", ingredient_str

    amount_str = parts[0]
    unit = parts[1]
    ingredient = "_".join(parts[2:])  # Rejoin the rest as ingredient name

    # Parse amount
    amount = None
    if amount_str and amount_str != "":
        try:
            # Handle ranges like "2-3"
            if "-" in amount_str:
                range_parts = amount_str.split("-")
                amount = (float(range_parts[0]) + float(range_parts[1])) / 2
            else:
                amount = float(amount_str)
        except ValueError:
            amount = None

    return amount, unit if unit else None, ingredient


def convert_json_to_db(json_file_path):
    """Convert the JSON file to SQLite database."""

    # Initialize the database
    database.init_database()

    # Read the JSON file
    with open(json_file_path, "r", encoding="utf-8") as f:
        recipes_data = json.load(f)

    print(f"Converting {len(recipes_data)} recipes...")

    # Convert each recipe
    for i, recipe_data in enumerate(recipes_data):
        print(f"Converting recipe {i+1}/{len(recipes_data)}: {recipe_data['title']}")

        # Parse ingredients
        ingredients = []
        for ing_str in recipe_data.get("ingredients", []):
            amount, unit, ingredient = parse_ingredient(ing_str)
            ingredients.append(
                {"amount": amount, "unit": unit, "ingredient": ingredient}
            )

        # Create the recipe
        try:
            recipe_id = database.create_recipe(
                title=recipe_data["title"],
                instructions=recipe_data["instructions"],
                ingredients=ingredients,
                image_path=recipe_data.get("image_path"),
                parent_id=recipe_data.get(
                    "parent_recipe"
                ),  # Note: this assumes parent_recipe is an ID
            )
            print(f"  -> Created recipe with ID {recipe_id}")
        except Exception as e:
            print(f"  -> Error creating recipe: {e}")

    print("Conversion completed!")


def main():
    # Find the JSON file
    json_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "frontend",
        "public",
        "data",
        "recipes.json",
    )

    if not os.path.exists(json_path):
        print(f"Error: Could not find recipes.json at {json_path}")
        sys.exit(1)

    print(f"Converting {json_path} to SQLite database...")
    convert_json_to_db(json_path)

    # Show some statistics
    recipes = database.get_all_recipes()
    print(f"\nDatabase now contains {len(recipes)} recipes.")

    # Show first few recipes as examples
    print("\nFirst 3 recipes:")
    for recipe in recipes[:3]:
        print(f"- {recipe['title']}: {len(recipe['ingredients'])} ingredients")


if __name__ == "__main__":
    main()
