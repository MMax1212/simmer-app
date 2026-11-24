"""Tests for US4.2.1: Implement Ingredient Name Stemming and Unit Aggregation Service.

Mapped directly to acceptance criteria in docs/tasks/sprint-4/US4.2.1.md.
"""
from __future__ import annotations

import pytest

from app.services.grocery import (
    aggregate_ingredients,
    classify_department,
    normalize_unit,
    stem_ingredient_name,
)


def test_US4_2_1_criterion_1_stem_ingredient_name():
    """Criterion 1: stem_ingredient_name strips preparation terms and singularizes nouns."""
    assert stem_ingredient_name("diced yellow onions") == "yellow onion"
    assert stem_ingredient_name("finely chopped fresh garlic") == "garlic"
    assert stem_ingredient_name("minced fresh ginger") == "ginger"
    assert stem_ingredient_name("tomatoes") == "tomato"
    assert stem_ingredient_name("berries") == "berry"
    assert stem_ingredient_name("boneless skinless chicken breasts") == "chicken breast"


def test_US4_2_1_criterion_2_normalize_unit():
    """Criterion 2: normalize_unit correctly categorizes volume, weight, and discrete units."""
    # Volume US
    canonical, family, factor = normalize_unit("tbsp")
    assert (canonical, family, factor) == ("tbsp", "volume_us", 3.0)
    canonical, family, factor = normalize_unit("cups")
    assert (canonical, family, factor) == ("cup", "volume_us", 48.0)

    # Weight US
    canonical, family, factor = normalize_unit("lbs")
    assert (canonical, family, factor) == ("lb", "weight_us", 16.0)
    canonical, family, factor = normalize_unit("oz")
    assert (canonical, family, factor) == ("oz", "weight_us", 1.0)

    # Discrete
    canonical, family, factor = normalize_unit("clove")
    assert (canonical, family, factor) == ("clove", "discrete_clove", 1.0)
    canonical, family, factor = normalize_unit("pinch")
    assert (canonical, family, factor) == ("pinch", "discrete_pinch", 1.0)


def test_US4_2_1_criterion_3_multi_recipe_aggregation_scenario_1():
    """Criterion 3: Aggregates fractional amounts across compatible units (Scenario 1)."""
    raw_items = [
        {"name": "extra virgin olive oil", "amount": 0.5, "unit": "cup", "recipe_id": 1},
        {"name": "olive oil", "amount": 0.25, "unit": "cup", "recipe_id": 2},
    ]
    results = aggregate_ingredients(raw_items)
    assert len(results) == 1
    item = results[0]
    assert item["name"] == "olive oil"
    assert item["amount"] == 0.75
    assert item["unit"] == "cup"
    assert item["department"] == "Pantry & Baking"
    assert item["source_recipe_id"] in (1, 2)


def test_US4_2_1_criterion_4_incompatible_units_remain_distinct():
    """Criterion 4: Incompatible units for same ingredient remain distinct rows."""
    raw_items = [
        {"name": "sugar", "amount": 2.0, "unit": "cup", "recipe_id": 10},
        {"name": "sugar", "amount": 1.0, "unit": "pinch", "recipe_id": 11},
    ]
    results = aggregate_ingredients(raw_items)
    assert len(results) == 2
    names = [r["name"] for r in results]
    assert names == ["sugar", "sugar"]
    units = {r["unit"] for r in results}
    assert units == {"cup", "pinch"}


def test_US4_2_1_criterion_5_classify_department():
    """Criterion 5: classify_department accurately categorizes ingredients."""
    assert classify_department("spinach") == "Produce"
    assert classify_department("salmon fillet") == "Meat & Seafood"
    assert classify_department("cheddar cheese") == "Dairy & Refrigerated"
    assert classify_department("all-purpose flour") == "Pantry & Baking"
    assert classify_department("mystery spice blend") == "Other"


def test_US4_2_1_criterion_6_performance_and_sorting():
    """Criterion 6: Aggregation completes quickly and sorts by aisle then name."""
    raw_items = [
        {"name": "flour", "amount": 1.0, "unit": "cup", "recipe_id": 1},
        {"name": "apples", "amount": 2.0, "unit": "piece", "recipe_id": 1},
        {"name": "butter", "amount": 0.5, "unit": "cup", "recipe_id": 2},
        {"name": "chicken breast", "amount": 1.0, "unit": "lb", "recipe_id": 2},
    ]
    results = aggregate_ingredients(raw_items)
    departments = [r["department"] for r in results]
    # Expected order: Produce -> Meat & Seafood -> Dairy & Refrigerated -> Pantry & Baking
    assert departments == [
        "Produce",
        "Meat & Seafood",
        "Dairy & Refrigerated",
        "Pantry & Baking",
    ]
