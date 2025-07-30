#!/usr/bin/env python3
"""
Initialize database with sample data if it doesn't exist
"""

import os
import sys

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core import database


def main():
    # Check if database exists
    if not os.path.exists(database.DATABASE_PATH):
        print("Database doesn't exist. Initializing...")
        database.init_database()
        print("Database initialized successfully!")
    else:
        print("Database already exists.")

    # Show some basic stats
    try:
        recipes = database.get_all_recipes()
        print(f"Database contains {len(recipes)} recipes.")
    except Exception as e:
        print(f"Error reading database: {e}")


if __name__ == "__main__":
    main()
