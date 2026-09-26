#!/usr/bin/env python3
"""Night shift station 2 (2026-09-26): exposure-ordered harvest, thin tiers.

Two products into the thinnest tiers, both with ingredient lists read from the
manufacturer's own disclosure on 2026-09-26:

  * Signature Select (Albertsons private label) Dish Soap, Ultra Concentrated,
    Ocean Scent — SmartLabel CA SB-258 disclosure, UPC 021130424481.
  * Rite Aid "Simplify Clean And Protect" medicated liquid hand soap
    (benzalkonium chloride 0.13%) — FDA OTC drug labeling, NDC 11822-2003.

Caveats carried into the records, not smoothed:
  * Both products enter UNGRADED (`safe: null`). Product grading is the Sifter
    lane; a blank here is honest, and no hazard is asserted that has no source.
  * Ingredient names not already in ingredients.json are added with `g: null`
    ("listed in the manufacturer disclosure, not yet graded"). That is the same
    honest ungraded state already used for complex mixtures in this repo.
  * Exposure is `untested` for both: no published per-product household
    penetration figure exists for a private-label SKU, and the basis says so
    rather than estimating.
  * No substitutes are attached, because no hazard grade is asserted yet and the
    substitute rule binds on D/F grades (`tasks/SPX-001`).

Run: python3 tools/harvest_2026_09_26.py
Then: python3 tools/validate_certainty.py --apply && python3 build.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
TODAY = "2026-09-26"

SS_SRC = "https://smartlabel.labelinsight.com/product/4844505/ingredients"
RA_SRC = "https://ndclist.com/ndc/11822-2003"

SS_INGS = [
    "Water",
    "Benzenesulfonic acid, C10-16-alkyl derivs., compds. with triethanolamine",
    "Fatty acids, C12-18, Me esters, sulfonated, sodium salts",
    "Sodium Laureth Sulfate",
    "Sodium Lauryl Sulfate",
    "Lauramine Oxide",
    "Alcohol",
    "Alcohols, C12-15, Ethoxylated",
    "Myristamine Oxide",
    "Benzene, C10-13 alkyl derivatives",
    "Triethanolamine",
    "Tetrasodium EDTA",
    "Fragrance",
    "Dipropylene Glycol",
    "Isobornyl Acetate",
    "2,6-Dimethyl-7-octen-2-ol",
    "Citronellyl Nitrile",
    "Terpinolene",
    "Limonene",
    "Hexahydro-methanoindenyl propionate",
    "Terpineol",
    "Buteth-3",
    "Colorant",
    "Sodium Benzotriazolyl Butylphenol Sulfonate",
    "Methylchloroisothiazolinone",
    "Methylisothiazolinone",
    "Tributyl Citrate",
]

RA_INGS = [
    "Benzalkonium Chloride",
    "Water",
    "Glycerin",
    "Cocamidopropyl Betaine",
    "Poloxamer 124",
    "Hydroxyethylcellulose",
    "Blue 1",
    "Citric Acid",
    "Methylchloroisothiazolinone",
    "Red 33",
    "Tetrasodium EDTA",
    "Methylisothiazolinone",
    "Fragrance",
]

PRODUCTS = [
    {
        "name": "Signature Select Dish Soap, Ultra Concentrated, Ocean Scent",
        "brand": "Signature Select",
        "cat": "Dish Soap",
        "safe": None,
        "ings": SS_INGS,
        "heritage": False,
        "source": "Signature Select SmartLabel disclosure (California Cleaning Product Right to Know Act)",
        "source_url": SS_SRC,
        "added": TODAY,
        "updated": TODAY,
        "note": (
            "Full intentionally-added ingredient list published on SmartLabel under the "
            "California Cleaning Product Right to Know Act. Fragrance is named but not "
            "broken out, and the fragrance components that ARE named (isobornyl acetate, "
            "citronellyl nitrile, terpinolene, terpineol) sit alongside it as separate "
            "entries, which is more disclosure than most SKUs in this tier publish. "
            "Entered ungraded: product grading is the Sifter lane."
        ),
        "owner": "Albertsons Companies, Inc.",
        "owner_ev": "reported",
        "owner_src": SS_SRC,
        "tier": "grocery",
        "tier_ev": "reported",
        "tier_src": SS_SRC,
        "tier_note": (
            "Signature Select is the Albertsons Companies private label, distributed by "
            "Better Living Brands LLC (Pleasanton, CA — Albertsons' headquarters address), "
            "which is the distributor named on the disclosure page itself."
        ),
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": None,
        "exposure_ev": "untested",
        "exposure_src": None,
        "exposure_basis": (
            "searched for a published per-product US household penetration figure for this "
            "SKU; private-label dish soaps are not individually covered by any open "
            "penetration dataset, and a chain-share figure would not separate this SKU from "
            "the rest of the Signature Select line. Left as a research gap rather than "
            "estimated."
        ),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "not_reviewed",
    },
    {
        "name": "Rite Aid Simplify Clean And Protect Medicated Liquid Hand Soap",
        "brand": "Rite Aid",
        "cat": "Hand Soap",
        "safe": None,
        "ings": RA_INGS,
        "heritage": False,
        "source": "FDA OTC drug labeling (NDC 11822-2003), labeler Rite Aid Corporation",
        "source_url": RA_SRC,
        "added": TODAY,
        "updated": TODAY,
        "note": (
            "Antibacterial hand soap, benzalkonium chloride 0.13%. Because it is an FDA OTC "
            "drug, the full inactive-ingredient list is a labelling requirement — which is "
            "why a store-brand hand soap discloses more than the store-brand cleaners beside "
            "it. Entered ungraded: product grading is the Sifter lane."
        ),
        "owner": "Rite Aid Corporation",
        "owner_ev": "verified",
        "owner_src": RA_SRC,
        "tier": "drugstore",
        "tier_ev": "reported",
        "tier_src": RA_SRC,
        "tier_note": "Rite Aid Corporation is the labeler of record on the FDA listing.",
        "substitutes": [],
        "no_substitute_known": None,
        "no_substitute_note": None,
        "exposure": None,
        "exposure_ev": "untested",
        "exposure_src": None,
        "exposure_basis": (
            "searched for a published per-product US household penetration figure for this "
            "SKU; none exists in the open sources. Left as a research gap rather than "
            "estimated."
        ),
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "not_reviewed",
    },
]

NEW_OWNERS = {
    "Albertsons Companies, Inc.": {
        "type": "public (ACI)",
        "detail": (
            "Operates Albertsons, Safeway, Vons, Jewel-Osco and others; the Signature Select "
            "and Signature SELECT house brands are its private label, distributed through "
            "Better Living Brands LLC, Pleasanton, CA."
        ),
        "ev": "reported",
        "src": SS_SRC,
        "brands": ["Signature Select", "Signature SELECT", "Better Living Brands", "O Organics"],
    },
    "Rite Aid Corporation": {
        "type": "public (RAD, formerly NYSE)",
        "detail": "Owns the Rite Aid and Simplify house brands; labeler of record on the FDA OTC listings.",
        "ev": "verified",
        "src": RA_SRC,
        "brands": ["Rite Aid", "Simplify"],
    },
}


def _new_ing(name):
    return {
        "g": None,
        "s": f"{name}. Listed in the manufacturer disclosure; not yet graded against GHS.",
        "ev": "Low",
        "gr": {},
        "impacts": [],
        "note": (
            "Added by the night-shift harvest from a manufacturer ingredient disclosure. "
            "No PubChem/ECHA grade has been resolved for this entry yet, so g is null "
            "rather than a guess. Sharing a key with an existing record is intentional."
        ),
    }


def main():
    prods = json.loads((DATA / "products.json").read_text(encoding="utf-8"))
    ings = json.loads((DATA / "ingredients.json").read_text(encoding="utf-8"))
    owners = json.loads((DATA / "owners.json").read_text(encoding="utf-8"))

    existing_prod = {p.get("name") for p in prods}
    lower = {}
    for k in ings:
        lower.setdefault(k.strip().lower(), k)

    def resolve(name):
        k = lower.get(name.strip().lower())
        if k:
            return k, False
        ings[name] = _new_ing(name)
        lower[name.strip().lower()] = name
        return name, True

    added_ings, added_prods = [], []
    for p in PRODUCTS:
        if p["name"] in existing_prod:
            continue
        p = dict(p)
        canon = []
        for n in p["ings"]:
            k, is_new = resolve(n)
            if is_new:
                added_ings.append(k)
            canon.append(k)
        p["ings"] = canon
        prods.append(p)
        added_prods.append(p["name"])

    added_owners = []
    for name, rec in NEW_OWNERS.items():
        if name not in owners["owners"]:
            owners["owners"][name] = rec
            added_owners.append(name)

    (DATA / "products.json").write_text(json.dumps(prods, indent=1, ensure_ascii=False), encoding="utf-8")
    (DATA / "ingredients.json").write_text(json.dumps(ings, indent=1, ensure_ascii=False), encoding="utf-8")
    (DATA / "owners.json").write_text(json.dumps(owners, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"added products: {added_prods}")
    print(f"added ingredients: {len(added_ings)}")
    for n in added_ings:
        print(f"  + {n}")
    print(f"added owner records: {added_owners}")


if __name__ == "__main__":
    main()
