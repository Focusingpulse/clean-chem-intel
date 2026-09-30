#!/usr/bin/env python3
"""Night-shift station 2 harvest, 2026-09-30 (Dolman).

Ordered by EXPOSURE, not price tier (Trellis, Sep 22 2026). Every ingredient list
below was read from a manufacturer filing read TODAY, 2026-09-30:

  * Walmart's own California SB-258 ingredient-disclosure filings, hosted on the
    Walmart CDN (i5.walmartimages.com). Four Great Value household products.
    Manufacturer of record is named on each filing: Henkel Corporation (laundry
    detergent), KIK Custom Products (two bathroom cleaners), BISSELL Homecare
    (carpet and upholstery cleaner).
  * KIK Consumer Products' / Homecare Labs' California SB-258 filings, published
    on kikcorp.com. Five value-brand products: Comet Classic (toilet bowl
    cleaner, all-purpose cleaner with bleach, glass cleaner), Spic and Span
    (Multi-Surface Cleaner, Sun Fresh), The Works (Foaming Bathroom Cleaner).

Why these: the order is exposure, and the two biggest verifiable gaps in the
current corpus are the largest US private label (Great Value, Walmart) and the
legacy value brands that sit on the same shelf at a lower price (Comet, Spic and
Span, The Works). Both publish full intentionally-added lists with CAS numbers,
which is why they can enter at all: the disclosure is the entry ticket.

The finding this fire, and it is the third instance of the same pattern: the
five-line bleach formula (Water, Sodium Hypochlorite, Sodium Hydroxide, Lauramine
Oxide, Fragrance) appears unchanged in FOUR products that carry three different
names and two different price points -- Comet Ultra All Purpose Cleaner with
Bleach, Comet Classic All Purpose Cleaner with Bleach, Great Value All Purpose
Cleaner with Bleach and Great Value Bathroom Cleaner with Bleach. All four are
the same maker's filing. The brand story is the difference.

Nothing here is graded. Product grading is the Sifter lane; a blank as-sold grade
is the honest state, and substitutes[] is left empty for the same reason (the
substitute rule binds on a D/F grade, and none of these carries one yet).

Idempotent: a product whose `name` already exists is skipped, and an ingredient
key already present is left untouched. Run it twice; the second run reports 0.

Usage:  python3 tools/harvest_2026_09_30.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TODAY = "2026-09-30"

DRY = "--dry-run" in sys.argv

ING_NOTE = (
    "Listed in a manufacturer or manufacturer-filing disclosure read 2026-09-30; "
    "not yet graded against GHS."
)

KIK_SRCS = "https://www.kikcorp.com/our-products/"
KIK_CHANNEL = "https://www.kikcorp.com/ingredients/"
WALMART = "https://corporate.walmart.com/about"
IB_LAUNDRY = ("https://www.indexbox.io/store/"
              "united-states-laundry-home-products-market-analysis-forecast-size-trends-and-insights/")
IB_SURFACE = ("https://www.indexbox.io/store/"
              "united-states-household-surface-cleaners-market-analysis-forecast-size-trends-and-insights/")
IB_TOILET = ("https://www.indexbox.io/store/"
             "united-states-toilet-cleaning-products-market-analysis-forecast-size-trends-and-insights/")

# Explicit aliases: label wording -> existing key, where the substance is the
# same and a second key would be a synonym for one CAS.
ALIASES = {
    # Same substance, two spellings across two filings by the same maker.
    "Alcohols C12-15 Ethoxylated": "Alcohols, C12-15, Ethoxylated",
    "Diethylene Glycol Monobutyl Ether": "Butoxydiglycol",
    # NOTE: "Sodium Metasilicate" (anhydrous, CAS 6834-92-0, The Works filing)
    # and "Sodium Metasilicate Pentahydrate" (CAS 10213-79-3, Great Value filing)
    # are DIFFERENT substances and must stay two keys. Do not alias them.
}

# --------------------------------------------------------------------------
# 1. Great Value Ultimate Fresh Original Clean Laundry Detergent 170 oz
#    Walmart SB-258 filing, disclosure dated 11/22/2019, UPC 0007874227940,
#    GS1 10000424 Laundry Detergents. Manufacturer of record Henkel
#    Corporation, distributor Walmart, Inc.
# --------------------------------------------------------------------------
GV_LAUNDRY_INGS = [
    "Water",
    "Alcohols, C12-15, Ethoxylated",
    "Sodium Laureth Sulfate",
    "Sodium Citrate",
    "Triethanolamine Alkyl C10-16-benzenesulfate",
    "Alcohol",
    "Cocamidopropyl Betaine",
    "Sodium Cocoate",
    "Sodium C10-16 Alkylbenzenesulfonate",
    "Tetrasodium Iminodisuccinate",
    "Benzenesulfonic acid, 2,2'-(1,2-ethenediyl)bis[5-[[4-[(2-hydroxyethyl)methylamino]-6-(phenylamino)-1,3,5-triazin-2-yl]amino]-, disodium salt",
    "2-Propenoic acid, telomer with sodium sulfite (1:1), sodium salt",
    "Calcium Chloride",
    "2-Butenedioic acid (2E), with ethylene esters",
    "Benzene, C10-13, alkyl derivatives",
    "Protease",
    "Colorant",
    "2-Bromo-2-Nitropropane-1,3-Diol",
    "Amylase",
    "Potassium Chloride",
    "Methylchloroisothiazolinone",
    "Methylisothiazolinone",
    "Fragrance",
    "2-t-Butylcyclohexyl Acetate",
    "Limonene",
    "Methyl Beta-Naphthyl Ether",
    "Gamma-Undecalactone",
    "Ethylene Brassylate",
    "Tetramethyl Acetyloctahydro-Naphthalenes",
    "Hexyl Cinnamal",
    "Alpha-Isomethyl Ionone",
    "Hexahydro-Methanoindenyl Propionate",
]

# --------------------------------------------------------------------------
# 2. Great Value Bathroom Cleaner with Bleach
#    Walmart filing, disclosure 7/3/2019, UPC 0 78742 07532 7. Manufacturer of
#    record KIK Custom Products, distributor Walmart, Inc.
# --------------------------------------------------------------------------
GV_BATH_BLEACH_INGS = [
    "Water",
    "Sodium Hypochlorite",
    "Sodium Hydroxide",
    "Lauramine Oxide",
    "Fragrance",
]

# --------------------------------------------------------------------------
# 3. Great Value Lemon Scent Foaming Bathroom Cleaner
#    Walmart filing, disclosure 12/18/2019, UPC 0 78742 34733 2. Manufacturer
#    of record KIK Custom Products. The filing's own "Description of Product"
#    field reads "Air Freshener", which does not match the product name; the
#    ingredient list is the aerosol bathroom-cleaner formula (isobutane
#    propellant, four quat actives).
# --------------------------------------------------------------------------
GV_BATH_FOAM_INGS = [
    "Water",
    "Isobutane",
    "Butoxydiglycol",
    "Tetrasodium EDTA",
    "Sodium Lauryl Sarcosinate",
    "Lauramine Oxide",
    "Sodium Metasilicate Pentahydrate",
    "Fragrance",
    "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride",
    "Myristamine Oxide",
    "Quaternium-24",
    "Didecyldimonium Chloride",
    "Dimethyldioctylammonium Chloride",
    "Aminomethyl Propanol",
    "Ammonium Hydroxide",
    "2-Methylamino-2-Methyl-1-Propanol",
]

# --------------------------------------------------------------------------
# 4. Great Value Carpet & Upholstery Cleaner Oxy
#    Walmart filing, disclosure 8/6/2019, UPC 78742204291, GS1 10000749
#    Surface Care Other. Manufacturer of record BISSELL Homecare, Inc.
# --------------------------------------------------------------------------
GV_CARPET_INGS = [
    "Water",
    "Alcohol Alkoxylate",
    "Sodium Citrate",
    "Hydrogen Peroxide",
    "Linear Alcohol Ethoxylate",
    "Sodium Caprylyl Sulfonate",
    "Alkyl Polyglucoside",
    "Sodium Polyacrylate",
    "Citric Acid",
    "Fragrance",
]

# --------------------------------------------------------------------------
# 5. Comet Classic Toilet Bowl Cleaner
#    KIK / Homecare Labs filing, disclosure 8/5/2019, UPC 8 10003 44007 5.
# --------------------------------------------------------------------------
COMET_TOILET_INGS = [
    "Water",
    "Sulfamic Acid",
    "Alcohols, C9-11, Ethoxylated",
    "Fragrance",
    "Acid Blue 93",
]

# --------------------------------------------------------------------------
# 6. Comet Classic All Purpose Cleaner with Bleach
#    KIK / HomeCare Labs filing, disclosure August 8 2019, UPC 8 10003 44037 2.
# --------------------------------------------------------------------------
COMET_APC_BLEACH_INGS = [
    "Water",
    "Sodium Hypochlorite",
    "Sodium Hydroxide",
    "Lauramine Oxide",
    "Fragrance",
]

# --------------------------------------------------------------------------
# 7. Comet Classic Glass Cleaner
#    KIK / Homecare Labs filing, disclosure 12/4/2019, UPC 8 10003 44041 9.
# --------------------------------------------------------------------------
COMET_GLASS_INGS = [
    "Water",
    "Butoxyethyl Acetate",
    "Propylene Glycol",
    "C9-C11 Alkyl Polyglucoside",
    "Ammonium Hydroxide",
    "Tetrasodium EDTA",
    "Direct Blue 86",
]

# --------------------------------------------------------------------------
# 8. Spic and Span Multi-Surface Cleaner, Sun Fresh
#    KIK / Homecare Labs filing, disclosure 8/5/2019, UPC 8 11435 00101 8.
#    The filing prints DMDM Hydantoin as a "nonfunctional constituent" on the
#    California nonfunctional-constituent list rather than as an intended
#    ingredient, and prints water's CAS as 7732-18-2.
# --------------------------------------------------------------------------
SNS_SUNFRESH_INGS = [
    "Water",
    "Tetrasodium EDTA",
    "Sodium Hydroxide",
    "Sodium Carbonate",
    "Citric Acid",
    "Sodium Xylene Sulfonate",
    "Alcohols, C10-16, Ethoxylated",
    "Fragrance",
    "Fatty Acids, C8-C18 and C18 Unsaturated",
    "Cocamidopropyl Betaine",
    "DMDM Hydantoin",
    "Red 4",
    "Acid Orange 7",
]

# --------------------------------------------------------------------------
# 9. The Works Foaming Bathroom Cleaner, Fresh Citrus Scent
#    KIK / HomeCare Labs filing, disclosure August 9 2019, UPC 0 74157 64282 6.
# --------------------------------------------------------------------------
WORKS_FOAM_INGS = [
    "Water",
    "Isobutane",
    "Butoxydiglycol",
    "Tetrasodium EDTA",
    "Undeceth-3",
    "Sodium Metasilicate",
    "Fragrance",
    "Quaternary Ammonium Compounds, Benzyl-C12-18-Alkyldimethyl, Chlorides",
    "Alkyl (68% C12, 32% C14) Dimethyl Ethylbenzyl Ammonium Chloride",
    "Limonene",
    "Citral",
    "Linalool",
    "Geraniol",
    "Citronellol",
    "Eugenol",
]


def surface_basis(what, maker_note):
    return (
        f"Derived, not measured. The source states that approximately 95% of US "
        f"households use at least one surface cleaner product per month, that "
        f"all-purpose cleaners are the largest single segment at an estimated "
        f"30-35% of category value, and that specialised cleaners (bathroom, "
        f"kitchen, glass, floor) hold 30-35% with bathroom the largest "
        f"sub-segment. {maker_note} Searched for a published US household-"
        f"penetration or brand-share figure for this specific {what} and located "
        f"none; SKU-level private-label share is not published. Rounded to one "
        f"significant figure, order-of-magnitude."
    )


PRODUCTS = [
    {
        "name": "Great Value Ultimate Fresh Original Clean Laundry Detergent",
        "brand": "Great Value",
        "cat": "Laundry",
        "safe": None,
        "ings": GV_LAUNDRY_INGS,
        "heritage": False,
        "source": (
            "Walmart California Cleaning Product Right to Know (SB-258) "
            "ingredient disclosure for this product, published by Walmart on its "
            "own CDN (disclosure dated 11/22/2019, UPC 0007874227940, GS1 "
            "10000424 Laundry Detergents). Manufacturer of record Henkel "
            "Corporation, distributor Walmart, Inc. Thirty-two intentionally "
            "added ingredients with CAS numbers, including the enzymes protease "
            "and amylase and nine individually named fragrance components. Read "
            "today from the served PDF."
        ),
        "source_url": "https://i5.walmartimages.com/dfw/4ff9c6c9-c2eb/k2-_63b24117-3373-429f-8d97-8ee6b5d762f1.v1.pdf",
        "note": (
            "The largest US retailer's flagship private label, in the highest-"
            "penetration cleaning category, and the most complete disclosure in "
            "this database for a laundry detergent: enzymes, preservatives and "
            "nine fragrance constituents are all named. Two things the filing "
            "itself flags are worth reading: ethanol is marked present on the "
            "California Prop 65, IARC carcinogen and US NTP carcinogen lists, "
            "and both enzymes are marked present on the EU respiratory "
            "sensitiser and AOEC asthmagen lists. The manufacturer of record is "
            "Henkel, not Walmart. Entered ungraded."
        ),
        "owner": "Walmart Inc.",
        "tier": "grocery",
        "tier_ev": "reported",
        "tier_src": "https://i5.walmartimages.com/dfw/4ff9c6c9-c2eb/k2-_63b24117-3373-429f-8d97-8ee6b5d762f1.v1.pdf",
        "tier_note": "Walmart house brand; the filing names Walmart, Inc. as distributor and Henkel Corporation as manufacturer of record.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 10,
        "exposure_ev": "extrapolated",
        "exposure_src": IB_LAUNDRY,
        "exposure_basis": (
            "Derived, not measured. The source states household penetration for "
            "the US laundry and home products category is above 98%, and that "
            "private label and retail-brand products are now estimated at 18-22% "
            "of unit volume in laundry care. Great Value is Walmart's flagship "
            "private label and Walmart's own corporate page states approximately "
            "280 million customers and members visit more than 10,900 stores and "
            "clubs each week, the broadest household reach of any US retailer. "
            "Searched for a published household-penetration or unit-share figure "
            "for this SKU and located none. One significant figure, "
            "order-of-magnitude."
        ),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "full",
    },
    {
        "name": "Great Value Bathroom Cleaner with Bleach",
        "brand": "Great Value",
        "cat": "Bathroom",
        "safe": None,
        "ings": GV_BATH_BLEACH_INGS,
        "heritage": False,
        "source": (
            "Walmart California Cleaning Product Right to Know (SB-258) "
            "ingredient disclosure for this product, published by Walmart on its "
            "own CDN (disclosure dated 7/3/2019, UPC 0 78742 07532 7, GS1 "
            "10000746 Cleaners Other). Manufacturer of record KIK Custom "
            "Products, distributor Walmart, Inc. Five intentionally added "
            "ingredients with CAS numbers. The filing itself marks sodium "
            "hydroxide as present on the California non-cancer hazards list. Read "
            "today from the served PDF."
        ),
        "source_url": "https://i5.walmartimages.com/dfw/4ff9c6c9-37fa/k2-_dada1fb7-8242-4e10-b797-09c40a336a32.v1.pdf_1",
        "note": (
            "THE SAME FIVE-LINE FORMULA AS THREE OTHER PRODUCTS. Water, sodium "
            "hypochlorite, sodium hydroxide, lauramine oxide and fragrance is the "
            "whole list, and it is the identical list on Comet Ultra All Purpose "
            "Cleaner with Bleach, on Comet Classic All Purpose Cleaner with "
            "Bleach, and on Great Value All Purpose Cleaner with Bleach. Four "
            "names, two brands, two price points, one formula, all four disclosed "
            "by KIK or its Homecare Labs arm. Entered ungraded."
        ),
        "owner": "Walmart Inc.",
        "tier": "grocery",
        "tier_ev": "reported",
        "tier_src": "https://i5.walmartimages.com/dfw/4ff9c6c9-37fa/k2-_dada1fb7-8242-4e10-b797-09c40a336a32.v1.pdf_1",
        "tier_note": "Walmart house brand; the filing names Walmart, Inc. as distributor and KIK Custom Products as manufacturer of record.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 5,
        "exposure_ev": "extrapolated",
        "exposure_src": IB_SURFACE,
        "exposure_basis": surface_basis(
            "Walmart house-brand bathroom cleaner",
            "Bathroom cleaners are the largest specialised sub-segment, and "
            "Walmart has the broadest household reach of any US retailer, but a "
            "store-brand bleach bathroom spray is one SKU among many."),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "full",
    },
    {
        "name": "Great Value Lemon Scent Foaming Bathroom Cleaner",
        "brand": "Great Value",
        "cat": "Bathroom",
        "safe": None,
        "ings": GV_BATH_FOAM_INGS,
        "heritage": False,
        "source": (
            "Walmart California Cleaning Product Right to Know (SB-258) "
            "ingredient disclosure for this product, published by Walmart on its "
            "own CDN (disclosure dated 12/18/2019, UPC 0 78742 34733 2). "
            "Manufacturer of record KIK Custom Products, distributor Walmart, "
            "Inc. Sixteen intentionally added ingredients with CAS numbers, "
            "including four quaternary ammonium actives named individually and an "
            "aerosol propellant. The filing marks isobutane as present on the EU "
            "CMR list and butoxydiglycol as present on the California toxic air "
            "contaminants list. Read today from the served PDF."
        ),
        "source_url": "https://i5.walmartimages.com/dfw/4ff9c6c9-f2cb/k2-_eb28805b-57ca-4102-87bb-a7a5fc760a6a.v1.pdf",
        "note": (
            "The filing's own 'Description of Product' field reads 'Air "
            "Freshener', which is wrong: the list is an aerosol bathroom-cleaner "
            "formula with a propellant and four quat actives. The mismatch is "
            "recorded rather than corrected, because the document is the "
            "manufacturer's and its filed category is part of what it says. The "
            "fragrance blend is withheld as CBI here even though the same maker "
            "names fragrance components on other filings, which is the "
            "disclosure gap inside a single manufacturer. Entered ungraded."
        ),
        "owner": "Walmart Inc.",
        "tier": "grocery",
        "tier_ev": "reported",
        "tier_src": "https://i5.walmartimages.com/dfw/4ff9c6c9-f2cb/k2-_eb28805b-57ca-4102-87bb-a7a5fc760a6a.v1.pdf",
        "tier_note": "Walmart house brand; the filing names Walmart, Inc. as distributor and KIK Custom Products as manufacturer of record.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 3,
        "exposure_ev": "extrapolated",
        "exposure_src": IB_SURFACE,
        "exposure_basis": surface_basis(
            "Walmart house-brand aerosol bathroom cleaner",
            "An aerosol bathroom spray is a narrower SKU than a general bathroom "
            "cleaner and competes with national brands on the same shelf."),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "full",
    },
    {
        "name": "Great Value Carpet & Upholstery Cleaner Oxy",
        "brand": "Great Value",
        "cat": "Floor & Carpet",
        "safe": None,
        "ings": GV_CARPET_INGS,
        "heritage": False,
        "source": (
            "Walmart California Cleaning Product Right to Know (SB-258) "
            "ingredient disclosure for this product, published by Walmart on its "
            "own CDN (disclosure dated 8/6/2019, UPC 78742204291, GS1 10000749 "
            "Surface Care Other). Manufacturer of record BISSELL Homecare, Inc., "
            "distributor Walmart, Inc. Ten ingredient lines. Read today from the "
            "served PDF."
        ),
        "source_url": "https://i5.walmartimages.com/dfw/4ff9c6c9-9c9f/k2-_e4d0c289-d348-4639-b02c-bd3448d4f082.v1.pdf",
        "note": (
            "A third manufacturer of record on Walmart's own house brand: BISSELL "
            "Homecare, not KIK and not Henkel. Four of the ten lines are printed "
            "as 'Proprietary' with no CAS -- alcohol alkoxylate, linear alcohol "
            "ethoxylate, alkyl polyglucoside and sodium polyacrylate -- so the "
            "filing discloses some substances and withholds others in the same "
            "document. The stain-removal claim rests on hydrogen peroxide, which "
            "is named. Entered ungraded."
        ),
        "owner": "Walmart Inc.",
        "tier": "grocery",
        "tier_ev": "reported",
        "tier_src": "https://i5.walmartimages.com/dfw/4ff9c6c9-9c9f/k2-_e4d0c289-d348-4639-b02c-bd3448d4f082.v1.pdf",
        "tier_note": "Walmart house brand; the filing names Walmart, Inc. as distributor and BISSELL Homecare, Inc. as manufacturer of record.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 2,
        "exposure_ev": "extrapolated",
        "exposure_src": IB_SURFACE,
        "exposure_basis": surface_basis(
            "store-brand carpet and upholstery cleaning concentrate",
            "Carpet and upholstery cleaning is a smaller sub-category than "
            "surface cleaning, is bought for a machine rather than routinely, and "
            "the concentrate is diluted before use."),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "full",
    },
    {
        "name": "Comet Classic Toilet Bowl Cleaner",
        "brand": "Comet",
        "cat": "Bathroom",
        "safe": None,
        "ings": COMET_TOILET_INGS,
        "heritage": False,
        "source": (
            "KIK Consumer Products / Homecare Labs California Cleaning Product "
            "Right to Know (SB-258) ingredient disclosure for this product, "
            "published on kikcorp.com (disclosure dated 8/5/2019, UPC "
            "8 10003 44007 5). Five intentionally added ingredients with CAS "
            "numbers. Read today from the served PDF."
        ),
        "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/11/Comet-Classic_Toilet-Bowl-Cleaner-24oz_8-10003-44007-5.pdf",
        "note": (
            "A legacy value brand's acid toilet bowl cleaner, and chemically the "
            "opposite of the bleach products carrying the same brand: the "
            "cleaning agent is sulfamic acid in place of sodium hypochlorite. "
            "Sulfamic acid and hypochlorite products must never be mixed, and "
            "that is a use statement, not a hazard finding. The dye is named "
            "individually. Entered ungraded."
        ),
        "owner": "KIK Consumer Products",
        "tier": "mass",
        "tier_ev": "reported",
        "tier_src": KIK_SRCS,
        "tier_note": "Nationally distributed value brand sold through grocery, mass and hardware channels; market-position vocabulary, not a single retail channel.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 5,
        "exposure_ev": "extrapolated",
        "exposure_src": IB_TOILET,
        "exposure_basis": (
            "Derived, not measured. The source states that residential households "
            "account for roughly 55-60% of US toilet-cleaning product volume and "
            "that the residential segment spans about 130 million households; "
            "liquid cleaners are the dominant format at 40-45% of volume. Comet "
            "is a legacy value brand holding a modest share of a routinely "
            "repeated cleaning task. Searched for a published per-product US "
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
        "name": "Comet Classic All Purpose Cleaner with Bleach",
        "brand": "Comet",
        "cat": "All-Purpose",
        "safe": None,
        "ings": COMET_APC_BLEACH_INGS,
        "heritage": False,
        "source": (
            "KIK Consumer Products / HomeCare Labs California Cleaning Product "
            "Right to Know (SB-258) ingredient disclosure for this product, "
            "published on kikcorp.com (disclosure dated August 8 2019, UPC "
            "8 10003 44037 2). Five intentionally added ingredients with CAS "
            "numbers. The filing marks sodium hydroxide as present on the "
            "California non-cancer hazards list. Read today from the served PDF."
        ),
        "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/10/Comet-Classic_-All-purpose-cleaner-with-Bleach-32oz_8-10003-44037-2.pdf",
        "note": (
            "THE THIRD COPY OF ONE FORMULA IN THIS DATABASE. Water, sodium "
            "hypochlorite, sodium hydroxide, lauramine oxide and fragrance is also "
            "the complete list on Comet Ultra All Purpose Cleaner with Bleach, on "
            "Great Value All Purpose Cleaner with Bleach and on Great Value "
            "Bathroom Cleaner with Bleach. All four are the same maker's filings, "
            "disclosed between July 2019 and January 2021, sold under three brand "
            "names at different prices. Entered ungraded."
        ),
        "owner": "KIK Consumer Products",
        "tier": "mass",
        "tier_ev": "reported",
        "tier_src": KIK_SRCS,
        "tier_note": "Nationally distributed value brand sold through grocery, mass and hardware channels.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 3,
        "exposure_ev": "extrapolated",
        "exposure_src": IB_SURFACE,
        "exposure_basis": surface_basis(
            "Comet bleach all-purpose spray",
            "All-purpose cleaners are the largest single segment, but a "
            "bleach-based spray from a value brand is one option among many in "
            "it."),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "full",
    },
    {
        "name": "Comet Classic Glass Cleaner",
        "brand": "Comet",
        "cat": "Glass",
        "safe": None,
        "ings": COMET_GLASS_INGS,
        "heritage": False,
        "source": (
            "KIK Consumer Products / Homecare Labs California Cleaning Product "
            "Right to Know (SB-258) ingredient disclosure for this product, "
            "published on kikcorp.com (disclosure dated 12/4/2019, UPC "
            "8 10003 44041 9). Seven intentionally added ingredients with CAS "
            "numbers. Read today from the served PDF."
        ),
        "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/12/Comet-Classic_Glass-Cleaner-32oz_8-10003-44041-9.pdf",
        "note": (
            "An ammonia glass cleaner from a value brand, and a useful contrast "
            "with the bleach products under the same brand: no hypochlorite, no "
            "quaternary ammonium active, and no fragrance component named beyond "
            "the blend. The solvent is butoxyethyl acetate and the alkali is "
            "ammonium hydroxide, both named. Entered ungraded."
        ),
        "owner": "KIK Consumer Products",
        "tier": "mass",
        "tier_ev": "reported",
        "tier_src": KIK_SRCS,
        "tier_note": "Nationally distributed value brand sold through grocery, mass and hardware channels.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 3,
        "exposure_ev": "extrapolated",
        "exposure_src": IB_SURFACE,
        "exposure_basis": surface_basis(
            "Comet value-brand glass cleaner",
            "Glass cleaners sit inside the specialised cleaner segment; a value "
            "brand competes against two nationally dominant brands on the same "
            "shelf."),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "full",
    },
    {
        "name": "Spic and Span Multi-Surface Cleaner, Sun Fresh",
        "brand": "Spic and Span",
        "cat": "All-Purpose",
        "safe": None,
        "ings": SNS_SUNFRESH_INGS,
        "heritage": False,
        "source": (
            "KIK Consumer Products / Homecare Labs California Cleaning Product "
            "Right to Know (SB-258) ingredient disclosure for this product, "
            "published on kikcorp.com (disclosure dated 8/5/2019, UPC "
            "8 11435 00101 8). Thirteen lines with CAS numbers. The filing lists "
            "DMDM Hydantoin as a nonfunctional constituent on the California "
            "nonfunctional-constituent list rather than as an intended "
            "ingredient, and prints water's CAS as 7732-18-2. Read today from the "
            "served PDF."
        ),
        "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/12/SNS_Multi-Purpose-Cleaner-Sun-Fresh-28oz_8-11435-00101-8.pdf",
        "note": (
            "A dilutable concentrate from a brand dating to 1933. Two things "
            "stand out in the filing itself: the preservative DMDM Hydantoin is "
            "declared on the California nonfunctional-constituent list, which is "
            "a category the database does not otherwise see, and two colorants "
            "(Red 4 and Acid Orange 7) are named individually. Entered ungraded."
        ),
        "owner": "KIK Consumer Products",
        "tier": "mass",
        "tier_ev": "reported",
        "tier_src": KIK_SRCS,
        "tier_note": "Nationally distributed value brand sold through grocery, mass and hardware channels.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 3,
        "exposure_ev": "extrapolated",
        "exposure_src": IB_SURFACE,
        "exposure_basis": surface_basis(
            "Spic and Span multi-surface concentrate",
            "All-purpose cleaners are the largest single segment; the brand is a "
            "legacy value name holding a modest share of it."),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "full",
    },
    {
        "name": "The Works Foaming Bathroom Cleaner, Fresh Citrus Scent",
        "brand": "The Works",
        "cat": "Bathroom",
        "safe": None,
        "ings": WORKS_FOAM_INGS,
        "heritage": False,
        "source": (
            "KIK Consumer Products / HomeCare Labs California Cleaning Product "
            "Right to Know (SB-258) ingredient disclosure for this product, "
            "published on kikcorp.com (disclosure dated August 9 2019, UPC "
            "0 74157 64282 6). Fifteen intentionally added ingredients with CAS "
            "numbers, including two quaternary ammonium actives named "
            "individually and six fragrance components named as EU fragrance "
            "allergens. The filing marks isobutane as present on the EU CMR "
            "list. Read today from the served PDF."
        ),
        "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/10/The-Works_Foaming-Bathroom-Cleaner-Fresh-Citrus-Scent-22oz_0-74157-64282-6.pdf",
        "note": (
            "A value-brand aerosol bathroom cleaner, and the most fragrance-"
            "transparent filing in tonight's set: six components are named "
            "individually with CAS numbers and flagged as EU fragrance allergens "
            "(limonene, citral, linalool, geraniol, citronellol, eugenol), where "
            "the same maker's Great Value foaming bathroom cleaner withholds the "
            "blend as CBI. That contrast inside one manufacturer is the "
            "disclosure gap made concrete. Entered ungraded."
        ),
        "owner": "KIK Consumer Products",
        "tier": "mass",
        "tier_ev": "reported",
        "tier_src": KIK_SRCS,
        "tier_note": "Nationally distributed value brand sold through grocery, mass and hardware channels.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 3,
        "exposure_ev": "extrapolated",
        "exposure_src": IB_SURFACE,
        "exposure_basis": surface_basis(
            "value-brand foaming bathroom cleaner",
            "Bathroom cleaners are the largest specialised sub-segment; a value "
            "brand holds a modest share of it against national brands."),
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
            ing = ALIASES.get(ing, ing)
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

    # Case-variant guard: no key may differ from an existing key only by case.
    lower_all = {k.lower(): k for k in list(ingredients) + new_ing_keys}
    collisions = [k for k in new_ing_keys if lower_all[k.lower()] != k]
    if collisions:
        raise SystemExit(f"HALT: case-variant keys minted: {collisions}")

    resolving = set(ingredients) | set(new_ing_keys)
    for prod in added_products:
        missing = [i for i in prod["ings"] if i not in resolving]
        if missing:
            raise SystemExit(f"HALT: {prod['name']} references unknown ingredients: {missing}")

    owners = json.loads(open(os.path.join(DATA, "owners.json"), encoding="utf-8").read())
    registry = owners["owners"]
    if added_products:
        for prod in added_products:
            if prod["owner"] not in registry:
                raise SystemExit(f"HALT: owner {prod['owner']!r} not in owners.json")
            brands = registry[prod["owner"]].get("brands") or []
            if prod["brand"] not in brands:
                raise SystemExit(
                    f"HALT: brand {prod['brand']!r} is not in the brands list of "
                    f"owner {prod['owner']!r}; apply_owners() would silently null it.")

    print(f"products to add: {len(added_products)}")
    for p in added_products:
        print(f"  + {p['name']}  ({len(p['ings'])} ingredients, exposure "
              f"{p['exposure']}/{p['exposure_ev']}, tier {p['tier']}, owner {p['owner']})")
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
            "s": f"{ing}. Listed in a manufacturer disclosure read {TODAY}; not yet graded against GHS.",
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
