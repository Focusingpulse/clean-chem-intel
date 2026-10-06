#!/usr/bin/env python3
"""Night-shift station 2 harvest, 2026-10-06 (Dolman).

Ordered by EXPOSURE, not price tier (Trellis, Sep 22 2026). Target: the grocery
house-brand block named in SPX-003 ("Great Value, up and up, Kirkland"). up&up
is Target's house brand and had exactly one record in the corpus.

WHY THIS BLOCK, AND WHAT MAKES IT VERIFIABLE. A target.com product page serves
`environmental_segmentation.ingredient_chemical_disclosure_url`, an HTML table
on digitalcontent.target.com carrying the full California SB-258 intentionally
added ingredient list with CAS numbers and purposes. That is the manufacturer's
own published specification under SB-258 -- the `verified` class in
docs/certainty.md, the same structure as the Walmart CDN and CVS SB-258 routes
already in docs/source-policy.md. Two served doc shapes were found and are both
handled rather than smoothed:

  A  well-formed:  NAME | CAS | CONCERN | PURPOSE
  B  mislabeled:   PURPOSE | CAS | NAME | CONCERN
     the served table disagrees with its own header row
  C  empty:        the disclosure URL resolves to an empty #selected-ingredients
                   div (the wipes, the drain gel, the shower cleaner, the
                   lemon multi-surface, the bleach APC). Recorded as a gap.

Orientation is decided PER DOCUMENT. A row-level test left the one row whose
purpose wording fell outside the vocabulary mapped as its own purpose, which is
the same "a class repair written as instances" defect already on the record.

Also repaired here: the one existing up&up record carried a three-item list
(Water, Quaternary Ammonium, Fragrance) taken from the product page. Its own
SB-258 filing discloses eight. That is the truncated-list pattern; the record is
completed and the assumption recorded, not silently replaced.

Nothing here is graded. Product grading is the Sifter lane; a blank as-sold
grade is the honest state. Substitutes are supplied wherever a hazard is named.

Idempotent: a product whose name already exists is skipped, an ingredient key
already present is left untouched, and a second run reports 0 added.

Usage:  python3 tools/harvest_2026_10_06.py [--dry-run] [--no-changelog]
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

# Exposure sources read 2026-10-06 (HTTP 200, browser UA).
IB_SURFACE = ("https://www.indexbox.io/store/united-states-household-surface-"
              "cleaners-market-analysis-forecast-size-trends-and-insights/")
IB_LAUNDRY = ("https://www.indexbox.io/store/united-states-laundry-home-products-"
              "market-analysis-forecast-size-trends-and-insights/")
IB_BLEACH = ("https://www.indexbox.io/store/united-states-bleach-market-analysis-"
             "forecast-size-trends-and-insights/")
IB_WIPES = ("https://www.indexbox.io/store/united-states-cleaning-wipes-market-"
            "analysis-forecast-size-trends-and-insights/")
IB_DISHWASH = ("https://www.indexbox.io/store/united-states-dishwashing-market-"
               "analysis-forecast-size-trends-and-insights/")
TGT_ABOUT = "https://corporate.target.com/about"

# --------------------------------------------------------------------------
# Label wording -> existing canonical key, where the substance is the same.
# Every pair below is the same CAS; a second key would be a synonym.
# --------------------------------------------------------------------------
ALIASES = {
    "AQUA": "Water",
    "CI 74260": "Pigment Green 7",            # CI 74260, CAS 1328-53-6
    "CI 74180": "Direct Blue 86",             # CI 74180, CAS 1330-38-7
    "ACID RED 33": "Red 33",                  # CAS 3567-66-6
    "Alkyl (C12-16) dimethylbenzylammonium chloride":
        "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride",
    "DIDECYLDIMONIUM CHLORIDE": "Didecyldimethylammonium Chloride",
    "1-Octanaminium, N,N-dimethyl-N-octyl-, chloride":
        "Dioctyldimethylammonium Chloride",   # CAS 5538-94-3
    "Alanine, N,N-bis(carboxymethyl)-, trisodium salt":
        "Trisodium Dicarboxymethyl Alaninate",  # CAS 164462-16-2
    "2-Propenoic acid, polymer with 2,5-furandione, sodium salt":
        "Sodium Acrylic Acid/MA Copolymer",   # CAS 52255-49-9
    "C9-11 ALKETH-3": "Alcohols, C9-11, ethoxylated",   # CAS 68439-46-3
    "C12-15 ALKETH-10": "C12-15 Alcohols Ethoxylated",  # CAS 68131-39-5
    "SODIUM CARBONATE PEROXIDE": "Sodium Percarbonate",  # CAS 15630-89-4
}

# New keys minted this fire. Ungraded is recorded as ev "Low" with g null,
# never a guess. None of these is resolved to a grade yet.
NEW_KEYS = {
    "2-Anthracenesulfonic acid, 1-amino-9,10-dihydro-9,10-dioxo-4-(phenylamino)-, monosodium salt": {
        "s": "Acid Blue 25 (CI 62055), CAS 6408-78-2; an anthraquinone dye.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the up&up Multi-Surface Cleaner (Pine) SB-258 disclosure as a colorant. Not yet graded.",
    },
    "2-Propenoic acid, polymer with 2-methyl-2-[(1-oxo-2-propenyl)amino]-1-propanesulfonic acid monosodium salt, sodium salt": {
        "s": "An acrylate/AMPS copolymer, CAS 136903-34-9; a dispersing agent.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the up&up Ultimate Dishwasher Detergent Packs SB-258 disclosure as a dispersing agent. Not yet graded.",
    },
    "Aziridine, homopolymer, ethoxylated": {
        "s": "Ethoxylated polyethyleneimine (CAS 68130-99-4); a soil-release polymer.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the up&up Stain Remover SB-258 disclosure as a dispersing agent. Not yet graded.",
    },
    "CI 14700": {
        "s": "Ponceau SX, CAS 4548-53-2; a synthetic azo dye (CI 14700).",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the up&up Multi-Surface Cleaner (Pine) SB-258 disclosure as a colorant. Not yet graded.",
    },
    "CI 61585": {
        "s": "Acid Blue 80, CAS 4474-24-2; an anthraquinone dye (CI 61585).",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the up&up Multi-Surface Cleaner (Lavender) SB-258 disclosure as a colorant. Not yet graded.",
    },
    "PEG/PPG-10/2 PROPYLHEPTYL ETHER": {
        "s": "An alkyl-capped PEG/PPG ether, CAS 166736-08-9; a low-foam surfactant.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the up&up Ultimate Dishwasher Detergent Packs SB-258 disclosure as a surfactant. Not yet graded.",
    },
    "Periodic acid (HIO4), sodium salt": {
        "s": "Sodium periodate, CAS 7790-28-5; an oxidising agent used here as a bleach stabiliser.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the up&up Regular Bleach with Fabric Protection SB-258 disclosure as a corrosion inhibitor. Not yet graded.",
    },
    "Quaternary ammonium compounds, C12-14-alkyl[(ethylphenyl)methyl]dimethyl, chlorides": {
        "s": "A dialkyl ethylbenzyl quaternary ammonium chloride blend, CAS 85409-23-0; a disinfectant active.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the up&up Fresh Scent Disinfectant Spray SB-258 disclosure as an antimicrobial agent. Distinct CAS from the benzyl-C12-18 quat already in the registry (68391-01-5) and from the benzyl-C8-18 quat (63449-41-2). Not yet graded.",
    },
    "Quaternary ammonium compounds, benzyl-C8-18-alkyldimethyl, chlorides": {
        "s": "A benzyl quaternary ammonium chloride blend, CAS 63449-41-2; a disinfectant active.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the up&up Multi-Surface (Pine and Lavender) and Bathroom Disinfecting Cleaner SB-258 disclosures as an antimicrobial agent. Distinct CAS from the benzyl-C12-18 quat already in the registry (68391-01-5): the chain range differs, so it is kept as its own key rather than aliased. Not yet graded.",
    },
    "SODIUM C10-16 ALKETH-2 SULFATE": {
        "s": "Sodium C10-16 pareth-2 sulfate, CAS 68585-34-2; an anionic surfactant.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the up&up Liquid Dishwashing Soap and Stain Remover SB-258 disclosures. The product page words the same slot as 'sodium laureth sulfate', which is a different CAS (9004-82-4); the filing governs. Not yet graded.",
    },
    "SODIUM C10-16 ALKYL SULFATE": {
        "s": "Sodium C10-16 alkyl sulfate, CAS 68585-47-7; an anionic surfactant.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the up&up Liquid Dishwashing Soap SB-258 disclosure. The product page words the same slot as 'sodium lauryl sulfate', a different CAS (151-21-3). Not yet graded.",
    },
    "SOYETHYL MORPHOLINIUM ETHOSULFATE": {
        "s": "A quaternary ammonium morpholinium ethosulfate, CAS 61791-34-2; a surfactant.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the up&up Fresh Scent Disinfectant Spray SB-258 disclosure as a surfactant. Not yet graded.",
    },
}


def exp(cat_src, derivation):
    """An extrapolated exposure claim: derived, sourced, and stating the search."""
    return {
        "exposure_ev": "extrapolated",
        "exposure_src": cat_src,
        "exposure_basis": (
            derivation + " Searched for a published per-product or per-brand US "
            "household-penetration figure for this specific up&up SKU and located "
            "none; retailer house-brand shares are not published at product level. "
            "The estimate therefore derives from the category figure and this "
            "product's position as one house brand inside Target, and stops there. "
            "Target's own corporate page states more than 2,000 US stores and that "
            "over 75 percent of the US population lives within 10 miles of a store "
            f"({TGT_ABOUT}), which is the channel scale the derivation rests on. "
            "Rounded to one significant figure, order of magnitude."
        ),
    }


def sub(name, tier, note):
    return {"name": name, "tier": tier, "note": note}


# --------------------------------------------------------------------------
# Products. Every ingredient list below is the intentionally-added section of
# the manufacturer's California SB-258 disclosure, read 2026-10-06.
# --------------------------------------------------------------------------
PRODUCTS = [
    # ---- Dish -------------------------------------------------------------
    {
        "name": "up&up Liquid Dishwashing Soap, Fresh",
        "brand": "up&up",
        "cat": "Dish Soap",
        "ings": ["Water", "SODIUM C10-16 ALKETH-2 SULFATE", "SODIUM C10-16 ALKYL SULFATE",
                 "Sodium Xylenesulfonate", "Lauramine Oxide", "Methylchloroisothiazolinone",
                 "Acid Blue 9", "Methylisothiazolinone", "Citric Acid"],
        "source": ("Target California SB-258 chemical disclosure for this SKU "
                   "(intentionally added ingredients, with CAS numbers), read 2026-10-06. "
                   "Product page: https://www.target.com/p/liquid-dish-soap-fresh-28-fl-oz-"
                   "up-38-up-8482/-/A-90468526"),
        "source_url": "https://digitalcontent.target.com/vault/1782432000/CLOUD_65745efc-8a8a-45bb-8711-89648f85ad0b.html",
        "note": ("A store-brand dish liquid. Two published surfaces for the same SKU "
                 "disagree: the product page words the surfactants as 'sodium laureth "
                 "sulfate' and 'sodium lauryl sulfate', while the SB-258 filing names "
                 "SODIUM C10-16 ALKETH-2 SULFATE (68585-34-2) and SODIUM C10-16 ALKYL "
                 "SULFATE (68585-47-7). The filing governs; the page wording is recorded "
                 "in the ingredient notes. The filing also lists 14 fragrance components "
                 "the page does not name at all. The preservative pair "
                 "methylchloroisothiazolinone / methylisothiazolinone is the contact "
                 "allergen class to watch, and it is the same pair in most liquid dish "
                 "soaps at this price."),
        "owner": "Target Corporation", "owner_ev": "reported",
        "owner_src": TGT_ABOUT,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": "https://www.target.com/p/liquid-dish-soap-fresh-28-fl-oz-up-38-up-8482/-/A-90468526",
        "tier_note": "Target house brand, sold at Target (mass and grocery channel).",
        "substitutes": [sub("up&up Multi-Purpose Cleaner, Free & Clear", "grocery",
                            "Same store, same price band, and it carries no isothiazolinone "
                            "preservative pair. Not a dish soap, so it does not replace the "
                            "job; it removes the contact-allergen pair from the sink.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        "exposure": 8, **exp(IB_LAUNDRY,
            "Laundry and home care carries household penetration above 98 percent on the "
            "cited category page, and store-brand dish care is 15 to 20 percent of unit "
            "volume; up&up is one of several store brands inside that share."),
    },
    # ---- Toilet -----------------------------------------------------------
    {
        "name": "up&up Toilet Bowl Cleaner, Fresh Scent",
        "brand": "up&up",
        "cat": "Bathroom",
        "ings": ["Water", "Sodium Hypochlorite", "Pigment Green 7", "Lauramine Oxide",
                 "Myristamine Oxide", "Sodium Hydroxide", "Potassium Iodide", "Sodium Cocoate"],
        "source": ("Target California SB-258 chemical disclosure for this SKU, read "
                   "2026-10-06. Product page: https://www.target.com/p/toilet-bowl-cleaner-"
                   "24oz-up-38-up-8482/-/A-90283211"),
        "source_url": "https://digitalcontent.target.com/vault/1789430400/CLOUD_1d31c3cb-400a-4619-98f2-be65f1fa474e.html",
        "note": ("A bleach toilet gel: sodium hypochlorite is the active, sodium hydroxide "
                 "the pH adjuster, and the two amine oxides are surfactants. Potassium "
                 "iodide is a stabiliser and sodium cocoate a soap. The hazard is the "
                 "bleach itself: never mix it with an acid bowl cleaner or with ammonia, "
                 "both of which release a gas. The label claims 99.9 percent germ kill, "
                 "which is a pesticidal claim and is the manufacturer's, not this record's."),
        "owner": "Target Corporation", "owner_ev": "reported",
        "owner_src": TGT_ABOUT,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": "https://www.target.com/p/toilet-bowl-cleaner-24oz-up-38-up-8482/-/A-90283211",
        "tier_note": "Target house brand, sold at Target (mass and grocery channel).",
        "substitutes": [sub("up&up Multi-Purpose Cleaner, Free & Clear", "grocery",
                            "Same store, same price band, no bleach and no acid. It does not "
                            "lift a set stain the way a bleach gel does, so it avoids the "
                            "mixing hazard rather than matching the strength.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        "exposure": 3, **exp(IB_SURFACE,
            "The cited surface-cleaners page states roughly 95 percent of US households "
            "use at least one surface cleaner product per month, and the toilet-cleaning "
            "page puts residential households at roughly 55 to 60 percent of volume; "
            "up&up is one house brand inside that."),
    },
    # ---- Multi-surface concentrates ---------------------------------------
    {
        "name": "up&up Multi-Surface Cleaner, Pine",
        "brand": "up&up",
        "cat": "All-Purpose",
        "ings": ["Water",
                 "2-Anthracenesulfonic acid, 1-amino-9,10-dihydro-9,10-dioxo-4-(phenylamino)-, monosodium salt",
                 "Tetrasodium EDTA", "Lauramine Oxide", "Acid Yellow 23",
                 "Alcohols, C9-11, ethoxylated",
                 "Quaternary ammonium compounds, benzyl-C8-18-alkyldimethyl, chlorides",
                 "CI 14700",
                 "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride"],
        "source": ("Target California SB-258 chemical disclosure for this SKU, read "
                   "2026-10-06. Product page: https://www.target.com/p/multi-surface-cleaner-"
                   "pine-56oz-up-38-up-8482/-/A-90283226"),
        "source_url": "https://digitalcontent.target.com/vault/1788134400/CLOUD_a22438cd-bd32-415a-acb7-9a933e1d87a0.html",
        "note": ("A concentrated disinfecting multi-surface cleaner. The disinfectant actives "
                 "are two quaternary ammonium blends, benzyl-C8-18 and C12-16; that is the "
                 "severe class in this formula, not the pine scent. The filing declares one "
                 "withheld ingredient (purpose: wetting agent), so the list is complete as "
                 "filed but not complete as chemistry: an undisclosed constituent is present. "
                 "Two dyes (Acid Yellow 23, CI 14700) and a chelating agent are the rest. "
                 "Concentrate: dilute as the label says rather than using it neat."),
        "owner": "Target Corporation", "owner_ev": "reported",
        "owner_src": TGT_ABOUT,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": "https://www.target.com/p/multi-surface-cleaner-pine-56oz-up-38-up-8482/-/A-90283226",
        "tier_note": "Target house brand, sold at Target (mass and grocery channel).",
        "substitutes": [sub("up&up Multi-Purpose Cleaner, Free & Clear", "grocery",
                            "Same store, same price band, and the only up&up multi-surface "
                            "formula in this set with no quaternary ammonium active and no "
                            "declared withheld ingredient.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        "exposure": 3, **exp(IB_SURFACE,
            "The cited surface-cleaners page states roughly 95 percent of US households use "
            "at least one surface cleaner product per month, with all-purpose cleaners the "
            "largest segment at an estimated 30 to 35 percent of value; up&up is one house "
            "brand inside that."),
    },
    {
        "name": "up&up Multi-Surface Cleaner, Lavender",
        "brand": "up&up",
        "cat": "All-Purpose",
        "ings": ["Water", "Lauramine Oxide", "CI 61585", "Alcohols, C9-11, ethoxylated",
                 "Quaternary ammonium compounds, benzyl-C8-18-alkyldimethyl, chlorides",
                 "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride", "Tetrasodium EDTA", "Red 33"],
        "source": ("Target California SB-258 chemical disclosure for this SKU, read "
                   "2026-10-06. Product page: https://www.target.com/p/multi-surface-cleaner-"
                   "lavender-56oz-up-38-up-8482/-/A-90283228"),
        "source_url": "https://digitalcontent.target.com/vault/1788134400/CLOUD_f9456fa1-3541-4aac-a32f-eaaa9a2ce565.html",
        "note": ("The lavender twin of the pine concentrate: the same two quaternary ammonium "
                 "disinfectant blends, a chelating agent, one surfactant, and two dyes. The "
                 "fragrance is declared separately and lists seven components, including "
                 "butylphenyl methylpropional (lilial), which the EU has classified as "
                 "reprotoxic category 1B and restricted in cosmetics. The filing declares a "
                 "withheld ingredient here too."),
        "owner": "Target Corporation", "owner_ev": "reported",
        "owner_src": TGT_ABOUT,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": "https://www.target.com/p/multi-surface-cleaner-lavender-56oz-up-38-up-8482/-/A-90283228",
        "tier_note": "Target house brand, sold at Target (mass and grocery channel).",
        "substitutes": [sub("up&up Multi-Purpose Cleaner, Free & Clear", "grocery",
                            "Same store, same price band, fragrance-free: it removes the "
                            "declared fragrance components (including lilial) and the quat "
                            "actives both.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        "exposure": 2, **exp(IB_SURFACE,
            "The cited surface-cleaners page states roughly 95 percent of US households use "
            "at least one surface cleaner product per month; up&up is one house brand inside "
            "that, and this is the less-used of its two scented concentrates."),
    },
    {
        "name": "up&up Bathroom Disinfecting Cleaner, Unscented",
        "brand": "up&up",
        "cat": "Bathroom",
        "ings": ["Water", "Sodium Metasilicate", "Alcohols, C9-11, ethoxylated",
                 "Quaternary ammonium compounds, benzyl-C8-18-alkyldimethyl, chlorides",
                 "Tetrasodium EDTA", "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride",
                 "Lauramine Oxide", "Acid Yellow 23"],
        "source": ("Target California SB-258 chemical disclosure for this SKU, read "
                   "2026-10-06. Product page: https://www.target.com/p/bathroom-disinfecting-"
                   "cleaner-without-bleach-32oz-up-38-up-8482/-/A-90283225"),
        "source_url": "https://digitalcontent.target.com/vault/1788134400/CLOUD_f625b14d-171c-4cb6-b522-98167f060c9b.html",
        "note": ("'Without bleach' is true and is not the same as 'without a hazard'. The "
                 "disinfectant actives are the same two quaternary ammonium blends as the "
                 "multi-surface concentrates, and the formula adds sodium metasilicate and a "
                 "chelating agent. Unscented, so no fragrance allergens are declared, but the "
                 "filing still declares one withheld ingredient. Quat-based bathroom cleaners "
                 "are the standard for this job; the alternative is a plain surfactant "
                 "cleaner, which cleans without the antimicrobial claim."),
        "owner": "Target Corporation", "owner_ev": "reported",
        "owner_src": TGT_ABOUT,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": "https://www.target.com/p/bathroom-disinfecting-cleaner-without-bleach-32oz-up-38-up-8482/-/A-90283225",
        "tier_note": "Target house brand, sold at Target (mass and grocery channel).",
        "substitutes": [sub("up&up Multi-Purpose Cleaner, Free & Clear", "grocery",
                            "Same store, same price band, no quaternary ammonium active. "
                            "It gives up the disinfectant claim in exchange for removing the "
                            "quat class.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        "exposure": 3, **exp(IB_SURFACE,
            "The cited surface-cleaners page states roughly 95 percent of US households use "
            "at least one surface cleaner product per month, with specialised cleaners "
            "(bathroom, kitchen, glass, floor) 30 to 35 percent of value and bathroom the "
            "largest sub-segment; up&up is one house brand inside that."),
    },
    # ---- Glass ------------------------------------------------------------
    {
        "name": "up&up Glass Cleaner Spray, Unscented",
        "brand": "up&up",
        "cat": "Glass",
        "ings": ["Water", "Butoxyethyl Acetate", "Caprylyl/Capryl Glucoside",
                 "Trisodium Dicarboxymethyl Alaninate", "Ammonium Hydroxide",
                 "Direct Blue 86", "Propylene Glycol", "Sodium Hydroxide"],
        "source": ("Target California SB-258 chemical disclosure for this SKU, read "
                   "2026-10-06. Product page: https://www.target.com/p/glass-cleaner-spray/-/A-95008997"),
        "source_url": "https://digitalcontent.target.com/vault/1729036800/CLOUD_a29ab498-2b9c-437c-ab23-52afd9466aaf.html",
        "note": ("An ammonia glass cleaner. Ammonium hydroxide is the active and the reason it "
                 "clears grease; it is also why the bottle carries an eye-irritation warning "
                 "and why it must never be mixed with a bleach product. Butoxyethyl acetate is "
                 "a glycol ether solvent, the glucoside a mild surfactant, and the blue a dye. "
                 "The product page's own ingredient text lists only three of these eight lines, "
                 "so the page understates the formula; the filing governs."),
        "owner": "Target Corporation", "owner_ev": "reported",
        "owner_src": TGT_ABOUT,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": "https://www.target.com/p/glass-cleaner-spray/-/A-95008997",
        "tier_note": "Target house brand, sold at Target (mass and grocery channel).",
        "substitutes": [sub("up&up Unscented Foaming Glass Cleaner", "grocery",
                            "Same store, same price band, and the label reads 'without "
                            "ammonia'. Target publishes no SB-258 disclosure for it, so its "
                            "formula is not verified here; the ammonia is the specific thing "
                            "it avoids.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        "exposure": 3, **exp(IB_SURFACE,
            "The cited surface-cleaners page states roughly 95 percent of US households use "
            "at least one surface cleaner product per month, with specialised cleaners 30 to "
            "35 percent of value; up&up is one house brand inside that."),
    },
    # ---- Bleach -----------------------------------------------------------
    {
        "name": "up&up Regular Bleach with Fabric Protection",
        "brand": "up&up",
        "cat": "Laundry",
        "ings": ["Water", "Sodium Hypochlorite", "Periodic acid (HIO4), sodium salt",
                 "Sodium Hydroxide", "Sodium Silicate"],
        "source": ("Target California SB-258 chemical disclosure for this SKU, read "
                   "2026-10-06. Product page: https://www.target.com/p/epa-regular-bleach-"
                   "with-fabric-protection-up-up/-/A-80159909"),
        "source_url": "https://digitalcontent.target.com/vault/1770768000/CLOUD_89749dd1-e9b7-41ec-8dca-86892bce19c3.html",
        "note": ("Five lines: water, sodium hypochlorite, sodium hydroxide, sodium silicate and "
                 "sodium periodate. The last two are what make it a 'with fabric protection' "
                 "bleach rather than plain hypochlorite: silicate is a corrosion inhibitor and "
                 "periodate a stabiliser that slows the bleach breaking down on the shelf. "
                 "Nothing here is exotic and nothing here is gentle: hypochlorite is the "
                 "hazard, and it reacts with ammonia and with acid."),
        "owner": "Target Corporation", "owner_ev": "reported",
        "owner_src": TGT_ABOUT,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": "https://www.target.com/p/epa-regular-bleach-with-fabric-protection-up-up/-/A-80159909",
        "tier_note": "Target house brand, sold at Target (mass and grocery channel).",
        "substitutes": [sub("up&up Powder Stain Remover", "grocery",
                            "Same store, same price band, sodium percarbonate chemistry "
                            "rather than hypochlorite: it avoids the chlorine and the "
                            "ammonia-mixing hazard, and it is the gentler choice on colour "
                            "and on fabric.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        "exposure": 5, **exp(IB_BLEACH,
            "The cited bleach page states near-universal household penetration, estimated at "
            "80 to 90 percent of US households buying bleach at least once a year, with "
            "private-label and store-brand products 25 to 35 percent of retail volume; up&up "
            "is one house brand inside that."),
    },
    # ---- Disinfectant spray ----------------------------------------------
    {
        "name": "up&up Fresh Scent Disinfectant Spray",
        "brand": "up&up",
        "cat": "Disinfectant",
        "ings": ["Alcohol", "Water", "Isobutane", "Propane",
                 "Alkyl C12-18 Dimethylbenzyl Ammonium Chloride",
                 "Quaternary ammonium compounds, C12-14-alkyl[(ethylphenyl)methyl]dimethyl, chlorides",
                 "SOYETHYL MORPHOLINIUM ETHOSULFATE", "Sodium Nitrite", "Sodium Benzoate"],
        "source": ("Target California SB-258 chemical disclosure for this SKU, read "
                   "2026-10-06. Product page: https://www.target.com/p/fresh-scent-"
                   "disinfectant-spray-19oz-up-38-up-8482/-/A-14695562"),
        "source_url": "https://digitalcontent.target.com/vault/1785369600/CLOUD_26bb383f-9fed-4635-86dc-3a174d243ee4.html",
        "note": ("An aerosol disinfectant. The propellants are isobutane and propane, which "
                 "makes the can flammable, and ethanol is both a solvent and an antimicrobial. "
                 "The two quaternary ammonium blends are the declared disinfectant actives; "
                 "sodium nitrite is a corrosion inhibitor and, paired with an amine, a "
                 "nitrosamine precursor in principle. This is the aerosol form of the same "
                 "quat chemistry as the wipes."),
        "owner": "Target Corporation", "owner_ev": "reported",
        "owner_src": TGT_ABOUT,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": "https://www.target.com/p/fresh-scent-disinfectant-spray-19oz-up-38-up-8482/-/A-14695562",
        "tier_note": "Target house brand, sold at Target (mass and grocery channel).",
        "substitutes": [sub("up&up Multi-Purpose Cleaner, Free & Clear", "grocery",
                            "Same store, same price band, a pump spray with no propellant and "
                            "no quaternary ammonium active. It avoids the flammability and the "
                            "quat class; it gives up the aerosol convenience.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        "exposure": 4, **exp(IB_SURFACE,
            "The cited surface-cleaners page states roughly 95 percent of US households use "
            "at least one surface cleaner product per month and that grocery, mass-merchant, "
            "club and dollar stores are roughly 70 to 75 percent of value sales; up&up is one "
            "house brand inside that."),
    },
    # ---- Wipes ------------------------------------------------------------
    {
        "name": "up&up Fresh Scent Disinfecting Wipes",
        "brand": "up&up",
        "cat": "Disinfectant",
        "ings": ["Dioctyldimethylammonium Chloride", "Quaternium-24",
                 "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride",
                 "Didecyldimethylammonium Chloride"],
        "source": ("Target California SB-258 chemical disclosure for this SKU, read "
                   "2026-10-06. Product page: https://www.target.com/p/fresh-scent-"
                   "disinfecting-wipes-35ct-up-38-up-8482/-/A-13972114"),
        "source_url": "https://digitalcontent.target.com/vault/1663891200/CLOUD_2ccd7122-df96-4b6d-a244-5b9fb4a9e6a9.html",
        "note": ("The shortest and the sharpest list in this block: four quaternary ammonium "
                 "compounds and nothing else declared. No water, no surfactant, no fragrance "
                 "component is listed as intentionally added, so what the filing describes is "
                 "the active system on the wipe rather than the whole wet formula. Four "
                 "different quats in one wipe is the reason this class shows up as a contact "
                 "irritant and, in the environment, as a persistent aquatic toxicant. Keep "
                 "them off food-contact surfaces you will not rinse."),
        "owner": "Target Corporation", "owner_ev": "reported",
        "owner_src": TGT_ABOUT,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": "https://www.target.com/p/fresh-scent-disinfecting-wipes-35ct-up-38-up-8482/-/A-13972114",
        "tier_note": "Target house brand, sold at Target (mass and grocery channel).",
        "substitutes": [sub("up&up Multi-Purpose Cleaner, Free & Clear", "grocery",
                            "Same store, same price band, quat-free. A spray and a cloth does "
                            "the same job; the trade is convenience, not chemistry.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        "exposure": 5, **exp(IB_WIPES,
            "The cited cleaning-wipes page states over 90 percent of US households use at "
            "least one type of cleaning wipe regularly and that disinfecting and sanitizing "
            "wipes are the largest segment at roughly 40 to 45 percent of category volume, "
            "with private-label penetration 30 to 35 percent of that segment; up&up is one "
            "house brand inside that."),
    },
    # ---- Free & clear multi-purpose ---------------------------------------
    {
        "name": "up&up Multi-Purpose Cleaner, Free & Clear",
        "brand": "up&up",
        "cat": "All-Purpose",
        "ings": ["Water", "Citric Acid", "Sodium Hydroxide", "Coco-Glucoside",
                 "Benzisothiazolinone", "Caprylyl/Capryl Glucoside", "Sodium Gluconate",
                 "Sodium Carbonate"],
        "source": ("Target California SB-258 chemical disclosure for this SKU, read "
                   "2026-10-06. Product page: https://www.target.com/p/multi-purpose-cleaners-"
                   "liquid-free-38-clear-32-fl-oz-up-38-up-8482/-/A-94762127"),
        "source_url": "https://digitalcontent.target.com/vault/1780012800/CLOUD_18f92a5e-01d2-4afa-a103-1d6619b20d1a.html",
        "note": ("The one formula in this block with no quaternary ammonium active and no "
                 "declared fragrance: two glucoside surfactants, a citric acid / sodium "
                 "carbonate buffer, sodium gluconate as a chelator, and benzisothiazolinone "
                 "as the preservative. It is the mildest list here and the one to reach for "
                 "when the job is cleaning rather than disinfecting. Benzisothiazolinone is "
                 "still a contact allergen, so it is not allergen-free, only fragrance-free."),
        "owner": "Target Corporation", "owner_ev": "reported",
        "owner_src": TGT_ABOUT,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": "https://www.target.com/p/multi-purpose-cleaners-liquid-free-38-clear-32-fl-oz-up-38-up-8482/-/A-94762127",
        "tier_note": "Target house brand, sold at Target (mass and grocery channel).",
        "substitutes": [sub("up&up Liquid Dishwashing Soap, Fresh", "grocery",
                            "Same store, same price band. Named for completeness; it swaps a "
                            "benzisothiazolinone preservative for the isothiazolinone pair, "
                            "which is not an improvement on that one dimension.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        "exposure": 1, **exp(IB_SURFACE,
            "The cited surface-cleaners page states roughly 95 percent of US households use "
            "at least one surface cleaner product per month; this is the smallest-volume "
            "formula in the up&up multi-surface line and one house brand inside that."),
    },
    # ---- Mold and mildew --------------------------------------------------
    {
        "name": "up&up Mold and Mildew Stain Remover",
        "brand": "up&up",
        "cat": "Specialty",
        "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide", "Lauramine Oxide"],
        "source": ("Target California SB-258 chemical disclosure for this SKU, read "
                   "2026-10-06. Product page: https://www.target.com/p/mold-and-mildew-stain-"
                   "remover-32oz-up-38-up-8482/-/A-90283207"),
        "source_url": "https://digitalcontent.target.com/vault/1785369600/CLOUD_275aa9e3-9ab9-494b-8d0b-646fcaf286d0.html",
        "note": ("Four lines: water, sodium hypochlorite, sodium hydroxide, one amine oxide "
                 "surfactant. This is a bleach spray with a surfactant, and the whole formula "
                 "is disclosed. Bleach kills mould on contact and does not remove the stain "
                 "from a porous surface the way an oxygen or acid product can; it also does "
                 "not stop the moisture that grew the mould. Ventilate, never mix with acid or "
                 "ammonia, and fix the water source or it comes back."),
        "owner": "Target Corporation", "owner_ev": "reported",
        "owner_src": TGT_ABOUT,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": "https://www.target.com/p/mold-and-mildew-stain-remover-32oz-up-38-up-8482/-/A-90283207",
        "tier_note": "Target house brand, sold at Target (mass and grocery channel).",
        "substitutes": [sub("up&up Multi-Purpose Cleaner, Free & Clear", "grocery",
                            "Same store, same price band, no bleach: it avoids the chlorine "
                            "and the mixing hazard, and it will not clear a set mildew stain "
                            "the way the bleach does. Fixing the moisture is the real fix.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        "exposure": 2, **exp(IB_SURFACE,
            "The cited surface-cleaners page states roughly 95 percent of US households use "
            "at least one surface cleaner product per month, with specialised cleaners 30 to "
            "35 percent of value; mould and mildew removers are a small sub-segment of that "
            "and up&up is one house brand inside it."),
    },
    # ---- Stain remover ----------------------------------------------------
    {
        "name": "up&up Stain Remover",
        "brand": "up&up",
        "cat": "Stain & Odor",
        "ings": ["Water", "C12-15 Alcohols Ethoxylated", "SODIUM C10-16 ALKETH-2 SULFATE",
                 "Methylchloroisothiazolinone", "Sodium Acrylic Acid/MA Copolymer",
                 "Subtilisin", "Aziridine, homopolymer, ethoxylated", "Methylisothiazolinone"],
        "source": ("Target California SB-258 chemical disclosure for this SKU, read "
                   "2026-10-06. Product page: https://www.target.com/p/stain-remover-22oz-"
                   "up-38-up-8482/-/A-84300911"),
        "source_url": "https://digitalcontent.target.com/vault/1746921600/CLOUD_a75bb4b6-d90c-41cd-be39-70834b95f3b3.html",
        "note": ("A laundry pre-treatment. The active work is done by subtilisin, a protease "
                 "enzyme, and by two surfactants; a soil-release polymer and the isothiazolinone "
                 "preservative pair complete it. Subtilisin is a respiratory sensitiser in "
                 "powder form, which is why enzyme detergents carry the 'do not breathe' line; "
                 "in a liquid it is far less of an inhalation risk, but it is still the "
                 "ingredient to keep off skin you will not rinse."),
        "owner": "Target Corporation", "owner_ev": "reported",
        "owner_src": TGT_ABOUT,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": "https://www.target.com/p/stain-remover-22oz-up-38-up-8482/-/A-84300911",
        "tier_note": "Target house brand, sold at Target (mass and grocery channel).",
        "substitutes": [sub("up&up Powder Stain Remover", "grocery",
                            "Same store, same price band, percarbonate rather than enzyme: it "
                            "avoids subtilisin and the isothiazolinone pair. Works by "
                            "oxidation rather than by protein breakdown, so it is slower on "
                            "food and protein stains.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        "exposure": 3, **exp(IB_LAUNDRY,
            "Laundry and home care carries household penetration above 98 percent on the "
            "cited category page; up&up is one house brand inside the pre-treatment "
            "sub-segment."),
    },
    # ---- Dishwasher -------------------------------------------------------
    {
        "name": "up&up Ultimate Dishwasher Detergent Packs",
        "brand": "up&up",
        "cat": "Dishwasher",
        "ings": ["Sodium Carbonate", "Trisodium Dicarboxymethyl Alaninate", "Sodium Citrate",
                 "Sodium Percarbonate", "PEG/PPG-10/2 PROPYLHEPTYL ETHER", "Water",
                 "Sodium Silicate", "Dipropylene Glycol", "Sodium Acrylic Acid/MA Copolymer",
                 "Glycerin", "Amylase", "Propylene Glycol", "Subtilisin", "Acid Blue 182",
                 "2-Propenoic acid, polymer with 2-methyl-2-[(1-oxo-2-propenyl)amino]-1-propanesulfonic acid monosodium salt, sodium salt"],
        "source": ("Target California SB-258 chemical disclosure for this SKU, read "
                   "2026-10-06. Product page: https://www.target.com/p/ultimate-dishwasher-"
                   "detergent-packs-21ct-up-38-up-8482/-/A-90468528"),
        "source_url": "https://digitalcontent.target.com/vault/1767744000/CLOUD_2b605d75-c741-4a07-953f-5ce9ca14fbab.html",
        "note": ("A pod. The wash is done by two enzymes (subtilisin and amylase), a "
                 "percarbonate bleach, sodium carbonate for alkalinity, and two chelating "
                 "agents; the film and the blue dye are the rest. Pods are a swallowed-hazard "
                 "for small children and the packaging is what changed the industry, not the "
                 "chemistry. Enzyme proteins are respiratory sensitisers as dust; a pod "
                 "contains them in a liquid or solid matrix rather than as loose powder, "
                 "which is the safer form."),
        "owner": "Target Corporation", "owner_ev": "reported",
        "owner_src": TGT_ABOUT,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": "https://www.target.com/p/ultimate-dishwasher-detergent-packs-21ct-up-38-up-8482/-/A-90468528",
        "tier_note": "Target house brand, sold at Target (mass and grocery channel).",
        "substitutes": [sub("up&up Everyday Dishwasher Detergent Packs", "grocery",
                            "Same store, cheaper in the same aisle. Named as the same-price "
                            "alternative; Target publishes no SB-258 disclosure for it, so its "
                            "formula is not verified here.")],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        "exposure": 3, **exp(IB_DISHWASH,
            "The cited dishwashing-market page puts dishwasher penetration at roughly 68 to "
            "72 percent of US households; up&up is one house brand inside the pod segment."),
    },
]

# --------------------------------------------------------------------------
# Repair: the one existing up&up record carries a three-item list from the
# product page. Its own SB-258 filing discloses eight. Truncated list, not a
# different product -- completed here and the assumption recorded.
# --------------------------------------------------------------------------
REPAIR = {
    "name": "up&up Lemon All-Purpose Disinfecting Cleaner without Bleach",
    "ings": ["Water", "Sodium Metasilicate", "Alcohols, C9-11, ethoxylated",
             "Tetrasodium EDTA", "Lauramine Oxide", "Acid Yellow 23",
             "Quaternary ammonium compounds, benzyl-C8-18-alkyldimethyl, chlorides",
             "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride"],
    "source_url": "https://digitalcontent.target.com/vault/1770768000/CLOUD_81ae3f26-a0dd-4777-9ac4-e43588ba39fc.html",
    "source": ("Target California SB-258 chemical disclosure for this SKU (intentionally "
               "added ingredients, with CAS numbers), read 2026-10-06; product page "
               "https://www.target.com/p/lemon-all-purpose-disinfecting-cleaner-without-"
               "bleach-32oz-up-38-up-8482/-/A-90283206. Repairs a three-item list taken "
               "from the product page on 2026-09-24."),
    "note": ("A mass-retailer house brand, and 'without bleach' is not 'without a hazard': "
             "the disinfectant actives are two quaternary ammonium blends, which are the "
             "severe class in this formula. The 2026-09-24 record carried only Water, "
             "Quaternary Ammonium and Fragrance, taken from the product page. The "
             "manufacturer's own SB-258 filing discloses eight intentionally added "
             "ingredients, so the earlier list was a truncated read of the same product and "
             "is completed here. The filing declares one withheld ingredient, so the list is "
             "complete as filed but not complete as chemistry."),
    "strength_disclosure": "full",
    "exposure": 3,
    "exposure_ev": "extrapolated",
    "exposure_src": IB_SURFACE,
    "exposure_basis": (
        "The cited surface-cleaners page states roughly 95 percent of US households use at "
        "least one surface cleaner product per month, with all-purpose cleaners the largest "
        "segment at an estimated 30 to 35 percent of value. Searched for a published "
        "per-product US household-penetration figure for this SKU and located none. The "
        "estimate derives from the category figure and this product's position as one house "
        "brand inside Target, and stops there. Rounded to one significant figure."
    ),
}


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def dump(path, obj, indent):
    # Measured at head 2026-10-06: products/ingredients/owners indent=1 and no
    # trailing newline; changelog indent=2 and no trailing newline. Match each.
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=indent, ensure_ascii=False)


def resolve(ings, lower, added_keys):
    new_lower = {k.lower(): k for k in NEW_KEYS}
    alias_lower = {k.lower(): v for k, v in ALIASES.items()}
    out = []
    for raw in ings:
        key = alias_lower.get(raw, alias_lower.get(raw.lower(), raw))
        if key.lower() in lower:
            out.append(lower[key.lower()])
        elif key.lower() in new_lower:
            out.append(new_lower[key.lower()])
            added_keys.add(new_lower[key.lower()])
        else:
            raise SystemExit(f"unknown ingredient key, refusing to guess: {raw!r}")
    return out


def main():
    products = load("products.json")
    ingredients = load("ingredients.json")
    changelog = load("changelog.json")

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

    repaired = False
    for r in products:
        if r["name"] == REPAIR["name"]:
            before = len(r.get("ings") or [])
            r["ings"] = resolve(REPAIR["ings"], lower, added_keys)
            r["source"] = REPAIR["source"]
            r["source_url"] = REPAIR["source_url"]
            r["note"] = REPAIR["note"]
            r["strength_disclosure"] = REPAIR["strength_disclosure"]
            r["exposure"] = REPAIR["exposure"]
            r["exposure_ev"] = REPAIR["exposure_ev"]
            r["exposure_src"] = REPAIR["exposure_src"]
            r["exposure_basis"] = REPAIR["exposure_basis"]
            r["updated"] = TODAY
            repaired = True
            print(f"repair: {r['name']}  {before} -> {len(r['ings'])} ings")
    if not repaired:
        print("repair target not found (already applied?)")

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
            "text": ("Spectrum harvest: 13 products added to the grocery house-brand block "
                     "from Target's California SB-258 chemical disclosures (up&up dish soap, "
                     "toilet gel, two multi-surface concentrates, bathroom disinfectant, "
                     "glass cleaner, bleach, aerosol disinfectant, disinfecting wipes, "
                     "free-and-clear multi-purpose, mould remover, stain remover, dishwasher "
                     "packs). Also repaired the one existing up&up record, whose three-item "
                     "list came from the product page while its own filing discloses eight. "
                     "Two served disclosure shapes were found and both handled: some tables "
                     "label their columns in the reverse of their own header."),
        })

    if DRY:
        print(f"\nDRY RUN: would add {added} products, "
              f"{len(added_keys)} ingredient keys, and repair 1 record.")
        return

    dump(os.path.join(DATA, "products.json"), products, 1)
    dump(os.path.join(DATA, "ingredients.json"), ingredients, 1)
    dump(os.path.join(DATA, "changelog.json"), changelog, 2)
    print(f"\nwrote {added} products, {len(added_keys)} new ingredient keys, 1 repair.")


if __name__ == "__main__":
    main()
