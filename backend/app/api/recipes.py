from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy import func, select, distinct, or_
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.models import Ingredient, Recipe, RecipeStep, User
from app.schemas.recipe import RecipeCreate, RecipeOut, RecipeUpdate, RecipeSearchResult

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


# --- US2.2: Search Endpoint ---
@router.get("", response_model=RecipeSearchResult)
def search_recipes(
    db: DbSession,
    q: str | None = Query(default=None, max_length=100, description="Title/keyword query"),
    cuisine: str | None = Query(default=None, max_length=50),
    meal_type: str | None = Query (default=None, max_length=50),
    difficulty: str | None = Query(default=None),
    ingredient: str |None = Query(default= None, max_length=100),
    limit: int = Query(default=20, ge=1,le=100),
    offset: int = Query(default=0, ge=0),

): 
    filters = []
    # Test search across title, desription, and ingreadient, names
    if q and q.strip():
        term = f"%{q.strip()}%"
        filters.append(
            or_(
                Recipe.title.ilike(term),
                Recipe.description.ilike(term),
                Recipe.ingredients.any(Ingredient.name.ilike(term)),
            )
        )
    
    # Faceted category & ingredient filters
    if cuisine and cuisine.strip():
        filters.append(Recipe.cuisine.ilike(cuisine.strip()))
    if meal_type and meal_type.strip():
        filters.append(Recipe.meal_type.ilike(meal_type.strip()))
    if difficulty and difficulty.strip():
        filters.append(Recipe.difficulty == difficulty.strip().lower())
    if ingredient and ingredient.strip():
        filters.append(Recipe.ingredients.any(Ingredient.name.ilike(f"%{ingredient.strip()}%")))

    # Total count matching filters

    count_query = select(func.count(distinct(Recipe.id))).select_from(Recipe)
    if filters:
        count_query = count_query = count_query.where(*filters)
    total = db.scalar(count_query) or 0

    # Fetch matching recipes
    query = (
        select(Recipe)
        .options(selectinload(Recipe.owner))
        .order_by(Recipe.created_at.desc(), Recipe.id.desc())
    )
    if filters:
        query = query.where(*filters)
    query = query.offset(offset).limit(limit)
    items = db.scalars(query).all()

    return RecipeSearchResult(
        total = total,
        limit=limit,
        offset=offset,
        items=items,
    )


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
