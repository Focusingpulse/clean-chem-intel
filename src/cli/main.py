#!/usr/bin/env python3
"""
Clean Chem Intel CLI — analyze cleaning product ingredients.

Usage:
    python -m src.cli.main "Water, Sodium Laureth Sulfate, Fragrance"
    python -m src.cli.main --product "My Cleaner" --ingredients "Water, Sodium Laureth Sulfate"
"""
import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.core.parser import parse_ingredients
from src.core.models import ProductAnalysis
from src.core.scorer import score_product


def format_grade(grade):
    if grade is None:
        return "?"
    return grade.value if hasattr(grade, "value") else str(grade)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze cleaning product ingredients for health and environmental impact."
    )
    parser.add_argument(
        "ingredients",
        help="Comma-separated ingredient list (e.g. 'Water, Sodium Laureth Sulfate, Fragrance')",
    )
    parser.add_argument(
        "--product", "-p",
        default="Unknown Product",
        help="Product name (default: Unknown Product)",
    )
    args = parser.parse_args()

    # Parse ingredients
    ingredients = parse_ingredients(args.ingredients)

    # Create product analysis
    product = ProductAnalysis(
        product_name=args.product,
        ingredients=ingredients,
    )

    # Score
    product = score_product(product)

    # Print results
    print(f"\n{'='*60}")
    print(f"  Product: {product.product_name}")
    print(f"  Overall Grade: {format_grade(product.overall_grade)}")
    print(f"{'='*60}\n")

    print(f"  {'Ingredient':<40} {'CAS':<15} {'GHS':<20} {'Evidence'}")
    print(f"  {'-'*40} {'-'*15} {'-'*20} {'-'*10}")

    for ing in product.ingredients:
        cas = ing.cas_number or "?"
        ghs = ing.ghs_hazard or "None"
        evidence = ing.evidence_confidence.value if ing.evidence_confidence else "?"
        print(f"  {ing.name:<40} {cas:<15} {ghs:<20} {evidence}")

    if product.interaction_flags:
        print(f"\n  Interaction Flags:")
        for flag in product.interaction_flags:
            print(f"  ! {flag.flag}: {flag.concern}")

    # Print dimension grades for each ingredient
    print(f"\n  Dimension Grades:")
    print(f"  {'Ingredient':<30} {'Resp':<6} {'Derm':<6} {'Endo':<6} {'Org':<6} {'Env':<6} {'Work':<6}")
    print(f"  {'-'*30} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6}")
    for ing in product.ingredients:
        print(f"  {ing.name[:30]:<30} {format_grade(ing.respiratory_impact):<6} {format_grade(ing.dermal_impact):<6} {format_grade(ing.endocrine_impact):<6} {format_grade(ing.organ_toxicity):<6} {format_grade(ing.environmental_impact):<6} {format_grade(ing.worker_safety):<6}")

    print()


if __name__ == "__main__":
    main()
