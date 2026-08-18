"""
Seed the SQLite database with BMVC's known products and ingredients.

Run: python3 -m src.core.seed_db
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.core.database import init_db, upsert_ingredient, insert_product, link_product_ingredient, DB_PATH
from src.core.models import Ingredient, Grade, EvidenceLevel
from src.core.parser import load_seed_data
from src.core.scorer import score_ingredient


def seed():
    """Initialize and populate the database."""
    # Remove old DB for clean start
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = init_db()

    # Load ingredients from seed CSV and score them
    seed_data = load_seed_data()
    ingredient_ids = {}
    for name, ingredient in seed_data.items():
        scored = score_ingredient(ingredient)
        iid = upsert_ingredient(conn, scored)
        ingredient_ids[name] = iid

    # Add isopropyl alcohol (not in seed CSV yet)
    isopropyl = Ingredient(
        name="Isopropyl Alcohol",
        cas_number="67-63-0",
        pubchem_cid=3776,
        ghs_hazard="H225,H319,H336",
        summary="Highly flammable. Eye irritant. May cause drowsiness or dizziness. Common disinfectant.",
        is_volatile=True,
    )
    scored = score_ingredient(isopropyl)
    iso_id = upsert_ingredient(conn, scored)

    # Add castile soap (Dr. Bronner's style — saponified oils)
    castile = Ingredient(
        name="Castile Soap",
        cas_number=None,
        pubchem_cid=None,
        ghs_hazard="H315,H319",
        summary="Saponified vegetable oils. Mild skin and eye irritant. Biodegradable. Low overall hazard — one of the safest cleaning surfactants.",
        is_surfactant=True,
        is_biodegradable=True,
    )
    scored = score_ingredient(castile)
    castile_id = upsert_ingredient(conn, scored)

    # Add spring water (same as water but labeled for BMVC context)
    spring_water = Ingredient(
        name="Spring Water",
        cas_number="7732-18-5",
        pubchem_cid=962,
        ghs_hazard=None,
        summary="Natural spring water used as solvent base in homemade cleaning mixtures. No hazard.",
        is_biodegradable=True,
    )
    scored = score_ingredient(spring_water)
    water_id = upsert_ingredient(conn, scored)

    # Add Now brand essential oils (common ones used in cleaning)
    essential_oils = {
        "Tea Tree Oil": {
            "cas": "85085-48-9",
            "cid": None,
            "ghs": "H304,H315,H317,H335,H412",
            "summary": "Tea tree essential oil. Skin sensitizer. Aspiration hazard. Respiratory irritant. Mild aquatic toxicity. Antimicrobial properties — common in natural cleaning.",
            "volatile": True,
            "sensitizer": True,
        },
        "Lavender Oil": {
            "cas": "8000-28-0",
            "cid": None,
            "ghs": "H315,H317,H319",
            "summary": "Lavender essential oil. Skin sensitizer and eye irritant. Generally low hazard but can cause allergic dermatitis in sensitive individuals.",
            "volatile": True,
            "sensitizer": True,
        },
        "Lemon Oil": {
            "cas": "8008-56-8",
            "cid": None,
            "ghs": "H226,H304,H315,H317,H400",
            "summary": "Lemon essential oil. Contains limonene. Flammable. Skin sensitizer. Aspiration hazard. Very toxic to aquatic life.",
            "volatile": True,
            "sensitizer": True,
        },
        "Peppermint Oil": {
            "cas": "8006-90-4",
            "cid": None,
            "ghs": "H315,H317,H319,H335",
            "summary": "Peppermint essential oil. Skin and eye irritant. Respiratory irritant. Can cause sensitization with repeated exposure.",
            "volatile": True,
            "sensitizer": True,
        },
        "Eucalyptus Oil": {
            "cas": "8000-48-4",
            "cid": None,
            "ghs": "H304,H315,H317,H335",
            "summary": "Eucalyptus essential oil. Skin sensitizer. Aspiration hazard. Respiratory irritant. Toxic to pets — especially cats.",
            "volatile": True,
            "sensitizer": True,
        },
    }

    oil_ids = {}
    for name, info in essential_oils.items():
        oil = Ingredient(
            name=name,
            cas_number=info["cas"],
            pubchem_cid=info["cid"],
            ghs_hazard=info["ghs"],
            summary=info["summary"],
            is_volatile=info["volatile"],
            is_sensitizer=info["sensitizer"],
            is_aquatic_toxic="H400" in info["ghs"] or "H412" in info["ghs"],
        )
        scored = score_ingredient(oil)
        oil_ids[name] = upsert_ingredient(conn, scored)

    # Add Norwex microfiber cloth (tool, not chemical — tracked for completeness)
    norwex = Ingredient(
        name="Norwex Microfiber Cloth",
        cas_number=None,
        pubchem_cid=None,
        ghs_hazard=None,
        summary="Microfiber cleaning cloth. No chemical hazard — physical cleaning only. Reduces need for chemical cleaners. No ingredients to analyze.",
    )
    scored = score_ingredient(norwex)
    norwex_id = upsert_ingredient(conn, scored)

    # Add pumice stone (tool, not chemical)
    pumice = Ingredient(
        name="Pumice Stone",
        cas_number=None,
        pubchem_cid=None,
        ghs_hazard=None,
        summary="Natural volcanic rock used as abrasive. No chemical hazard — physical scrubbing only.",
    )
    scored = score_ingredient(pumice)
    pumice_id = upsert_ingredient(conn, scored)

    # --- Products ---

    # 1. Isopropyl Alcohol (standalone)
    p1 = insert_product(conn, "Isopropyl Alcohol", brand="TBD", category="Disinfectant",
                        notes="BMVC uses isopropyl alcohol for disinfection. Exact brand TBD.")
    link_product_ingredient(conn, p1, iso_id, 0, "Isopropyl Alcohol")

    # 2. Castile Soap (homemade base)
    p2 = insert_product(conn, "Castile Soap Cleaning Mixture", brand="Dr. Bronner's",
                        category="All-Purpose Cleaner",
                        notes="Homemade mixture. Exact recipe TBD — Chris will provide details.")
    link_product_ingredient(conn, p2, castile_id, 0, "Castile Soap")
    link_product_ingredient(conn, p2, water_id, 1, "Spring Water")

    # 3. Essential Oil Cleaning Spray (homemade)
    p3 = insert_product(conn, "Essential Oil Cleaning Spray", brand="Homemade",
                        category="All-Purpose Cleaner",
                        notes="Homemade mixture with Now brand essential oils. Exact recipe and oil types TBD.")
    link_product_ingredient(conn, p3, water_id, 0, "Spring Water")
    link_product_ingredient(conn, p3, iso_id, 1, "Isopropyl Alcohol")
    # Link all essential oils — Chris will specify which ones per recipe
    for i, (name, oid) in enumerate(oil_ids.items()):
        link_product_ingredient(conn, p3, oid, 2 + i, name)

    # 4. Norwex + Water (physical cleaning)
    p4 = insert_product(conn, "Norwex + Water Cleaning", brand="Norwex",
                        category="Physical Cleaning",
                        notes="Microfiber cloth with water only — no chemicals. Used for surfaces where chemical cleaners are unnecessary.")
    link_product_ingredient(conn, p4, norwex_id, 0, "Norwex Microfiber Cloth")
    link_product_ingredient(conn, p4, water_id, 1, "Spring Water")

    # 5. Pumice Stone (physical cleaning)
    p5 = insert_product(conn, "Pumice Stone Scrubbing", brand="N/A",
                        category="Physical Cleaning",
                        notes="Pumice stone for hard water stains and scrubbing. No chemicals.")
    link_product_ingredient(conn, p5, pumice_id, 0, "Pumice Stone")

    # Print summary
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ingredients")
    ing_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products")
    prod_count = cursor.fetchone()[0]

    print(f"Database seeded: {ing_count} ingredients, {prod_count} products")
    print(f"DB location: {DB_PATH}")
    print()
    print("Products:")
    cursor.execute("SELECT id, name, brand, category FROM products ORDER BY id")
    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[1]} ({row[2]}) — {row[3]}")

    print()
    print("Ingredients with hazard data:")
    cursor.execute("SELECT name, ghs_hazard, evidence_confidence FROM ingredients WHERE ghs_hazard IS NOT NULL ORDER BY name")
    for row in cursor.fetchall():
        print(f"  {row[0]:<35} GHS: {row[1]:<25} Evidence: {row[2]}")

    conn.close()


if __name__ == "__main__":
    seed()
