#!/usr/bin/env python3
"""Night-shift station 2 harvest, 2026-09-28 (Dolman).

Ordered by EXPOSURE, not price tier (Trellis, Sep 22 2026). Each ingredient list
below was read from a manufacturer filing read TODAY:

  * Walmart's own SB-258 ingredient-disclosure PDF (hosted on Walmart's CDN) for
    the two Great Value products. Manufacturer of record Vi-Jon, Inc.;
    distributor Walmart, Inc.
  * DailyMed's FDA OTC label for the Great Value antibacterial hand soap.
  * Sam's Club / Sam's West SB-258 ingredient-disclosure PDFs (hosted on the
    Sam's Club CDN) for the two Member's Mark products. Manufacturers of record
    Rockline Industries and Henkel Corporation.

Why these four: Walmart and Sam's Club store brands were entirely absent from
this database, and they are the single highest-exposure additions available.
Great Value is Walmart's flagship private label and Walmart is the largest
grocery retailer in the US; Member's Mark is the club-channel equivalent. The
thin channel tiers (dollar-store 4, drugstore 5) were examined first and
produced no new verifiable list tonight -- which is the dollar-store tier's own
documented finding, not an oversight. See the station-2 finding.

Nothing here is graded. Product grading is the Sifter lane; a blank as-sold
grade is the honest state.

Idempotent: a product whose `name` already exists is skipped, and an ingredient
key already present is left untouched. Run it twice; the second run reports 0.

Usage:  python3 tools/harvest_2026_09_28.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TODAY = "2026-09-28"

DRY = "--dry-run" in sys.argv

ING_NOTE = (
    "Listed in a manufacturer or manufacturer-filing disclosure read 2026-09-28; "
    "not yet graded against GHS."
)

WALMART_SRC = "https://corporate.walmart.com/about"

# --------------------------------------------------------------------------
# 1. Great Value Ultra Dishwashing Liquid, Original Scent
#    Source read today (pdftotext of the manufacturer filing):
#    https://i5.walmartimages.com/dfw/4ff9c6c9-d468/k2-_0a8f4faf-fd70-404d-9091-dd8469843856.v1.pdf
#    SB-258 disclosure dated 2019-08-12. 14 lines, CAS numbers present.
# --------------------------------------------------------------------------
GV_DISH_INGS = [
    "Water",
    "Sodium Laureth Sulfate",
    "Sodium Lauryl Sulfate",
    "Isopropylideneglycerol",
    "Lauramine Oxide",
    "Sodium Xylenesulfonate",
    "Fragrance",
    "Limonene",
    "Hexyl Cinnamal",
    "Methylisothiazolinone",
    "Methylchloroisothiazolinone",
    "Sodium Chloride",
    "Citric Acid",
    "Blue 1",
]

# --------------------------------------------------------------------------
# 2. Great Value Ultra Dish Liquid Antibacterial Hand Soap, Crisp Apple
#    Source read today (FDA OTC label, NDC 79903-136, labeler Walmart Inc.):
#    https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c092e30e-bd7a-4c31-95d5-3edc2170a185
#    Active chloroxylenol 0.3%. The label prints the two isothiazolinone
#    preservatives on one line; recorded under the two existing keys.
# --------------------------------------------------------------------------
GV_HAND_INGS = [
    "Chloroxylenol",
    "Water",
    "Sodium C10-16 Alkylbenzene Sulfonate",
    "Sodium Laureth Sulfate",
    "Cocamidopropyl Betaine",
    "Sodium Lauryl Sulfate",
    "Sodium Xylenesulfonate",
    "Propylene Glycol",
    "Sodium Chloride",
    "Fragrance",
    "Citric Acid",
    "Tetrasodium EDTA",
    "Methylisothiazolinone",
    "Methylchloroisothiazolinone",
    "Yellow 5",
    "Blue 1",
]

# --------------------------------------------------------------------------
# 3. Member's Mark Hard Surface Disinfecting Wipes
#    Source read today (SB-258, disclosed 2019-06-28, Level 1 non-fragrance /
#    Level 3 fragrance):
#    https://scene7.samsclub.com/is/content/samsclub/members-mark-ingredient-disclosure
#    Four quaternary ammonium actives named individually.
# --------------------------------------------------------------------------
MM_WIPES_INGS = [
    "Water",
    "Alkyl (50% C14, 40% C12, 10% C16) Dimethyl Benzyl Ammonium Chloride",
    "Secondary Alcohol Ethoxylate",
    "Octyl Decyl Dimethyl Ammonium Chloride",
    "Tetrasodium EDTA",
    "Didecyl Dimethyl Ammonium Chloride",
    "Sodium Silicate Pentahydrate",
    "Dioctyl Dimethyl Ammonium Chloride",
    "Fragrance",
    "Limonene",
]

# --------------------------------------------------------------------------
# 4. Member's Mark Ultimate Clean Dishwasher Pacs, Fresh Scent
#    Source read today (SB-258, disclosed 2019-11-08):
#    https://scene7.samsclub.com/is/content/samsclub/193968008505_pdf
#    Manufacturer of record Henkel Corporation. Two enzymes carry EU
#    respiratory-sensitizer and AOEC asthmagen listings on the filing itself.
# --------------------------------------------------------------------------
MM_DW_INGS = [
    "Sodium Sulfate",
    "Sodium Carbonate",
    "Sodium Carbonate Peroxide",
    "Water",
    "Trisodium Dicarboxymethyl Alaninate",
    "Sodium Citrate",
    "Sodium Carboxylate",
    "Ethoxylated Alcohol",
    "Polyvinyl Alcohol",
    "Protease",
    "Sodium Silicate",
    "Sodium Hydroxide",
    "Amylase",
    "Colorant",
    "Fragrance",
    "Limonene",
]

PRODUCTS = [
    {
        "name": "Great Value Ultra Dishwashing Liquid, Original Scent",
        "brand": "Great Value",
        "cat": "Dish Soap",
        "safe": None,
        "ings": GV_DISH_INGS,
        "heritage": False,
        "source": (
            "Walmart's own SB-258 ingredient-disclosure filing for this product, "
            "published under the California Cleaning Product Right to Know Act and "
            "hosted on Walmart's CDN (disclosure dated 2019-08-12, UPCs "
            "0007874218697 / 0007874218698 / 0007874213591). Manufacturer of record "
            "Vi-Jon, Inc.; distributor Walmart, Inc. Fourteen lines with CAS numbers. "
            "The two isothiazolinone preservatives and two EU fragrance allergens "
            "(limonene, hexyl cinnamal) are named individually."
        ),
        "source_url": "https://i5.walmartimages.com/dfw/4ff9c6c9-d468/k2-_0a8f4faf-fd70-404d-9091-dd8469843856.v1.pdf",
        "note": (
            "Walmart's flagship private-label dish soap, and the highest-exposure "
            "product this database did not carry. A store brand, not a brand-name "
            "one, which is the point: this is what most homes actually wash dishes "
            "with. Entered ungraded: product grading is the Sifter lane."
        ),
        "owner": "Walmart Inc.",
        "tier": "grocery",
        "tier_ev": "reported",
        "tier_src": WALMART_SRC,
        "tier_note": "Retailer private label, grocery channel. Market-position value is 'mass'.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 20,
        "exposure_ev": "extrapolated",
        "exposure_src": WALMART_SRC,
        "exposure_basis": (
            "Derived, not measured. Liquid dish soap is owned by over 95% of US "
            "households (category penetration), and Walmart's own corporate page "
            "states approximately 280 million customers and members visit more than "
            "10,900 stores and clubs each week. Great Value is Walmart's flagship "
            "private label. Searched for a published household-penetration or "
            "brand-share figure for the Great Value dish-soap SKU and located none; "
            "private-label share is not published at SKU level. One significant "
            "figure, order-of-magnitude."
        ),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "full",
    },
    {
        "name": "Great Value Ultra Dish Liquid Antibacterial Hand Soap, Crisp Apple",
        "brand": "Great Value",
        "cat": "Hand Soap",
        "safe": None,
        "ings": GV_HAND_INGS,
        "heritage": False,
        "source": (
            "FDA OTC drug label filed at DailyMed, NDC 79903-136, labeler and "
            "packager Walmart Inc. Active chloroxylenol 0.3%; 15 inactive "
            "ingredients named. Read today from the DailyMed label page."
        ),
        "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=c092e30e-bd7a-4c31-95d5-3edc2170a185",
        "note": (
            "A Walmart private-label antibacterial hand soap that discloses a full "
            "active-plus-inactive list only because it is an FDA drug. The same "
            "finding the dollar-store tier produced, repeated at the largest US "
            "retailer: disclosure follows regulatory force. Entered ungraded."
        ),
        "owner": "Walmart Inc.",
        "tier": "grocery",
        "tier_ev": "reported",
        "tier_src": WALMART_SRC,
        "tier_note": "Retailer private label, grocery channel.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 15,
        "exposure_ev": "extrapolated",
        "exposure_src": WALMART_SRC,
        "exposure_basis": (
            "Derived, not measured. Antibacterial hand soap is a near-universal "
            "household category and this is the largest US retailer's private label; "
            "Walmart's corporate page states approximately 280 million customer and "
            "member visits a week. Searched for a published SKU-level household "
            "figure for Great Value hand soap and located none. One significant "
            "figure, order-of-magnitude."
        ),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "full",
    },
    {
        "name": "Member's Mark Hard Surface Disinfecting Wipes",
        "brand": "Member's Mark",
        "cat": "Disinfectant",
        "safe": None,
        "ings": MM_WIPES_INGS,
        "heritage": False,
        "source": (
            "Sam's Club / Sam's West SB-258 ingredient-disclosure filing for this "
            "product (disclosure dated 2019-06-28, UPC 00078742031989), hosted on the "
            "Sam's Club CDN. Manufacturer of record Rockline Industries; distributor "
            "Sam's West, Inc. Level 1 non-fragrance disclosure (full) with a Level 3 "
            "fragrance disclosure. Four quaternary ammonium actives named "
            "individually, plus limonene as the named fragrance allergen."
        ),
        "source_url": "https://scene7.samsclub.com/is/content/samsclub/members-mark-ingredient-disclosure",
        "note": (
            "The club-channel equivalent of a store-brand disinfecting wipe, and "
            "the first Member's Mark product in this database. The filing names all "
            "four quat actives rather than printing 'quaternary ammonium compounds'. "
            "Entered ungraded."
        ),
        "owner": "Walmart Inc.",
        "tier": "grocery",
        "tier_ev": "reported",
        "tier_src": "https://corporate.walmart.com/about",
        "tier_note": "Sam's Club is a warehouse club within the grocery channel; tier key uses the channel vocabulary.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 8,
        "exposure_ev": "extrapolated",
        "exposure_src": WALMART_SRC,
        "exposure_basis": (
            "Derived, not measured. Wipes are a common household category, but the "
            "club channel reaches a smaller share of households than a grocery "
            "supercentre. Walmart's corporate page states approximately 280 million "
            "customer and member visits a week across all its stores and clubs. "
            "Searched for a Sam's Club member-household count and a published "
            "penetration figure for the Member's Mark wipe SKU; located neither. One "
            "significant figure, order-of-magnitude."
        ),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "full",
    },
    {
        "name": "Member's Mark Ultimate Clean Dishwasher Pacs, Fresh Scent",
        "brand": "Member's Mark",
        "cat": "Dishwasher",
        "safe": None,
        "ings": MM_DW_INGS,
        "heritage": False,
        "source": (
            "Sam's Club / Sam's West SB-258 ingredient-disclosure filing for this "
            "product (UPC 193968008505, disclosure dated 2019-11-08), hosted on the "
            "Sam's Club CDN. Manufacturer of record Henkel Corporation; distributor "
            "Sam's West, Inc. Sixteen lines with CAS numbers; the filing itself flags "
            "protease and amylase as present on EU respiratory-sensitizer and AOEC "
            "asthmagen lists. Two surfactants are marked CBI (confidential business "
            "information) and are recorded under their functional names."
        ),
        "source_url": "https://scene7.samsclub.com/is/content/samsclub/193968008505_pdf",
        "note": (
            "A club-channel dishwasher pac. The disclosure names the enzymes "
            "individually and carries their sensitizer listings, which most pac "
            "labels do not. Entered ungraded."
        ),
        "owner": "Walmart Inc.",
        "tier": "grocery",
        "tier_ev": "reported",
        "tier_src": "https://corporate.walmart.com/about",
        "tier_note": "Sam's Club is a warehouse club within the grocery channel.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 6,
        "exposure_ev": "extrapolated",
        "exposure_src": WALMART_SRC,
        "exposure_basis": (
            "Derived, not measured. Dishwasher ownership is a majority of US "
            "households but not near-universal, and the club channel reaches a "
            "smaller share than a grocery supercentre. Walmart's corporate page "
            "states approximately 280 million customer and member visits a week "
            "across all its stores and clubs. Searched for a Sam's Club "
            "member-household count and a published penetration figure for the "
            "Member's Mark pac SKU; located neither. One significant figure, "
            "order-of-magnitude."
        ),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "full",
    },
]


def main() -> int:
    prod_path = os.path.join(DATA, "products.json")
    ing_path = os.path.join(DATA, "ingredients.json")

    products = json.loads(open(prod_path, encoding="utf-8").read())
    ingredients = json.loads(open(ing_path, encoding="utf-8").read())

    existing_names = {p["name"] for p in products}
    lower_keys = {k.lower(): k for k in ingredients}

    added_products = []
    new_ing_keys = []
    seen_new = set()
    renamed = []

    for prod in PRODUCTS:
        if prod["name"] in existing_names:
            continue
        # Normalise against existing keys case-insensitively so a case-variant
        # never mints a duplicate (2026-09-27 lesson).
        ings = []
        for ing in prod["ings"]:
            if ing in ingredients:
                ings.append(ing)
            elif ing.lower() in lower_keys:
                canon = lower_keys[ing.lower()]
                renamed.append((ing, canon))
                ings.append(canon)
            else:
                if ing not in seen_new:
                    seen_new.add(ing)
                    new_ing_keys.append(ing)
                ings.append(ing)
        rec = dict(prod)
        rec["ings"] = ings
        rec["added"] = TODAY
        rec["updated"] = TODAY
        added_products.append(rec)

    resolving = set(ingredients) | set(new_ing_keys)
    for prod in added_products:
        missing = [i for i in prod["ings"] if i not in resolving]
        if missing:
            raise SystemExit(f"HALT: {prod['name']} references unknown ingredients: {missing}")

    owners = json.loads(open(os.path.join(DATA, "owners.json"), encoding="utf-8").read())
    registry = owners["owners"]
    for prod in added_products:
        if prod["owner"] not in registry:
            raise SystemExit(f"HALT: owner {prod['owner']!r} not in owners.json")

    print(f"products to add: {len(added_products)}")
    for p in added_products:
        print(f"  + {p['name']}  ({len(p['ings'])} ingredients, exposure "
              f"{p['exposure']}/{p['exposure_ev']}, tier {p['tier']})")
    print(f"new ingredient keys: {len(new_ing_keys)}")
    for a, b in renamed:
        print(f"  ~ case-normalised {a!r} -> {b!r}")

    if DRY:
        print("dry run — nothing written")
        return 0

    for ing in new_ing_keys:
        ingredients[ing] = {
            "ev": "Low",
            "g": None,
            "gr": {},
            "impacts": [],
            "note": ING_NOTE,
            "s": f"{ing}. Listed in a manufacturer disclosure read 2026-09-28; not yet graded against GHS.",
        }

    products.extend(added_products)

    open(prod_path, "w", encoding="utf-8").write(json.dumps(products, indent=1, ensure_ascii=False) + "\n")
    open(ing_path, "w", encoding="utf-8").write(json.dumps(ingredients, indent=1, ensure_ascii=False) + "\n")

    print(f"wrote {len(products)} products, {len(ingredients)} ingredients")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())