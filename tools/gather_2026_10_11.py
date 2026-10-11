#!/usr/bin/env python3
"""Daily gather (2026-10-11, 10:00Z maintenance lane): four products that were
missing from the database, plus the ingredient records they need. Each of the
four fills a FUNCTION the corpus did not carry at all, and one of them carries
a four-way ownership lineage the registry had recorded twice.

Sources read on 2026-10-11:

  - Wright's Silver Cream. J.A. Wright's own published ingredient table, which
    lists every ingredient with its CAS number and function (product codes 014,
    317A, 369). Cross-checked against the Weiman Products MSDS (issue date
    2009-08-13) and the current owner's California SB-258 posture.
    https://jawright.com/media/ingredient/wrights-silver-cream-ingredients.pdf
    https://www.lamarpa.edu/about/college-operations/security-emergency-management/_documents/msds/pp/Wrights%20Silver%20Cream%20MSDS.pdf
  - Glisten Disposer Care. The manufacturer's own SDS composition section
    (Summit Brands, product DP06N-PB, 'Glisten Disposer Care'), in two
    revisions (issue 2021-02-08 and 2025-10-27), plus the brand's product page.
    https://hdsupplysolutions.com/wcsstore/ExtendedSitesCatalogAssetStore/product/hdpro/additional/PR/PRO_880124_SDS_880124_SDS_E.pdf
    https://images.thdstatic.com/catalog/pdfImages/39/394d64ea-d666-4524-9115-baa3cb9be100.pdf
  - affresh Coffee Maker Cleaner. The maker's own SDS composition section
    (Whirlpool Corporation, product numbers W10511280 / W10355052 / W10921672,
    revision 2025-12-30). The SDS states the product is registered with the US
    EPA Safer Choice Program, so every component is listed.
    https://www.affresh.com/wp-content/uploads/2026/01/sds_affresh_coffee_maker_cleaner_20251230.pdf
  - Zep Grout Cleaner & Brightener. The maker's own SDS composition section
    (Zep Inc., product ZU104632, revision D054703) plus Zep's own California
    Cleaning Product Right to Know Act (SB-258) disclosure, which lists the
    intentionally added ingredients with CAS numbers and functions.
    https://images.thdstatic.com/catalog/pdfImages/04/04135db2-1895-4bb6-aa14-a5e98d19a1ed.pdf
    https://media.suthlbr.com/images/downloads/vendor/13955/8064776_ingredients.pdf

Why these four. The corpus is deep in the bleach/bathroom/disinfectant cluster
and in the mass laundry aisle, and thin in surfaces that are cleaned for a
reason OTHER than appearance. A keyword sweep of the 374-product corpus found
four functions with ZERO products: grout cleaning (0), silver/metal polishing
beyond a single brass polish (0), garbage-disposal cleaning (0), and coffee-
maker cleaning (0). Each product below is the category leader for one of those
functions and each maker publishes its own full ingredient list, so no grade
here is inferred from a marketing page.

Ownership note. Wright's Silver Cream is the reason the owner registry was
touched this run. The registry already carried "PurposeBuilt Brands" (verified
against its SEC registration statement) with the detail text naming "Weiman,
Goo Gone and Wright's" as its consumer specialty cleaning brands -- and it ALSO
carried a separate "Weiman Products, LLC" record minted 2026-10-10 that names
no parent. Both describe the same Gurnee, Illinois company: Weiman Products LLC
renamed itself PurposeBuilt Brands in 2020. Wright's is therefore attached to
PurposeBuilt Brands (the record that already names the brand) and the "Wright's"
brand is added to that record's brand list; the duplicate Weiman Products, LLC
record is flagged for the owner-dedupe lane rather than deleted here.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-11"

DRY = "--dry-run" in sys.argv
NO_CHANGELOG = "--no-changelog" in sys.argv

WRIGHT_ING = ("https://jawright.com/media/ingredient/"
              "wrights-silver-cream-ingredients.pdf")
WRIGHT_MSDS = ("https://www.lamarpa.edu/about/college-operations/"
               "security-emergency-management/_documents/msds/pp/"
               "Wrights%20Silver%20Cream%20MSDS.pdf")
WRIGHT_OWNER_SRC = "https://purposebuiltbrands.com/company"
GLISTEN_SDS = ("https://hdsupplysolutions.com/wcsstore/"
               "ExtendedSitesCatalogAssetStore/product/hdpro/additional/PR/"
               "PRO_880124_SDS_880124_SDS_E.pdf")
GLISTEN_SDS2 = ("https://images.thdstatic.com/catalog/pdfImages/39/"
                "394d64ea-d666-4524-9115-baa3cb9be100.pdf")
GLISTEN_OWNER_SRC = "https://summitbrands.com/product/glisten-garbage-disposer-cleaner/"
AFFRESH_SDS = ("https://www.affresh.com/wp-content/uploads/2026/01/"
               "sds_affresh_coffee_maker_cleaner_20251230.pdf")
AFFRESH_OWNER_SRC = "https://www.whirlpoolcorp.com/"
ZEP_SDS = ("https://images.thdstatic.com/catalog/pdfImages/04/"
           "04135db2-1895-4bb6-aa14-a5e98d19a1ed.pdf")
ZEP_SB258 = ("https://media.suthlbr.com/images/downloads/vendor/13955/"
             "8064776_ingredients.pdf")
ZEP_OWNER_SRC = "https://www.zep.com/"

# --------------------------------------------------------------------------
# Ingredient key resolution. Label wording -> existing canonical key, where the
# substance is the same and a second key would be a synonym for one CAS.
# --------------------------------------------------------------------------
ALIASES = {
    # Wright's prints the mineral form; the DB's Silica key is documented as
    # the crystalline-silica key ("Crystalline silica dust is a respiratory
    # hazard"), and quartz is crystalline silica (CAS 14808-60-7). Aliased
    # rather than minted, so the corpus does not carry two keys for one
    # substance. The CAS is recorded in the product source below.
    "Quartz": "Silica",
    # Zep's SB-258 filing prints the substance without the "yl" the DB's
    # canonical key carries; both are 2-butoxyethanol, CAS 111-76-2, the
    # substance already graded under the Butyloxyethanol key.
    "Butoxyethanol": "Butyloxyethanol",
    # Glisten's SDS prints the hydrotrope with a space; the DB's canonical key
    # (PubChem title) is the closed form. Same substance, CAS 1300-72-7.
    "Sodium xylene sulfonate": "Sodium Xylenesulfonate",
}

# New keys minted this fire. Shape follows the registry: ungraded is recorded
# as ev "Low"/"Medium" with g "Not Classified" (or null) and an explicit
# sourcing note, never a guess.
NEW_KEYS = {
    "Anhydrous aluminum silicate": {
        "s": "Anhydrous aluminium silicate (CAS 66402-68-4); a calcined-clay "
             "polishing abrasive.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on J.A. Wright's own published ingredient table for "
                "Wright's Silver Cream as 'Anhydrous aluminum silicate' (CAS "
                "66402-68-4, function 'Polishing agent'). PubChem PUG REST "
                "returns 404 for both the name and the CAS number -- no "
                "discrete CID resolves for this mineral -- so no GHS "
                "classification is available. Recorded Not Classified rather "
                "than guessed, the same way the DB carries Kaolin and other "
                "mineral keys. Distinct from the DB's Kaolin key (hydrated "
                "aluminium silicate, CAS 1332-58-7): this is the anhydrous "
                "(calcined) form.",
    },
    "Iron oxides": {
        "s": "Iron(III) oxide (CAS 1309-37-1); the red/pink colorant in metal "
             "polishes.",
        "ev": "Medium", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on J.A. Wright's own published ingredient table for "
                "Wright's Silver Cream as 'Iron oxides' (CAS 1309-37-1, "
                "function 'Colorant'). PubChem PUG REST resolves the CAS to "
                "CID 518696, returned title 'Iron oxide (Fe2O3)' -- the title "
                "was confirmed before the record was accepted. The headline "
                "(largest company-count) ECHA C&L block reports only H319 "
                "(18.5%, serious eye irritation) and H411 (12%, aquatic "
                "toxicity), BOTH below the 40% house bar, so no dimension "
                "grade is minted. Secondary notifier blocks carry H315, H318, "
                "H335, H370 and H372 without a consensus percentage; under the "
                "strict >=40% rule they are recorded here for auditability but "
                "do not drive a grade. Recorded Not Classified with the "
                "sub-consensus codes stated rather than graded.",
    },
    "Acrylic polymer emulsion": {
        "s": "Acrylic polymer emulsion; a thickener. Composition not specified "
             "on the disclosure.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on J.A. Wright's own published ingredient table for "
                "Wright's Silver Cream as 'Acrylic polymer emulsion' (function "
                "'Thickener') with the CAS number WITHHELD by the maker. No "
                "CAS, no discrete identity and no PubChem CID, so no "
                "classification is possible. Recorded Not Classified rather "
                "than guessed, the same way the DB carries other "
                "identity-withheld constituents (Silicone Emulsion, Glycol "
                "Ether).",
    },
    "Malic Acid": {
        "s": "Fruit acid (CAS 6915-15-7); the acidulant that does the cleaning "
             "in a bleach-alternative foaming disposer cleaner.",
        "ev": "High", "g": "H319,H315", "gr": {"derm": "C"},
        "impacts": ["derm"],
        "note": "Graded from PubChem GHS (CID 525, returned title 'Malic "
                "Acid'; the name was confirmed against CAS 6915-15-7 before "
                "the record was accepted). Headline ECHA C&L notifier "
                "consensus: H319 (serious eye irritation) 89.2% and H315 (skin "
                "irritation) 74.2%, both >=40% -> derm C by house precedent "
                "(Citric Acid, Sodium Xylenesulfonate). H318 (serious eye "
                "damage) sits at 10.5% and H302 (harmful if swallowed) at "
                "10.5%, both below the 40% bar. Disclosed by Summit Brands for "
                "Glisten Disposer Care at 15-40% by weight.",
    },
    "Alcohols, C10-16": {
        "s": "C10-16 linear alcohol (CAS 67762-41-8); a defoamer/surfactant "
             "co-component.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Summit Brands' own SDS composition section for "
                "Glisten Disposer Care as 'Alcohols, C10-16' (CAS "
                "67762-41-8) at 0.1-1% by weight. PubChem PUG REST returns 404 "
                "for both the name and the CAS number: this is a UVCB "
                "(a straight-chain alcohol cut whose composition varies with "
                "the feedstock), so no discrete CID resolves and no GHS "
                "classification is available. Recorded Not Classified rather "
                "than guessed.",
    },
    "Sodium Bisulfate": {
        "s": "Sodium acid sulfate (CAS 7681-38-1); the acid pH adjuster in "
             "coffee-maker cleaning tablets.",
        "ev": "High", "g": "H318", "gr": {"derm": "D"},
        "impacts": ["derm"],
        "note": "Graded from PubChem GHS (CID 516919, returned title 'Sodium "
                "Bisulfate'; the name was confirmed against CAS 7681-38-1 "
                "before the record was accepted). Headline ECHA C&L notifier "
                "consensus: H318 (causes serious eye damage) 99.6% -> derm D. "
                "Disclosed by Whirlpool Corporation for affresh Coffee Maker "
                "Cleaner at 30-40% by weight; the product is registered with "
                "the US EPA Safer Choice Program, which is why every component "
                "is listed on the SDS.",
    },
    "Urea Hydrochloride": {
        "s": "Urea hydrochloride (CAS 506-89-8); the acid that dissolves grout "
             "haze and mineral film.",
        "ev": "Medium", "g": "H335,H319,H315,H290",
        "gr": {"derm": "D", "resp": "C"}, "impacts": ["derm", "resp"],
        "note": "Graded from PubChem GHS (CID 101721, returned title 'Urea "
                "hydrochloride'; the name was confirmed against CAS 506-89-8 "
                "before the record was accepted). Headline ECHA C&L notifier "
                "consensus: H335 (respiratory irritation) 81%, H315 (skin "
                "irritation) 52.4%, H290 (may be corrosive to metals) 47.6% "
                "and H319 (serious eye irritation) 42.9%, all >=40%. H314 "
                "(severe skin burns) sits at 38.1% -- just below the 40% bar -- "
                "but maps to derm D under the >=10% corrosivity precedent, so "
                "derm lands at D rather than F. Disclosed by Zep Inc. for Grout "
                "Cleaner & Brightener at 10-20% by weight.",
    },
    "C9-11 Pareth-3": {
        "s": "C9-11 alcohol ethoxylate (CAS 68439-46-3); the nonionic "
             "emulsifier/surfactant in an acidic grout cleaner.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Zep Inc.'s own California SB-258 disclosure for "
                "Grout Cleaner & Brightener as 'C9-11 Pareth-3 (ethoxylated "
                "C9-11 alcohols)' (CAS 68439-46-3, function 'Emulsifier'). "
                "PubChem PUG REST returns 404 for both the name and the CAS "
                "number: this is a UVCB (an alcohol-ethoxylate cut whose "
                "ethoxylate number and chain distribution vary), so no "
                "discrete CID resolves and no GHS classification is available. "
                "Recorded Not Classified rather than guessed. See the DB's "
                "'Alcohol Ethoxylate' regulatory entry for the class-level "
                "EU/US story.",
    },
    "Quaternary Ammonium Compounds": {
        "s": "Coco-alkyl bis(hydroxyethyl)methyl, ethoxylated, quaternary "
             "ammonium chlorides (CAS 61791-10-4); the cleaning agent.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Zep Inc.'s own California SB-258 disclosure for "
                "Grout Cleaner & Brightener as 'Quaternary ammonium compounds, "
                "coco alkylbis(hydroxyethyl)methyl, ethoxylated, chlorides' "
                "(CAS 61791-10-4, function 'Cleaning Agent'). PubChem PUG REST "
                "returns 404 for both the name and the CAS number: this is a "
                "UVCB (a mixture of ethoxylated quaternary ammonium homologues "
                "keyed to the coco cut), so no discrete CID resolves and no GHS "
                "classification is available. Recorded Not Classified rather "
                "than guessed. The DB carries a separate class-level "
                "'Quaternary Ammonium' regulatory entry; this key is kept "
                "distinct because the label names a specific CAS.",
    },
    "Diethyl Phthalate": {
        "s": "Diethyl phthalate (CAS 84-66-2); a fragrance solvent/carrier and "
             "a phthalate.",
        "ev": "Medium", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Zep Inc.'s own California SB-258 disclosure for "
                "Grout Cleaner & Brightener as 'Diethyl Phthalate' (CAS "
                "84-66-2, function 'Fragrance'). PubChem PUG REST resolves the "
                "CAS to CID 6781, returned title 'Diethyl Phthalate' -- the "
                "title was confirmed before the record was accepted. The "
                "headline ECHA C&L block reports 'not meeting GHS hazard "
                "criteria' by 1710 of 1769 companies, so no consensus code "
                "reaches the 40% house bar and no dimension grade is minted. "
                "Secondary notifier blocks carry H315, H317 (skin sensitizer), "
                "H320, H335, H336 and H401 without a consensus percentage; "
                "they are recorded here for auditability but do not drive a "
                "grade. Recorded Not Classified rather than graded. NOTE for "
                "the sifter lane: DEP is a phthalate, and its regulatory "
                "concern (endocrine activity, the EU's phthalate restrictions) "
                "is a non-GHS matter that this grade does not capture -- the "
                "same gap the DB already flags for the glycol-ether class.",
    },
    "Acetophenone": {
        "s": "Acetophenone (CAS 98-86-2); a fragrance component (hypnotic/"
             "cherry note).",
        "ev": "High", "g": "H319,H302", "gr": {"derm": "C"},
        "impacts": ["derm"],
        "note": "Named on Zep Inc.'s own California SB-258 disclosure for "
                "Grout Cleaner & Brightener as 'Acetophenone' (CAS 98-86-2, "
                "function 'Fragrance'). Graded from PubChem GHS (CID 7410, "
                "returned title 'Acetophenone'; the name was confirmed against "
                "the CAS before the record was accepted). Headline ECHA C&L "
                "notifier consensus: H302 (harmful if swallowed) >99.9% and "
                "H319 (serious eye irritation) 99.9% -> derm C. H360 (may "
                "damage fertility or the unborn child) and H361 (suspected of "
                "damaging fertility or the unborn child) are listed without a "
                "notifier consensus percentage, so under the >=40% rule they "
                "are recorded here but do not drive a grade -- the same "
                "treatment the DB gives Potassium Iodide's H360/H362. The "
                "sub-consensus reproductive signal is flagged rather than "
                "graded.",
    },
}


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
# list, read 2026-10-11.
# --------------------------------------------------------------------------
PRODUCTS = [
    {
        "name": "Wright's Silver Cream",
        "brand": "Wright's",
        "cat": "Specialty",
        "ings": ["Water", "Anhydrous aluminum silicate", "Quartz",
                 "Sodium carbonate", "Sodium palmitate", "Iron oxides",
                 "Acrylic polymer emulsion", "Tetrasodium EDTA",
                 "Silicone emulsion", "Methylisothiazolinone",
                 "Benzisothiazolinone"],
        "source": ("J.A. Wright's own published ingredient table for Wright's "
                   "Silver Cream (product codes 014, 317A, 369), read "
                   "2026-10-11. The table lists every ingredient with its CAS "
                   "number and function: Water (7732-18-5, Diluent), Anhydrous "
                   "aluminum silicate (66402-68-4, Polishing agent), Quartz "
                   "(14808-60-7, Polishing agent), Sodium carbonate (497-19-8, "
                   "Builder), Sodium palmitate (408-35-5, Cleaning agent), "
                   "Iron oxides (1309-37-1, Colorant), Acrylic polymer emulsion "
                   "(CAS withheld, Thickener), Tetrasodium EDTA (64-02-8, "
                   "Chelating agent), Silicone emulsion (CAS not available, "
                   "Processing aid), Methylisothiazolinone (2682-20-4, "
                   "Preservative) and Benzisothiazolinone (2634-33-5, "
                   "Preservative). Cross-checked against the Weiman Products "
                   "MSDS (issue date 2009-08-13), whose composition section "
                   "names microcrystalline silica (14808-60-7) and sodium "
                   "carbonate (497-19-8) and records the silica carcinogenicity "
                   "note (NTP: yes; IARC Group 1) with the qualifier that "
                   "respirable silica dust is not generated in use of the "
                   "paste. The label term 'Quartz' (CAS 14808-60-7, crystalline "
                   "silica) is aliased to the DB's existing 'Silica' key, which "
                   "is documented as the crystalline-silica key."),
        "source_url": WRIGHT_ING,
        "note": ("A full ingredient table with CAS numbers and functions, "
                 "published by the maker on its own site -- the first SILVER / "
                 "METAL POLISH in the corpus beyond a single brass polish, and "
                 "the first product here whose abrasive is crystalline silica. "
                 "The formula is a mild abrasive paste: water carried by "
                 "anhydrous aluminum silicate and quartz (the polishing "
                 "agents), built with sodium carbonate, bound with sodium "
                 "palmitate soap, coloured with iron oxides and thickened with "
                 "an acrylic polymer emulsion, chelated with tetrasodium EDTA "
                 "and preserved with the two isothiazolinone preservatives the "
                 "DB already carries (Methylisothiazolinone, "
                 "Benzisothiazolinone). The maker's own SDS states the product "
                 "is ammonia-free and Kosher approved, and gives the "
                 "crystalline-silica carcinogenicity flag with the note that "
                 "respirable dust is not generated in use. The two "
                 "isothiazolinone preservatives are the same pair the corpus "
                 "already flags as contact allergens; here they sit in a "
                 "rinse-off paste rather than a leave-on product. Ownership "
                 "lineage: J.A. Wright & Company (founded 1873, Keene, New "
                 "Hampshire) was acquired by Weiman Products, LLC in 2006; "
                 "Weiman Products renamed itself PurposeBuilt Brands in 2020, "
                 "and its SEC registration statement names Wright's among its "
                 "consumer specialty cleaning brands."),
        "owner": "PurposeBuilt Brands", "owner_ev": "verified",
        "owner_src": WRIGHT_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": "https://jawright.com/silver-cream",
        "tier_note": ("Sold at mass grocery, hardware and home-center "
                      "retailers and by the brand directly; recorded as mass. "
                      "Channel evidence is the brand's own retail placement, "
                      "not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A silver and metal polish in the mass channel."),
    },
    {
        "name": "Glisten Disposer Care",
        "brand": "Glisten",
        "cat": "Specialty",
        "ings": ["Malic acid", "Sodium lauryl sulfate",
                 "Sodium C14-16 olefin sulfonate", "Sodium xylene sulfonate",
                 "Alcohols, C10-16"],
        "source": ("Summit Brands' own SDS composition section for Glisten "
                   "Disposer Care (product DP06N-PB, a 4.9 oz powder packet), "
                   "read 2026-10-11, in two revisions. The 2021-02-08 revision "
                   "lists Malic Acid (6915-15-7) 15-40%, Sodium lauryl sulfate "
                   "(151-21-3) 7-13%, Sulfonic acids, alkyl, sodium salts "
                   "(68439-57-6) 7-13% and Alcohols, C10-16 (67762-41-8) "
                   "0.1-1%. The 2025-10-27 revision lists Malic acid 15-40%, "
                   "Sodium lauryl sulfate 10-30%, Sulfonic acids, C14-16-alkane "
                   "hydroxy and C14-16-alkene, sodium salts (68439-57-6) 5-10% "
                   "and Sodium xylene sulfonate (1300-72-7) 1-5%. The brand's "
                   "own product page describes the packet as a bleach-"
                   "alternative foaming cleaner, biodegradable and safe for "
                   "disposers, plumbing and septic systems."),
        "source_url": GLISTEN_SDS,
        "note": ("A full composition section, published by the maker in its own "
                 "SDS -- the first GARBAGE-DISPOSAL cleaner in the corpus. The "
                 "corpus already carried Glisten's dishwasher and washing-"
                 "machine cleaners, but nothing that cleans the disposer "
                 "itself. The formula is an acid cleaner, not a bleach one: "
                 "malic acid (a fruit acid) at 15-40% does the dissolving, "
                 "carried by two anionic surfactants (sodium lauryl sulfate and "
                 "a C14-16 olefin sulfonate) that foam the powder into the "
                 "disposal chamber, with sodium xylene sulfonate as the "
                 "hydrotrope and a trace C10-16 alcohol defoamer. The maker "
                 "markets it explicitly as a bleach alternative -- the "
                 "transatlantic read is that this is the kind of acid-based "
                 "descaler EU formulators reach for where a US brand might "
                 "reach for chlorine. Sodium xylene sulfonate and sodium lauryl "
                 "sulfate are both already in the corpus; malic acid, the "
                 "C10-16 alcohol cut and the C14-16 olefin sulfonate "
                 "(already minted 2026-10-09) complete the list. The two SDS "
                 "revisions disagree on the surfactant ranges (SLS 7-13% in "
                 "2021 vs 10-30% in 2025) and on the hydrotrope (absent in "
                 "2021, 1-5% in 2025); both are recorded in the source rather "
                 "than silently reconciled."),
        "owner": "Summit Brands", "owner_ev": "verified",
        "owner_src": GLISTEN_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": GLISTEN_OWNER_SRC,
        "tier_note": ("Sold through mass retailers, home centers and hardware "
                      "chains; recorded as mass. Channel evidence is the "
                      "brand's own retail placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A garbage-disposal cleaner in the mass channel."),
    },
    {
        "name": "affresh Coffee Maker Cleaner",
        "brand": "Affresh",
        "cat": "Specialty",
        "ings": ["Citric acid", "Sodium bisulfate", "Sodium carbonate",
                 "Sodium gluconate", "Sodium acetate", "Polyethylene glycol"],
        "source": ("Whirlpool Corporation's own SDS composition section for "
                   "affresh Coffee Maker Cleaner (product numbers W10511280, "
                   "W10511280B, W10355052, W10921672), revision 2025-12-30, "
                   "read 2026-10-11: Citric acid (77-92-9) 30-40%, Sodium "
                   "bisulfate (7681-38-1) 30-40%, Sodium carbonate (497-19-8) "
                   "10-18%, Sodium gluconate (527-07-1) 2-7%, Sodium acetate "
                   "(127-09-3) 2-7% and Polyethylene glycol (25322-68-3) 1-6%. "
                   "The SDS states that the product is registered with the US "
                   "EPA Safer Choice Program, which is why every component is "
                   "listed rather than only the hazardous ones."),
        "source_url": AFFRESH_SDS,
        "note": ("A full composition section, published by the maker in its own "
                 "SDS -- the first COFFEE-MAKER cleaner in the corpus, and the "
                 "first product here registered with the US EPA Safer Choice "
                 "Program. The formula is a two-acid tablet: citric acid and "
                 "sodium bisulfate together are the descaler that dissolves "
                 "coffee oils and hard-water scale, buffered by sodium "
                 "carbonate (which also drives the effervescence), with sodium "
                 "gluconate, sodium acetate and a low-grade polyethylene glycol "
                 "as tablet binders and processing aids. Nothing in the list is "
                 "a preservative, a fragrance or a surfactant -- it is the "
                 "cleanest formulation in the corpus by hazard count, which is "
                 "consistent with its Safer Choice registration. The corpus "
                 "already carried affresh's washer and dishwasher cleaners; "
                 "this completes the affresh appliance-care line and fills the "
                 "coffee-maker function the corpus had zero products for. "
                 "Ownership note: affresh is Whirlpool Corporation's own brand "
                 "(NYSE: WHR)."),
        "owner": "Whirlpool Corporation", "owner_ev": "verified",
        "owner_src": AFFRESH_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": "https://www.affresh.com/",
        "tier_note": ("Sold at mass retailers and appliance channels and by the "
                      "brand directly; recorded as mass. Channel evidence is "
                      "the brand's own retail placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A coffee-maker cleaner in the mass channel."),
    },
    {
        "name": "Zep Grout Cleaner & Brightener",
        "brand": "Zep",
        "cat": "Bathroom",
        "ings": ["Water", "Urea hydrochloride", "Hydrochloric acid",
                 "C9-11 Pareth-3", "Butoxyethanol",
                 "Quaternary ammonium compounds", "Methyl salicylate",
                 "Isopropanol", "Eugenol", "Diethyl phthalate", "Acetophenone",
                 "Isoeugenol"],
        "source": ("Zep Inc.'s own California Cleaning Product Right to Know "
                   "Act (SB-258) disclosure for Zep Grout Cleaner & Brightener "
                   "(material number ZU104632, revision 2019-12-02), read "
                   "2026-10-11, which lists every intentionally added "
                   "ingredient with its CAS number and function: Water "
                   "(7732-18-5), urea hydrochloride (506-89-8, Acid), "
                   "Hydrochloric Acid (7647-01-0, Acid), C9-11 Pareth-3 "
                   "(68439-46-3, Emulsifier), Butoxyethanol (111-76-2, "
                   "Solubilizer), quaternary ammonium compounds, coco "
                   "alkylbis(hydroxyethyl)methyl, ethoxylated, chlorides "
                   "(61791-10-4, Cleaning Agent), Methyl Salicylate (119-36-8, "
                   "Fragrance), Isopropanol (67-63-0, Solubilizer), Eugenol "
                   "(97-53-0, Fragrance), Diethyl Phthalate (84-66-2, "
                   "Fragrance), Acetophenone (98-86-2, Fragrance) and "
                   "Isoeugenol (97-54-1, Fragrance). Cross-checked against the "
                   "maker's own SDS (revision D054703), whose composition "
                   "section names urea hydrochloride 10-20%, hydrochloric acid "
                   "1-3% and the C9-11 alcohol ethoxylate 1-3% and classifies "
                   "the product Skin Corrosion 1 / Serious Eye Damage 1 "
                   "(H314)."),
        "source_url": ZEP_SB258,
        "note": ("A full SB-258 disclosure plus the maker's own SDS -- the first "
                 "GROUT cleaner in the corpus, and the most concentrated "
                 "fragrance load in it. The formula is an acid grout descaler: "
                 "urea hydrochloride at 10-20% (a urea-hydrochloric acid "
                 "adduct that keeps the acid less volatile than free HCl) plus "
                 "1-3% free hydrochloric acid dissolve the mineral haze and "
                 "soap scum in grout, carried by a C9-11 alcohol ethoxylate "
                 "emulsifier and a coco quaternary ammonium cleaning agent, "
                 "with butoxyethanol and isopropanol as solubilizers. The maker "
                 "classifies the product itself Skin Corrosion 1 / Serious Eye "
                 "Damage 1. Five fragrance components are disclosed by name -- "
                 "methyl salicylate, eugenol, diethyl phthalate, acetophenone "
                 "and isoeugenol -- which makes this product a useful test of "
                 "the corpus's fragrance-allergen coverage: eugenol, "
                 "isoeugenol and methyl salicylate are all already carried as "
                 "EU fragrance allergens, and diethyl phthalate and "
                 "acetophenone are minted this run. Diethyl phthalate is "
                 "recorded Not Classified because no GHS code reaches the 40% "
                 "consensus bar, but it is a phthalate and its regulatory "
                 "concern is a non-GHS endocrine matter -- flagged in the "
                 "ingredient note rather than invented as a grade. Ownership: "
                 "Zep Inc. is owned by Truelink Capital Management, LLC, the "
                 "same owner the corpus already carries for Zep's Green Link "
                 "line."),
        "owner": "Truelink Capital Management, LLC", "owner_ev": "reported",
        "owner_src": ZEP_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": ZEP_OWNER_SRC,
        "tier_note": ("Sold through home centers, hardware chains and mass "
                      "retailers; recorded as mass. Channel evidence is the "
                      "owner's own retail placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A grout cleaner in the mass channel."),
    },
]


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

    # Owner registry: no new owners this run. One existing owner gains a brand.
    # Wright's is attached to PurposeBuilt Brands (the record that already names
    # the brand in its detail text); the duplicate "Weiman Products, LLC" record
    # is left in place and flagged for the owner-dedupe lane.
    BRAND_ADDITIONS = {
        "PurposeBuilt Brands": "Wright's",
    }
    for name, brand in BRAND_ADDITIONS.items():
        rec = owners["owners"].get(name)
        if rec is None:
            print(f"WARN owner not found for brand addition: {name}")
            continue
        brands = rec.setdefault("brands", [])
        if brand in brands:
            print(f"brand already listed: {name} / {brand}")
            continue
        brands.append(brand)
        print(f"owner brand added: {name} / {brand}")

    for r in products:
        for k in r["ings"]:
            if k not in ingredients:
                raise SystemExit(f"record {r['name']!r} references missing key {k!r}")

    if added and not NO_CHANGELOG:
        changelog.insert(0, {
            "date": TODAY,
            "text": ("Gather lane: 4 products added from manufacturer "
                     "disclosures read 2026-10-11, each filling a function the "
                     "corpus did not carry at all -- Wright's Silver Cream "
                     "(J.A. Wright's own ingredient table with CAS and "
                     "function, jawright.com), the first SILVER/METAL POLISH "
                     "beyond a single brass polish and the first product whose "
                     "abrasive is crystalline silica (the label term 'Quartz', "
                     "CAS 14808-60-7, aliased to the DB's existing 'Silica' "
                     "key); Glisten Disposer Care (Summit Brands' own SDS "
                     "composition, two revisions), the first GARBAGE-DISPOSAL "
                     "cleaner, an acid (malic-acid) bleach alternative rather "
                     "than a chlorine one; affresh Coffee Maker Cleaner "
                     "(Whirlpool's own SDS, revision 2025-12-30), the first "
                     "COFFEE-MAKER cleaner and the first product in the corpus "
                     "registered with the US EPA Safer Choice Program; and Zep "
                     "Grout Cleaner & Brightener (Zep's own California SB-258 "
                     "disclosure plus its SDS), the first GROUT cleaner and the "
                     "most concentrated disclosed fragrance load in the corpus "
                     "(five named fragrance components). Eleven new ingredient "
                     "keys: three graded (Malic Acid, CID 525, H319 89.2% / "
                     "H315 74.2% -> derm C; Sodium Bisulfate, CID 516919, H318 "
                     "99.6% -> derm D; Urea Hydrochloride, CID 101721, H335 "
                     "81% / H315 52.4% / H290 47.6% / H319 42.9% -> derm D, "
                     "resp C; Acetophenone, CID 7410, H302 >99.9% / H319 99.9% "
                     "-> derm C) and seven recorded Not Classified with an "
                     "explicit sourcing note (three resolve to no PubChem CID "
                     "at all -- Anhydrous aluminum silicate, Alcohols C10-16, "
                     "C9-11 Pareth-3 and the quaternary ammonium mixture are "
                     "UVCBs; Acrylic polymer emulsion has its CAS withheld by "
                     "the maker; Iron oxides and Diethyl Phthalate have only "
                     "sub-40% headline codes, with their sub-consensus codes "
                     "stated rather than graded). Three label terms were "
                     "ALIASED to existing keys rather than re-minted (Quartz -> "
                     "Silica; Butoxyethanol -> Butyloxyethanol; Sodium xylene "
                     "sulfonate -> Sodium Xylenesulfonate). One owner brand "
                     "added: Wright's under PurposeBuilt Brands. OWNER-REGISTRY "
                     "FINDING: the registry carries BOTH 'PurposeBuilt Brands' "
                     "(verified, SEC-sourced, detail text already naming Weiman "
                     "/ Goo Gone / Wright's) and a separate 'Weiman Products, "
                     "LLC' record minted 2026-10-10 that names no parent -- the "
                     "same Gurnee, Illinois company, which renamed itself "
                     "PurposeBuilt Brands in 2020. Wright's is attached to "
                     "PurposeBuilt Brands; the duplicate Weiman Products, LLC "
                     "record is flagged for the owner-dedupe lane rather than "
                     "deleted here."),
        })

    if DRY:
        print(f"\nDRY RUN: would add {added} products, "
              f"{len(added_keys)} ingredient keys.")
        return

    dump(os.path.join(DATA, "products.json"), products, 1)
    dump(os.path.join(DATA, "ingredients.json"), ingredients, 1)
    dump(os.path.join(DATA, "owners.json"), owners, 1)
    dump(os.path.join(DATA, "changelog.json"), changelog, 2)
    print(f"\nwrote {added} products, {len(added_keys)} new ingredient keys.")


if __name__ == "__main__":
    main()
