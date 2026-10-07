from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.core.catalogue import CANONICAL_TAGS, Category


class Ingredient(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    amount: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    unit: str | None = Field(default=None, max_length=40)
    ingredient: str = Field(min_length=1, max_length=250)


class RecipeContent(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=200)
    instructions: str = Field(default="", max_length=30000)
    ingredients: list[Ingredient] = Field(default_factory=list, max_length=200)


class RecipePart(RecipeContent):
    # Existing part IDs keep their identity and image when parts are reordered.
    id: int | None = Field(default=None, gt=0)


class RecipeWrite(RecipeContent):
    is_public: bool = True
    category: Category = "sonstiges"
    servings: int = Field(default=4, ge=1, le=1000, strict=True)
    tags: list[str] = Field(default_factory=list, max_length=20)
    parts: list[RecipePart] = Field(default_factory=list, max_length=30)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, tags):
        result = {}
        for tag in tags:
            tag = tag.strip()
            if not tag:
                continue
            if len(tag) > 60 or len(tag.casefold()) > 60:
                raise ValueError("Tags dürfen höchstens 60 Zeichen lang sein.")
            result.setdefault(tag.casefold(), CANONICAL_TAGS.get(tag.casefold(), tag))
        return list(result.values())


class Credentials(BaseModel):
    username: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=1, max_length=128)
