"""Grocery aggregation and ingredient normalization service (US4.2 / Task 4.2.1).

Implements SPK-3.1 algorithmic specifications:
1. Ingredient name stemming & noise reduction.
2. Unit normalization & dimensional arithmetic (Volume / Weight / Count).
3. Supermarket aisle / department categorization.
4. Safe aggregation without destructive or inaccurate unit coercion.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

# ---------------------------------------------------------------------------
# 1. Constants: Code-Standards.md Compliance (No Magic Numbers)
# ---------------------------------------------------------------------------
DECIMAL_PRECISION: int = 2
DEFAULT_FALLBACK_AMOUNT: float = 1.0
MIN_VALID_AMOUNT: float = 0.0

# Volume conversion factors (Base unit = teaspoon / tsp)
TSP_PER_TSP: float = 1.0
TSP_PER_TBSP: float = 3.0
TSP_PER_FL_OZ: float = 6.0
TSP_PER_CUP: float = 48.0
MIN_CUP_THRESHOLD: float = 12.0  # 1/4 cup (12 tsp / 4 tbsp)
TSP_PER_PINT: float = 96.0
TSP_PER_QUART: float = 192.0
TSP_PER_GALLON: float = 768.0
TSP_PER_ML: float = 0.202884
TSP_PER_LITER: float = 202.884

# Weight conversion factors (Base unit = ounce / oz)
OZ_PER_OZ: float = 1.0
OZ_PER_LB: float = 16.0
OZ_PER_GRAM: float = 0.035274
OZ_PER_KG: float = 35.274

# Metric scaling boundary (1000g = 1kg, 1000ml = 1L)
METRIC_KILO_THRESHOLD: float = 1000.0

# Supermarket Aisle Sort Sequence (Produce first, Other last)
DEPARTMENT_ORDER: dict[str, int] = {
    "Produce": 1,
    "Meat & Seafood": 2,
    "Dairy & Refrigerated": 3,
    "Pantry & Baking": 4,
    "Other": 5,
}

# ---------------------------------------------------------------------------
# 2. Preparation Words & Irregular Plurals for Stemming
# ---------------------------------------------------------------------------
PREP_WORDS: set[str] = {
    "diced", "chopped", "minced", "sliced", "fresh", "crushed", "grated",
    "shredded", "peeled", "cooked", "raw", "boneless", "skinless", "large",
    "medium", "small", "cloves", "clove", "stalks", "stalk", "heads", "head",
    "bunches", "bunch", "can", "cans", "leaves", "leaf", "sprigs", "sprig",
    "to taste", "optional", "finely", "roughly", "thinly", "coarsely",
    "ground", "warm", "cold", "melted", "softened", "divided", "heaping",
    "packed", "dry", "extra", "virgin",
}

IRREGULAR_PLURALS: dict[str, str] = {
    "tomatoes": "tomato",
    "potatoes": "potato",
    "berries": "berry",
    "strawberries": "strawberry",
    "blueberries": "blueberry",
    "cherries": "cherry",
    "halves": "half",
    "loaves": "loaf",
    "cloves": "clove",
    "ribs": "rib",
}


def stem_ingredient_name(name: str) -> str:
    """Normalize an ingredient name to a canonical singular form.

    Args:
        name: Raw ingredient string (e.g., "2 cups diced red onions").

    Returns:
        Stemmed canonical singular noun phrase (e.g., "red onion").

    Examples:
        - "diced onions" -> "onion"
        - "2 cloves of fresh garlic" -> "garlic"
        - "chopped fresh cilantro" -> "cilantro"
        - "boneless skinless chicken breasts" -> "chicken breast"
    """
    if not name or not name.strip():
        return ""

    # Strip punctuation and numbers; keep letters, hyphens, and whitespace
    text = name.lower().strip()
    text = re.sub(r"[^\w\s-]", " ", text)
    text = re.sub(r"\b\d+\b", " ", text)

    # Tokenize and filter out filler words and preparation descriptors
    tokens = text.split()
    filtered_tokens: list[str] = [
        token for token in tokens
        if token not in ("of", "and", "or", "for", "with", "a", "an", "the")
        and token not in PREP_WORDS
    ]

    if not filtered_tokens:
        filtered_tokens = [w for w in text.split() if w not in ("of", "a", "the")]

    if not filtered_tokens:
        return name.strip().lower()

    # Singularize the terminal word of the phrase
    last_word = filtered_tokens[-1]
    if last_word in IRREGULAR_PLURALS:
        filtered_tokens[-1] = IRREGULAR_PLURALS[last_word]
    elif last_word.endswith("ies") and len(last_word) > 4:
        filtered_tokens[-1] = last_word[:-3] + "y"
    elif last_word.endswith("es") and not last_word.endswith(
        ("cheese", "sauce", "paste", "rice", "spice")
    ):
        if last_word.endswith(("ches", "shes", "xes", "sses", "toes", "zoes")):
            filtered_tokens[-1] = last_word[:-2]
        elif last_word.endswith("ves"):
            filtered_tokens[-1] = last_word[:-3] + "f"
        else:
            filtered_tokens[-1] = last_word[:-1]
    elif last_word.endswith("s") and not last_word.endswith(("ss", "us", "is", "beans", "hummus")):
        filtered_tokens[-1] = last_word[:-1]

    return " ".join(filtered_tokens).strip()


# ---------------------------------------------------------------------------
# 3. Unit Normalization & Tables
# ---------------------------------------------------------------------------
UNIT_ALIASES: dict[str, str] = {
    # Volume: teaspoons
    "t": "tsp", "tsp": "tsp", "teaspoon": "tsp", "teaspoons": "tsp",
    # Volume: tablespoons
    "tb": "tbsp", "tbs": "tbsp", "tbsp": "tbsp", "tablespoon": "tbsp", "tablespoons": "tbsp",
    # Volume: fluid ounces
    "fl oz": "fl oz", "fluid ounce": "fl oz", "fluid ounces": "fl oz",
    # Volume: cups
    "c": "cup", "cup": "cup", "cups": "cup",
    # Volume: pints, quarts, gallons
    "pt": "pint", "pint": "pint", "pints": "pint",
    "qt": "quart", "quart": "quart", "quarts": "quart",
    "gal": "gallon", "gallon": "gallon", "gallons": "gallon",
    # Volume: metric
    "ml": "ml", "milliliter": "ml", "milliliters": "ml",
    "l": "l", "liter": "l", "liters": "l",
    # Weight: ounces
    "oz": "oz", "ounce": "oz", "ounces": "oz",
    # Weight: pounds
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb",
    # Weight: metric
    "g": "g", "gram": "g", "grams": "g",
    "kg": "kg", "kilogram": "kg", "kilograms": "kg",
    # Discrete / Count units
    "clove": "clove", "cloves": "clove",
    "pinch": "pinch", "pinches": "pinch",
    "dash": "dash", "dashes": "dash",
    "slice": "slice", "slices": "slice",
    "piece": "piece", "pieces": "piece",
    "can": "can", "cans": "can",
    "stalk": "stalk", "stalks": "stalk",
    "sprig": "sprig", "sprigs": "sprig",
    "head": "head", "heads": "head",
    "bunch": "bunch", "bunches": "bunch",
    "package": "package", "packages": "package", "pkg": "package",
}

VOLUME_FACTORS: dict[str, float] = {
    "tsp": TSP_PER_TSP,
    "tbsp": TSP_PER_TBSP,
    "fl oz": TSP_PER_FL_OZ,
    "cup": TSP_PER_CUP,
    "pint": TSP_PER_PINT,
    "quart": TSP_PER_QUART,
    "gallon": TSP_PER_GALLON,
    "ml": TSP_PER_ML,
    "l": TSP_PER_LITER,
}

WEIGHT_FACTORS: dict[str, float] = {
    "oz": OZ_PER_OZ,
    "lb": OZ_PER_LB,
    "g": OZ_PER_GRAM,
    "kg": OZ_PER_KG,
}


def normalize_unit(unit_str: str | None) -> tuple[str, str, float]:
    """Normalize a unit string into canonical name, dimensional family, and factor.

    Args:
        unit_str: Raw unit from ingredient record (e.g., "TBSP", "cups", "cloves").

    Returns:
        tuple of (canonical_unit, family_key, conversion_factor_to_base).
    """
    if not unit_str or not unit_str.strip():
        return ("", "count", 1.0)

    clean_unit = unit_str.lower().strip()
    canonical = UNIT_ALIASES.get(clean_unit, clean_unit)

    if canonical in VOLUME_FACTORS:
        family = "volume_metric" if canonical in ("ml", "l") else "volume_us"
        return (canonical, family, VOLUME_FACTORS[canonical])

    if canonical in WEIGHT_FACTORS:
        family = "weight_metric" if canonical in ("g", "kg") else "weight_us"
        return (canonical, family, WEIGHT_FACTORS[canonical])

    return (canonical, f"discrete_{canonical}", 1.0)


def choose_best_display_unit(
    family: str, base_amount: float, original_canonical: str
) -> tuple[float, str]:
    """Format accumulated base amounts into clean, human-readable grocery units.

    Args:
        family: Dimensional family (volume_us, weight_us, volume_metric, etc.).
        base_amount: Accumulated sum in family base unit (tsp for volume, oz for weight).
        original_canonical: Original unit string to preserve for discrete items.

    Returns:
        tuple of (scaled_amount, display_unit).
    """
    if family == "volume_us":
        if base_amount >= TSP_PER_CUP or original_canonical == "cup":
            cups = base_amount / TSP_PER_CUP
            return (round(cups, DECIMAL_PRECISION), "cup")
        if base_amount >= TSP_PER_TBSP:
            tbsp = base_amount / TSP_PER_TBSP
            return (round(tbsp, DECIMAL_PRECISION), "tbsp")
        return (round(base_amount, DECIMAL_PRECISION), "tsp")

    if family == "volume_metric":
        ml = base_amount / TSP_PER_ML
        if ml >= METRIC_KILO_THRESHOLD:
            return (round(ml / METRIC_KILO_THRESHOLD, DECIMAL_PRECISION), "l")
        return (round(ml, DECIMAL_PRECISION), "ml")

    if family == "weight_us":
        if base_amount >= OZ_PER_LB:
            lbs = base_amount / OZ_PER_LB
            return (round(lbs, DECIMAL_PRECISION), "lb")
        return (round(base_amount, DECIMAL_PRECISION), "oz")

    if family == "weight_metric":
        grams = base_amount / OZ_PER_GRAM
        if grams >= METRIC_KILO_THRESHOLD:
            return (round(grams / METRIC_KILO_THRESHOLD, DECIMAL_PRECISION), "kg")
        return (round(grams, DECIMAL_PRECISION), "g")

    return (round(base_amount, DECIMAL_PRECISION), original_canonical)


# ---------------------------------------------------------------------------
# 4. Supermarket Aisle / Department Mapping
# ---------------------------------------------------------------------------
DEPARTMENT_MAP: dict[str, set[str]] = {
    "Produce": {
        "onion", "garlic", "tomato", "potato", "carrot", "bell pepper", "chili pepper",
        "lemon", "lime", "apple", "banana", "spinach", "lettuce", "basil",
        "cilantro", "parsley", "ginger", "avocado", "mushroom", "cucumber",
        "celery", "rosemary", "thyme", "zucchini", "broccoli", "scallion",
        "shallot", "jalapeno", "cabbage", "kale", "mint", "dill", "chive",
        "berry", "strawberry", "blueberry", "orange", "corn",
    },
    "Meat & Seafood": {
        "chicken", "chicken breast", "chicken thigh", "beef", "ground beef",
        "pork", "pork chop", "turkey", "lamb", "bacon", "sausage", "steak",
        "fish", "salmon", "tuna", "shrimp", "cod", "tilapia", "crab",
        "lobster", "prosciutto", "ham", "pancetta", "anchovy", "meat",
    },
    "Dairy & Refrigerated": {
        "milk", "butter", "cheese", "cheddar", "mozzarella", "parmesan",
        "heavy cream", "cream", "yogurt", "egg", "sour cream", "cream cheese",
        "mayo", "mayonnaise", "tofu", "ricotta", "feta", "ghee",
    },
    "Pantry & Baking": {
        "oil", "olive oil", "vegetable oil", "canola oil", "sesame oil",
        "flour", "sugar", "brown sugar", "salt", "black pepper", "baking powder",
        "baking soda", "yeast", "vanilla", "cocoa", "rice", "pasta", "noodle",
        "spaghetti", "vinegar", "balsamic vinegar", "soy sauce", "broth",
        "chicken broth", "beef broth", "stock", "cumin", "cinnamon",
        "paprika", "oregano", "honey", "mustard", "bean", "black bean",
        "chickpea", "tomato paste", "tomato sauce", "breadcrumbs", "oats",
        "cornstarch", "curry powder", "chili powder", "garlic powder", "onion powder",
    },
}


def classify_department(ingredient_name: str) -> str:
    """Determine the supermarket aisle department for an ingredient name.

    Args:
        ingredient_name: Normalized ingredient name string.

    Returns:
        One of 'Produce', 'Meat & Seafood', 'Dairy & Refrigerated',
        'Pantry & Baking', or 'Other'.
    """
    stemmed = stem_ingredient_name(ingredient_name)
    targets = [stemmed, ingredient_name.lower()] if stemmed else [ingredient_name.lower()]

    for dept, keywords in DEPARTMENT_MAP.items():
        for keyword in keywords:
            for target in targets:
                if re.search(r"\b" + re.escape(keyword) + r"\b", target):
                    return dept

    return "Other"


# ---------------------------------------------------------------------------
# 5. Core Aggregation Orchestration
# ---------------------------------------------------------------------------
def aggregate_ingredients(
    raw_items: list[Mapping[str, Any] | Any]
) -> list[dict[str, Any]]:
    """Aggregate raw recipe ingredients into a consolidated, categorized grocery list.

    Args:
        raw_items: Collection of ingredient dicts or objects with 'name',
                   'amount', 'unit', and optional 'recipe_id' / 'source_recipe_id'.

    Returns:
        List of aggregated grocery item dictionaries sorted by aisle.
    """
    if not raw_items:
        return []

    groups: dict[tuple[str, str], dict[str, Any]] = {}

    for item in raw_items:
        raw_name = (
            getattr(item, "name", None)
            or (item.get("name") if isinstance(item, Mapping) else "")
        )
        raw_amount = (
            getattr(item, "amount", None)
            if not isinstance(item, Mapping)
            else item.get("amount")
        )
        raw_unit = (
            getattr(item, "unit", None)
            if not isinstance(item, Mapping)
            else item.get("unit")
        )
        source_id = (
            getattr(item, "recipe_id", None)
            or getattr(item, "source_recipe_id", None)
            or (
                item.get("recipe_id") or item.get("source_recipe_id")
                if isinstance(item, Mapping)
                else None
            )
        )

        stemmed_name = stem_ingredient_name(str(raw_name))
        if not stemmed_name:
            continue

        try:
            amt = float(raw_amount) if raw_amount is not None else DEFAULT_FALLBACK_AMOUNT
            if amt <= MIN_VALID_AMOUNT:
                amt = DEFAULT_FALLBACK_AMOUNT
        except (ValueError, TypeError):
            amt = DEFAULT_FALLBACK_AMOUNT

        canonical_unit, family, factor = normalize_unit(raw_unit)
        base_amount = amt * factor

        group_key = (stemmed_name, family)

        if group_key not in groups:
            groups[group_key] = {
                "name": stemmed_name,
                "family": family,
                "base_amount": 0.0,
                "original_canonical": canonical_unit,
                "source_recipe_id": source_id,
            }

        groups[group_key]["base_amount"] += base_amount
        if groups[group_key]["source_recipe_id"] is None and source_id is not None:
            groups[group_key]["source_recipe_id"] = source_id

    aggregated_list: list[dict[str, Any]] = []
    for (stemmed_name, family), data in groups.items():
        disp_amount, disp_unit = choose_best_display_unit(
            family, data["base_amount"], data["original_canonical"]
        )
        dept = classify_department(stemmed_name)

        aggregated_list.append({
            "name": stemmed_name,
            "amount": disp_amount,
            "unit": disp_unit,
            "department": dept,
            "source_recipe_id": data["source_recipe_id"],
        })

    aggregated_list.sort(
        key=lambda x: (DEPARTMENT_ORDER.get(x["department"], 99), x["name"])
    )
    return aggregated_list
