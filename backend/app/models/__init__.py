# Import every model here so Base.metadata knows about all tables.
from app.models.recipe import Ingredient, Recipe
from app.models.user import User

__all__ = ["User", "Recipe", "Ingredient"]
