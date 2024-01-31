import json
from models import db, Rezept, Zutat, Bewertung, Tag, Bild, RezeptSchritt


def fill_database(app):
    with app.app_context():
        with open("recipes.json", "r", encoding="utf-8") as file:
            recipes = json.load(file)

        for recipe in recipes:
            new_recipe = Rezept(
                titel=recipe["title"],
                anweisung=recipe["instructions"],
            )
            db.session.add(new_recipe)
            db.session.flush()  # This is used to get the id of the new_recipe before committing.

            for ingredient in recipe["ingredients"]:
                menge, einheit, bezeichnung = ingredient.split("_")
                new_zutat = Zutat(
                    rezept_id=new_recipe.id,
                    menge=menge if menge != "__" else None,
                    einheit=einheit if einheit != "__" else None,
                    bezeichnung=bezeichnung,
                )
                db.session.add(new_zutat)

            # Add handling for tags, ratings, and images if needed
            # ...

            db.session.commit()


def clear_database(app):
    with app.app_context():
        db.session.execute("TRUNCATE TABLE rezept RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE zutat RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE bewertung RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE tag RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE bild RESTART IDENTITY CASCADE;")
        db.session.execute("TRUNCATE TABLE rezept_schritt RESTART IDENTITY CASCADE;")
        db.session.commit()
