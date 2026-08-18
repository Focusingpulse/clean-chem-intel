"""
Ingredient parser — takes a raw ingredient string and returns matched ingredients.

Example:
    "Water, Sodium Laureth Sulfate, Fragrance"
    -> [Ingredient("Water", ...), Ingredient("Sodium Laureth Sulfate", ...), Ingredient("Fragrance", ...)]
"""
import csv
import re
from pathlib import Path
from typing import Optional

from .models import Ingredient


SEED_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "seeds" / "ingredients.csv"


# Common synonyms / alternate names -> canonical name
SYNONYMS = {
    "sles": "Sodium Laureth Sulfate",
    "sls": "Sodium Lauryl Sulfate",
    "naoh": "Sodium Hydroxide",
    "lye": "Sodium Hydroxide",
    "caustic soda": "Sodium Hydroxide",
    "quat": "Quaternary Ammonium Compounds (DDAC)",
    "ddac": "Quaternary Ammonium Compounds (DDAC)",
    "alcohol": "Ethanol",
    "ethanol alcohol": "Ethanol",
    "h2o2": "Hydrogen Peroxide",
    "bleach": "Hydrogen Peroxide",  # contextual — may need refinement
    "citrus extract": "Limonene",
    "d-limonene": "Limonene",
}


def load_seed_data(path: Path = SEED_DATA_PATH) -> dict[str, Ingredient]:
    """Load seed ingredient data from CSV into a lookup dict keyed by lowercase name."""
    ingredients = {}
    if not path.exists():
        return ingredients
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            ingredient = Ingredient(
                name=name,
                cas_number=row.get("cas_number") or None,
                pubchem_cid=int(row["pubchem_cid"]) if row.get("pubchem_cid") and row["pubchem_cid"] != "N/A" else None,
                ghs_hazard=row.get("ghs_hazard") or None,
                summary=row.get("summary") or None,
            )
            ingredients[name.lower()] = ingredient
    return ingredients


def normalize_name(name: str) -> str:
    """Normalize an ingredient name for matching."""
    name = name.strip().lower()
    # Remove common filler words
    name = re.sub(r"\s+", " ", name)
    return name


def split_ingredient_list(ingredient_string: str) -> list[str]:
    """
    Split a raw ingredient list string into individual ingredient names.
    Handles commas, semicolons, and 'and' as separators.
    Removes parenthetical content that isn't part of the ingredient name
    (but keeps it for reference).
    """
    # Replace semicolons and ' and ' with commas
    normalized = re.sub(r"\s*;\s*", ",", ingredient_string)
    normalized = re.sub(r"\s+and\s+", ",", normalized, flags=re.IGNORECASE)
    # Split on commas
    parts = [p.strip() for p in normalized.split(",")]
    # Filter empty strings
    parts = [p for p in parts if p]
    return parts


def match_ingredient(name: str, seed_data: dict[str, Ingredient]) -> Optional[Ingredient]:
    """
    Try to match an ingredient name against known ingredients.
    Returns a matched Ingredient or None if no match found.
    """
    normalized = normalize_name(name)

    # Direct match
    if normalized in seed_data:
        return seed_data[normalized]

    # Synonym match
    if normalized in SYNONYMS:
        canonical = SYNONYMS[normalized].lower()
        if canonical in seed_data:
            return seed_data[canonical]

    # Partial / fuzzy match — check if the name contains a known ingredient
    for known_name, ingredient in seed_data.items():
        if known_name in normalized or normalized in known_name:
            return ingredient

    # No match found — return an unmatched ingredient
    return Ingredient(name=name.strip(), evidence_confidence=None)  # type: ignore[arg-type]


def parse_ingredients(ingredient_string: str, seed_data: Optional[dict] = None) -> list[Ingredient]:
    """
    Parse a raw ingredient string into a list of Ingredient objects.

    Args:
        ingredient_string: Raw ingredient list, e.g. "Water, Sodium Laureth Sulfate, Fragrance"
        seed_data: Optional pre-loaded seed data dict. If None, loads from CSV.

    Returns:
        List of matched/unmatched Ingredient objects.
    """
    if seed_data is None:
        seed_data = load_seed_data()

    parts = split_ingredient_list(ingredient_string)
    results = []
    for part in parts:
        matched = match_ingredient(part, seed_data)
        if matched:
            results.append(matched)
        else:
            # Unmatched ingredient — still include it, flagged as unknown
            results.append(Ingredient(name=part))
    return results
