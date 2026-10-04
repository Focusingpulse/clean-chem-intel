#!/usr/bin/env python3
"""Night-shift station 2 harvest, 2026-09-29 (Dolman).

Ordered by EXPOSURE, not price tier (Trellis, Sep 22 2026). Every ingredient
list below was read from a manufacturer filing read TODAY:

  * KIK Consumer Products' own California SB-258 ingredient-disclosure PDFs
    (kikcorp.com), the manufacturer's published specification. Four products.
  * DailyMed FDA OTC drug labels for two pharmacy-chain house-brand hand soaps
    and one dollar-store house-brand antiseptic. Three products.

Why these: the thin channel tiers (dollar-store 4 products, drugstore 5) were
examined first, per the order. What they produced is itself the finding: both
tiers disclose a full intentionally-added list ONLY where a federal regulator
forces it (an FDA drug label). Their house-brand *cleaners* publish nothing --
the dollar-store finding, reproduced at the drugstore tier. So the clean,
verifiable additions available there are hand soaps and an antiseptic, and the
bulk of tonight's exposure gain is the value-brand cleaner tier that KIK
publishes in full.

Nothing here is graded. Product grading is the Sifter lane; a blank as-sold
grade is the honest state, and substitutes[] is left empty for the same reason
(the substitute rule binds on a D/F grade, and none of these carries one yet).

Idempotent: a product whose `name` already exists is skipped, and an ingredient
key already present is left untouched. Run it twice; the second run reports 0.

Usage:  python3 tools/harvest_2026_09_29.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TODAY = "2026-09-29"

DRY = "--dry-run" in sys.argv

ING_NOTE = (
    "Listed in a manufacturer or manufacturer-filing disclosure read 2026-09-29; "
    "not yet graded against GHS."
)

KIK_SRCS = "https://www.kikcorp.com/our-products/"
KIK_CHANNEL = "https://www.kikcorp.com/ingredients/"
INDEXBOX = ("https://www.indexbox.io/store/"
            "united-states-laundry-home-products-market-analysis-forecast-size-trends-and-insights/")

# --------------------------------------------------------------------------
# 1. CVS Health Handsoap
#    FDA OTC label, NDC 51316-705, labeler CVS Pharmacy Inc., manufacturer of
#    record Apollo Health and Beauty Care. Label effective 2026-05-20.
#    https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=e582bdcf-0d8b-39f1-e053-2995a90a01f2
#    Active benzalkonium chloride. 19 inactives. Label prints
#    "citric acid monohydrate" (recorded under the existing Citric Acid key)
#    and "aloe vera leaf" (recorded under the existing Aloe Vera key).
# --------------------------------------------------------------------------
CVS_SOAP_INGS = [
    "Benzalkonium Chloride",
    "Water",
    "Hydroxyethylcellulose",
    "Edetate Sodium",
    "Blue 1",
    "Green Tea Leaf",
    "Methylisothiazolinone",
    "Sodium Citrate",
    "Citric Acid",
    "Sulisobenzone",
    "Methylchloroisothiazolinone",
    "Aloe Vera",
    "Propylene Glycol",
    "Glycerin",
    "Red 33",
    "Polyquaternium-7",
    "Cocamidopropyl Betaine",
    "Fragrance",
    "Polysorbate 20",
    "Decyl Glucoside",
]

# --------------------------------------------------------------------------
# 2. Rite Aid Simplify Crisp Clean Scent Lather Hand Soap
#    FDA OTC label, NDC 11822-2002, labeler Rite Aid Corporation, manufacturer
#    of record Apollo Health and Beauty Care. Label effective 2026-05-08.
#    https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=20d75a2f-8b82-924c-e063-6294a90ae09c
#    A different product from the Simplify "Clean And Protect" hand soap already
#    in this database (NDC 11822-2003): different formula, different NDC.
# --------------------------------------------------------------------------
RA_SOAP_INGS = [
    "Benzalkonium Chloride",
    "Water",
    "Cetrimonium Chloride",
    "Cocamide MEA",
    "Citric Acid",
    "Glycerin",
    "Lauramidopropylamine Oxide",
    "Sodium Sulfate",
    "Yellow 5",
    "Red 40",
    "Red 33",
    "Methylisothiazolinone",
    "Methylchloroisothiazolinone",
    "Tetrasodium EDTA",
    "PEG-120 Methyl Glucose Dioleate",
    "Sodium Chloride",
    "Fragrance",
]

# --------------------------------------------------------------------------
# 3. Dollar General Isopropyl Alcohol 70 Percent
#    FDA OTC label, NDC 55910-275, labeler Dolgencorp, Inc. (Dollar General &
#    Rexall). Label effective 2025-02-05. Two lines: the active and water.
#    The smallest list in the database, and that is the point of recording it.
# --------------------------------------------------------------------------
DG_IPA_INGS = [
    "Isopropyl Alcohol",
    "Water",
]

# --------------------------------------------------------------------------
# 4. Comet Ultra Fresh Scent All Purpose Cleaner with Bleach
#    KIK/Homecare Labs SB-258 filing, disclosure dated 2021-01-28, UPC
#    8 10003 44071 6. https://www.kikcorp.com/wp-content/uploads/2021/03/
#    Comet-Ultra_Fresh-Scent-All-Purpose-Cleaner-with-Bleach_-32oz_10003-4407....pdf
#    Five lines, CAS numbers present.
# --------------------------------------------------------------------------
COMET_INGS = [
    "Water",
    "Sodium Hypochlorite",
    "Sodium Hydroxide",
    "Lauramine Oxide",
    "Fragrance",
]

# --------------------------------------------------------------------------
# 5. Spic and Span Everyday Antibacterial Cleaner, Fresh Citrus Scent
#    KIK/Homecare Labs SB-258 filing, disclosure dated 2019-08-05, UPC
#    8 11435 00649 5. Ten lines. Four quaternary ammonium actives named
#    individually rather than printed as "quaternary ammonium compounds".
#    The filing prints the dye as "Green Dye" with no CAS; recorded under the
#    existing Colorant key, matching house convention.
# --------------------------------------------------------------------------
SNS_INGS = [
    "Water",
    "Octyl Decyl Dimethyl Ammonium Chloride",
    "Dioctyl Dimethyl Ammonium Chloride",
    "Didecyl Dimethyl Ammonium Chloride",
    "Alkyl (50% C14, 40% C12, 10% C16) Dimethyl Benzyl Ammonium Chloride",
    "Tetrasodium EDTA",
    "Sodium Metasilicate Pentahydrate",
    "C12-15 Alcohols Ethoxylated",
    "Fragrance",
    "Colorant",
]

# --------------------------------------------------------------------------
# 6/7. Greased Lightning All Purpose Cleaner and
#      Top Job Basic Multi-Purpose Cleaner & Degreaser
#    KIK SB-258 filings, both disclosed 2019-08-08 / 2019-08-07. The two
#    filings carry the SAME nine-line formula from the same contract
#    manufacturer (Homecare Labs), which is itself worth recording: a
#    brand-name cleaning product and a value-tier one, sold at different
#    price points, are the same bottle. The filing lists Water twice;
#    de-duplicated here.
# --------------------------------------------------------------------------
GL_TOJOB_INGS = [
    "Water",
    "Alkylbenzene Sulfonic Acid",
    "Dipropylene Glycol Butyl Ether",
    "Undeceth-40",
    "Sodium Hydroxide",
    "Butyloxyethanol",
    "Tetrasodium EDTA",
    "Fragrance",
    "Limonene",
]

PRODUCTS = [
    {
        "name": "CVS Health Handsoap",
        "brand": "CVS Health",
        "cat": "Hand Soap",
        "safe": None,
        "ings": CVS_SOAP_INGS,
        "heritage": False,
        "source": (
            "FDA OTC drug label filed at DailyMed, NDC 51316-705, labeler CVS "
            "Pharmacy Inc., manufacturer of record Apollo Health and Beauty Care. "
            "Active benzalkonium chloride; 19 inactive ingredients named. Label "
            "effective 2026-05-20. Read today from the DailyMed label."
        ),
        "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=e582bdcf-0d8b-39f1-e053-2995a90a01f2",
        "note": (
            "A second CVS house-brand hand soap, a different formula and a "
            "different NDC from the one already recorded. It discloses a full "
            "active-plus-inactive list for one reason: it is an FDA drug. Two "
            "preservatives (methylisothiazolinone and methylchloroisothiazolinone) "
            "and an ultraviolet absorber (sulisobenzone) are named on the label. "
            "Entered ungraded: product grading is the Sifter lane."
        ),
        "owner": "CVS Health Corporation",
        "tier": "drugstore",
        "tier_ev": "reported",
        "tier_src": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=e582bdcf-0d8b-39f1-e053-2995a90a01f2",
        "tier_note": "CVS Pharmacy is the labeler of record on the FDA listing; the chain is the brand's own definition, not an inference from the shelf.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 2,
        "exposure_ev": "extrapolated",
        "exposure_src": INDEXBOX,
        "exposure_basis": (
            "Derived, not measured. Liquid hand soap is a near-universal household "
            "category and drugstore private label is a small single-digit share of "
            "it. Searched for a published US household-penetration or brand-share "
            "figure for this specific CVS hand-soap SKU and located none; private "
            "label share is not published at SKU level. Rounded to one significant "
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
        "name": "Rite Aid Simplify Crisp Clean Scent Lather Hand Soap",
        "brand": "Rite Aid",
        "cat": "Hand Soap",
        "safe": None,
        "ings": RA_SOAP_INGS,
        "heritage": False,
        "source": (
            "FDA OTC drug label filed at DailyMed, NDC 11822-2002, labeler Rite "
            "Aid Corporation, manufacturer of record Apollo Health and Beauty "
            "Care. Active benzalkonium chloride; 16 inactive ingredients named. "
            "Label effective 2026-05-08. Read today from the DailyMed label."
        ),
        "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=20d75a2f-8b82-924c-e063-6294a90ae09c",
        "note": (
            "A second Rite Aid 'Simplify' hand soap: a different product from the "
            "Simplify Clean And Protect soap already recorded (different NDC, "
            "different formula, a cetrimonium chloride conditioner and a PEG "
            "rheology modifier the other does not carry). Full active-plus-"
            "inactive list, because it is an FDA drug. Entered ungraded."
        ),
        "owner": "Rite Aid Corporation",
        "tier": "drugstore",
        "tier_ev": "reported",
        "tier_src": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=20d75a2f-8b82-924c-e063-6294a90ae09c",
        "tier_note": "Rite Aid Corporation is the labeler of record on the FDA listing and owns the Simplify house brand.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 2,
        "exposure_ev": "extrapolated",
        "exposure_src": INDEXBOX,
        "exposure_basis": (
            "Derived, not measured. Hand soap is a near-universal household "
            "category and a drugstore private label is a small single-digit share "
            "of it. Searched for a published US household-penetration or "
            "brand-share figure for this Simplify SKU and located none; private "
            "label share is not published at SKU level. One significant figure."
        ),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "full",
    },
    {
        "name": "Dollar General Isopropyl Alcohol 70 Percent",
        "brand": "Dollar General",
        "cat": "Disinfectant",
        "safe": None,
        "ings": DG_IPA_INGS,
        "heritage": False,
        "source": (
            "FDA OTC drug label filed at DailyMed, NDC 55910-275, labeler "
            "Dolgencorp, Inc. (Dollar General & Rexall). Active isopropyl "
            "alcohol, one inactive ingredient (water). Label effective "
            "2025-02-05. Read today from the DailyMed label."
        ),
        "source_url": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=dbe58ba6-1581-4399-b6fe-09e1c95dd73c",
        "note": (
            "A two-line disclosure. In the tier built for buyers with the least "
            "information, this is close to the floor of what a product can say "
            "about itself, and it is still more than any dollar-store house-brand "
            "cleaner publishes. Isopropyl alcohol is recorded here as a household "
            "disinfectant and solvent, the same footing on which hydrogen peroxide "
            "already sits in this database. Entered ungraded."
        ),
        "owner": "Dollar General Corporation",
        "tier": "dollar-store",
        "tier_ev": "reported",
        "tier_src": "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=dbe58ba6-1581-4399-b6fe-09e1c95dd73c",
        "tier_note": "Dolgencorp, Inc. (Dollar General & Rexall) is the labeler of record on the FDA listing; the retailer is the house brand's own definition.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": None,
        "exposure_ev": "untested",
        "exposure_src": None,
        "exposure_basis": (
            "Searched for a published US household-penetration or sales-share "
            "figure for isopropyl alcohol and located no citable one; the "
            "laundry-and-home-products category data this database uses does not "
            "cover first-aid antiseptics. Left as a research gap rather than "
            "estimated from an unrelated category."
        ),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "full",
    },
    {
        "name": "Comet Ultra Fresh Scent All Purpose Cleaner with Bleach",
        "brand": "Comet",
        "cat": "All-Purpose",
        "safe": None,
        "ings": COMET_INGS,
        "heritage": False,
        "source": (
            "KIK Consumer Products / Homecare Labs SB-258 ingredient-disclosure "
            "filing for this product, published under the California Cleaning "
            "Product Right to Know Act (disclosure dated 2021-01-28, UPC "
            "8 10003 44071 6). Five lines with CAS numbers. The filing itself "
            "marks sodium hydroxide as present on the California non-cancer "
            "hazards list."
        ),
        "source_url": "https://www.kikcorp.com/wp-content/uploads/2021/03/Comet-Ultra_Fresh-Scent-All-Purpose-Cleaner-with-Bleach_-32oz_10003-4407....pdf",
        "note": (
            "A bleach-based all-purpose spray from a brand that has been on the "
            "value shelf since the 1950s and that this database carried only as a "
            "powder and a bathroom variant. Five lines: what is in it, and nothing "
            "it is not. Entered ungraded."
        ),
        "owner": "KIK Consumer Products",
        "tier": "mass",
        "tier_ev": "reported",
        "tier_src": KIK_SRCS,
        "tier_note": "A nationally distributed value brand sold through grocery, mass and hardware channels; market-position vocabulary, not a single retail channel.",
        "substitutes": [
            {
                "name": "Spic and Span Everyday Antibacterial Cleaner, Fresh Citrus Scent",
                "tier": "mass",
                "note": (
                    "Same manufacturer, same value price point, no bleach. Avoids "
                    "the sodium hypochlorite and sodium hydroxide load if the "
                    "concern is corrosivity or mixing risk. It carries its own "
                    "quaternary ammonium actives, so read both lists."
                ),
            }
        ],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 3,
        "exposure_ev": "extrapolated",
        "exposure_src": INDEXBOX,
        "exposure_basis": (
            "Derived, not measured. All-purpose cleaner is a near-universal "
            "household category (the source states household penetration for the "
            "laundry and home-products basket above 98%). Bleach-based all-purpose "
            "sprays are a fraction of it, and Comet is a legacy value brand rather "
            "than a category leader. Searched for a published per-product US "
            "household-penetration figure for this SKU and located none. One "
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
        "name": "Spic and Span Everyday Antibacterial Cleaner, Fresh Citrus Scent",
        "brand": "Spic and Span",
        "cat": "All-Purpose",
        "safe": None,
        "ings": SNS_INGS,
        "heritage": False,
        "source": (
            "KIK Consumer Products / Homecare Labs SB-258 ingredient-disclosure "
            "filing for this product, published under the California Cleaning "
            "Product Right to Know Act (disclosure dated 2019-08-05, UPC "
            "8 11435 00649 5). Ten lines with CAS numbers. Four quaternary "
            "ammonium actives are named individually rather than printed as "
            "'quaternary ammonium compounds'."
        ),
        "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/12/SNS_Everyday-Antibacterial-Cleaner-Fresh-Citrus-Scent-28oz_8-11435-00649-5-1.pdf",
        "note": (
            "An antibacterial all-purpose spray from a brand dating to 1933. The "
            "filing names all four quat actives and the metasilicate builder; the "
            "only thing it withholds is the dye, printed as 'Green Dye' with no "
            "CAS. Entered ungraded."
        ),
        "owner": "KIK Consumer Products",
        "tier": "mass",
        "tier_ev": "reported",
        "tier_src": KIK_SRCS,
        "tier_note": "Nationally distributed value brand sold through grocery, mass and hardware channels.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 2,
        "exposure_ev": "extrapolated",
        "exposure_src": INDEXBOX,
        "exposure_basis": (
            "Derived, not measured. All-purpose cleaner is a near-universal "
            "category; Spic and Span is a legacy value brand holding a small share "
            "of it, and the household-use rights sit with KIK while the "
            "professional-use rights stay with Procter & Gamble. Searched for a "
            "published per-product US household-penetration figure and located "
            "none. One significant figure, order-of-magnitude."
        ),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "full",
    },
    {
        "name": "Greased Lightning All Purpose Cleaner",
        "brand": "Greased Lightning",
        "cat": "All-Purpose",
        "safe": None,
        "ings": GL_TOJOB_INGS,
        "heritage": False,
        "source": (
            "KIK Consumer Products / Homecare Labs SB-258 ingredient-disclosure "
            "filing for this product, published under the California Cleaning "
            "Product Right to Know Act (disclosure dated 2019-08-07, UPC "
            "0 81238 84204 4). Nine lines with CAS numbers. The filing itself "
            "marks sodium hydroxide and 2-butoxyethanol as present on the "
            "California non-cancer hazards list and limonene as an EU fragrance "
            "allergen."
        ),
        "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/10/Greased-Lighting_All-Purpose-Cleaner-16oz_0-81238-84204-4.pdf",
        "note": (
            "A degreasing all-purpose spray sold mainly through grocery, hardware "
            "and auto channels. The filing names 2-butoxyethanol, a glycol-ether "
            "solvent the manufacturer's own filing flags on the California "
            "non-cancer hazards list, and names limonene as the fragrance "
            "allergen. Entered ungraded."
        ),
        "owner": "KIK Consumer Products",
        "tier": "mass",
        "tier_ev": "reported",
        "tier_src": KIK_SRCS,
        "tier_note": "Nationally distributed value brand sold through grocery, hardware and automotive channels.",
        "substitutes": [
            {
                "name": "Spic and Span Everyday Antibacterial Cleaner, Fresh Citrus Scent",
                "tier": "mass",
                "note": (
                    "Same manufacturer and roughly the same value price point, no "
                    "glycol-ether solvent. Avoids 2-butoxyethanol. It is a quat "
                    "cleaner, so it trades one active class for another rather "
                    "than removing the load; read its list."
                ),
            }
        ],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 2,
        "exposure_ev": "extrapolated",
        "exposure_src": INDEXBOX,
        "exposure_basis": (
            "Derived, not measured. All-purpose cleaner is a near-universal "
            "category; Greased Lightning is a mid-tier degreaser brand, heavily "
            "sold in automotive and hardware channels, holding a small share of "
            "household use. Searched for a published per-product US "
            "household-penetration figure and located none. One significant "
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
        "name": "Top Job Basic Multi-Purpose Cleaner & Degreaser",
        "brand": "Top Job",
        "cat": "All-Purpose",
        "safe": None,
        "ings": GL_TOJOB_INGS,
        "heritage": False,
        "source": (
            "KIK Consumer Products SB-258 ingredient-disclosure filing for this "
            "product, published under the California Cleaning Product Right to "
            "Know Act (disclosure dated 2019-08-08, UPC 8 36272 01036 8). Nine "
            "lines with CAS numbers. The filing itself marks sodium hydroxide and "
            "2-butoxyethanol as present on the California non-cancer hazards list "
            "and limonene as an EU fragrance allergen."
        ),
        "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/10/Top-Job_-Basic-Multi-Purpose-Cleaner-Degreaser-20oz_8-36272-01036-8.pdf",
        "note": (
            "TOP JOB AND GREASED LIGHTNING ARE THE SAME FORMULA. Both filings name "
            "the same nine lines from the same contract manufacturer (Homecare "
            "Labs, Lawrenceville GA), disclosed a day apart in 2019, and the two "
            "are sold at different price points under different brand stories. "
            "That is what the disclosure is for. Entered ungraded."
        ),
        "owner": "KIK Consumer Products",
        "tier": "mass",
        "tier_ev": "reported",
        "tier_src": KIK_SRCS,
        "tier_note": "Value-tier brand marketed by KIK Consumer Products; distributed through value, grocery and dollar channels.",
        "substitutes": [
            {
                "name": "Spic and Span Everyday Antibacterial Cleaner, Fresh Citrus Scent",
                "tier": "mass",
                "note": (
                    "Same manufacturer, same value price point, no 2-butoxyethanol. "
                    "Note that the swap is between two products of the same maker, "
                    "so it changes the active class rather than the supplier."
                ),
            }
        ],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 2,
        "exposure_ev": "extrapolated",
        "exposure_src": INDEXBOX,
        "exposure_basis": (
            "Derived, not measured. All-purpose cleaner is a near-universal "
            "category; Top Job is a legacy value brand holding a small share of "
            "it, and the brand moved from Procter & Gamble to the value shelf in "
            "the 1990s. Searched for a published per-product US "
            "household-penetration figure and located none. One significant "
            "figure, order-of-magnitude."
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

    if added_products:
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
    for k in new_ing_keys:
        print(f"    * {k}")
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
            "s": f"{ing}. Listed in a manufacturer disclosure read 2026-09-29; not yet graded against GHS.",
        }

    products.extend(added_products)

    open(prod_path, "w", encoding="utf-8").write(
        json.dumps(products, indent=1, ensure_ascii=False) + "\n")
    open(ing_path, "w", encoding="utf-8").write(
        json.dumps(ingredients, indent=1, ensure_ascii=False) + "\n")

    print(f"wrote {len(products)} products, {len(ingredients)} ingredients")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
