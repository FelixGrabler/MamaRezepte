from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy import delete, or_, select
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import selectinload

from app.core import config, database as db
from app.core.auth import optional_user, required_user
from app.core.images import save_image
from app.models.schemas import RecipeWrite
from app.core.catalogue import Category

router = APIRouter(prefix="/recipes", tags=["recipes"])


def find_recipe(session, recipe_id, user, *, edit=False):
    recipe = session.get(db.Recipe, recipe_id)
    if recipe is None or not db.visible(db.root_of(session, recipe), user):
        raise HTTPException(404, "Rezept nicht gefunden.")
    if edit and (recipe.parent_id is not None or user is None or recipe.owner_id != user["id"]):
        raise HTTPException(403, "Nur eigene Rezepte können bearbeitet werden.")
    return recipe


def validate_parts(recipe, payload):
    existing_ids = {part.id for part in recipe.parts}
    supplied_ids = [part.id for part in payload.parts if part.id is not None]
    if len(supplied_ids) != len(set(supplied_ids)) or not set(supplied_ids).issubset(existing_ids):
        raise HTTPException(422, "Rezeptteile müssen zu diesem Rezept gehören und dürfen nicht doppelt vorkommen.")


@router.put("/{recipe_id}/favourite")
def add_favourite(recipe_id: int, user=Depends(required_user)):
    with db.session() as session:
        recipe = find_recipe(session, recipe_id, user)
        if recipe.parent_id is not None:
            raise HTTPException(400, "Bitte das Hauptrezept als Favorit markieren.")
        insert = postgres_insert if session.bind.dialect.name == "postgresql" else sqlite_insert
        session.execute(insert(db.Favourite).values(user_id=user["id"], recipe_id=recipe_id)
                        .on_conflict_do_nothing(index_elements=["user_id", "recipe_id"]))
    return {"is_favourite": True}


@router.delete("/{recipe_id}/favourite")
def remove_favourite(recipe_id: int, user=Depends(required_user)):
    with db.session() as session:
        find_recipe(session, recipe_id, user)
        session.execute(delete(db.Favourite).where(db.Favourite.user_id == user["id"],
                                                   db.Favourite.recipe_id == recipe_id))
    return {"is_favourite": False}


@router.get("/")
def list_recipes(category: Category | None = None, tags: list[str] = Query(default=[]),
                 favourites: bool = False, user=Depends(optional_user)):
    if favourites and user is None:
        raise HTTPException(401, "Bitte zuerst anmelden.")
    with db.session() as session:
        access = db.Recipe.is_public.is_(True)
        if user:
            access = or_(access, db.Recipe.owner_id == user["id"])
        starred = db.favourite_ids(session, user)
        query = select(db.Recipe).where(db.Recipe.parent_id.is_(None), access)
        if category is not None:
            query = query.where(db.Recipe.category == category)
        for tag in tags:
            query = query.where(db.Recipe.tags.any(db.RecipeTag.key == tag.strip().casefold()))
        if favourites:
            query = query.where(db.Recipe.id.in_(starred))
        recipes = session.scalars(query.options(
            selectinload(db.Recipe.ingredients), selectinload(db.Recipe.tags),
            selectinload(db.Recipe.parts).selectinload(db.Recipe.ingredients),
            selectinload(db.Recipe.parts).selectinload(db.Recipe.tags),
        ).order_by(db.Recipe.title)).all()
        return [db.serialize(recipe, user, starred) for recipe in recipes]


@router.post("/", status_code=201)
def create_recipe(payload: RecipeWrite, user=Depends(required_user)):
    with db.session() as session:
        recipe = db.Recipe()
        validate_parts(recipe, payload)
        db.apply_recipe(recipe, payload, user)
        session.add(recipe)
        session.flush()
        return db.serialize(recipe, user, db.favourite_ids(session, user))


@router.get("/{recipe_id}")
def get_recipe(recipe_id: int, user=Depends(optional_user)):
    with db.session() as session:
        return db.serialize(find_recipe(session, recipe_id, user), user, db.favourite_ids(session, user))


@router.put("/{recipe_id}")
def update_recipe(recipe_id: int, payload: RecipeWrite, user=Depends(required_user)):
    with db.session() as session:
        recipe = find_recipe(session, recipe_id, user, edit=True)
        validate_parts(recipe, payload)
        db.apply_recipe(recipe, payload, user)
        session.flush()
        return db.serialize(recipe, user, db.favourite_ids(session, user))


@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int, user=Depends(required_user)):
    with db.session() as session:
        session.delete(find_recipe(session, recipe_id, user, edit=True))
    return {"ok": True}


@router.post("/{recipe_id}/image")
def upload_image(recipe_id: int, image: UploadFile = File(...), user=Depends(required_user)):
    with db.session() as session:
        recipe = find_recipe(session, recipe_id, user, edit=True)
        data = image.file.read(config.MAX_IMAGE_BYTES + 1)
        try:
            name = save_image(data)
        finally:
            image.file.close()
        recipe.image_path = f"uploads/{name}"
        session.flush()
        return db.serialize(recipe, user, db.favourite_ids(session, user))


@router.delete("/{recipe_id}/image")
def remove_image(recipe_id: int, user=Depends(required_user)):
    with db.session() as session:
        recipe = find_recipe(session, recipe_id, user, edit=True)
        recipe.image_path = None
    return {"ok": True}


@router.get("/{recipe_id}/image")
def get_image(recipe_id: int, user=Depends(optional_user)):
    with db.session() as session:
        recipe = find_recipe(session, recipe_id, user)
        if not recipe.image_path:
            raise HTTPException(404, "Bild nicht gefunden.")
        if recipe.image_path.startswith("uploads/"):
            base = config.UPLOAD_DIR.resolve()
            path = (base / recipe.image_path.removeprefix("uploads/")).resolve()
        else:
            base = config.IMAGE_DIR.resolve()
            path = (base / recipe.image_path.removeprefix("images/")).resolve()
        if not path.is_relative_to(base) or not path.is_file():
            raise HTTPException(404, "Bild nicht gefunden.")
        return FileResponse(path, headers={"Cache-Control": "private, no-store", "Vary": "Cookie",
                                           "X-Content-Type-Options": "nosniff"})
