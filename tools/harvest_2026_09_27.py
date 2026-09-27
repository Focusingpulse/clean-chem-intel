#!/usr/bin/env python3
"""Night-shift station 2 harvest, 2026-09-27 (Dolman).

Ordered by EXPOSURE, not price tier (Trellis, Sep 22 2026). Five products whose
ingredient lists were read from a manufacturer or manufacturer-filing source
today. Nothing here is graded: product grading is the Sifter lane, and a blank
as-sold grade is the honest state.

Cluster 1 — fragranced consumer products (Sandra's Sep-24 expansion mandate:
air fresheners / plug-ins, fabric softeners, general odor-emitting household
products; Dr. Swan's research domain). These are the highest-exposure products
this database did not carry.

Cluster 2 — one genuine dollar-store tier addition (SPX-001), disclosed only
because a federal regulator forces it: an FDA OTC drug label.

Idempotent: a product whose `name` already exists is skipped, and an ingredient
key already present is left untouched. Run it twice; the second run reports 0
products added.

Usage:  python3 tools/harvest_2026_09_27.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TODAY = "2026-09-27"

DRY = "--dry-run" in sys.argv

# --------------------------------------------------------------------------
# Glade PlugIns Scented Oil refills, Hawaiian Breeze — SC Johnson
# Source read today: https://whatsinsidescjohnson.com/en-us/brands/glade/plug-ins/scented-oil/hawaiian-breeze-refills
# --------------------------------------------------------------------------
GLADE_INGS = [
    "Fragrance Oil",
    "Fragrance",
    "Dipropylene Glycol",
    "2-t-Butylcyclohexyl Acetate",
    "Ethyl Hexanoate",
    "PPG-2 Methyl Ether Acetate",
    "Linalool",
    "Ethyl 2-Methylbutyrate",
    "2-Phenoxyethyl Isobutyrate",
    "3a,4,5,6,7,7a-Hexahydro-4,7-methanoinden-6-yl Acetate",
    "Diethyl Malonate",
    "Tricyclodecenyl Propionate",
    "Dimethylcyclohex-3-ene-1-carbaldehyde",
    "Hexyl Acetate",
    # The SC Johnson page prints "gamma-undecalactone"; recorded under the existing
    # key "Gamma-Undecalactone" to avoid re-creating a case-variant duplicate.
    "Gamma-Undecalactone",
    "Amyl Acetate",
    "4-tert-Butylcyclohexyl Acetate",
    "gamma-Nonalactone",
    "Cinnamal",    "Ionone",
    "Isopentyl Cyclohexyl Acetate",
    "Methylbenzyl Acetate",
    "Ethyl Butyrate",
    "3-Hexenol",
    "Eugenol",
    "Limonene",
    "3-Methylbutyl Butyrate",
    "Mixed Ionones",
    "Citrus Aurantium Dulcis (Orange) Peel Oil",
    "Ethyl Hydroxypyrone",
    "Allyl 3-Cyclohexylpropionate",
    "Undecanal",
    "Ethyl 2,4-Dimethyl-1,3-dioxolane-2-acetate",
    "Octanal",
    "Dimethyl Phenethyl Butyrate",
    "Phenethyl Isobutyrate",
    "Chouji Yu",
    "Methyl N-Methylanthranilate",
    "Triethyl Citrate",
    "Vanillin",
    "Ethyl Vanillin",
    "1-Methyl-4-(4-methylpentyl)cyclohex-3-ene-1-carbaldehyde",
    "Decanal",
    "Geranyl Acetate",
    "beta-Caryophyllene",
    "Linalyl Acetate",
    "Terpineol Acetate",
]

# --------------------------------------------------------------------------
# Febreze AIR (Air Effects) Odor-Fighting Air Freshener, Fresh Sky — P&G
# SmartLabel read today: https://smartlabel.pg.com/en-us/00037000969990.html
# --------------------------------------------------------------------------
FEBREZE_INGS = [
    "Water",
    "Alcohol Denat.",
    "PEG-60 Hydrogenated Castor Oil",
    "Fragrance",
    "Sodium Citrate",
    "Hydroxypropyl Cyclodextrin",
    "Diethylhexyl Sodium Sulfosuccinate",
    "Benzisothiazolinone",
    "Nitrogen",
]

# --------------------------------------------------------------------------
# Suavitel Liquid Fabric Softener, Field Flowers — Colgate-Palmolive
# Label list as published on the SmartLabel-enabled pack (read today via the
# SmartLabel record colgatepalmolive.com/en-us/smartlabel/35000472991 and the
# retailer label transcription). The pack's first line is the marketing phrase
# "Made With Love And Water"; recorded here as Water.
# --------------------------------------------------------------------------
SUAVITEL_INGS = [
    "Water",
    "Dihydrogenated Tallowamidoethyl Hydroxyethylmonium Methosulfate",
    "Fragrance",
    "Polyquaternium-32",
    "Lactic Acid",
    "Polyquaternium-7",
    "Methylisothiazolinone",
    "Methylchloroisothiazolinone",
    "Octylisothiazolinone",
    "Colorant",
]

# --------------------------------------------------------------------------
# Fels-Naptha Heavy Duty Laundry Bar Soap — Henkel Corporation
# SDS composition section read today:
# https://pim.henkelgroup.net/henkel/sds/L/2567828/US/EN?matName=BAR+SOAP+FELS+NAPTHA+BROWN
# --------------------------------------------------------------------------
FELS_INGS = [
    "Fatty Acids, Tallow, Sodium Salts",
    "Fatty Acids, Coconut Oil, Sodium Salts",
    "Fatty Acids, Tallow",
    # The SDS prints "Glycerol" (CAS 56-81-5) and "D-Limonene"; recorded under the
    # existing database keys "Glycerin" and "Limonene" (same substances) rather than
    # creating synonym keys for the same CAS, which is how the duplicate-key class
    # cleaned up on 2026-09-26 re-enters.
    "Glycerin",
    "Limonene",
    "Cineole",
]

# --------------------------------------------------------------------------
# Assured Antiseptic Wet Wipes Vitamin E and Aloe — Greenbrier International
# (Dollar Tree house brand). FDA OTC drug label read today:
# https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=c04e2921-20d7-43c2-b9b9-07df8e425312
# NDC 33992-5111, labeler Greenbrier International, Inc.
# --------------------------------------------------------------------------
ASSURED_INGS = [
    "Benzalkonium Chloride",
    "Water",
    "Aloe Vera Leaf Extract",
    "Propylene Glycol",
    "Glycerin",
    "Phenoxyethanol",
    "Disodium Cocoamphodiacetate",
    "Polysorbate 20",
    "Sorbitol",
    "Disodium EDTA",
    "Tocopheryl Acetate",
    "Fragrance",
]

PRODUCTS = [
    {
        "name": "Glade PlugIns Scented Oil Air Freshener Refills, Hawaiian Breeze",
        "brand": "Glade",
        "cat": "Specialty",
        "safe": None,
        "ings": GLADE_INGS,
        "heritage": False,
        "source": "SC Johnson What's Inside ingredient disclosure (California Cleaning Product Right to Know Act)",
        "source_url": "https://whatsinsidescjohnson.com/en-us/brands/glade/plug-ins/scented-oil/hawaiian-breeze-refills",
        "note": "This is the disclosure that most of this category does not make. An air freshener is normally a single line reading 'fragrance', which is an unidentifiable blend. SC Johnson publishes the fragrance at component level on its own site under the California Cleaning Product Right to Know Act, so the blend resolves into named substances instead of staying a blank. The components marked with an asterisk on the source page are on SC Johnson's own skin-allergen list. Category is the honest remainder bucket (CCI-006 Rev 1); an air freshener is not a room or a cleaning task. Entered ungraded: product grading is the Sifter lane.",
        "owner": "SC Johnson",
        "owner_ev": "verified",
        "owner_src": "https://whatsinsidescjohnson.com/en-us/brands/glade/plug-ins/scented-oil/hawaiian-breeze-refills",
        "tier": "mass",
        "tier_ev": "reported",
        "tier_src": "https://simporter.com/trends/plug-in-air-freshener/",
        "tier_note": "Mass-market national brand; market-position vocabulary, not a retail channel (the `tier` key carries both, filed as a known conflict).",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 6,
        "exposure_ev": "extrapolated",
        "exposure_src": "https://simporter.com/trends/plug-in-air-freshener/",
        "exposure_basis": "Derived, not measured. Glade PlugIns holds 19.3% of the US plug-in air freshener category (Simporter, April 2026, which also puts Febreze PLUG at 28.7%, private label at 19.0% and Air Wick at 15.8%), and the home-fragrance category reaches household penetration above 85% (IndexBox, 2026). Searched for a published household-penetration figure for the plug-in format itself or for this brand and found none; the derivation therefore assumes roughly a third of households use a plug-in at all, which is an assumption stated here rather than sourced. One significant figure, order of magnitude.",
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "not_reviewed",
    },
    {
        "name": "Febreze AIR Freshener, Fresh Sky",
        "brand": "Febreze",
        "cat": "Specialty",
        "safe": None,
        "ings": FEBREZE_INGS,
        "heritage": False,
        "source": "Procter & Gamble SmartLabel ingredient disclosure",
        "source_url": "https://smartlabel.pg.com/en-us/00037000969990.html",
        "note": "A rare case in this category where the base formula is published in full and the fragrance is the only unresolved line. The page carries a fragrance-ingredient tab that names more components than the summary list does, and P&G flags which entries sit on the California Cleaning Product Right to Know Act designated list or the EU fragrance-allergen list. Nitrogen is the aerosol propellant. Category is the honest remainder bucket (CCI-006 Rev 1). Entered ungraded: product grading is the Sifter lane.",
        "owner": "Procter & Gamble",
        "owner_ev": "verified",
        "owner_src": "https://smartlabel.pg.com/en-us/00037000969990.html",
        "tier": "mass",
        "tier_ev": "reported",
        "tier_src": "https://simporter.com/trends/plug-in-air-freshener/",
        "tier_note": "Mass-market national brand; market-position vocabulary, not a retail channel.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 8,
        "exposure_ev": "extrapolated",
        "exposure_src": "https://simporter.com/trends/plug-in-air-freshener/",
        "exposure_basis": "Derived, not measured. Febreze is the leading US air-care brand: Febreze PLUG holds 28.7% of the plug-in air freshener category (Simporter, April 2026) and Febreze holds roughly 43% of Amazon US air-freshener unit volume (IndexBox, 2025). Searched for a per-SKU or per-brand household-penetration figure for Febreze AIR specifically and found none, so the estimate is a category-share read applied to home-fragrance penetration above 85% (IndexBox, 2026) with a format-share assumption stated rather than sourced. One significant figure.",
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "not_reviewed",
    },
    {
        "name": "Suavitel Liquid Fabric Softener, Field Flowers",
        "brand": "Suavitel",
        "cat": "Laundry",
        "safe": None,
        "ings": SUAVITEL_INGS,
        "heritage": False,
        "source": "Colgate-Palmolive SmartLabel ingredient disclosure (pack transcription)",
        "source_url": "https://www.colgatepalmolive.com/en-us/smartlabel/35000472991",
        "note": "A fabric softener is a fragranced consumer product in the sense Sandra's Sep-24 expansion names, and this is the largest such brand the database did not carry. It also carries two preservative allergens (methylisothiazolinone and methylchloroisothiazolinone) plus octylisothiazolinone, all three named on the pack rather than hidden behind 'preservative'. The pack's first line reads 'Made With Love And Water'; recorded here as Water. Colgate-Palmolive's own SDS for the regular variant states structure below the pack list (an acrylamide trace at below 0.1 percent, and a quaternized triethanolamine diester at 1 to 5 percent) — that is an SDS composition section, not the consumer list, and is not merged in here. Entered ungraded: product grading is the Sifter lane.",
        "owner": "Colgate-Palmolive",
        "owner_ev": "verified",
        "owner_src": "https://www.colgatepalmolive.com/en-us/smartlabel/35000472991",
        "tier": "mass",
        "tier_ev": "reported",
        "tier_src": "https://giantfood.com/groceries/product/suavitel-field-flowers-liquid-fabric-softener-46-oz-jug/168076",
        "tier_note": "National mass-market brand distributed through grocery, mass and dollar channels; market-position vocabulary, not a single retail channel.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": 3,
        "exposure_ev": "extrapolated",
        "exposure_src": "https://www.indexbox.io/store/united-states-fabric-softeners-conditioners-market-report/",
        "exposure_basis": "Derived, not measured. Fabric-conditioner household penetration in the US is 80 to 85% (IndexBox, 2026), liquid is 65 to 75% of category volume, and Colgate-Palmolive is estimated at 3.52% of the global textile-softener market on $0.19B of 2024 revenue (ReportPrime, 2024) — a world figure, not a US one, which understates the brand in its home hemisphere. Searched for a US household-penetration figure for Suavitel itself and found none. The one-significant-figure result of the chain is 3, reported as such rather than dressed up.",
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "not_reviewed",
    },
    {
        "name": "Fels-Naptha Heavy Duty Laundry Bar Soap",
        "brand": "Fels-Naptha",
        "cat": "Laundry",
        "safe": None,
        "ings": FELS_INGS,
        "heritage": True,
        "heritage_note": "The heritage case this database is built to hold: a bar soap in continuous use since the 1890s, still sold on the same promise, whose modern SDS shows a composition that is mostly tallow and coconut soaps with a terpene fraction at 1 to 5 percent. Commonly cited first-sale year is 1893; treated here as reported, not verified against a primary record.",
        "source": "Henkel Corporation safety data sheet, composition section",
        "source_url": "https://pim.henkelgroup.net/henkel/sds/L/2567828/US/EN?matName=BAR+SOAP+FELS+NAPTHA+BROWN",
        "note": "Entered from the manufacturer's SDS composition section, not from a consumer pack list. The SDS prints concentration ranges only and withholds the balance as trade secret, so this is a partial disclosure and is recorded as partial rather than smoothed. A Canadian-market SDS under the same manufacturer declares formaldehyde on the Prop 65 list; the US SDS composition section read today does not, and the two are different filings for different markets, so no Prop 65 flag is carried here on that basis alone. Category follows the other laundry bar soaps already in the database (Zote). Entered ungraded: product grading is the Sifter lane.",
        "owner": "Henkel",
        "owner_ev": "verified",
        "owner_src": "https://pim.henkelgroup.net/henkel/sds/L/2567828/US/EN?matName=BAR+SOAP+FELS+NAPTHA+BROWN",
        "tier": "grocery",
        "tier_ev": "reported",
        "tier_src": "https://pim.henkelgroup.net/henkel/sds/L/2567828/US/EN?matName=BAR+SOAP+FELS+NAPTHA+BROWN",
        "tier_note": "Grocery-and-mass laundry aisle; the channel the SDS distribution line and the other laundry bars in this database sit in.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": None,
        "exposure_ev": "untested",
        "exposure_src": None,
        "exposure_basis": "searched for a published household-penetration or sales-share figure for Fels-Naptha and for the laundry-bar format; found none, and the laundry-care category figure (above 95% of households, IndexBox) describes the category, not this bar. This is our research gap, not a statement about the product. Left null rather than estimated.",
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "partial",
    },
    {
        "name": "Assured Antiseptic Wet Wipes Vitamin E and Aloe",
        "brand": "Assured",
        "cat": "Disinfectant",
        "safe": None,
        "ings": ASSURED_INGS,
        "heritage": False,
        "source": "FDA OTC drug label via DailyMed (SPL)",
        "source_url": "https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=c04e2921-20d7-43c2-b9b9-07df8e425312",
        "note": "The dollar-store tier discloses exactly where a federal regulator makes it disclose, and nowhere else — this is that rule made concrete. The same house brand's general cleaners publish no ingredient list at all, but an antiseptic wipe is an FDA OTC drug, so the full active and inactive list is filed and public, with Greenbrier International named as the labeler of record. The active is benzalkonium chloride, a quaternary ammonium, which the database already carries. Entered ungraded: product grading is the Sifter lane. NDC 33992-5111.",
        "owner": "Greenbrier International",
        "owner_ev": "verified",
        "owner_src": "https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=c04e2921-20d7-43c2-b9b9-07df8e425312",
        "tier": "dollar-store",
        "tier_ev": "reported",
        "tier_src": "https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=c04e2921-20d7-43c2-b9b9-07df8e425312",
        "tier_note": "Assured is the Dollar Tree house brand; Greenbrier International, Inc. is the labeler of record on the FDA filing.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": None,
        "exposure_ev": "untested",
        "exposure_src": None,
        "exposure_basis": "searched for a published household-penetration or sales figure for this SKU and for the Assured brand; found none. Dollar-store channel share exists at the store level, not the SKU level, and would not separate this wipe from the rest of the aisle. Left null rather than estimated.",
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "not_reviewed",
    },
]

ING_NOTE = (
    "Added by the night-shift spectrum harvest (2026-09-27) from a manufacturer or "
    "manufacturer-filing disclosure. No PubChem/ECHA grade has been resolved for this "
    "entry yet, so g is null rather than a guess. Sharing a key with an existing record "
    "is intentional."
)


def main() -> int:
    prod_path = os.path.join(DATA, "products.json")
    ing_path = os.path.join(DATA, "ingredients.json")

    products = json.loads(open(prod_path, encoding="utf-8").read())
    ingredients = json.loads(open(ing_path, encoding="utf-8").read())

    existing_names = {p["name"] for p in products}

    added_products = []
    new_ing_keys = []
    seen_new = set()

    for prod in PRODUCTS:
        if prod["name"] in existing_names:
            continue
        for ing in prod["ings"]:
            if ing not in ingredients and ing not in seen_new:
                seen_new.add(ing)
                new_ing_keys.append(ing)
        rec = dict(prod)
        rec["added"] = TODAY
        rec["updated"] = TODAY
        added_products.append(rec)

    # Referential check: every product's ingredients must resolve after the add.
    resolving = set(ingredients) | set(new_ing_keys)
    for prod in added_products:
        missing = [i for i in prod["ings"] if i not in resolving]
        if missing:
            raise SystemExit(f"HALT: {prod['name']} references unknown ingredients: {missing}")

    # Owner check: the owner key must exist in owners.json (apply_owners() rewrites
    # `owner` from that registry on every build, so a product-only owner is wiped).
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
            "s": f"{ing}. Listed in a manufacturer disclosure read 2026-09-27; not yet graded against GHS.",
        }

    products.extend(added_products)

    open(prod_path, "w", encoding="utf-8").write(json.dumps(products, indent=1, ensure_ascii=False) + "\n")
    open(ing_path, "w", encoding="utf-8").write(json.dumps(ingredients, indent=1, ensure_ascii=False) + "\n")

    print(f"wrote {len(products)} products, {len(ingredients)} ingredients")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
