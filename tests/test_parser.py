"""
Tests for the ingredient parser.
"""
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.parser import split_ingredient_list, match_ingredient, parse_ingredients, load_seed_data
from src.core.models import Ingredient


class TestSplitIngredientList:
    def test_simple_comma_separated(self):
        result = split_ingredient_list("Water, Sodium Laureth Sulfate, Fragrance")
        assert result == ["Water", "Sodium Laureth Sulfate", "Fragrance"]

    def test_semicolon_separated(self):
        result = split_ingredient_list("Water; Sodium Laureth Sulfate; Fragrance")
        assert result == ["Water", "Sodium Laureth Sulfate", "Fragrance"]

    def test_with_and(self):
        result = split_ingredient_list("Water, Sodium Laureth Sulfate and Fragrance")
        assert result == ["Water", "Sodium Laureth Sulfate", "Fragrance"]

    def test_empty_string(self):
        result = split_ingredient_list("")
        assert result == []

    def test_single_ingredient(self):
        result = split_ingredient_list("Water")
        assert result == ["Water"]

    def test_extra_spaces(self):
        result = split_ingredient_list("Water,  Sodium Laureth Sulfate ,   Fragrance")
        assert result == ["Water", "Sodium Laureth Sulfate", "Fragrance"]


class TestMatchIngredient:
    def test_direct_match(self):
        seed_data = {"water": Ingredient(name="Water", cas_number="7732-18-5")}
        result = match_ingredient("Water", seed_data)
        assert result is not None
        assert result.name == "Water"
        assert result.cas_number == "7732-18-5"

    def test_case_insensitive(self):
        seed_data = {"water": Ingredient(name="Water")}
        result = match_ingredient("WATER", seed_data)
        assert result is not None
        assert result.name == "Water"

    def test_synonym_match(self):
        seed_data = {"sodium lauryl sulfate": Ingredient(name="Sodium Lauryl Sulfate")}
        result = match_ingredient("SLS", seed_data)
        assert result is not None
        assert result.name == "Sodium Lauryl Sulfate"

    def test_no_match(self):
        seed_data = {"water": Ingredient(name="Water")}
        result = match_ingredient("Unknown Chemical XYZ", seed_data)
        assert result is not None  # Returns unmatched ingredient
        assert result.name == "Unknown Chemical XYZ"
        assert result.cas_number is None


class TestParseIngredients:
    def test_parse_known_ingredients(self):
        ingredients = parse_ingredients("Water, Sodium Laureth Sulfate, Fragrance")
        assert len(ingredients) == 3
        assert ingredients[0].name == "Water"
        assert ingredients[1].name == "Sodium Laureth Sulfate"
        assert ingredients[2].name == "Fragrance"

    def test_parse_mixed_known_unknown(self):
        ingredients = parse_ingredients("Water, Unknown Chemical XYZ, Citric Acid")
        assert len(ingredients) == 3
        assert ingredients[0].name == "Water"
        assert ingredients[1].name == "Unknown Chemical XYZ"
        assert ingredients[1].cas_number is None  # Unknown
        assert ingredients[2].name == "Citric Acid"

    def test_parse_empty(self):
        ingredients = parse_ingredients("")
        assert len(ingredients) == 0


class TestSeedData:
    def test_load_seed_data(self):
        seed_data = load_seed_data()
        assert len(seed_data) > 0
        assert "water" in seed_data
        assert "sodium laureth sulfate" in seed_data
        assert seed_data["water"].cas_number == "7732-18-5"
