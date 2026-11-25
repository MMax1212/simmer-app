"""Automated test suite for grocery aggregation service (US4.2 / Task 4.2.1 & 4.2.6).

Verifies SPK-3.1 algorithmic requirements:
1. Ingredient stemming & noise reduction.
2. Unit normalization & dimensional arithmetic.
3. Supermarket aisle / department categorization.
4. Aggregation arithmetic across multiple recipes with non-destructive guards.
"""
from __future__ import annotations

import pytest

from app.services.grocery import (
    aggregate_ingredients,
    classify_department,
    normalize_unit,
    stem_ingredient_name,
)


# ---------------------------------------------------------------------------
# 1. Stemming & Name Normalization Tests
# ---------------------------------------------------------------------------
class TestIngredientStemming:
    """Verifies preparation word stripping and singularization."""

    def test_strip_common_prep_words(self):
        assert stem_ingredient_name("diced yellow onions") == "yellow onion"
        assert stem_ingredient_name("finely chopped fresh garlic") == "garlic"
        assert stem_ingredient_name("minced fresh ginger") == "ginger"
        assert stem_ingredient_name("peeled and sliced carrots") == "carrot"
        assert stem_ingredient_name("boneless skinless chicken breasts") == "chicken breast"

    def test_singularize_plurals(self):
        assert stem_ingredient_name("onions") == "onion"
        assert stem_ingredient_name("tomatoes") == "tomato"
        assert stem_ingredient_name("potatoes") == "potato"
        assert stem_ingredient_name("strawberries") == "strawberry"
        assert stem_ingredient_name("eggs") == "egg"
        assert stem_ingredient_name("cloves") == "clove"

    def test_empty_and_whitespace(self):
        assert stem_ingredient_name("") == ""
        assert stem_ingredient_name("   ") == ""
        assert stem_ingredient_name("salt") == "salt"


# ---------------------------------------------------------------------------
# 2. Unit Normalization Tests
# ---------------------------------------------------------------------------
class TestUnitNormalization:
    """Verifies unit alias mapping and conversion factor assignment."""

    def test_volume_units_family(self):
        canonical, family, factor = normalize_unit("tbsp")
        assert canonical == "tbsp"
        assert family == "volume_us"
        assert factor == 3.0

        canonical, family, factor = normalize_unit("teaspoons")
        assert canonical == "tsp"
        assert family == "volume_us"
        assert factor == 1.0

        canonical, family, factor = normalize_unit("cups")
        assert canonical == "cup"
        assert family == "volume_us"
        assert factor == 48.0

    def test_weight_units_family(self):
        canonical, family, factor = normalize_unit("lbs")
        assert canonical == "lb"
        assert family == "weight_us"
        assert factor == 16.0

        canonical, family, factor = normalize_unit("ounces")
        assert canonical == "oz"
        assert family == "weight_us"
        assert factor == 1.0

    def test_discrete_units_are_isolated(self):
        canonical, family, factor = normalize_unit("clove")
        assert canonical == "clove"
        assert family == "discrete_clove"
        assert factor == 1.0

        canonical, family, factor = normalize_unit("pinch")
        assert canonical == "pinch"
        assert family == "discrete_pinch"


# ---------------------------------------------------------------------------
# 3. Department Classification Tests
# ---------------------------------------------------------------------------
class TestDepartmentClassification:
    """Verifies supermarket aisle categorization."""

    def test_produce(self):
        assert classify_department("yellow onion") == "Produce"
        assert classify_department("garlic") == "Produce"
        assert classify_department("fresh basil") == "Produce"
        assert classify_department("roma tomato") == "Produce"

    def test_meat_and_seafood(self):
        assert classify_department("chicken breast") == "Meat & Seafood"
        assert classify_department("ground beef") == "Meat & Seafood"
        assert classify_department("salmon fillet") == "Meat & Seafood"

    def test_dairy_and_refrigerated(self):
        assert classify_department("whole milk") == "Dairy & Refrigerated"
        assert classify_department("unsalted butter") == "Dairy & Refrigerated"
        assert classify_department("cheddar cheese") == "Dairy & Refrigerated"
        assert classify_department("egg") == "Dairy & Refrigerated"

    def test_pantry_and_baking(self):
        assert classify_department("olive oil") == "Pantry & Baking"
        assert classify_department("all-purpose flour") == "Pantry & Baking"
        assert classify_department("kosher salt") == "Pantry & Baking"
        assert classify_department("black pepper") == "Pantry & Baking"
        assert classify_department("spaghetti") == "Pantry & Baking"

    def test_other(self):
        assert classify_department("kitchen twine") == "Other"


# ---------------------------------------------------------------------------
# 4. Aggregation Arithmetic & Integration Tests (Scenario 1 in intent_4.md)
# ---------------------------------------------------------------------------
class TestAggregateIngredients:
    """Verifies end-to-end multi-recipe ingredient aggregation arithmetic."""

    def test_scenario_1_combine_olive_oil_across_two_recipes(self):
        """Validates Scenario 1 from intent_4.md:

        Garlic Pasta (1/2 cup olive oil) + Focaccia (1/4 cup olive oil)
        -> Consolidated 'olive oil — 0.75 cup' in 'Pantry & Baking'.
        """
        raw_items = [
            {"name": "extra virgin olive oil", "amount": 0.5, "unit": "cup", "recipe_id": 10},
            {"name": "olive oil", "amount": 0.25, "unit": "cup", "recipe_id": 12},
        ]
        result = aggregate_ingredients(raw_items)
        assert len(result) == 1
        item = result[0]
        assert item["name"] == "olive oil"
        assert item["amount"] == 0.75
        assert item["unit"] == "cup"
        assert item["department"] == "Pantry & Baking"

    def test_aggregate_diced_and_chopped_onions(self):
        """Validates combining 1/2 cup diced onions and 1 cup chopped onion -> 1.5 cups onion."""
        raw_items = [
            {"name": "diced onions", "amount": 0.5, "unit": "cup"},
            {"name": "chopped onion", "amount": 1.0, "unit": "cup"},
        ]
        result = aggregate_ingredients(raw_items)
        assert len(result) == 1
        assert result[0]["name"] == "onion"
        assert result[0]["amount"] == 1.5
        assert result[0]["unit"] == "cup"
        assert result[0]["department"] == "Produce"

    def test_volume_unit_conversions_tbsp_and_tsp(self):
        """2 tbsp (6 tsp) + 6 tsp (2 tbsp) = 4 tbsp (or 12 tsp)."""
        raw_items = [
            {"name": "soy sauce", "amount": 2.0, "unit": "tbsp"},
            {"name": "soy sauce", "amount": 6.0, "unit": "tsp"},
        ]
        result = aggregate_ingredients(raw_items)
        assert len(result) == 1
        assert result[0]["name"] == "soy sauce"
        assert result[0]["amount"] == 4.0
        assert result[0]["unit"] == "tbsp"

    def test_weight_unit_conversions_oz_and_lb(self):
        """8 oz ground beef + 0.5 lb (8 oz) ground beef = 1.0 lb (stemmed to 'beef')."""
        raw_items = [
            {"name": "ground beef", "amount": 8.0, "unit": "oz"},
            {"name": "ground beef", "amount": 0.5, "unit": "lb"},
        ]
        result = aggregate_ingredients(raw_items)
        assert len(result) == 1
        assert result[0]["name"] == "beef"
        assert result[0]["amount"] == 1.0
        assert result[0]["unit"] == "lb"
        assert result[0]["department"] == "Meat & Seafood"

    def test_incompatible_units_remain_separate_guardrail(self):
        """Guarantees non-destructive safety:

        2 cups sugar + 1 pinch sugar must remain 2 distinct rows.
        """
        raw_items = [
            {"name": "granulated sugar", "amount": 2.0, "unit": "cup"},
            {"name": "sugar", "amount": 1.0, "unit": "pinch"},
        ]
        result = aggregate_ingredients(raw_items)
        assert len(result) == 2
        units = {r["unit"] for r in result}
        assert "cup" in units
        assert "pinch" in units

    def test_empty_input_returns_empty_list(self):
        assert aggregate_ingredients([]) == []

    def test_invalid_negative_amount_defaults_to_one(self):
        raw_items = [{"name": "salt", "amount": -2.0, "unit": "tsp"}]
        result = aggregate_ingredients(raw_items)
        assert len(result) == 1
        assert result[0]["amount"] == 1.0
