from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import Recipe, RecipeCreate
from app.core import database

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("/", response_model=List[Recipe])
async def get_recipes():
    """Get all recipes."""
    return database.get_all_recipes()


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: int):
    """Get a single recipe by ID."""
    recipe = database.get_recipe_by_id(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("/", response_model=Recipe)
async def create_recipe(recipe: RecipeCreate):
    """Create a new recipe."""
    recipe_id = database.create_recipe(
        title=recipe.title,
        instructions=recipe.instructions,
        ingredients=[ing.model_dump() for ing in recipe.ingredients],
        image_path=recipe.image_path,
        parent_id=recipe.parent_id,
    )
    return database.get_recipe_by_id(recipe_id)


@router.delete("/{recipe_id}")
async def delete_recipe(recipe_id: int):
    """Delete a recipe."""
    if not database.delete_recipe(recipe_id):
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"message": "Recipe deleted successfully"}
