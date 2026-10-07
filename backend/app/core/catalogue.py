"""Fixed recipe categories and initial classification of the family collection."""
from typing import Literal

Category = Literal["Suppe", "Hauptspeiße", "Nachspeiße", "Frühstück", "sonstiges"]
CATEGORIES = ["Suppe", "Hauptspeiße", "Nachspeiße", "Frühstück", "sonstiges"]
SUGGESTED_TAGS = ["süß", "Fleisch", "vegetarisch", "Mama-Rezept"]
CANONICAL_TAGS = {name.casefold(): name for name in SUGGESTED_TAGS}

LEGACY_CATEGORIES = {
    "Suppe": {1, 14, 21, 31, 32, 33, 38, 47, 55, 56, 58, 59, 61, 65, 66, 68, 71, 72},
    "Hauptspeiße": {4, 5, 10, 11, 12, 13, 17, 18, 20, 22, 25, 26, 27, 34, 35, 42, 43,
                    48, 51, 52, 53, 54, 57, 64, 67, 70, 73, 74},
    "Nachspeiße": {3, 6, 7, 8, 9, 29, 39, 44, 69, 75, 76, 78, 79, 81, 82, 83, 84, 85, 87, 88},
    "Frühstück": {2},
}


def legacy_category(recipe_id):
    return next((name for name, ids in LEGACY_CATEGORIES.items() if recipe_id in ids), "sonstiges")
