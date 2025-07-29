from pydantic import BaseModel
from typing import List, Optional


class IngredientBase(BaseModel):
    amount: Optional[float] = None
    unit: Optional[str] = None
    ingredient: str


class Ingredient(IngredientBase):
    pass


class TagBase(BaseModel):
    name: str


class Tag(TagBase):
    id: int


class RecipeBase(BaseModel):
    title: str
    instructions: str
    image_path: Optional[str] = None
    parent_id: Optional[int] = None


class RecipeCreate(RecipeBase):
    ingredients: List[IngredientBase]


class Recipe(RecipeBase):
    id: int
    ingredients: List[Ingredient]
    tags: List[str] = []


class RecipeTagRequest(BaseModel):
    recipe_id: int
    tag_id: int
