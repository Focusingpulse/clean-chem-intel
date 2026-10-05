#!/usr/bin/env python3
"""Night-shift station 2 harvest, 2026-10-05 (Dolman).

Ordered by EXPOSURE, not price tier (Trellis, Sep 22 2026). Target: the thinnest
channel tier in the spectrum. Measured at head: drugstore = 7 products, the
fewest of the four channel tiers (dollar-store 15, grocery 25, apothecary-bulk
11). SPX-002 names the drugstore tier explicitly.

Why this block. The drugstore house-brand CLEANERS (all-purpose, glass, toilet,
disinfecting wipes) are published only on cvs.com / walgreens.com / riteaid.com
product pages, which return 403 to a machine fetch and are not enumerable. That
is a disclosure gap and is filed as one, not filled. What IS machine-readable
and authoritative is the FDA OTC drug label, because a store-brand antiseptic,
rubbing alcohol or hydrogen peroxide is a regulated OTC drug: the label is the
manufacturer's own filing and it lists every active and inactive ingredient.
DailyMed (NLM) serves those filings. This fire therefore adds the drugstore
house-brand antiseptic / disinfectant staples -- the products a household
actually keeps under the sink and in the first-aid kit -- with verified lists.

Two findings this block produces, each legible from the labels alone:

  1. **The drugstore house brands are contract-manufactured, like the dollar
     store.** The labeler of record is the chain (CVS Pharmacy, Inc. / Walgreen
     Co.), but the maker named in the same filing is a third party: Nice-Pak
     Products, LLC (both chains' hydrogen peroxide), Kleen Test Products
     Corporation (both chains' alcohol wipes and CVS's peroxide wipes), and
     FillTech USA, LLC (Walgreens sanitizing wipes). Same shape as the
     dollar-store finding: the shelf says the chain, the filing says the
     contract maker.
  2. **The simplest formulas are the cheapest products.** CVS and Walgreens
     hydrogen peroxide is two lines -- hydrogen peroxide and water. CVS's own
     rubbing alcohol adds a propellant and a preservative (nitrogen, sodium
     benzoate) that the hydrogen peroxide does not need. The scented
     benzethonium wipe is eleven lines.

Nothing here is graded. Product grading is the Sifter lane; a blank as-sold
grade is the honest state. Substitutes are supplied because a reader can act on
a first-aid-aisle hazard today.

Idempotent: a product whose `name` already exists is skipped, an ingredient key
already present is left untouched, and a second run reports 0 added.

Usage:  python3 tools/harvest_2026_10_05.py [--dry-run] [--no-changelog]
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-05"

DRY = "--dry-run" in sys.argv
NO_CHANGELOG = "--no-changelog" in sys.argv

DM = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
SETID = {
    "cvs_ipa": "2bd271ff-bb2e-426b-a7ad-87bb7dfb3df6",
    "cvs_h2o2": "7f518646-c8fe-499a-b5e4-8e5a5a90e01d",
    "cvs_ipa_wipes": "7e027210-9729-4659-8a75-b6b2ac60f7bc",
    "cvs_h2o2_wipes": "d2c22ab0-9647-4025-8282-6b492209b04c",
    "walg_h2o2": "eea239fe-554f-4487-9312-3ab0af27d530",
    "walg_ipa_wipes": "e8b0ecc3-3a30-47c9-b7d1-518681d575b4",
    "walg_san_wipes": "42de3b25-692b-eaff-e063-6294a90a0d21",
}

# Exposure sources read and quoted 2026-10-05 (HTTP 200, browser UA).
IB_CLEAN_WIPES = ("https://www.indexbox.io/store/"
                  "united-states-cleaning-wipes-market-analysis-forecast-"
                  "size-trends-and-insights/")
IB_DIS_WIPES = ("https://www.indexbox.io/store/"
                "united-states-kw-disinfecting-wipes-840-market-analysis-"
                "forecast-size-trends-and-insights/")

CVS_OWNER_SRC = ("https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm"
                 "?setid=63798c63-94fe-4ba8-8692-ca8be43c151e")
WALG_OWNER_SRC = ("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
                  "?setid=b45cbd3b-cba7-4c26-90bf-ec729dae3")

# --------------------------------------------------------------------------
# Ingredient key resolution. Label wording -> existing canonical key, where the
# substance is the same and a second key would be a synonym for one CAS.
# --------------------------------------------------------------------------
ALIASES = {
    # DailyMed lists the (S)-form under its IUPAC-ish name; the registry key is
    # the plain name used by every other record.
    "Limonene, (+)-": "Limonene",
}

# New keys minted this fire. Shape follows the registry: ungraded is recorded as
# ev "Low" with g null, never a guess. None of these is resolved to a grade yet.
NEW_KEYS = {
    "Laureth-4": {
        "s": "Ethoxylated lauryl alcohol surfactant (average 4 EO units); a "
             "nonionic detergent and wetting agent used in wipes and cleaners.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Walgreens Sanitizing Wipes OTC label (DailyMed, "
                "labeler Walgreens, maker FillTech USA, LLC) as an inactive "
                "ingredient. The printed Drug Facts panel words this class as "
                "'alkoxylated alcohol'; the SPL ingredient entry resolves it to "
                "Laureth-4. Not yet graded.",
    },
    "Isosteareth-10": {
        "s": "Ethoxylated isostearyl alcohol surfactant (average 10 EO units); "
             "a nonionic emulsifier and wetting agent.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Walgreens Sanitizing Wipes OTC label (DailyMed) "
                "as an inactive ingredient. The printed Drug Facts panel words "
                "this class as 'ethoxylated fatty alcohol'; the SPL ingredient "
                "entry resolves it to Isosteareth-10. Not yet graded.",
    },
    "Steareth-21": {
        "s": "Ethoxylated stearyl alcohol surfactant (average 21 EO units); a "
             "nonionic emulsifier used to keep a wipe's lotion stable.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Walgreens Sanitizing Wipes OTC label (DailyMed) "
                "as an inactive ingredient. Not yet graded.",
    },
    "Caprylyl Glycol": {
        "s": "1,2-Octanediol; a glycol used as a skin-conditioning agent and "
             "preservative booster.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Walgreens Sanitizing Wipes OTC label (DailyMed) "
                "as an inactive ingredient. The printed Drug Facts panel words "
                "it as '1,2-octanediol'; the SPL ingredient entry resolves it "
                "to Caprylyl Glycol. Not yet graded.",
    },
    "Sorbic Acid": {
        "s": "A naturally occurring straight-chain unsaturated fatty acid used "
             "as a preservative (E200).",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Walgreens Sanitizing Wipes OTC label (DailyMed) "
                "as an inactive ingredient. Not yet graded.",
    },
    "Polysorbate 80": {
        "s": "Polyoxyethylene (20) sorbitan monooleate; a nonionic surfactant "
             "and emulsifier.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the CVS Hydrogen Peroxide Wipes OTC label (DailyMed, "
                "labeler CVS Pharmacy, maker Kleen Test Products Corporation) "
                "as an inactive ingredient. Not yet graded.",
    },
}


def exp_wipes(cat_note: str) -> dict:
    return {
        "exposure_ev": "extrapolated",
        "exposure_src": IB_CLEAN_WIPES,
        "exposure_basis": (
            "Derived, not measured. The source states that the US cleaning "
            "wipes market has high household penetration, 'over 90% of US "
            "households use at least one type of cleaning wipe regularly', and "
            "that disinfecting and sanitizing wipes are the largest segment at "
            "roughly 40 to 45 percent of category volume with private-label "
            "penetration reaching 30 to 35 percent of that segment. Searched "
            "for a published per-product or per-brand US household-penetration "
            "figure for this specific store-brand wipe and located none; "
            "retailer brand shares for the drugstore channel are not published "
            "at product level. The estimate therefore derives from category "
            "penetration and the product's position as one store brand inside "
            "the drugstore channel, and stops there. Rounded to one significant "
            "figure, order-of-magnitude. " + cat_note
        ),
    }


def exp_untested(cat_note: str) -> dict:
    return {
        "exposure": None,
        "exposure_ev": "untested",
        "exposure_src": None,
        "exposure_basis": (
            "Searched for a published US household-penetration figure for "
            "rubbing alcohol or hydrogen peroxide as a household product, and "
            "for the household antiseptic category, in the open sources this "
            "database uses (IndexBox category pages, CDC/ATSDR, market "
            "summaries). Located no citable household-base figure. The market "
            "reports that exist report channel share of category value (for "
            "example, household and retail as a share of the rubbing-alcohol "
            "market), which is a share of sales and not a share of households "
            "and is not a substitute for one. Left as a research gap rather "
            "than estimated. " + cat_note
        ),
    }


def sub(name, tier, note):
    return {"name": name, "tier": tier, "note": note}


# --------------------------------------------------------------------------
# Products. Every ingredient list below is the SPL ingredient section of the
# FDA OTC drug label, read 2026-10-05 from DailyMed.
# --------------------------------------------------------------------------
PRODUCTS = [
    # ---- CVS Health (labeler CVS Pharmacy, Inc.) --------------------------
    {
        "name": "CVS Health Isopropyl Rubbing Alcohol 70%",
        "brand": "CVS Health",
        "cat": "Disinfectant",
        "ings": ["Isopropyl Alcohol", "Water", "Sodium Benzoate", "Nitrogen"],
        "source": ("FDA OTC drug label (Drug Facts) via DailyMed, labeler CVS "
                   "Pharmacy, Inc. Active: isopropyl alcohol 70 percent by "
                   "volume. Inactive: nitrogen, purified water, sodium "
                   "benzoate. NDC 51316-979; aerosol spray."),
        "source_url": DM + SETID["cvs_ipa"],
        "note": ("The label is a first-aid antiseptic, and the formula is "
                 "short: alcohol, water, a preservative and a propellant. The "
                 "sodium benzoate is a denaturant and preservative; nitrogen "
                 "is the aerosol propellant. 70 percent is the concentration "
                 "the label and general guidance both point at -- below about "
                 "60 percent it stops working as a disinfectant and above "
                 "about 90 percent it evaporates too fast. Flammable: keep it "
                 "away from any ignition source."),
        "owner": "CVS Health Corporation", "owner_ev": "reported",
        "owner_src": CVS_OWNER_SRC,
        "tier": "drugstore", "tier_ev": "reported",
        "tier_src": DM + SETID["cvs_ipa"],
        "tier_note": ("Sold under the CVS Health house brand; the OTC label's "
                      "labeler of record is CVS Pharmacy, Inc. Channel evidence "
                      "is the labeler identity, not a per-SKU retail page."),
        "substitutes": [sub("CVS Hydrogen Peroxide 3% Solution", "drugstore",
                            "Same store, same price band. Avoids the "
                            "flammability and the inhalation/drowsiness hazard "
                            "of a 70 percent alcohol; hydrogen peroxide carries "
                            "its own eye-damage hazard. Do not mix the two.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "exposure": None, "exposure_ev": "untested", "exposure_src": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A 70 percent isopropyl rubbing-alcohol spray."),
    },
    {
        "name": "CVS Hydrogen Peroxide 3% Solution",
        "brand": "CVS Health",
        "cat": "Disinfectant",
        "ings": ["Hydrogen Peroxide", "Water"],
        "source": ("FDA OTC drug label (Drug Facts) via DailyMed, labeler CVS "
                   "Pharmacy, Inc.; maker named in the filing Nice-Pak "
                   "Products, LLC. Active: hydrogen peroxide (stabilized) 3 "
                   "percent. Inactive: purified water. Two lines, the whole "
                   "formula."),
        "source_url": DM + SETID["cvs_h2o2"],
        "note": ("Two ingredients. The whole product is a 3 percent peroxide "
                 "solution in water; the label uses it as a first-aid "
                 "antiseptic and an oral debriding agent. The maker of record "
                 "is Nice-Pak Products, LLC, a contract manufacturer -- the "
                 "chain on the front, the contract maker in the filing. Keep "
                 "it in its own opaque bottle; light and heat break it down."),
        "owner": "CVS Health Corporation", "owner_ev": "reported",
        "owner_src": CVS_OWNER_SRC,
        "tier": "drugstore", "tier_ev": "reported",
        "tier_src": DM + SETID["cvs_h2o2"],
        "tier_note": ("Sold under the CVS Health house brand; labeler of "
                      "record CVS Pharmacy, Inc. Channel evidence is the "
                      "labeler identity."),
        "substitutes": [sub("CVS Health Isopropyl Rubbing Alcohol 70%",
                            "drugstore",
                            "Same store, same price band. Avoids hydrogen "
                            "peroxide's eye-damage and aquatic-toxicity "
                            "hazard; alcohol carries its own flammability "
                            "hazard. Never mix the two in one container.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "exposure": None, "exposure_ev": "untested", "exposure_src": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A 3 percent hydrogen peroxide solution."),
    },
    {
        "name": "CVS Isopropyl Rubbing Alcohol Wipes",
        "brand": "CVS Health",
        "cat": "Disinfectant",
        "ings": ["Isopropyl Alcohol", "Water"],
        "source": ("FDA OTC drug label (Drug Facts) via DailyMed, labeler CVS "
                   "Pharmacy, Inc.; maker named in the filing Kleen Test "
                   "Products Corporation. Active: isopropyl alcohol. Inactive: "
                   "water. NDC 51316-953; 40 per canister."),
        "source_url": DM + SETID["cvs_ipa_wipes"],
        "note": ("The wipe version of the rubbing alcohol. Two lines: alcohol "
                 "and water on a cloth. The maker of record is Kleen Test "
                 "Products Corporation, a contract manufacturer that also "
                 "makes the Walgreens alcohol wipes -- the same factory, two "
                 "chains. Alcohol wipes are flammable while wet; let them dry "
                 "before discarding."),
        "owner": "CVS Health Corporation", "owner_ev": "reported",
        "owner_src": CVS_OWNER_SRC,
        "tier": "drugstore", "tier_ev": "reported",
        "tier_src": DM + SETID["cvs_ipa_wipes"],
        "tier_note": ("Sold under the CVS house brand; labeler of record CVS "
                      "Pharmacy, Inc."),
        "substitutes": [sub("CVS Hydrogen Peroxide Wipes", "drugstore",
                            "Same store, same price band. Avoids the "
                            "flammability of an alcohol wipe; hydrogen "
                            "peroxide carries its own eye-damage hazard.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "exposure": 2, "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_wipes("A store-brand isopropyl alcohol wipe in the drugstore "
                    "channel."),
    },
    {
        "name": "CVS Hydrogen Peroxide Wipes",
        "brand": "CVS Health",
        "cat": "Disinfectant",
        "ings": ["Hydrogen Peroxide", "Water", "Polysorbate 80"],
        "source": ("FDA OTC drug label (Drug Facts) via DailyMed, labeler CVS "
                   "Pharmacy, maker named in the filing Kleen Test Products "
                   "Corporation. Active: hydrogen peroxide. Inactive: "
                   "polysorbate 80, water."),
        "source_url": DM + SETID["cvs_h2o2_wipes"],
        "note": ("Three lines: peroxide, water, and a surfactant "
                 "(polysorbate 80) that helps the solution wet the cloth and "
                 "the surface. The maker of record is Kleen Test Products "
                 "Corporation. Same contract factory as the alcohol wipes on "
                 "the next shelf."),
        "owner": "CVS Health Corporation", "owner_ev": "reported",
        "owner_src": CVS_OWNER_SRC,
        "tier": "drugstore", "tier_ev": "reported",
        "tier_src": DM + SETID["cvs_h2o2_wipes"],
        "tier_note": ("Sold under the CVS house brand; labeler of record CVS "
                      "Pharmacy."),
        "substitutes": [sub("CVS Isopropyl Rubbing Alcohol Wipes", "drugstore",
                            "Same store, same price band. Avoids hydrogen "
                            "peroxide's eye-damage hazard; alcohol wipes are "
                            "flammable while wet.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "exposure": 2, "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_wipes("A store-brand hydrogen peroxide wipe in the drugstore "
                    "channel."),
    },
    # ---- Walgreens (labeler Walgreen Co.) ---------------------------------
    {
        "name": "Walgreens Hydrogen Peroxide 3% Solution",
        "brand": "Walgreens",
        "cat": "Disinfectant",
        "ings": ["Hydrogen Peroxide", "Water"],
        "source": ("FDA OTC drug label (Drug Facts) via DailyMed, labeler "
                   "Walgreen Co.; maker named in the filing Nice-Pak "
                   "Products, LLC. Active: hydrogen peroxide. Inactive: water. "
                   "NDC 0363-0871; 16 oz and 32 oz bottles."),
        "source_url": DM + SETID["walg_h2o2"],
        "note": ("Two lines, and the same contract maker as the CVS version: "
                 "Nice-Pak Products, LLC. The two chains' house-brand peroxide "
                 "is the same two-ingredient formula from the same factory, "
                 "different labels and prices."),
        "owner": "Walgreens Boots Alliance, Inc.", "owner_ev": "reported",
        "owner_src": WALG_OWNER_SRC,
        "tier": "drugstore", "tier_ev": "reported",
        "tier_src": DM + SETID["walg_h2o2"],
        "tier_note": ("Sold under the Walgreens house brand; labeler of record "
                      "Walgreen Co."),
        "substitutes": [sub("Walgreens 70% Isopropyl Alcohol Wipes",
                            "drugstore",
                            "Same store, same price band. Avoids hydrogen "
                            "peroxide's eye-damage and aquatic-toxicity "
                            "hazard; alcohol wipes are flammable while wet.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "exposure": None, "exposure_ev": "untested", "exposure_src": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A 3 percent hydrogen peroxide solution."),
    },
    {
        "name": "Walgreens 70% Isopropyl Alcohol Wipes",
        "brand": "Walgreens",
        "cat": "Disinfectant",
        "ings": ["Isopropyl Alcohol", "Water"],
        "source": ("FDA OTC drug label (Drug Facts) via DailyMed, labeler "
                   "Walgreen Company; maker named in the filing Kleen Test "
                   "Products Corporation. Active: isopropyl alcohol 70 "
                   "percent. Inactive: water. NDC 0363-6505."),
        "source_url": DM + SETID["walg_ipa_wipes"],
        "note": ("Two lines, and the same contract maker as the CVS alcohol "
                 "wipes: Kleen Test Products Corporation. The label carries "
                 "the concentration (70 percent) on the front, which matters "
                 "-- a wipe below about 60 percent is not doing the same job."),
        "owner": "Walgreens Boots Alliance, Inc.", "owner_ev": "reported",
        "owner_src": WALG_OWNER_SRC,
        "tier": "drugstore", "tier_ev": "reported",
        "tier_src": DM + SETID["walg_ipa_wipes"],
        "tier_note": ("Sold under the Walgreens house brand; labeler of record "
                      "Walgreen Company."),
        "substitutes": [sub("Walgreens Hydrogen Peroxide 3% Solution",
                            "drugstore",
                            "Same store, same price band. Avoids the "
                            "flammability of an alcohol wipe; hydrogen "
                            "peroxide carries its own eye-damage hazard.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "exposure": 2, "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_wipes("A store-brand isopropyl alcohol wipe in the drugstore "
                    "channel."),
    },
    {
        "name": "Walgreens Sanitizing Wipes",
        "brand": "Walgreens",
        "cat": "Disinfectant",
        "ings": ["Benzethonium Chloride", "Water", "Laureth-4", "Limonene",
                 "Glycerin", "Isosteareth-10", "Cocamidopropyl Betaine",
                 "Steareth-21", "Phenoxyethanol", "Caprylyl Glycol",
                 "Sorbic Acid"],
        "source": ("FDA OTC drug label (Drug Facts) via DailyMed, labeler "
                   "Walgreens; maker named in the filing FillTech USA, LLC. "
                   "Active: benzethonium chloride 0.13 percent. Inactive: "
                   "purified water, alkoxylated alcohol (SPL: Laureth-4), "
                   "d-limonene (SPL: Limonene, (+)-), ethoxylated fatty "
                   "alcohol (SPL: Isosteareth-10), cocamidopropyl betaine, "
                   "glycerin, 2-phenoxyethanol, 1,2-octanediol (SPL: Caprylyl "
                   "Glycol), sorbic acid."),
        "source_url": DM + SETID["walg_san_wipes"],
        "note": ("Eleven lines, and the only one of the seven here with a "
                 "fragrance allergen disclosed by name: d-limonene. The active "
                 "is benzethonium chloride at 0.13 percent, a quaternary "
                 "antiseptic, not an alcohol. The maker of record is FillTech "
                 "USA, LLC, a third contract manufacturer. The printed Drug "
                 "Facts panel words three of these as generic classes "
                 "('alkoxylated alcohol', 'ethoxylated fatty alcohol', "
                 "'1,2-octanediol'); the SPL ingredient entries resolve them to "
                 "Laureth-4, Isosteareth-10 and Caprylyl Glycol. A reader "
                 "avoiding fragrance allergens should know limonene is on the "
                 "label even though the product is unscented on the nose."),
        "owner": "Walgreens Boots Alliance, Inc.", "owner_ev": "reported",
        "owner_src": WALG_OWNER_SRC,
        "tier": "drugstore", "tier_ev": "reported",
        "tier_src": DM + SETID["walg_san_wipes"],
        "tier_note": ("Sold under the Walgreens house brand; labeler of record "
                      "Walgreens."),
        "substitutes": [sub("Walgreens 70% Isopropyl Alcohol Wipes",
                            "drugstore",
                            "Same store, same price band. Avoids benzethonium "
                            "chloride and the fragrance allergen d-limonene; "
                            "alcohol wipes are flammable while wet and harsher "
                            "on skin.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "exposure": 2, "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_wipes("A store-brand benzethonium-chloride sanitizing wipe in "
                    "the drugstore channel."),
    },
]


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def dump(path, obj, indent):
    # Measured at head: products/ingredients indent=1 no trailing newline;
    # changelog indent=2 no trailing newline. Match each file, do not assume.
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=indent, ensure_ascii=False)


def resolve(ings, lower, added_keys):
    new_lower = {k.lower(): k for k in NEW_KEYS}
    alias_lower = {k.lower(): v for k, v in ALIASES.items()}
    out = []
    for raw in ings:
        key = alias_lower.get(raw.lower(), raw)
        if key.lower() in lower:
            out.append(lower[key.lower()])
        elif key.lower() in new_lower:
            out.append(new_lower[key.lower()])
            added_keys.add(new_lower[key.lower()])
        else:
            raise SystemExit(f"unknown ingredient key, refusing to guess: {raw!r}")
    return out


def main():
    products = load(os.path.join(DATA, "products.json"))
    ingredients = load(os.path.join(DATA, "ingredients.json"))
    changelog = load(os.path.join(DATA, "changelog.json"))

    names = {r["name"] for r in products}
    lower = {k.lower(): k for k in ingredients}

    added = 0
    added_keys = set()
    for p in PRODUCTS:
        if p["name"] in names:
            print(f"skip (exists): {p['name']}")
            continue
        rec = dict(p)
        rec["ings"] = resolve(rec["ings"], lower, added_keys)
        rec.setdefault("no_substitute_known", None)
        rec.setdefault("no_substitute_note", None)
        rec.setdefault("heritage", False)
        rec.setdefault("safe", None)
        rec.setdefault("conc", None)
        rec.setdefault("conc_src", None)
        rec.setdefault("conc_ev", "untested")
        rec.setdefault("grade_as_sold", None)
        rec.setdefault("grade_as_sold_src", None)
        products.append(rec)
        names.add(rec["name"])
        added += 1
        print(f"add: {rec['name']}  ({len(rec['ings'])} ings)")

    for key in sorted(added_keys):
        if key.lower() in lower:
            print(f"key exists, not re-minting: {key}")
            continue
        ingredients[key] = NEW_KEYS[key]
        lower[key.lower()] = key
        print(f"new ingredient key: {key}")

    for r in products:
        for k in r["ings"]:
            if k not in ingredients:
                raise SystemExit(f"record {r['name']!r} references missing key {k!r}")

    if added and not NO_CHANGELOG:
        changelog.insert(0, {
            "date": TODAY,
            "text": ("Spectrum harvest: 7 products added to the drugstore tier "
                     "from FDA OTC drug labels read 2026-10-05 via DailyMed "
                     "(CVS Health and Walgreens house-brand rubbing alcohol, "
                     "hydrogen peroxide and wipes). The drugstore house brands "
                     "are contract-manufactured: Nice-Pak Products (both "
                     "chains' peroxide), Kleen Test Products (both chains' "
                     "alcohol wipes), FillTech USA (Walgreens sanitizing "
                     "wipes). The simplest formulas are the cheapest "
                     "products -- peroxide is two lines."),
        })

    if DRY:
        print(f"\nDRY RUN: would add {added} products, "
              f"{len(added_keys)} ingredient keys.")
        return

    dump(os.path.join(DATA, "products.json"), products, 1)
    dump(os.path.join(DATA, "ingredients.json"), ingredients, 1)
    dump(os.path.join(DATA, "changelog.json"), changelog, 2)
    print(f"\nwrote {added} products, {len(added_keys)} new ingredient keys.")


if __name__ == "__main__":
    main()
