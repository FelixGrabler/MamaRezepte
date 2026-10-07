"""Versioned upgrades for already-installed databases."""
from sqlalchemy import text

CATEGORY_CONSTRAINT = "category IN ('Suppe', 'Hauptspeise', 'Nachspeise', 'Frühstück', 'sonstiges')"


def upgrade_schema(db):
    from .database import Migration
    name = 'category-spelling-v2'
    if db.get(Migration, name):
        return
    if db.bind.dialect.name == 'postgresql':
        # Drop the previous spelling constraint before updating existing rows.
        # init_database holds an advisory transaction lock during this upgrade.
        db.execute(text('ALTER TABLE recipes DROP CONSTRAINT IF EXISTS recipe_category'))
        db.execute(text("UPDATE recipes SET category = CASE category WHEN 'Hauptspeiße' THEN 'Hauptspeise' WHEN 'Nachspeiße' THEN 'Nachspeise' ELSE category END WHERE category IN ('Hauptspeiße', 'Nachspeiße')"))
        db.execute(text(f'ALTER TABLE recipes ADD CONSTRAINT recipe_category CHECK ({CATEGORY_CONSTRAINT})'))
    db.add(Migration(name=name))
