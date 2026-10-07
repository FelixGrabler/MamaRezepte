from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from app.core import database as db
from app.core.auth import optional_user
from app.core.catalogue import SUGGESTED_TAGS

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/")
def get_tags(user=Depends(optional_user)):
    with db.session() as session:
        access = db.Recipe.is_public.is_(True)
        if user:
            access = or_(access, db.Recipe.owner_id == user["id"])
        names = session.scalars(select(db.RecipeTag.name).join(db.Recipe)
                                .where(db.Recipe.parent_id.is_(None), access)
                                .distinct().order_by(db.RecipeTag.name)).all()
        tags = {name.casefold(): name for name in SUGGESTED_TAGS}
        for name in names:
            tags.setdefault(name.casefold(), name)
        return [{"name": name} for name in sorted(tags.values(), key=str.casefold)]
