"""Fixed recipe categories and tag suggestions."""
from typing import Literal

Category = Literal["Suppe", "Hauptspeise", "Nachspeise", "Frühstück", "sonstiges"]
CATEGORIES = ["Suppe", "Hauptspeise", "Nachspeise", "Frühstück", "sonstiges"]
SUGGESTED_TAGS = ["süß", "Fleisch", "vegetarisch", "Mama-Rezept"]
CANONICAL_TAGS = {name.casefold(): name for name in SUGGESTED_TAGS}
