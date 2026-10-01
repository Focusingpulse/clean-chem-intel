#!/usr/bin/env python3
"""Night-shift station 2 harvest, 2026-10-01 (Dolman).

Ordered by EXPOSURE, not price tier (Trellis, Sep 22 2026). Every ingredient
list below was read from a manufacturer California SB-258 ingredient-disclosure
filing read TODAY, 2026-10-01, from KIK Consumer Products' own disclosure index
at https://www.kikcorp.com/ingredients/ .

Why these: the previous two station-2 fires took the Walmart house brand and the
branded value cleaners (Comet, Spic and Span, The Works). The remaining unread
part of the same index is the **value bleach shelf** -- the generic and
value-brand liquid bleaches that sit beside Clorox at a lower price. Bleach is
one of the highest-penetration household cleaning categories in the country
(IndexBox: 80-90% of US households buy bleach at least once a year, and
private-label/store brands are 25-35% of retail bleach volume), so this is the
largest exposure block still missing from the corpus.

The finding: **the value bleach shelf has three legible formulas, and which one
you get depends on the maker, not the price.**

  1. THREE LINES -- water, sodium hypochlorite, sodium hydroxide.
     101 Regular, Arctic White, SMART, Value Star, Smart Products APC.
     The scented variants add "Fragrance ingredients" plus the EU fragrance
     allergens the maker chose to name (limonene, linalool).
  2. FIVE LINES with two builders -- water, sodium hypochlorite, sodium
     hydroxide, SODIUM SILICATE, SODIUM METAPERIODATE. A-1 and Hi-lex, both
     James Austin Company (a KIK company since 2018).
  3. FIVE LINES with a surfactant and a fragrance -- water, sodium
     hypochlorite, sodium hydroxide, LAURAMINE OXIDE, Fragrance. Comet Ultra,
     Comet Classic, Great Value APC w/ Bleach, Great Value Bathroom w/ Bleach
     (entered on the two previous fires).

So the cheapest bleaches are also the simplest, and the two "extra" ingredients
that appear anywhere in the value shelf are a builder pair on the Austin's
labels and a surfactant-plus-fragrance pair on the branded ones. That is a
finding a person can act on and it is not a scare: nothing here is hidden, the
lists are short, and the unscented version of any of them drops the fragrance
allergens at the same price.

Ownership: 101, A-1 and Austin's are the James Austin Company, acquired by KIK
in 2018 (kikcorp.com timeline; austinsbleach.com/meet-austins/). Arctic White,
Hi-lex, Pure Bright, SMART and Value Star disclose as KIK International LLC.
Parent recorded as KIK Consumer Products for all of them.

Nothing here is graded. Product grading is the Sifter lane; a blank as-sold
grade is the honest state. Where a same-price substitute exists it is named and
it is the unscented variant of the same brand, which is the only substitute that
is genuinely the same price.

Idempotent: a product whose `name` already exists is skipped, and an ingredient
key already present is left untouched. Run it twice; the second run reports 0.

Usage:  python3 tools/harvest_2026_10_01.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-01"

DRY = "--dry-run" in sys.argv

KIK_INDEX = "https://www.kikcorp.com/ingredients/"
KIK_PRODUCTS = "https://www.kikcorp.com/our-products/"
AUSTINS = "https://austinsbleach.com/meet-austins/"
IB_BLEACH = ("https://www.indexbox.io/store/"
             "united-states-bleach-market-analysis-forecast-size-trends-and-insights/")
IB_BLEACH_NA = ("https://www.indexbox.io/store/"
                "northern-america-bleach-market-analysis-forecast-size-trends-and-insights/")

ING_NOTE = ("Listed in a manufacturer or manufacturer-filing disclosure read "
            "2026-10-01; not yet graded against GHS.")

# Label wording -> existing canonical key, where the substance is the same and a
# second key would be a synonym for one CAS. Checked case-insensitively against
# the live registry before use; the writer halts if a target key is absent.
ALIASES = {
    # The Pure Bright filing uses the British spelling; the graded key is the
    # US one. CAS 1300-72-7 on both. Third synonym for this substance found in
    # the registry (see gaps/sodium-xylene-sulfonate-third-key-2026-10-01.md).
    "Sodium Xylenesulphonate": "Sodium Xylenesulfonate",
    # The value filings name the dye by its Colour Index name; the registry
    # already carries specific dye keys rather than collapsing them to
    # "Colorant" (Acid Blue 93, Direct Blue 86, CI Acid Blue 145).
    "C.I. Acid Blue 40": "C.I. Acid Blue 40",
}

# New keys minted this fire. Shape follows the registry's existing entries.
NEW_KEYS = {
    "Sodium Metaperiodate": {
        "s": "Sodium metaperiodate. Strong inorganic oxidizer; used as a "
             "detergent builder/bleach stabilizer on two value bleach labels.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the A-1 Concentrated Bleach and Hi-lex Bleach "
                "disclosures (both James Austin Company / KIK) with CAS "
                "7790-28-5, listed as a detergent builder. Not yet graded "
                "against GHS; recorded rather than guessed. Note for the "
                "grading lane: periodate is an oxidizer and the usual builder "
                "in this shelf is sodium silicate, which both labels also "
                "carry, so the pair is worth a second look.",
    },
    "PEG-8": {
        "s": "Polyethylene glycol 8. Solvent/humectant; CAS 25322-68-3.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Pure Bright Stain Remover & Color Booster "
                "disclosure with CAS 25322-68-3, the generic polyethylene "
                "glycol CAS. Kept as its own key rather than folded into 'PEG' "
                "because the registry already carries grade-specific keys "
                "(PEG-9, PEG-150) and the label names a grade. Not yet graded.",
    },
    "C.I. Acid Blue 40": {
        "s": "Acid Blue 40, a blue anthraquinone dye (Colour Index 61585).",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Pure Bright Stain Remover & Color Booster "
                "disclosure with CAS 6424-85-7, as a dye. Kept as its own key "
                "because the registry already keeps named dyes distinct "
                "(Acid Blue 93, Direct Blue 86, CI Acid Blue 145). Not yet "
                "graded.",
    },
}


def exp(basis_suffix: str) -> dict:
    return {
        "exposure_ev": "extrapolated",
        "exposure_src": IB_BLEACH,
        "exposure_basis": (
            "Derived, not measured. The source states that bleach has "
            "near-universal household penetration, estimated at 80 to 90 "
            "percent of United States households purchasing bleach at least "
            "once per year, and that private-label and store-brand products "
            "account for an estimated 25 to 35 percent of retail bleach "
            "volume, up from roughly 15 to 20 percent a decade ago. Searched "
            "for a published per-brand or per-SKU US household-penetration "
            "figure for this product and located none; brand shares for the "
            "value shelf are not published (Euromonitor reports the category "
            "by company, with Clorox at 65 percent of value and Walmart at 14 "
            "percent, not by value brand). The estimate therefore stops at the "
            "tier and divides it across the value brands on this shelf. "
            "Rounded to one significant figure, order-of-magnitude. "
            + basis_suffix
        ),
    }


def sub(name, tier, note):
    return {"name": name, "tier": tier, "note": note}


UNSCENTED_SUB = ("The unscented version of the same brand, same size, same "
                 "shelf and same price. Drops the fragrance and the named EU "
                 "fragrance allergens and changes nothing else in the formula.")

# --------------------------------------------------------------------------
# 1-3. 101 (James Austin Company / KIK). UPCs 0-54200-04053-3 (regular 128oz),
#      0-54200-04424-1 (lemon 128oz), 0-54200-04425-8 (lavender 128oz).
#      Disclosure dated 08/21/2019.
# --------------------------------------------------------------------------
P_101_REG = {
    "name": "101 Regular Bleach, 128 oz",
    "brand": "101",
    "cat": "Disinfectant",
    "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide"],
    "source": ("James Austin Company California Cleaning Product Right to Know "
               "(SB-258) ingredient disclosure for 101 Regular Bleach, 128 fl "
               "oz, published on the KIK Consumer Products disclosure index. "
               "UPC 0-54200-04053-3, date of disclosure 08/21/2019. Three "
               "intentionally added ingredients with CAS numbers; the filing "
               "marks sodium hydroxide as present on the California non-cancer "
               "hazards list."),
    "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/11/101_Regular-Bleach-128oz_0-54200-04053-3.pdf",
    "note": ("Three ingredients. That is the whole disclosed formula on a "
             "gallon of generic bleach that costs a fraction of the national "
             "brand: water, sodium hypochlorite and sodium hydroxide. The "
             "hypochlorite is the bleach and the hydroxide is what keeps it "
             "stable on the shelf; there is no surfactant, no fragrance, no "
             "dye and no thickener. This is the simplest formula on the "
             "bleach shelf and it is also the cheapest, which cuts against "
             "the usual assumption about what a value product is cut with. "
             "The hazard is the hypochlorite itself: corrosive, an aquatic "
             "toxicant, and never to be mixed with ammonia or acid."),
    "owner": "KIK Consumer Products",
    "owner_ev": "verified",
    "owner_src": KIK_PRODUCTS,
    "tier": "mass",
    "tier_ev": "reported",
    "tier_src": KIK_INDEX,
    "tier_note": ("A nationally distributed value bleach sold through grocery, "
                  "mass and value channels; market-position vocabulary, not a "
                  "single retail channel. The manufacturer's own index lists "
                  "it as a household consumer product."),
    "substitutes": [sub("101 Lemon Scent Bleach, 128 oz", "mass",
                        "Same brand, same price, adds a lemon fragrance and the "
                        "named EU fragrance allergens. Choose the unscented "
                        "version if fragrance is the concern; if the concern is "
                        "the hypochlorite, no bleach is a substitute for "
                        "bleach -- see the oxygen-based booster in this "
                        "harvest.")],
    "exposure": 2,
    "strength_disclosure": "full",
    "added": TODAY, "updated": TODAY,
}

P_101_LEMON = {
    "name": "101 Lemon Scent Bleach, 128 oz",
    "brand": "101",
    "cat": "Disinfectant",
    "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide",
             "Fragrance", "Limonene"],
    "source": ("James Austin Company California Cleaning Product Right to Know "
               "(SB-258) ingredient disclosure for 101 Lemon Scent Bleach, 128 "
               "fl oz, published on the KIK Consumer Products disclosure index. "
               "UPC 0-54200-04424-1, date of disclosure 08/21/2019. Five "
               "intentionally added ingredients with CAS numbers; limonene is "
               "flagged as an EU fragrance allergen."),
    "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/11/101_Lemon-Scent-Bleach-128oz_0-54200-04424-1.pdf",
    "note": ("The unscented formula plus two lines: a fragrance and limonene, "
             "the latter flagged on the filing as an EU fragrance allergen. "
             "That is the entire difference between this and 101 Regular "
             "Bleach, and it is the whole difference in price. Limonene is a "
             "recognised skin sensitiser; anyone who reacts to scented "
             "cleaners is reacting to this line, not to the bleach."),
    "owner": "KIK Consumer Products",
    "owner_ev": "verified",
    "owner_src": KIK_PRODUCTS,
    "tier": "mass",
    "tier_ev": "reported",
    "tier_src": KIK_INDEX,
    "tier_note": ("A nationally distributed value bleach sold through grocery, "
                  "mass and value channels."),
    "substitutes": [sub("101 Regular Bleach, 128 oz", "mass", UNSCENTED_SUB)],
    "exposure": 1,
    "strength_disclosure": "full",
    "added": TODAY, "updated": TODAY,
}

P_101_LAV = {
    "name": "101 Lavender Scent Bleach, 128 oz",
    "brand": "101",
    "cat": "Disinfectant",
    "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide",
             "Fragrance", "Limonene", "Linalool"],
    "source": ("James Austin Company California Cleaning Product Right to Know "
               "(SB-258) ingredient disclosure for 101 Lavender Scent Bleach, "
               "128 fl oz, published on the KIK Consumer Products disclosure "
               "index. UPC 0-54200-04425-8, date of disclosure 08/21/2019. Six "
               "intentionally added ingredients with CAS numbers; limonene and "
               "linalool are flagged as EU fragrance allergens."),
    "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/11/101_Lavender-Scent-Bleach-128oz_0-54200-04425-8.pdf",
    "note": ("The lemon variant plus linalool. Two named fragrance allergens on "
             "one line of a bleach bottle, both printed with CAS numbers "
             "because California requires it. Neither is a bleach hazard; both "
             "are fragrance hazards, and both disappear in the unscented "
             "version at the same price."),
    "owner": "KIK Consumer Products",
    "owner_ev": "verified",
    "owner_src": KIK_PRODUCTS,
    "tier": "mass",
    "tier_ev": "reported",
    "tier_src": KIK_INDEX,
    "tier_note": ("A nationally distributed value bleach sold through grocery, "
                  "mass and value channels."),
    "substitutes": [sub("101 Regular Bleach, 128 oz", "mass", UNSCENTED_SUB)],
    "exposure": 1,
    "strength_disclosure": "full",
    "added": TODAY, "updated": TODAY,
}

# --------------------------------------------------------------------------
# 4. A-1 Concentrated Bleach (James Austin Company). UPC 0 54200 04571 2,
#    disclosure 11/27/2019.
# --------------------------------------------------------------------------
P_A1 = {
    "name": "A-1 Concentrated Bleach, 121 oz",
    "brand": "A-1",
    "cat": "Disinfectant",
    "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide",
             "Sodium Silicate", "Sodium Metaperiodate"],
    "source": ("James Austin Company California Cleaning Product Right to Know "
               "(SB-258) ingredient disclosure for A-1 Concentrated Bleach, 121 "
               "fl oz, published on the KIK Consumer Products disclosure index. "
               "UPC 0 54200 04571 2, date of disclosure 11/27/2019. Five "
               "intentionally added ingredients with CAS numbers; the filing "
               "marks sodium hydroxide as present on the California non-cancer "
               "hazards list."),
    "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/12/A-1_Concentrated-Bleach-121oz_0-54200-04571-2.pdf",
    "note": ("A different five-line bleach, and the difference is two builders. "
             "Where the branded value bleaches add a surfactant and a "
             "fragrance, this one adds sodium silicate and sodium "
             "metaperiodate. Austin's has been making bleach since the 1930s "
             "and this is the formula the family company kept. Sodium "
             "metaperiodate is an oxidizer and is not a common additive on "
             "this shelf, so it is recorded here ungraded rather than waved "
             "through. Everything else is the plain three-line bleach."),
    "owner": "KIK Consumer Products",
    "owner_ev": "verified",
    "owner_src": AUSTINS,
    "tier": "mass",
    "tier_ev": "reported",
    "tier_src": KIK_INDEX,
    "tier_note": ("A nationally distributed value bleach; the Austin's line is "
                  "sold through grocery and value channels. James Austin "
                  "Company is a KIK Custom Products company."),
    "substitutes": [sub("101 Regular Bleach, 128 oz", "mass",
                        "Same shelf, same price band, three disclosed "
                        "ingredients instead of five. Avoids the sodium "
                        "silicate and the sodium metaperiodate entirely; "
                        "carries the same hypochlorite, which is the real "
                        "hazard on any bleach.")],
    "exposure": 2,
    "strength_disclosure": "full",
    "added": TODAY, "updated": TODAY,
}

# --------------------------------------------------------------------------
# 5-6. Arctic White (KIK International LLC). UPCs 0 41596 02095 9 (128oz,
#      disclosure August 8 2019), 0 41596 02097 3 (lavender 96oz, August 9 2019).
# --------------------------------------------------------------------------
P_AW = {
    "name": "Arctic White Bleach, 128 oz",
    "brand": "Arctic White",
    "cat": "Disinfectant",
    "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide"],
    "source": ("KIK International LLC California Cleaning Product Right to Know "
               "(SB-258) ingredient disclosure for Arctic White Bleach, 128 fl "
               "oz, published on the KIK Consumer Products disclosure index. "
               "UPC 0 41596 02095 9, date of disclosure August 8, 2019. Three "
               "intentionally added ingredients with CAS numbers."),
    "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/10/Arctic-White_Bleach-128oz_0-41596-02095-9.pdf",
    "note": ("The same three lines as 101 Regular, from the same corporate "
             "family, under a different label and a different price. This is "
             "the third separate value brand in this database whose complete "
             "disclosed bleach formula is water, sodium hypochlorite and "
             "sodium hydroxide. Whatever the label says, the bottle is the "
             "same three chemicals."),
    "owner": "KIK Consumer Products",
    "owner_ev": "verified",
    "owner_src": KIK_PRODUCTS,
    "tier": "mass",
    "tier_ev": "reported",
    "tier_src": KIK_INDEX,
    "tier_note": ("A nationally distributed value bleach sold through grocery "
                  "and value channels."),
    "substitutes": [sub("101 Regular Bleach, 128 oz", "mass",
                        "A different label on the same three-ingredient "
                        "formula at a comparable price. Listed because it is "
                        "the same bottle chemically, not because it is "
                        "better.")],
    "exposure": 1,
    "strength_disclosure": "full",
    "added": TODAY, "updated": TODAY,
}

P_AW_LAV = {
    "name": "Arctic White Bleach, Lavender Scented, 96 oz",
    "brand": "Arctic White",
    "cat": "Disinfectant",
    "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide", "Fragrance"],
    "source": ("KIK International LLC California Cleaning Product Right to Know "
               "(SB-258) ingredient disclosure for Arctic White Bleach Lavender "
               "Scented, 96 fl oz, published on the KIK Consumer Products "
               "disclosure index. UPC 0 41596 02097 3, date of disclosure "
               "August 9, 2019. Four intentionally added ingredients with CAS "
               "numbers where the filing supplies them."),
    "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/10/Arctic-White_-Bleach-Lavender-Scented-96oz_0-41596-02097-3.pdf",
    "note": ("The scented version of the same bottle. The fragrance is "
             "disclosed as 'Fragrance ingredients, not available' rather than "
             "by name, so unlike the 101 scented bleaches this label does not "
             "name its fragrance allergens. That is a disclosure difference, "
             "not a formula difference, and it is worth noticing: the same "
             "kind of product from the same company can be more or less "
             "readable depending on which label you pick up."),
    "owner": "KIK Consumer Products",
    "owner_ev": "verified",
    "owner_src": KIK_PRODUCTS,
    "tier": "mass",
    "tier_ev": "reported",
    "tier_src": KIK_INDEX,
    "tier_note": ("A nationally distributed value bleach sold through grocery "
                  "and value channels."),
    "substitutes": [sub("Arctic White Bleach, 128 oz", "mass",
                        "The unscented version of the same brand, same shelf, "
                        "comparable price. Drops the fragrance line.")],
    "exposure": 1,
    "strength_disclosure": "full",
    "added": TODAY, "updated": TODAY,
}

# --------------------------------------------------------------------------
# 7. Hi-lex Bleach Regular Scent Concentrated (KIK International LLC).
#    UPC 0 59647 35020 7, disclosure August 8, 2019.
# --------------------------------------------------------------------------
P_HILEX = {
    "name": "Hi-lex Bleach Regular Scent Concentrated, 121 oz",
    "brand": "Hi-lex",
    "cat": "Disinfectant",
    "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide",
             "Sodium Silicate", "Sodium Metaperiodate"],
    "source": ("KIK International LLC California Cleaning Product Right to Know "
               "(SB-258) ingredient disclosure for Hi-lex Bleach Regular Scent "
               "Concentrated, 121 fl oz, published on the KIK Consumer Products "
               "disclosure index. UPC 0 59647 35020 7, date of disclosure "
               "August 8, 2019. Five intentionally added ingredients with CAS "
               "numbers; the filing marks sodium hydroxide as present on the "
               "California non-cancer hazards list."),
    "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/10/Hi-lex_Bleach-Regular-Scent-Concentrated-121oz_0-59647-35020-7.pdf",
    "note": ("The same five lines as A-1 Concentrated Bleach, disclosed by a "
             "different legal entity inside the same company. Two of the six "
             "value bleaches in this database carry the sodium silicate and "
             "sodium metaperiodate pair and they are the two Austin's-side "
             "formulas. The other four are the three-line version."),
    "owner": "KIK Consumer Products",
    "owner_ev": "verified",
    "owner_src": KIK_PRODUCTS,
    "tier": "mass",
    "tier_ev": "reported",
    "tier_src": KIK_INDEX,
    "tier_note": ("A nationally distributed value bleach sold through grocery "
                  "and value channels."),
    "substitutes": [sub("Value Star Bleach, 128 oz", "mass",
                        "Same shelf, same price band, three disclosed "
                        "ingredients. Avoids the sodium silicate and the "
                        "sodium metaperiodate.")],
    "exposure": 1,
    "strength_disclosure": "full",
    "added": TODAY, "updated": TODAY,
}

# --------------------------------------------------------------------------
# 8-9. SMART and Value Star (KIK International LLC).
#    UPC 0 17926 00210 0 (SMART 128oz, August 8 2019);
#    UPC 8 91107 00128 7 (Value Star 128oz, August 8 2019);
#    UPC 8 91107 00099 0 (Value Star lavender 96oz, August 8 2019).
# --------------------------------------------------------------------------
P_SMART = {
    "name": "SMART Bleach, 128 oz",
    "brand": "SMART",
    "cat": "Disinfectant",
    "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide"],
    "source": ("KIK International LLC California Cleaning Product Right to Know "
               "(SB-258) ingredient disclosure for SMART Bleach, 128 fl oz, "
               "published on the KIK Consumer Products disclosure index. UPC 0 "
               "17926 00210 0, date of disclosure August 8, 2019. Three "
               "intentionally added ingredients with CAS numbers."),
    "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/10/SMART-Bleach-128oz-017926002100.pdf",
    "note": ("The fourth value brand with the same three-line formula. The "
             "registry now carries five separate labels whose entire disclosed "
             "bleach formula is water, sodium hypochlorite and sodium "
             "hydroxide. The labels are the difference."),
    "owner": "KIK Consumer Products",
    "owner_ev": "verified",
    "owner_src": KIK_PRODUCTS,
    "tier": "mass",
    "tier_ev": "reported",
    "tier_src": KIK_INDEX,
    "tier_note": ("A nationally distributed value bleach sold through grocery "
                  "and value channels."),
    "substitutes": [sub("Value Star Bleach, 128 oz", "mass",
                        "Same three-ingredient formula, same shelf, comparable "
                        "price.")],
    "exposure": 1,
    "strength_disclosure": "full",
    "added": TODAY, "updated": TODAY,
}

P_VS = {
    "name": "Value Star Bleach, 128 oz",
    "brand": "Value Star",
    "cat": "Disinfectant",
    "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide"],
    "source": ("KIK International LLC California Cleaning Product Right to Know "
               "(SB-258) ingredient disclosure for Value Star Bleach, 128 fl "
               "oz, published on the KIK Consumer Products disclosure index. "
               "UPC 8 91107 00128 7, date of disclosure August 8, 2019. Three "
               "intentionally added ingredients with CAS numbers."),
    "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/10/Value-Star_Bleach-128oz_8-91107-00128-7.pdf",
    "note": ("The fifth value brand with the identical three-line formula. At "
             "this point the pattern is not a coincidence to be reported "
             "brand by brand: the value bleach shelf in the United States is "
             "supplied by one company, and the formula does not change when "
             "the label does."),
    "owner": "KIK Consumer Products",
    "owner_ev": "verified",
    "owner_src": KIK_PRODUCTS,
    "tier": "mass",
    "tier_ev": "reported",
    "tier_src": KIK_INDEX,
    "tier_note": ("A nationally distributed value bleach sold through grocery "
                  "and value channels."),
    "substitutes": [sub("SMART Bleach, 128 oz", "mass",
                        "Same three-ingredient formula, same shelf, comparable "
                        "price.")],
    "exposure": 1,
    "strength_disclosure": "full",
    "added": TODAY, "updated": TODAY,
}

P_VS_LAV = {
    "name": "Value Star Bleach, Lavender, 96 oz",
    "brand": "Value Star",
    "cat": "Disinfectant",
    "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide", "Fragrance"],
    "source": ("KIK International LLC California Cleaning Product Right to Know "
               "(SB-258) ingredient disclosure for Value Star Bleach Lavender, "
               "96 fl oz, published on the KIK Consumer Products disclosure "
               "index. UPC 8 91107 00099 0, date of disclosure August 8, 2019. "
               "Four intentionally added ingredients with CAS numbers where "
               "the filing supplies them."),
    "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/10/Value-Star_Bleach-Lavender-96oz_8-91107-00099-0.pdf",
    "note": ("Scented version of the same bottle, with the fragrance disclosed "
             "as a class rather than by name, the same way Arctic White does "
             "it. The unscented Value Star drops the line at the same price."),
    "owner": "KIK Consumer Products",
    "owner_ev": "verified",
    "owner_src": KIK_PRODUCTS,
    "tier": "mass",
    "tier_ev": "reported",
    "tier_src": KIK_INDEX,
    "tier_note": ("A nationally distributed value bleach sold through grocery "
                  "and value channels."),
    "substitutes": [sub("Value Star Bleach, 128 oz", "mass", UNSCENTED_SUB)],
    "exposure": 1,
    "strength_disclosure": "full",
    "added": TODAY, "updated": TODAY,
}

# --------------------------------------------------------------------------
# 10. Pure Bright Clear Ammonia (KIK International LLC). UPC 0 59647 21012 9,
#     disclosure August 8, 2019.
# --------------------------------------------------------------------------
P_AMMONIA = {
    "name": "Pure Bright Clear Ammonia, 64 oz",
    "brand": "Pure Bright",
    "cat": "Glass",
    "ings": ["Water", "Ammonium Hydroxide", "Tetrasodium EDTA",
             "Sodium C10-16 Alkylbenzenesulfonate", "Sodium Xylenesulfonate"],
    "source": ("KIK International LLC California Cleaning Product Right to Know "
               "(SB-258) ingredient disclosure for Pure Bright Clear Ammonia, "
               "64 fl oz, published on the KIK Consumer Products disclosure "
               "index. UPC 0 59647 21012 9, date of disclosure August 8, 2019. "
               "Five intentionally added ingredients with CAS numbers."),
    "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/10/Purebright-Clear-Ammonia-64oz_0-59647-21012-9.pdf",
    "note": ("The ammonia shelf, which this database did not carry. Clear "
             "ammonia is a different chemistry from bleach and the two must "
             "never be mixed: ammonium hydroxide plus sodium hypochlorite "
             "produces chloramine gas. Five disclosed lines and no fragrance, "
             "so it is a genuinely unscented cleaner, which is why it survives "
             "in households that avoid scent. It carries its own hazards: "
             "ammonium hydroxide is corrosive and a respiratory irritant, and "
             "tetrasodium EDTA is a chelator that persists."),
    "owner": "KIK Consumer Products",
    "owner_ev": "verified",
    "owner_src": KIK_PRODUCTS,
    "tier": "mass",
    "tier_ev": "reported",
    "tier_src": KIK_INDEX,
    "tier_note": ("A nationally distributed value cleaner sold through "
                  "grocery and value channels."),
    "substitutes": [sub("Pure Bright Stain Remover & Color Booster", "mass",
                        "Same brand and price band, no ammonia. Use it for the "
                        "jobs ammonia is for (glass, grease, laundry "
                        "brightening) without the respiratory irritant and "
                        "without the mixing risk.")],
    "exposure": 1,
    "strength_disclosure": "full",
    "added": TODAY, "updated": TODAY,
}

# --------------------------------------------------------------------------
# 11. Pure Bright Stain Remover & Color Booster (KIK International LLC).
#     UPC 0 59647 21029 7, disclosure Oct 13, 2020.
# --------------------------------------------------------------------------
P_BOOSTER = {
    "name": "Pure Bright Stain Remover & Color Booster",
    "brand": "Pure Bright",
    "cat": "Stain & Odor",
    "ings": ["Water", "Hydrogen Peroxide", "Cetrimonium Chloride",
             "Sodium Xylenesulfonate", "Myristamine Oxide", "Lauramine Oxide",
             "PEG-8", "Disodium Distyrylbiphenyl Disulfonate",
             "Citric Acid", "C.I. Acid Blue 40", "Fragrance"],
    "source": ("KIK International LLC California Cleaning Product Right to Know "
               "(SB-258) ingredient disclosure for Pure Bright Stain Remover & "
               "Color Booster, published on the KIK Consumer Products "
               "disclosure index. UPC 0 59647 21029 7, date of disclosure "
               "October 13, 2020. Eleven intentionally added ingredients with "
               "CAS numbers."),
    "source_url": "https://www.kikcorp.com/wp-content/uploads/2020/10/Pure-Bright_Stain-Remover-Color-Booster_0-59647-21029-7.pdf",
    "note": ("Not a bleach, and it is the most useful record in this harvest. "
             "The active is hydrogen peroxide, the oxygen bleach that does the "
             "same brightening job as chlorine bleach without the chlorine. "
             "Eleven lines, all named: two surfactants, a chelator, a "
             "fluorescent whitening agent, citric acid as the pH adjuster, a "
             "dye and a fragrance. Compare it with the three-line chlorine "
             "bleaches above and the trade is legible: you get a longer list "
             "and a gentler active. The fluorescent whitening agent is the "
             "one to know about, because it is what makes whites look brighter "
             "without cleaning them."),
    "owner": "KIK Consumer Products",
    "owner_ev": "verified",
    "owner_src": KIK_PRODUCTS,
    "tier": "mass",
    "tier_ev": "reported",
    "tier_src": KIK_INDEX,
    "tier_note": ("A nationally distributed value laundry additive sold "
                  "through grocery and value channels."),
    "substitutes": [sub("Pure Bright Germicidal Ultra Bleach, 128 oz", "mass",
                        "The chlorine version from the same brand if you want "
                        "the disinfecting power. The trade runs the other way: "
                        "shorter list, harsher active.")],
    "exposure": 1,
    "strength_disclosure": "full",
    "added": TODAY, "updated": TODAY,
}

# --------------------------------------------------------------------------
# 12. Pure Bright RTU Germicide with Bleach (KIK International LLC).
#     UPC 59647 21021, disclosure September 30, 2020.
# --------------------------------------------------------------------------
P_RTU = {
    "name": "Pure Bright RTU Germicide with Bleach, 32 oz",
    "brand": "Pure Bright",
    "cat": "Disinfectant",
    "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide",
             "Lauramine Oxide", "Fragrance"],
    "source": ("KIK International LLC California Cleaning Product Right to Know "
               "(SB-258) ingredient disclosure for Pure Bright RTU Germicide "
               "with Bleach, 32 fl oz, published on the KIK Consumer Products "
               "disclosure index. UPC 59647 21021, date of disclosure September "
               "30, 2020. Five intentionally added ingredients with CAS "
               "numbers."),
    "source_url": "https://www.kikcorp.com/wp-content/uploads/2020/09/Pure-Bright_RTU-Germicide-with-Bleach-32oz_59647-21021.pdf",
    "note": ("The fifth copy of the branded five-line bleach formula in this "
             "database, after Comet Ultra, Comet Classic, Great Value All "
             "Purpose Cleaner with Bleach and Great Value Bathroom Cleaner with "
             "Bleach. Ready to use, so it is the spray version of the same "
             "chemistry. Same maker as the Great Value and Comet entries."),
    "owner": "KIK Consumer Products",
    "owner_ev": "verified",
    "owner_src": KIK_PRODUCTS,
    "tier": "mass",
    "tier_ev": "reported",
    "tier_src": KIK_INDEX,
    "tier_note": ("A nationally distributed value cleaner sold through grocery "
                  "and value channels."),
    "substitutes": [sub("101 Regular Bleach, 128 oz", "mass",
                        "The three-line bleach, diluted. Same active, fewer "
                        "added lines, lower cost per use; the trade is that "
                        "you mix it yourself.")],
    "exposure": 1,
    "strength_disclosure": "full",
    "added": TODAY, "updated": TODAY,
}

# Per-product exposure estimate and the last line of its basis. The number is a
# whole-number percentage of US households, one significant figure.
EXPO = {
    "101 Regular Bleach, 128 oz": (2, "The 101 line is one of the larger value bleach brands and was seen at Walmart and grocery value shelves."),
    "101 Lemon Scent Bleach, 128 oz": (1, "A scent variant of the same brand; a fraction of the brand's own volume."),
    "101 Lavender Scent Bleach, 128 oz": (1, "A scent variant of the same brand; a fraction of the brand's own volume."),
    "A-1 Concentrated Bleach, 121 oz": (2, "Austin's is one of the older value bleach lines, sold through grocery and value channels."),
    "Arctic White Bleach, 128 oz": (1, "A value bleach label; no published share located."),
    "Arctic White Bleach, Lavender Scented, 96 oz": (1, "A scent variant; a fraction of the brand's own volume."),
    "Hi-lex Bleach Regular Scent Concentrated, 121 oz": (1, "A value bleach label; no published share located."),
    "SMART Bleach, 128 oz": (1, "A value bleach label; no published share located."),
    "Value Star Bleach, 128 oz": (1, "A value bleach label; no published share located."),
    "Value Star Bleach, Lavender, 96 oz": (1, "A scent variant; a fraction of the brand's own volume."),
    "Pure Bright Clear Ammonia, 64 oz": (1, "Ammonia is a smaller category than bleach and this label is sold mainly through janitorial and foodservice suppliers as well as value retail, so household reach is lower than the bleaches."),
    "Pure Bright Stain Remover & Color Booster": (1, "The oxygen-booster category is smaller than bleach; no published per-product share located."),
    "Pure Bright RTU Germicide with Bleach, 32 oz": (1, "A ready-to-use germicide sold mainly through janitorial and foodservice suppliers as well as value retail."),
}

PRODUCTS = [
    (P_101_REG, "101 Regular Bleach: the three-line formula; the fifth value "
                "brand with the identical disclosed list."),
    (P_101_LEMON, "101 Lemon: the same bottle plus a fragrance and limonene, "
                  "a named EU fragrance allergen."),
    (P_101_LAV, "101 Lavender: two named fragrance allergens on one bleach "
                "bottle."),
    (P_A1, "A-1: a different five-line bleach, built with sodium silicate and "
           "sodium metaperiodate rather than a surfactant."),
    (P_AW, "Arctic White: the three-line formula under a fourth label."),
    (P_AW_LAV, "Arctic White lavender: fragrance disclosed as a class, not by "
               "name -- a disclosure difference from the 101 scented bleaches."),
    (P_HILEX, "Hi-lex: the Austin's-side five-line formula under a second "
              "label."),
    (P_SMART, "SMART: the three-line formula under a fifth label."),
    (P_VS, "Value Star: the three-line formula under a sixth label."),
    (P_VS_LAV, "Value Star lavender: the unscented bottle plus a fragrance "
               "line."),
    (P_AMMONIA, "Pure Bright Clear Ammonia: the ammonia shelf, absent from the "
                "database until now; the one cleaner that must never meet "
                "bleach."),
    (P_BOOSTER, "Pure Bright Stain Remover & Color Booster: the oxygen-based "
                "alternative, eleven named lines against the bleaches' three."),
    (P_RTU, "Pure Bright RTU Germicide with Bleach: the fifth copy of the "
            "branded five-line bleach formula."),
]


def main() -> int:
    prods = json.load(open(os.path.join(DATA, "products.json")))
    ings = json.load(open(os.path.join(DATA, "ingredients.json")))
    low = {k.lower(): k for k in ings}

    existing = {p.get("name") for p in prods}
    added = 0
    minted = []

    # Mint new keys first so the alias/canonical resolution below can see them.
    for k, v in NEW_KEYS.items():
        if k.lower() in low:
            print(f"  note: key {k!r} already present, left untouched")
            continue
        ings[k] = v
        low[k.lower()] = k
        minted.append(k)

    def resolve(name: str) -> str:
        canon = ALIASES.get(name, name)
        if canon.lower() in low:
            return low[canon.lower()]
        # Not a case-variant of anything: mint it.
        if canon in ings:
            return canon
        ings[canon] = {"s": f"{canon}. Listed in a manufacturer or "
                            f"manufacturer-filing disclosure read {TODAY}; "
                            f"not yet graded against GHS.",
                       "ev": "Low", "g": None, "gr": {}, "impacts": [],
                       "note": ING_NOTE}
        low[canon.lower()] = canon
        minted.append(canon)
        return canon

    for p, why in PRODUCTS:
        if p["name"] in existing:
            print(f"  skip (exists): {p['name']}")
            continue
        rec = dict(p)
        rec["ings"] = [resolve(x) for x in p["ings"]]
        rec.update(exp(EXPO[p["name"]][1]))
        rec["heritage"] = False
        rec["safe"] = None
        rec["conc"] = None
        rec["conc_src"] = None
        rec["conc_ev"] = "untested"
        rec["grade_as_sold"] = None
        rec["grade_as_sold_src"] = None
        rec["no_substitute_known"] = None
        rec["no_substitute_note"] = None
        prods.append(rec)
        existing.add(p["name"])
        added += 1
        print(f"  + {p['name']}  ({len(rec['ings'])} lines)")

    print(f"\nadded: {added}   minted keys: {len(minted)} -> {minted}")

    # Every new product must carry the four field groups the build checks.
    for p in prods:
        if p["name"] in existing:
            for f in ("exposure", "exposure_ev", "exposure_src", "tier",
                      "tier_ev", "owner", "owner_ev", "owner_src",
                      "strength_disclosure"):
                if f not in p:
                    print(f"HALT: {p['name']} missing field {f}")
                    return 1

    if DRY:
        print("(dry run — nothing written)")
        return 0

    json.dump(prods, open(os.path.join(DATA, "products.json"), "w"),
              indent=1, ensure_ascii=False)
    json.dump(ings, open(os.path.join(DATA, "ingredients.json"), "w"),
              indent=1, ensure_ascii=False)

    # Owner record: 101, A-1 and Austin's are the James Austin Company, a KIK
    # company since 2018. Arctic White, Hi-lex, Pure Bright, SMART and Value
    # Star disclose as KIK International LLC.
    op = os.path.join(DATA, "owners.json")
    owners = json.load(open(op))
    kik = owners["owners"]["KIK Consumer Products"]
    newbrands = ["101", "A-1", "Arctic White", "Hi-lex", "Pure Bright",
                 "SMART", "Value Star", "Austin's", "James Austin Company"]
    before = list(kik.get("brands", []))
    for b in newbrands:
        if b not in kik["brands"]:
            kik["brands"].append(b)
    bs = kik.setdefault("brand_sources", {})
    bs["reported_by_austins_site"] = [
        "101", "A-1", "Austin's", "James Austin Company"]
    bs["reported_by_kik_ingredients_index"] = [
        "Arctic White", "Hi-lex", "Pure Bright", "SMART", "Value Star"]
    kik["brands_added_2026_10_01"] = {
        "added": [b for b in newbrands if b not in before],
        "why": ("The value bleach shelf. 101, A-1 and Austin's are the James "
                "Austin Company, acquired by KIK Custom Products in 2018 "
                "(kikcorp.com timeline; austinsbleach.com/meet-austins/ "
                "states 'Austin's became part of KIK Custom Products, "
                "America's largest bleach supplier'). Arctic White, Hi-lex, "
                "Pure Bright, SMART and Value Star disclose as KIK "
                "International LLC on the KIK disclosure index."),
        "known_limitation": ("apply_owners() stamps ONE src per owner record, "
                             "so every brand on this list receives the KIK "
                             "record's src (the SEC asset purchase agreement "
                             "for the Comet/Spic and Span business), which "
                             "does not mention the value brands. The per-brand "
                             "sources are recorded in brand_sources and are "
                             "read by nothing. Filed as a gap, not fixed "
                             "silently."),
    }
    json.dump(owners, open(op, "w"), indent=1, ensure_ascii=False)
    print("owners.json: KIK brands extended ->",
          [b for b in newbrands if b not in before])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
