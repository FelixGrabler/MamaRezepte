import pytest
from sqlalchemy import text
from app.core import database as db


def test_category_upgrade_preserves_ids_parts_and_favourites(client):
    if db.engine.dialect.name != 'postgresql':
        pytest.skip('Existing database upgrade is for PostgreSQL')
    before = client.get('/api/recipes/48').json()
    with db.engine.begin() as conn:
        conn.execute(text("DELETE FROM migration_history WHERE name = 'category-spelling-v2'"))
        conn.execute(text('ALTER TABLE recipes DROP CONSTRAINT recipe_category'))
        conn.execute(text("UPDATE recipes SET category = CASE category WHEN 'Hauptspeise' THEN 'Hauptspeiße' WHEN 'Nachspeise' THEN 'Nachspeiße' ELSE category END"))
        conn.execute(text("ALTER TABLE recipes ADD CONSTRAINT recipe_category CHECK (category IN ('Suppe', 'Hauptspeiße', 'Nachspeiße', 'Frühstück', 'sonstiges'))"))
        conn.execute(text('INSERT INTO favourites (user_id, recipe_id) VALUES (9999, 48)'))
    db.init_database()
    db.init_database()
    assert client.get('/api/recipes/48').json() == before
    assert client.get('/api/recipes/88').json()['category'] == 'Nachspeise'
    with db.engine.begin() as conn:
        assert conn.scalar(text("SELECT count(*) FROM recipes WHERE category IN ('Hauptspeiße', 'Nachspeiße')")) == 0
        assert conn.scalar(text('SELECT recipe_id FROM favourites WHERE user_id=9999')) == 48
        conn.execute(text('DELETE FROM favourites WHERE user_id=9999'))
