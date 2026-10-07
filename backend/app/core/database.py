"""Persistent recipe aggregates. Parts inherit access from their root recipe."""
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Boolean, CheckConstraint, Float, ForeignKey, Integer, String, Text, UniqueConstraint, create_engine, event, select, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from . import config
from .schema import upgrade_schema


class Base(DeclarativeBase):
    pass


class Recipe(Base):
    __tablename__ = "recipes"
    __table_args__ = (
        CheckConstraint("servings BETWEEN 1 AND 1000", name="recipe_servings_range"),
        CheckConstraint("category IN ('Suppe', 'Hauptspeise', 'Nachspeise', 'Frühstück', 'sonstiges')", name="recipe_category"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    instructions: Mapped[str] = mapped_column(Text, default="")
    image_path: Mapped[str | None] = mapped_column(Text)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, index=True)
    owner_username: Mapped[str | None] = mapped_column(String(64))
    category: Mapped[str] = mapped_column(String(40), default="sonstiges", index=True)
    servings: Mapped[int] = mapped_column(Integer, default=4)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    ingredients: Mapped[list["Ingredient"]] = relationship(cascade="all, delete-orphan", order_by="Ingredient.id")
    tags: Mapped[list["RecipeTag"]] = relationship(cascade="all, delete-orphan", order_by="RecipeTag.name")
    favourites: Mapped[list["Favourite"]] = relationship(cascade="all, delete-orphan")
    parts: Mapped[list["Recipe"]] = relationship(cascade="all, delete-orphan", order_by="Recipe.position, Recipe.id")


class Ingredient(Base):
    __tablename__ = "ingredients"
    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    amount: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(40))
    ingredient: Mapped[str] = mapped_column(Text)


class RecipeTag(Base):
    __tablename__ = "recipe_tags"
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    name: Mapped[str] = mapped_column(String(60), primary_key=True)
    key: Mapped[str] = mapped_column(String(60), index=True)
    __table_args__ = (UniqueConstraint("recipe_id", "key"),)


class Favourite(Base):
    __tablename__ = "favourites"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)


class Migration(Base):
    __tablename__ = "migration_history"
    name: Mapped[str] = mapped_column(String(100), primary_key=True)


def build_engine():
    url = config.DATABASE_URL or URL.create(
        "postgresql+psycopg", username="recipes",
        password=Path(config.DATABASE_PASSWORD_FILE).read_text().strip(),
        host="recipes-db", database="recipes",
    )
    engine = create_engine(url, pool_pre_ping=True)
    if engine.dialect.name == "sqlite":
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(conn, _):
            conn.execute("PRAGMA foreign_keys=ON")
    return engine


engine = build_engine()
SessionLocal = sessionmaker(engine, expire_on_commit=False)


@contextmanager
def session():
    with SessionLocal.begin() as db:
        yield db


def init_database():
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            conn.execute(text("SELECT pg_advisory_xact_lock(725321)"))
        Base.metadata.create_all(conn)
        with SessionLocal(bind=conn) as db:
            upgrade_schema(db)
            db.flush()


def root_of(db, recipe):
    while recipe.parent_id is not None:
        recipe = db.get(Recipe, recipe.parent_id)
    return recipe


def visible(recipe, user):
    return recipe.is_public or (user is not None and recipe.owner_id == user["id"])


def favourite_ids(db, user):
    if user is None:
        return set()
    return set(db.scalars(select(Favourite.recipe_id).where(Favourite.user_id == user["id"])))


def serialize(recipe, user, favourites=frozenset()):
    return dict(id=recipe.id, title=recipe.title, instructions=recipe.instructions,
                parent_id=recipe.parent_id, image_path=recipe.image_path,
                image_url=f"/api/recipes/{recipe.id}/image" if recipe.image_path else None,
                owner_id=recipe.owner_id, owner_username=recipe.owner_username, is_public=recipe.is_public,
                category=recipe.category, servings=recipe.servings,
                is_favourite=recipe.id in favourites,
                can_edit=user is not None and recipe.owner_id == user["id"],
                ingredients=[dict(amount=i.amount, unit=i.unit, ingredient=i.ingredient) for i in recipe.ingredients],
                tags=[t.name for t in sorted(recipe.tags, key=lambda tag: tag.key)], parts=[serialize(p, user, favourites) for p in recipe.parts])


def apply_content(record, payload):
    record.title = payload.title
    record.instructions = payload.instructions
    record.ingredients = [Ingredient(**i.model_dump()) for i in payload.ingredients]


def apply_recipe(record, payload, user):
    apply_content(record, payload)
    record.owner_id = user["id"]
    record.owner_username = user["username"]
    record.category = payload.category
    record.servings = payload.servings
    record.is_public = payload.is_public
    existing = {tag.key: tag for tag in record.tags}
    record.tags = [existing.get(name.casefold()) or RecipeTag(name=name, key=name.casefold()) for name in payload.tags]
    parts = []
    existing_parts = {child.id: child for child in record.parts}
    for position, part in enumerate(payload.parts):
        child = existing_parts[part.id] if part.id is not None else Recipe()
        apply_content(child, part)
        child.owner_id = user["id"]
        child.owner_username = user["username"]
        child.category = payload.category
        child.servings = payload.servings
        child.is_public = payload.is_public
        child.position = position
        parts.append(child)
    record.parts = parts
