from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import CurrentUser, DbSession
from app.models import Ingredient, Recipe, User
from app.schemas.recipe import RecipeCreate, RecipeOut, RecipeUpdate

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


def _get_recipe(db: DbSession, recipe_id: int) -> Recipe:
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


def _require_owner(recipe: Recipe, user: User) -> None:
    if recipe.owner_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only change your own recipes")


def _set_ingredients(recipe: Recipe, body: RecipeCreate) -> None:
    recipe.ingredients = [Ingredient(position=i, **ing.model_dump()) for i, ing in enumerate(body.ingredients)]


@router.post("", response_model=RecipeOut, status_code=status.HTTP_201_CREATED)
def create_recipe(body: RecipeCreate, user: CurrentUser, db: DbSession):
    """US1.4: create a recipe with instructions, times and ingredients."""
    recipe = Recipe(owner=user, **body.model_dump(exclude={"ingredients"}))
    _set_ingredients(recipe, body)
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.get("/{recipe_id}", response_model=RecipeOut)
def read_recipe(recipe_id: int, db: DbSession):
    return _get_recipe(db, recipe_id)


@router.put("/{recipe_id}", response_model=RecipeOut)
def update_recipe(recipe_id: int, body: RecipeUpdate, user: CurrentUser, db: DbSession):
    recipe = _get_recipe(db, recipe_id)
    _require_owner(recipe, user)
    for field, value in body.model_dump(exclude={"ingredients"}).items():
        setattr(recipe, field, value)
    _set_ingredients(recipe, body)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int, user: CurrentUser, db: DbSession):
    recipe = _get_recipe(db, recipe_id)
    _require_owner(recipe, user)
    db.delete(recipe)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
