from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import Tag, TagBase, RecipeTagRequest
from app.core import database

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=List[Tag])
async def get_tags():
    """Get all tags."""
    return database.get_all_tags()


@router.post("/", response_model=Tag)
async def create_tag(tag: TagBase):
    """Create a new tag."""
    tag_id = database.create_tag(tag.name)
    if tag_id is None:
        raise HTTPException(status_code=400, detail="Tag already exists")
    return {"id": tag_id, "name": tag.name}


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int):
    """Delete a tag."""
    if not database.delete_tag(tag_id):
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"message": "Tag deleted successfully"}


# Recipe-Tag relationship endpoints
@router.post("/recipe-tags")
async def add_tag_to_recipe(request: RecipeTagRequest):
    """Add a tag to a recipe."""
    if not database.add_tag_to_recipe(request.recipe_id, request.tag_id):
        raise HTTPException(status_code=400, detail="Failed to add tag to recipe")
    return {"message": "Tag added to recipe successfully"}


@router.delete("/recipe-tags")
async def remove_tag_from_recipe(request: RecipeTagRequest):
    """Remove a tag from a recipe."""
    if not database.remove_tag_from_recipe(request.recipe_id, request.tag_id):
        raise HTTPException(status_code=404, detail="Tag relationship not found")
    return {"message": "Tag removed from recipe successfully"}
