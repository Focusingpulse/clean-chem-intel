#!/usr/bin/env python3
"""Daily gather (2026-10-06, 10:00Z maintenance lane): four high-volume US
cleaning products that were missing from the database, plus the ingredient
records and owner-registry entries they need.

Sources read on 2026-10-06:

  - BISSELL "Clean and Protect or Advanced Clean and Protect" ingredient list —
    the manufacturer's own CPIC-format disclosure, in order of concentration.
    https://supplier.bissell.com/Ingredients_Domestic/Clean%20and%20Protect%20or%20Advanced%20Clean%20and%20Protect%20Ingredient%20List.pdf
  - Earth Breeze Laundry Detergent Sheets, Fragrance Free (SKU L-06-LS-FF, the
    current US core product) — the manufacturer's own per-SKU ingredient table.
    https://help.earthbreeze.com/commonly-asked-questions/laundry-detergent-sheet-ingredients
  - Green Gobbler Drain Clog Remover — the manufacturer's own ingredient sheet.
    https://greengobbler.com/mwdownloads/download/link/id/2434
  - Sprayway Glass Cleaner (SW-050) — the manufacturer's own SDS, section 3.
    https://www.msdsdigital.com/system/files/SPRAYWAY%20GLASS%20CLEANER%20%20SW050.pdf

Why these four. The corpus is thin in three places and has no entry at all in
four brand families a US household is likely to own:

  - Floor & Carpet holds 11 products and no BISSELL. BISSELL is the number-one
    floor-care manufacturer in North America by sales and publishes a full
    CPIC-format ingredient list for its machine formulas.
  - Laundry holds 39 products and no detergent SHEET. The sheet is now a real
    US category (Earth Breeze is the largest seller) and it is a different
    delivery form from anything the DB carries: a film-cast solid, not a
    liquid, powder or pod.
  - Specialty holds 28 products and no Green Gobbler. Green Gobbler is the
    leading direct-to-consumer drain brand and its whole pitch is "no lye, no
    bleach", so it is the honest counter-entry to the caustic drain openers
    already recorded.
  - Glass holds 17 products and no Sprayway. Sprayway is the number-two US
    glass brand by unit share with the category's number-one sales velocity
    (the acquirer's own figure), and it is the aerosol glass cleaner the DB
    was missing.

Disclosure quality, stated honestly:
  - BISSELL and Earth Breeze publish a FULL intentionally-added list.
  - Green Gobbler publishes four lines and withholds the identity of its
    active as "Caustic Replacement" (trade secret). Recorded as the label term,
    ungraded, the same way the DB already carries "Proprietary Surfactant" and
    "Confidential Stabilizer Package".
  - Sprayway's SDS names only the hazardous components and states the rest are
    "not hazardous or below required disclosure limits". Water is the balance.
    This is a partial disclosure and is recorded as such.

Grading follows the house rule (docs/source-policy.md, docs/scoring-rubric.md):
only H-codes at >=40% ECHA C&L notifier consensus drive a dimension grade, read
from the headline (largest company-count) block of PubChem PUG View. Every
returned PubChem title was checked against the intended substance before the
record was accepted. All three new keys this run resolve to "Not Classified"
or to no CID at all, so no dimension grade is minted here — that is the honest
result, not an omission.

Nothing here is product-graded. Product grading is the Sifter lane; a blank
as-sold grade is the honest state, and substitutes[] is left empty for the same
reason (the substitute rule binds on a D/F grade, and none of these carries one
yet).

Run: python3 tools/gather_2026_10_06.py
Then: python3 build.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-06"

DRY = "--dry-run" in sys.argv
NO_CHANGELOG = "--no-changelog" in sys.argv

BISSELL_URL = ("https://supplier.bissell.com/Ingredients_Domestic/"
               "Clean%20and%20Protect%20or%20Advanced%20Clean%20and%20"
               "Protect%20Ingredient%20List.pdf")
BISSELL_OWNER_SRC = "https://www.bissell.com/en-us/about-us/our-history/"
EB_URL = ("https://help.earthbreeze.com/commonly-asked-questions/"
          "laundry-detergent-sheet-ingredients")
EB_OWNER_SRC = "https://earthbreeze.com/pages/about-us"
GG_URL = "https://greengobbler.com/mwdownloads/download/link/id/2434"
GG_OWNER_SRC = "https://greengobbler.com/mwdownloads/download/link/id/1852"
SPRAYWAY_URL = ("https://www.msdsdigital.com/system/files/"
                "SPRAYWAY%20GLASS%20CLEANER%20%20SW050.pdf")
SPRAYWAY_OWNER_SRC = ("https://www.highlinewarren.com/blog/976-Highline-Warren-"
                      "Acquires-Sprayway-a-Leader-in-Glass-Surface-Care")

# --------------------------------------------------------------------------
# Ingredient key resolution. Label wording -> existing canonical key, where the
# substance is the same and a second key would be a synonym for one CAS.
# --------------------------------------------------------------------------
ALIASES = {
    # Earth Breeze prints "sodium lauryl sulfate"; the DB key is the same
    # substance. (The manufacturer's own CAS column prints 68585-47-7 for this
    # line, which is the C10-16 alkyl-sulfate mixture rather than pure SLS
    # 151-21-3; that mismatch is noted on the product record.)
    "Sodium Dodecyl Sulfate": "Sodium Lauryl Sulfate",
    # Sprayway's SDS prints "Ethanol, 2-butoxy-"; the DB key is Butyloxyethanol.
    "Ethanol, 2-butoxy-": "Butyloxyethanol",
    # Green Gobbler's sheet prints "C9-C11 Alcohols ethoxylated"; the DB key is
    # the same substance (CAS 68439-46-3).
    "C9-C11 Alcohols ethoxylated": "Alcohols, C9-11, ethoxylated",
}

# New keys minted this fire. Shape follows the registry: ungraded is recorded as
# ev "Low"/"Medium" with g "Not Classified" (or null) and an explicit sourcing
# note, never a guess.
NEW_KEYS = {
    "Silicone Defoamer": {
        "s": "A silicone antifoam, typically a polydimethylsiloxane emulsion; "
             "added to suppress foam during machine cleaning.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on the BISSELL CPIC ingredient list as 'Silicone "
                "Defoamer' with no CAS. PubChem PUG REST returns 404 for the "
                "name and for 'Polydimethylsiloxane' — no discrete CID "
                "resolves — so no GHS classification is available. Recorded "
                "Not Classified rather than guessed. Distinct from the DB key "
                "'Dimethicone' (a named polymer) and from 'Silicone Emulsion' "
                "(a formulated emulsion); this is the label's class term.",
    },
    "Kaolin": {
        "s": "Hydrated aluminium silicate clay (china clay); a mineral builder "
             "and opacifier.",
        "ev": "Medium", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on the Earth Breeze Laundry Detergent Sheets ingredient "
                "table as 'kaolin' (manufacturer CAS column 92704-41-1; the "
                "CAS registry entry for kaolin is 1332-58-7). PubChem PUG REST "
                "returns 404 for the name — no discrete CID resolves for this "
                "UVCB mineral — so no GHS classification is available. Recorded "
                "Not Classified rather than guessed, the same way the DB "
                "already carries Bentonite and Smectite Clay.",
    },
    "Caustic Replacement": {
        "s": "The manufacturer's trade name for the active in Green Gobbler's "
             "drain opener; a non-caustic, non-hypochlorite clog dissolver.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "This is a label term, not a substance name: Green Gobbler's "
                "own ingredient sheet and SDS both print 'Caustic Replacement' "
                "and withhold the chemical name, CAS and exact concentration "
                "as a trade secret (5-10% per the SDS). No substance can be "
                "graded, so the key is recorded Not Classified with this note "
                "rather than assigned a grade. The brand's own claim is that "
                "it contains no sodium hydroxide and no chlorine/chloride or "
                "halide chemicals; that claim is the manufacturer's, not "
                "independently verified here.",
    },
}

# --------------------------------------------------------------------------
# Owners. BISSELL and Highline Warren are new to the registry; Green Gobbler is
# a brand of PurposeBuilt Brands, which is already recorded.
# --------------------------------------------------------------------------
NEW_OWNERS = {
    "Bissell": {
        "type": "private, family-owned",
        "detail": ("BISSELL Homecare, Inc., founded 1876 by Melville R. "
                   "Bissell in Grand Rapids, Michigan, and still owned by the "
                   "Bissell family; Anna Bissell led the company from 1889 and "
                   "is described by the company as the first female CEO in "
                   "America. Headquartered in Walker, Michigan. The company "
                   "states it is the number-one floor-care manufacturer in "
                   "North America by sales. It publishes CPIC-format "
                   "ingredient lists for its machine formulas on its own "
                   "supplier site."),
        "ev": "verified",
        "src": BISSELL_OWNER_SRC,
        "brands": ["BISSELL"],
    },
    "Highline Warren": {
        "type": "private",
        "detail": ("Highline Warren LLC, a private supplier of automotive and "
                   "household care products. It acquired the Sprayway brand "
                   "from PLZ Corp in January 2026; before that the brand sat "
                   "inside PLZ Corp, which had acquired Sprayway Inc. in 2005. "
                   "The acquirer's own announcement states Sprayway is the "
                   "number-two US glass brand by unit share with the "
                   "category's number-one sales velocity."),
        "ev": "reported",
        "src": SPRAYWAY_OWNER_SRC,
        "brands": ["Sprayway"],
    },
    "Earth Breeze": {
        "type": "private, venture-backed",
        "detail": ("Earth Breeze (Earth Breeze Inc), founded 2019, "
                   "headquartered in Medford, Oregon. The brand's own About "
                   "page states it is the number-one laundry detergent sheet "
                   "with over 3 million customers and that its core Fresh "
                   "Scent and Fragrance Free sheets are made at its "
                   "Harrodsburg, Kentucky plant. It is independently operated "
                   "and not owned by a consumer-goods conglomerate; "
                   "third-party profiles list a single identified minority "
                   "investor, the climate-focused fund Something Good "
                   "Ventures, with day-to-day control held by the company's "
                   "own leadership."),
        "ev": "reported",
        "src": EB_OWNER_SRC,
        "brands": ["Earth Breeze"],
    },
}

# Brands to append to an owner record that already exists.
OWNER_BRAND_ADDS = {
    "PurposeBuilt Brands": {
        "brands": ["Green Gobbler"],
        "note": ("Green Gobbler is a PurposeBuilt Brands brand: the Green "
                 "Gobbler SDS names 'PurposeBuilt Brands, 755 Tri-State "
                 "Parkway, Gurnee, IL 60031' as the manufacturer, and the "
                 "brand's own site prints the same Gurnee address. Added to "
                 "the brand list on 2026-10-06."),
    },
}


def exp_untested(cat_note: str) -> dict:
    return {
        "exposure": None,
        "exposure_ev": "untested",
        "exposure_src": None,
        "exposure_basis": (
            "Searched for a published US household-penetration figure for this "
            "product and for its category in the open sources this database "
            "uses (IndexBox category pages, market summaries). Located no "
            "citable household-base figure; the reports that exist give "
            "channel share of category value, which is not a share of "
            "households and is not a substitute for one. Left as a research "
            "gap rather than estimated. " + cat_note
        ),
    }


# --------------------------------------------------------------------------
# Products. Every ingredient list below is the manufacturer's own published
# list, read 2026-10-06.
# --------------------------------------------------------------------------
PRODUCTS = [
    {
        "name": "BISSELL Advanced Clean + Protect",
        "brand": "BISSELL",
        "cat": "Floor & Carpet",
        "ings": ["Water", "Alcohol Alkoxylate", "Sodium Citrate",
                 "Acrylic Polymer", "Linear Alcohol Ethoxylate",
                 "Sodium Caprylyl Sulfonate", "Alkyl Polyglucoside",
                 "Sodium Polyacrylate", "Fragrance", "Silicone Defoamer",
                 "Sodium Hydroxide", "Methylisothiazolinone",
                 "Benzisothiazolinone"],
        "source": ("Manufacturer ingredient disclosure (supplier.bissell.com, "
                   "'Clean and Protect or Advanced Clean and Protect "
                   "Ingredient List', CPIC format, in order of highest to "
                   "lowest concentration): Water (7732-18-5), Alcohol "
                   "Alkoxylate (proprietary), Sodium Citrate (68-04-2), "
                   "Acrylic Polymer (proprietary), Linear Alcohol Ethoxylate "
                   "(proprietary), Sodium Caprylyl Sulfonate (5324-84-5), "
                   "Alkyl Polyglucoside (proprietary), Sodium Polyacrylate "
                   "(proprietary), Fragrance (proprietary), Silicone Defoamer "
                   "(proprietary), Sodium Hydroxide (1310-73-2), "
                   "Methylisothiazolinone (2682-20-4), Benzisothiazolinone "
                   "(2634-33-5)."),
        "source_url": BISSELL_URL,
        "note": ("A full intentionally-added list, published by the maker in "
                 "CPIC format. The formula is a water-based carpet and "
                 "upholstery machine cleaner: alcohol alkoxylate, linear "
                 "alcohol ethoxylate, sodium caprylyl sulfonate and alkyl "
                 "polyglucoside are the surfactant package, sodium citrate and "
                 "sodium polyacrylate the builders and anti-redeposition "
                 "agents, acrylic polymer the soil-release polymer, and the "
                 "isothiazolinone pair the preservative. Sodium hydroxide is "
                 "the pH adjuster. The manufacturer publishes this single "
                 "list for both the Clean + Protect and the Advanced Clean + "
                 "Protect formulas, so the record is named for the Advanced "
                 "product and the list covers both. The brand's own claim is "
                 "no phosphates, dyes, optical brighteners or heavy metals, "
                 "which the list supports: none appears."),
        "owner": "Bissell", "owner_ev": "verified",
        "owner_src": BISSELL_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": BISSELL_URL,
        "tier_note": ("Sold at mass, hardware and home-improvement retailers; "
                      "recorded as mass. Channel evidence is the brand's own "
                      "retail placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A carpet and upholstery machine-cleaning formula in "
                       "the mass channel."),
    },
    {
        "name": "Earth Breeze Laundry Detergent Sheets, Fragrance Free",
        "brand": "Earth Breeze",
        "cat": "Laundry",
        "ings": ["Sodium Lauryl Sulfate", "Polyvinyl Alcohol", "Kaolin",
                 "Water", "Laureth-7", "Glycerin", "Sodium Citrate",
                 "Caprylyl/Capryl Glucoside", "Lauryl Glucoside",
                 "Cocamidopropyl Betaine", "Lauramidopropylamine Oxide",
                 "Tetrasodium Glutamate Diacetate", "Protease Enzyme",
                 "Amylase Enzyme", "Citric Acid"],
        "source": ("Manufacturer ingredient disclosure (help.earthbreeze.com, "
                   "'Earth Breeze Product Ingredients', SKU L-06-LS-FF — "
                   "Laundry Detergent Sheets Fragrance Free, USA): sodium "
                   "lauryl sulfate, polyvinyl alcohol, kaolin, water (aqua), "
                   "laureth-7, glycerin, sodium citrate, caprylyl/capryl "
                   "glucoside, lauryl glucoside, cocamidopropyl betaine, "
                   "lauramidopropylamine oxide, tetrasodium glutamate "
                   "diacetate, protease enzyme, amylase enzyme, citric acid."),
        "source_url": EB_URL,
        "note": ("A full intentionally-added list for the current US core "
                 "product, published by the maker per SKU. The sheet is a "
                 "film-cast solid: polyvinyl alcohol is the film former that "
                 "holds the cleaning ingredients until the sheet dissolves, "
                 "kaolin is the mineral builder, glycerin the viscosity "
                 "modifier, and the surfactant package is sodium lauryl "
                 "sulfate plus four milder nonionic/amphoteric surfactants "
                 "(laureth-7, caprylyl/capryl glucoside, lauryl glucoside, "
                 "cocamidopropyl betaine, lauramidopropylamine oxide). Two "
                 "enzymes (protease, amylase) carry protein and starch stains, "
                 "tetrasodium glutamate diacetate is the chelant, and citric "
                 "acid sets pH. The manufacturer's own CAS column prints "
                 "68585-47-7 for the line it labels 'sodium lauryl sulfate', "
                 "which is the C10-16 alkyl-sulfate mixture rather than pure "
                 "SLS (151-21-3); the label term is recorded and the mismatch "
                 "is stated here rather than resolved by guess. The brand's "
                 "claims of no optical brighteners, parabens, dyes or added "
                 "preservatives are consistent with the list — none appears."),
        "owner": "Earth Breeze", "owner_ev": "reported",
        "owner_src": EB_URL,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": EB_URL,
        "tier_note": ("Sold direct-to-consumer and at mass retailers; recorded "
                      "as mass. Channel evidence is the brand's own retail "
                      "placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A laundry detergent sheet in the mass channel."),
    },
    {
        "name": "Green Gobbler Drain Clog Remover",
        "brand": "Green Gobbler",
        "cat": "Specialty",
        "ings": ["Water", "Caustic Replacement",
                 "Alcohols, C9-11, ethoxylated", "Xanthan Gum"],
        "source": ("Manufacturer ingredient sheet (greengobbler.com, 'Drain "
                   "Clog Remover', product codes G0015/G0015C/G0665, revision "
                   "2021-07-27): Water (7732-18-5, diluent), Caustic "
                   "replacement (cleaning agent; no CAS published), C9-C11 "
                   "alcohols ethoxylated (68439-46-3, cleaning agent), Xanthan "
                   "gum (11138-66-2, thickener)."),
        "source_url": GG_URL,
        "note": ("A PARTIAL disclosure, and the honest edge of the tool: the "
                 "manufacturer names four lines and withholds the identity of "
                 "its active as 'Caustic Replacement' (trade secret). The SDS "
                 "for the same product family puts that active at 5-10% and "
                 "the alcohol ethoxylate at 0.5-1.5%. The brand's whole pitch "
                 "is that it is a non-caustic, non-hypochlorite alternative to "
                 "lye and bleach drain openers — the manufacturer states it "
                 "contains no sodium hydroxide and no chlorine, chloride or "
                 "halide chemicals. That claim is the manufacturer's; it is "
                 "recorded as a claim, not verified here. This is the honest "
                 "counter-entry to the caustic drain openers already in the "
                 "database."),
        "owner": "PurposeBuilt Brands", "owner_ev": "verified",
        "owner_src": GG_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": GG_URL,
        "tier_note": ("Sold direct-to-consumer and at mass and hardware "
                      "retailers; recorded as mass. Channel evidence is the "
                      "brand's own retail placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "partial",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A drain opener in the mass channel."),
    },
    {
        "name": "Sprayway Glass Cleaner",
        "brand": "Sprayway",
        "cat": "Glass",
        "ings": ["Water", "Ethanol", "Butyloxyethanol", "Propane", "Butane"],
        "source": ("Manufacturer safety data sheet (Sprayway, Inc., Sprayway "
                   "Glass Cleaner SW-050, SDS number RE1000000075, section 3): "
                   "Ethanol (64-17-5, 1-<5%), Ethanol, 2-butoxy- (111-76-2, "
                   "1-<5%), Propane (74-98-6, 1-<5%), Butane (106-97-8, "
                   "1-<5%). The sheet states 'Other components are not "
                   "hazardous or are below required disclosure limits'; water "
                   "is the balance."),
        "source_url": SPRAYWAY_URL,
        "note": ("A PARTIAL disclosure: the SDS names only the components that "
                 "cross the hazard-disclosure threshold and states the rest "
                 "are non-hazardous or below the limit. The formula is an "
                 "aerosol glass cleaner — ethanol and 2-butoxyethanol are the "
                 "solvent pair, propane and butane the propellant — and water "
                 "is the balance. The product is ammonia-free by the brand's "
                 "own positioning, and no ammonia appears on the sheet. "
                 "Because the non-hazardous fraction is unnamed, the list "
                 "below is what the manufacturer discloses, not a full "
                 "intentionally-added list."),
        "owner": "Highline Warren", "owner_ev": "reported",
        "owner_src": SPRAYWAY_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": SPRAYWAY_URL,
        "tier_note": ("Sold at mass, grocery, hardware and auto retailers; "
                      "recorded as mass. Channel evidence is the brand's own "
                      "retail placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "partial",
        "added": TODAY, "updated": TODAY,
        **exp_untested("An aerosol glass cleaner in the mass channel."),
    },
]


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def dump(path, obj, indent):
    # Measured at head: products/ingredients/owners indent=1 no trailing
    # newline; changelog indent=2 no trailing newline. Match each file.
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
    owners = load(os.path.join(DATA, "owners.json"))
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

    added_owners = 0
    for name, rec in NEW_OWNERS.items():
        if name in owners["owners"]:
            print(f"owner exists, not re-adding: {name}")
            continue
        owners["owners"][name] = rec
        added_owners += 1
        print(f"new owner entry: {name}")

    for name, upd in OWNER_BRAND_ADDS.items():
        rec = owners["owners"].get(name)
        if rec is None:
            print(f"WARN owner not found for brand add: {name}")
            continue
        brands = rec.setdefault("brands", [])
        for b in upd["brands"]:
            if b not in brands:
                brands.append(b)
                print(f"owner brand added: {name} -> {b}")
        if upd.get("note"):
            rec["brand_note"] = upd["note"]

    for r in products:
        for k in r["ings"]:
            if k not in ingredients:
                raise SystemExit(f"record {r['name']!r} references missing key {k!r}")

    if added and not NO_CHANGELOG:
        changelog.insert(0, {
            "date": TODAY,
            "text": ("Gather lane: 4 products added from manufacturer "
                     "disclosures read 2026-10-06 -- BISSELL Advanced Clean + "
                     "Protect (full CPIC list with CAS, supplier.bissell.com), "
                     "Earth Breeze Laundry Detergent Sheets Fragrance Free "
                     "(full per-SKU list, help.earthbreeze.com), Green Gobbler "
                     "Drain Clog Remover (four lines, active withheld as a "
                     "trade secret, greengobbler.com) and Sprayway Glass "
                     "Cleaner (SDS section 3, hazardous components only). Four "
                     "brand families new to the corpus: BISSELL, Earth Breeze, "
                     "Green Gobbler and Sprayway. Three new ingredient keys, "
                     "all recorded Not Classified with a sourcing note rather "
                     "than graded -- Silicone Defoamer (no PubChem CID), "
                     "Kaolin (UVCB mineral, no discrete CID) and Caustic "
                     "Replacement (a trade-secret label term, not a "
                     "substance). Three owner-registry entries added: BISSELL "
                     "Homecare (private, family-owned since 1876), Highline "
                     "Warren (acquired the Sprayway brand from PLZ Corp in "
                     "January 2026) and Earth Breeze (private, founded 2019, "
                     "Medford OR); Green Gobbler added to the existing "
                     "PurposeBuilt Brands brand list. Fills the thinnest "
                     "category (Floor & Carpet, 11 products) and adds the "
                     "first laundry SHEET and the first non-caustic drain "
                     "opener to the corpus."),
        })

    if DRY:
        print(f"\nDRY RUN: would add {added} products, "
              f"{len(added_keys)} ingredient keys, {added_owners} owners.")
        return

    dump(os.path.join(DATA, "products.json"), products, 1)
    dump(os.path.join(DATA, "ingredients.json"), ingredients, 1)
    dump(os.path.join(DATA, "owners.json"), owners, 1)
    dump(os.path.join(DATA, "changelog.json"), changelog, 2)
    print(f"\nwrote {added} products, {len(added_keys)} new ingredient keys, "
          f"{added_owners} owner entries.")


if __name__ == "__main__":
    main()
