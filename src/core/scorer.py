"""
Scoring engine — assigns grades to ingredients and overall product grades.

Scoring is transparent: every grade traces to a data source and a rule.
See docs/scoring-rubric.md for the full rubric.
"""
from .models import Grade, Ingredient, InteractionFlag, ProductAnalysis, EvidenceLevel


# GHS hazard statement -> dimension impact mapping
# See https://pubchem.ncbi.nlm.nih.gov/ghs/ for full H-statement definitions
GHS_TO_GRADES = {
    # H314 (severe skin burns) -> dermal F, respiratory C
    "H314": {"dermal_impact": Grade.F, "worker_safety": Grade.D},
    # H318 (serious eye damage) -> dermal D
    "H318": {"dermal_impact": Grade.D},
    # H315 (skin irritation) -> dermal C
    "H315": {"dermal_impact": Grade.C},
    # H317 (skin sensitization) -> dermal D
    "H317": {"dermal_impact": Grade.D, "is_sensitizer": True},
    # H319 (eye irritation) -> dermal C
    "H319": {"dermal_impact": Grade.C},
    # H335 (respiratory irritation) -> respiratory C
    "H335": {"respiratory_impact": Grade.C},
    # H304 (aspiration hazard) -> respiratory D
    "H304": {"respiratory_impact": Grade.D},
    # H302 (harmful if swallowed) -> organ C
    "H302": {"organ_toxicity": Grade.C},
    # H228 (flammable solid) -> worker safety C
    "H228": {"worker_safety": Grade.C},
    # H225 (highly flammable) -> worker safety C
    "H225": {"worker_safety": Grade.C},
    # H226 (flammable) -> worker safety B
    "H226": {"worker_safety": Grade.B},
    # H290 (corrosive to metals) -> worker safety C
    "H290": {"worker_safety": Grade.C},
    # H400 (very toxic to aquatic life) -> environmental F
    "H400": {"environmental_impact": Grade.F, "is_aquatic_toxic": True},
    # H412 (harmful to aquatic life) -> environmental C
    "H412": {"environmental_impact": Grade.C, "is_aquatic_toxic": True},
}


def score_ingredient(ingredient: Ingredient) -> Ingredient:
    """
    Score an ingredient based on its GHS hazard data and known properties.
    Updates the ingredient's grade fields in place and returns it.
    """
    if not ingredient.ghs_hazard:
        # No GHS data — can't score, leave as None
        return ingredient

    hazard_codes = [h.strip() for h in ingredient.ghs_hazard.split(",")]

    for code in hazard_codes:
        if code in GHS_TO_GRADES:
            impacts = GHS_TO_GRADES[code]
            for field, value in impacts.items():
                if field == "is_sensitizer":
                    ingredient.is_sensitizer = True
                elif field == "is_aquatic_toxic":
                    ingredient.is_aquatic_toxic = True
                elif field.startswith("_"):
                    continue
                else:
                    # Only update if not already set to something worse
                    current = getattr(ingredient, field, None)
                    if current is None or _grade_worse(value, current):
                        setattr(ingredient, field, value)

    # Set evidence confidence based on data availability
    if ingredient.pubchem_cid and ingredient.ghs_hazard:
        ingredient.evidence_confidence = EvidenceLevel.MEDIUM
    elif ingredient.ghs_hazard:
        ingredient.evidence_confidence = EvidenceLevel.LOW
    else:
        ingredient.evidence_confidence = EvidenceLevel.EXTRAPOLATED

    return ingredient


def _grade_worse(new: Grade, current: Grade) -> bool:
    """Return True if new grade is worse than current."""
    order = {Grade.A: 0, Grade.B: 1, Grade.C: 2, Grade.D: 3, Grade.F: 4}
    return order.get(new, 0) > order.get(current, 0)


def check_interactions(ingredients: list[Ingredient]) -> list[InteractionFlag]:
    """
    Check for interaction flags between ingredients.
    See docs/scoring-rubric.md for interaction rules.
    """
    flags = []

    has_penetration_enhancer = any(i.is_penetration_enhancer for i in ingredients)
    has_sensitizer = any(i.is_sensitizer for i in ingredients)
    has_volatile = any(i.is_volatile for i in ingredients)
    has_respiratory_irritant = any(
        i.respiratory_impact and _grade_worse(i.respiratory_impact, Grade.B) for i in ingredients
    )
    has_non_biodegradable = any(i.is_biodegradable is False for i in ingredients)
    has_aquatic_toxic = any(i.is_aquatic_toxic for i in ingredients)
    has_surfactant = any(i.is_surfactant for i in ingredients)
    has_known_irritant = any(
        i.dermal_impact and _grade_worse(i.dermal_impact, Grade.B) for i in ingredients
    )

    if has_penetration_enhancer and has_sensitizer:
        flags.append(InteractionFlag(
            flag="Dermal absorption risk",
            trigger="Penetration enhancer + sensitizer present",
            concern="More of the sensitizer may reach systemic circulation",
        ))

    if has_volatile and has_respiratory_irritant:
        flags.append(InteractionFlag(
            flag="Indoor air quality",
            trigger="Volatile organic + respiratory irritant",
            concern="Combined effect on airway during use",
        ))

    if has_non_biodegradable and has_aquatic_toxic:
        flags.append(InteractionFlag(
            flag="Environmental persistence",
            trigger="Non-biodegradable + aquatic toxic",
            concern="Long-term ecosystem impact",
        ))

    if has_surfactant and has_known_irritant:
        flags.append(InteractionFlag(
            flag="Compounded irritation",
            trigger="Surfactant + known irritant",
            concern="Enhanced penetration of irritant through skin/mucosa",
        ))

    return flags


def score_product(product: ProductAnalysis) -> ProductAnalysis:
    """
    Score all ingredients in a product and compute the overall product grade.
    """
    # Score each ingredient
    product.ingredients = [score_ingredient(i) for i in product.ingredients]

    # Check for interaction flags
    product.interaction_flags = check_interactions(product.ingredients)

    # Compute overall grade:
    # The overall grade is the worst dimension grade supported by
    # Medium or higher evidence confidence.
    grade_order = {Grade.A: 0, Grade.B: 1, Grade.C: 2, Grade.D: 3, Grade.F: 4}
    dimensions = [
        "respiratory_impact",
        "dermal_impact",
        "endocrine_impact",
        "organ_toxicity",
        "environmental_impact",
        "worker_safety",
    ]

    worst = Grade.A
    for ingredient in product.ingredients:
        if ingredient.evidence_confidence in (EvidenceLevel.HIGH, EvidenceLevel.MEDIUM):
            for dim in dimensions:
                grade = getattr(ingredient, dim, None)
                if grade and grade_order.get(grade, 0) > grade_order.get(worst, 0):
                    worst = grade

    product.overall_grade = worst
    return product
