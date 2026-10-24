from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.models import Ingredient, Recipe, RecipeStep, User
from app.schemas.recipe import RecipeCreate, RecipeOut, RecipeUpdate

router = APIRouter(prefix="/api/v1/recipes", tags=["recipes"])


# --- US1.4 & US1.5: Recipe Helper (Lookup by ID) ---
def _get_recipe(db: DbSession, recipe_id: int) -> Recipe:
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


# --- US1.4 & US1.5: Recipe Authorization Helper (Owner or Admin Check) ---
def _require_owner(recipe: Recipe, user: User) -> None:
    if recipe.author_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only change your own recipes")


# --- US1.4: Recipe Creation & Saving Helper (Attach Ingredients & Steps) ---
def _set_children(recipe: Recipe, body: RecipeCreate) -> None:
    recipe.ingredients = [Ingredient(position=i, **item.model_dump()) for i, item in enumerate(body.ingredients)]
    recipe.steps = [RecipeStep(**step.model_dump()) for step in body.steps]


# --- US1.4: Recipe Creation & Saving (Create Recipe Endpoint) ---
@router.post("", response_model=RecipeOut, status_code=201)
def create_recipe(body: RecipeCreate, user: CurrentUser, db: DbSession):
    recipe = Recipe(owner=user, **body.model_dump(exclude={"ingredients", "steps"}))
    _set_children(recipe, body)
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


# --- US1.5: Personal Recipe Tab (Get Author-Filtered Saved Recipes with Pagination) ---
@router.get("/my-recipes", response_model=list[RecipeOut])
def my_recipes(user: CurrentUser, db: DbSession, offset: int = Query(default=0, ge=0),
               limit: int = Query(default=20, ge=1, le=100)):
    query = (select(Recipe).where(Recipe.author_id == user.id)
             .options(selectinload(Recipe.ingredients), selectinload(Recipe.steps), selectinload(Recipe.owner))
             .order_by(Recipe.created_at.desc(), Recipe.id.desc()).offset(offset).limit(limit))
    return db.scalars(query).all()


# --- US1.5: Recipe Detail View (Read Recipe by ID) ---
@router.get("/{recipe_id}", response_model=RecipeOut)
def read_recipe(recipe_id: int, db: DbSession):
    return _get_recipe(db, recipe_id)


# --- US1.4: Recipe Creation & Saving (Update Recipe Endpoint) ---
@router.put("/{recipe_id}", response_model=RecipeOut)
def update_recipe(recipe_id: int, body: RecipeUpdate, user: CurrentUser, db: DbSession):
    recipe = _get_recipe(db, recipe_id)
    _require_owner(recipe, user)
    for field, value in body.model_dump(exclude={"ingredients", "steps"}).items():
        setattr(recipe, field, value)
    # Delete old ordered rows before inserting replacements with the same step numbers.
    recipe.ingredients.clear()
    recipe.steps.clear()
    db.flush()
    _set_children(recipe, body)
    db.commit()
    db.refresh(recipe)
    return recipe


# --- US1.5: Recipe Management (Delete Recipe Endpoint) ---
@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int, user: CurrentUser, db: DbSession):
    recipe = _get_recipe(db, recipe_id)
    _require_owner(recipe, user)
    db.delete(recipe)
    db.commit()
    return Response(status_code=204)
