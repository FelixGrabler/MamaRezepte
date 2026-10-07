"""Small recipe collection used only by tests."""
from sqlalchemy import text
from app.core import database as db


def seed_recipes():
    with db.session() as session:
        if session.get(db.Recipe, 48):
            return
        def recipe(id, title, category, image=None):
            return db.Recipe(id=id, title=title, instructions='Zubereiten.',
                             owner_id=1003, owner_username='felix', is_public=True,
                             category=category, servings=4, image_path=image)
        pizza = recipe(48, 'Pizza', 'Hauptspeise', 'images/pizza.jpg')
        pizza.parts = [recipe(49, 'Pizzateig', 'Hauptspeise'), recipe(50, 'Pizzasoße', 'Hauptspeise')]
        pizza.parts[0].ingredients = [db.Ingredient(amount=500, unit='g', ingredient='Mehl')]
        soup = recipe(61, 'Tomatensuppe', 'Suppe', 'images/tomatensuppe.jpg')
        cake = recipe(88, 'Marmor-Gugelhupf', 'Nachspeise', 'images/marmor_gugelhupf.jpg')
        for root in (pizza, soup, cake):
            root.tags = [db.RecipeTag(name='Mama-Rezept', key='mama-rezept')]
        session.add_all([pizza, soup, cake])
        session.flush()
        if db.engine.dialect.name == 'postgresql':
            session.execute(text("SELECT setval(pg_get_serial_sequence('recipes', 'id'), 88)"))
