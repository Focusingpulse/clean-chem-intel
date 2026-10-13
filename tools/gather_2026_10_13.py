#!/usr/bin/env python3
"""Daily gather (2026-10-13, 10:00Z maintenance lane): four products that were
missing from the database, the ingredient records they need, one owner record,
and one regulatory-watch entry.

Each of the four fills a FUNCTION the corpus did not carry, and each ingredient
list below is the maker's own published disclosure (or the maker's own SDS
composition section), read 2026-10-13.

Sources read on 2026-10-13:

  - Lestoil Heavy Duty Multi-Purpose Cleaner. The Clorox Company's own
    California Cleaning Product Right to Know Act (SB-258) disclosure, served
    through Clorox's SmartLabel page for the 48 fl oz and 28 fl oz sizes (both
    carry the identical list), cross-checked against Clorox's own SDS
    composition section (product CLO33910), which quantifies the four
    hazardous components.
    https://smartlabel.labelinsight.com/product/6115464/ingredients
    https://smartlabel.labelinsight.com/product/6115457/ingredients
    https://content.oppictures.com/Master_Images/Master_PDF_Files/CLO33910_SDS.PDF
  - Lemi Shine Dish Detergent Booster. The maker's own ingredient page, which
    publishes a per-product table with CAS numbers for every Lemi Shine
    formula. The Booster is EPA Safer Choice certified.
    https://lemishine.com/pages/ingredients
  - DampRid Fragrance Free Moisture Absorber. W.M. Barr's own SDS composition
    section (product codes FG44/FG45/FG46/FG47 and the FG01K refill), which
    quantifies calcium chloride and the two minor salts.
    https://damprid.com/wp-content/uploads/2020/07/DampRid-Lo-Profile-Fragrance-and-Fragrance-Free-SDS-09-24-18.pdf
    https://damprid.com/wp-content/uploads/2017/07/DR_Moisture_Absorber_SDS-FG01K.pdf
  - Ozium Air Sanitizer Spray, Original. Niteo Products' own SDS composition
    section (product OZ-1, EPA Reg. No. 51838-2), plus the CARB settlement
    agreement that is the regulatory-watch entry this run.
    https://eunoffgsnusqmqgzpigj.supabase.co/storage/v1/object/public/product-media/sds/ozium-air-sanitizer-original.pdf
    https://ww2.arb.ca.gov/sites/default/files/2023-12/niteo_products_llc_sa.pdf

Why these four. The corpus is deep in the bleach / bathroom / disinfectant
cluster and in the mass laundry aisle, and it is thin in the two things a
transparency engine should be best at: the solvent-heavy "heavy duty" shelf and
the aerosol air-care shelf. Lestoil is the classic dilutable petroleum-solvent
cleaner and carries the largest disclosed aromatic load in the corpus (toluene,
ethylbenzene, naphthalene, trimethylbenzene, nonane, Stoddard-type light
aromatic hydrocarbons); Ozium is an EPA-registered air SANITIZER whose own SDS
is 30-50% isopropanol plus 20-30% liquefied petroleum gas, and it is the subject
of a real US enforcement action. DampRid adds a function with zero products
(indoor humidity control) and Lemi Shine Booster adds the dishwasher-booster
function to a brand the corpus already carries.

Grading method (stated because it is not the raw tool output). The house rule
is the strict >=40% ECHA C&L notifier consensus, applied via
tools/grade_batch.py. The tool's headline field concatenates every strong code
without de-duplicating across notifier blocks, so the headline below is the
de-duplicated set: codes at >=40% notifier consensus, UNION the EU harmonized
classification codes when PubChem lists them in a leading block without
percentages. Dimension grades use the database's existing mapping (H314 -> derm
F, H318/H317 -> derm D, H315/H319 -> derm C, H332/H335/H336 -> resp C, H373 ->
organ C, H351 -> canc C, H361 -> repro C, H400 -> env F, H410/H411 -> env D).
Every CID below was checked against the returned title before the record was
accepted; one name lookup was REJECTED for returning a different compound (see
the 'Caramel' note).

Ownership note. Two owner records gain a brand (Clorox gains Lestoil; NiTEO
Products gains Ozium) and one owner record is minted (W.M. Barr, the DampRid
maker, which the registry did not carry).
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-13"

DRY = "--dry-run" in sys.argv
NO_CHANGELOG = "--no-changelog" in sys.argv

LESTOIL_SMARTLABEL = "https://smartlabel.labelinsight.com/product/6115464/ingredients"
LESTOIL_SDS = ("https://content.oppictures.com/Master_Images/Master_PDF_Files/"
               "CLO33910_SDS.PDF")
LEMISHINE_ING = "https://lemishine.com/pages/ingredients"
DAMPRID_SDS = ("https://damprid.com/wp-content/uploads/2020/07/"
               "DampRid-Lo-Profile-Fragrance-and-Fragrance-Free-SDS-09-24-18.pdf")
DAMPRID_SDS2 = ("https://damprid.com/wp-content/uploads/2017/07/"
                "DR_Moisture_Absorber_SDS-FG01K.pdf")
DAMPRID_OWNER_SRC = "https://damprid.com/about-wm-barr/"
OZIUM_SDS = ("https://eunoffgsnusqmqgzpigj.supabase.co/storage/v1/object/public/"
             "product-media/sds/ozium-air-sanitizer-original.pdf")
OZIUM_OWNER_SRC = ("https://highlander-partners.com/news-posts/niteo-products-a-"
                   "portfolio-company-of-highlander-partners-acquires-air-care-"
                   "assets-including-the-ozium-and-scents-brands-from-kraco/")
CARB_SETTLEMENT = ("https://ww2.arb.ca.gov/sites/default/files/2023-12/"
                   "niteo_products_llc_sa.pdf")

# --------------------------------------------------------------------------
# New ingredient keys. Grades are the de-duplicated >=40% ECHA consensus set
# (see the module docstring for the method).
# --------------------------------------------------------------------------
NEW_KEYS = {
    "Light Aromatic Hydrocarbons": {
        "ev": "Low",
        "g": "Not Classified",
        "gr": {},
        "impacts": [],
        "note": (
            "UVCB petroleum distillate (the Stoddard-solvent stream, CAS "
            "8052-41-3). PubChem PUG REST returns 404 for both the descriptive "
            "name and the CAS, so there is no discrete record to grade and no "
            "grade is assigned. Recorded unclassified per the UVCB convention "
            "already used here for 'Petroleum Distillates, Hydrotreated Light' "
            "and 'Distillates (petroleum), hydrotreated middle' -- this is NOT "
            "a finding that the substance is non-hazardous. The maker's own SDS "
            "for this product lists it as one of the formula's hazardous "
            "components (3-7% by weight). Disclosed by Clorox on its California "
            "SB-258 SmartLabel page for Lestoil as 'Light Aromatic "
            "Hydrocarbons'."),
        "s": ("Petroleum distillate (Stoddard-solvent type). No discrete "
              "PubChem record; not graded."),
        "added": TODAY,
    },
    "Sodium Linoleate": {
        "ev": "High",
        "g": "H315",
        "gr": {"derm": "C"},
        "impacts": ["derm"],
        "note": (
            "Graded from PubChem GHS (CID 23676150, returned title 'Sodium "
            "Linoleate'; the returned title was confirmed against the intended "
            "substance before the record was accepted). Headline ECHA C&L "
            "notifier consensus: H315 (causes skin irritation) 100% -> derm C. "
            "Disclosed by Clorox on its California SB-258 SmartLabel page for "
            "Lestoil as 'Sodium Linoleate'."),
        "s": ("Soap salt (sodium salt of linoleic acid); skin irritant."),
        "added": TODAY,
    },
    "Trimethylpentanediol": {
        "ev": "High",
        "g": "H319,H335",
        "gr": {"derm": "C", "resp": "C"},
        "impacts": ["derm", "resp"],
        "note": (
            "Graded from PubChem GHS (CID 8946, returned title "
            "'2,2,4-Trimethyl-1,3-pentanediol'; the returned title was "
            "confirmed against the intended substance before the record was "
            "accepted). ECHA C&L notifier consensus: H319 (serious eye "
            "irritation) 96.3% -> derm C; H335 (may cause respiratory "
            "irritation) 59.4% -> resp C. H302 (18.4%) and H315 (17.2%) sit "
            "below the 40% house bar and are not graded. Disclosed by Clorox on "
            "its California SB-258 SmartLabel page for Lestoil as "
            "'Trimethylpentanediol'."),
        "s": ("2,2,4-Trimethyl-1,3-pentanediol; eye and respiratory irritant."),
        "added": TODAY,
    },
    "Nonane": {
        "ev": "High",
        "g": "H336,H319,H315,H304,H226",
        "gr": {"derm": "C", "resp": "C"},
        "impacts": ["derm", "resp"],
        "note": (
            "Graded from PubChem GHS (CID 8141, returned title 'Nonane'; the "
            "returned title was confirmed against the intended substance before "
            "the record was accepted). ECHA C&L notifier consensus: H226 "
            "(flammable liquid) 65.8%, H304 (may be fatal if swallowed and "
            "enters airways) 65.3%, H315 (skin irritation) 55% -> derm C, H319 "
            "(serious eye irritation) 53.4% -> derm C, H336 (may cause "
            "drowsiness or dizziness) 55.3% -> resp C. The aquatic codes sit "
            "below the house bar (H410 31%, H400 22.2%, H411 13.4%) and are not "
            "graded. Disclosed by Clorox on its California SB-258 SmartLabel "
            "page for Lestoil as 'Nonane'."),
        "s": ("Straight-chain C9 alkane; flammable, aspiration hazard, skin and "
              "eye irritant, causes drowsiness."),
        "added": TODAY,
    },
    "Trimethylbenzene": {
        "ev": "Medium",
        "g": "H319,H315,H312,H302,H226",
        "gr": {"derm": "C"},
        "impacts": ["derm"],
        "note": (
            "The maker discloses the label term 'Trimethylbenzene' with no "
            "isomer. PubChem's name lookup for 'Trimethylbenzene' resolves to "
            "the 1,2,3-isomer (CID 10686, returned title '1,2,3-"
            "Trimethylbenzene'), which is the record graded here; the "
            "1,2,4-isomer (CID 7247, the most common commercial isomer) was "
            "cross-checked and agrees on the irritancy codes (H315, H319). "
            "Because the grade is taken from one isomer of a mixed-isomer "
            "label term, confidence is recorded as Medium rather than High. "
            "ECHA C&L notifier consensus for CID 10686: H226 (flammable) 96.1%, "
            "H315 (skin irritation) 91.7% -> derm C, H319 (serious eye "
            "irritation) 81.5% -> derm C, H312 (harmful in contact with skin) "
            "77.8%, H302 (harmful if swallowed) 66.4%. H335 (35.7%) and H332 "
            "(28.5%) sit below the 40% house bar and are not graded. Disclosed "
            "by Clorox on its California SB-258 SmartLabel page for Lestoil as "
            "'Trimethylbenzene'."),
        "s": ("Mixed trimethylbenzene isomers; flammable, skin and eye "
              "irritant."),
        "added": TODAY,
    },
    "Toluene": {
        "ev": "High",
        "g": "H373,H361,H336,H315,H304,H225",
        "gr": {"derm": "C", "resp": "C", "organ": "C", "repro": "C"},
        "impacts": ["derm", "repro", "resp"],
        "note": (
            "Graded from PubChem GHS (CID 1140, returned title 'Toluene'; the "
            "returned title was confirmed against the intended substance before "
            "the record was accepted). ECHA C&L notifier consensus and the EU "
            "harmonized classification agree: H225 (highly flammable) 98.5-"
            "100%, H304 (may be fatal if swallowed and enters airways) 99.8-"
            "100%, H315 (skin irritation) 98.5-100% -> derm C, H336 (may cause "
            "drowsiness or dizziness) 98.3-100% -> resp C, H361 (suspected of "
            "damaging fertility or the unborn child) 95.3-100% -> repro C, H373 "
            "(may cause damage to organs through prolonged or repeated "
            "exposure) 98.4-100% -> organ C. H412 (16.5%) sits below the house "
            "bar and is not graded. Disclosed by Clorox on its California "
            "SB-258 SmartLabel page for Lestoil as 'Toluene' and flagged there "
            "with the SB-258 designated-list marker."),
        "s": ("Aromatic solvent. Flammable, aspiration hazard, reproductive "
              "toxicant, organ toxicant on repeated exposure."),
        "added": TODAY,
    },
    "Ethylbenzene": {
        "ev": "High",
        "g": "H373,H332,H304,H225",
        "gr": {"derm": "C", "resp": "C", "organ": "C"},
        "impacts": ["derm", "resp"],
        "note": (
            "Graded from PubChem GHS (CID 7500, returned title 'Ethylbenzene'; "
            "the returned title was confirmed against the intended substance "
            "before the record was accepted). Headline ECHA C&L notifier "
            "consensus: H225 (highly flammable) >99.9%, H332 (harmful if "
            "inhaled) 99.9% -> resp C; the EU harmonized classification adds "
            "H304 (aspiration hazard) and H373 (organ damage on prolonged or "
            "repeated exposure) -> organ C. H304 (17.3%) and H373 (17.2%) sit "
            "below the 40% notifier bar on their own and are carried here from "
            "the harmonized classification, which is stated in the note rather "
            "than silently folded in. Disclosed by Clorox on its California "
            "SB-258 SmartLabel page for Lestoil as 'Ethylbenzene' and flagged "
            "there with the SB-258 designated-list marker."),
        "s": ("Aromatic solvent. Flammable, harmful if inhaled, aspiration "
              "hazard, organ toxicant on repeated exposure."),
        "added": TODAY,
    },
    "Naphthalene": {
        "ev": "High",
        "g": "H410,H400,H351,H302",
        "gr": {"canc": "C", "env": "F"},
        "impacts": ["canc", "aqua"],
        "note": (
            "Graded from PubChem GHS (CID 931, returned title 'Naphthalene'; "
            "the returned title was confirmed against the intended substance "
            "before the record was accepted). ECHA C&L notifier consensus and "
            "the EU harmonized classification agree: H302 (harmful if "
            "swallowed) 99.8%, H351 (suspected of causing cancer) 98.9% -> canc "
            "C, H400 (very toxic to aquatic life) 99.6% -> env F, H410 (very "
            "toxic to aquatic life with long lasting effects) 99.9% -> env F. "
            "H228 (flammable solid, 38.8%) sits below the 40% house bar and is "
            "not graded. Disclosed by Clorox on its California SB-258 "
            "SmartLabel page for Lestoil as 'Naphthalene' and flagged there "
            "with the SB-258 designated-list marker."),
        "s": ("Mothball chemistry. Suspected carcinogen; very toxic to aquatic "
              "life."),
        "added": TODAY,
    },
    "Caramel": {
        "ev": "Low",
        "g": "Not Classified",
        "gr": {},
        "impacts": [],
        "note": (
            "Colorant. PubChem's name lookup for 'Caramel' resolves to CID "
            "61634, whose returned title is '3,5-Dimethyl-1,2-cyclopentanedione' "
            "-- a DIFFERENT compound (a flavour substance), not caramel colour. "
            "That lookup was rejected rather than accepted, which is exactly "
            "the failure mode the house rule warns about. Caramel colour is a "
            "UVCB (CAS 8028-89-5) and PubChem PUG REST returns 404 for the CAS, "
            "so there is no discrete record to grade and no grade is assigned. "
            "Recorded unclassified rather than guessed. Disclosed by Clorox on "
            "its California SB-258 SmartLabel page for Lestoil as 'Caramel'."),
        "s": "Caramel colourant (UVCB). No discrete PubChem record; not graded.",
        "added": TODAY,
    },
    "1,1-Difluoroethane": {
        "ev": "High",
        "g": "H280,H220",
        "gr": {},
        "impacts": [],
        "note": (
            "Graded from PubChem GHS (CID 6368, returned title "
            "'1,1-Difluoroethane'; the returned title was confirmed against the "
            "intended substance before the record was accepted). ECHA C&L "
            "notifier consensus: H220 (extremely flammable gas) 95% -> physical "
            "hazard only; H280 (contains gas under pressure) 77.9%. No health "
            "dimension grade applies to the propellant itself. Disclosed by "
            "Niteo Products in the SDS composition section for Ozium Air "
            "Sanitizer Spray Original (>=5% to <10%)."),
        "s": ("HFC-152a aerosol propellant. Extremely flammable gas; no health "
              "hazard grade."),
        "added": TODAY,
    },
    "Cymbopogon Schoenanthus Oil": {
        "ev": "Extrapolated",
        "g": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": (
            "Lemongrass oil (CAS 8007-02-1). PubChem PUG REST returns 404 for "
            "the botanical name, the INCI name and the CAS, so there is no "
            "direct GHS record; the entry is extrapolated from the "
            "essential-oil class in this database, which carries "
            "skin-sensitization grades (H315/H317, derm C-D) across its "
            "members, not graded directly. Flagged for verification rather than "
            "assigned a sourced grade. Disclosed by Niteo Products in the SDS "
            "composition section for Ozium Air Sanitizer Spray Original "
            "(0.1-1%)."),
        "s": ("Lemongrass oil (essential-oil class). No direct PubChem record; "
              "extrapolated, not graded directly."),
        "added": TODAY,
    },
}

# Label terms that name a substance the database already carries. Aliasing
# instead of re-minting keeps one key per substance.
ALIASES = {
    "C10-12 Alcohol Ethoxylates": "Alcohol Ethoxylate",
    "Orange, sweet, ext.": "Orange Oil",
    "Petroleum gases, liquefied, sweetened": "Liquefied Petroleum Gas",
    "d-Limonene": "Limonene",
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
            "gap rather than estimated. " + cat_note),
    }


# --------------------------------------------------------------------------
# Products. Every ingredient list below is the maker's own published list or
# the maker's own SDS composition section, read 2026-10-13.
# --------------------------------------------------------------------------
PRODUCTS = [
    {
        "name": "Lestoil Heavy Duty Multi-Purpose Cleaner",
        "brand": "Lestoil",
        "cat": "Specialty",
        "ings": ["Water", "Sodium Tallate", "Light Aromatic Hydrocarbons",
                 "Sodium Linoleate", "Sodium Oleate",
                 "C10-12 Alcohol Ethoxylates", "Trimethylpentanediol",
                 "Xanthan Gum", "Nonane", "Trimethylbenzene",
                 "Sodium Hydroxide", "Tetrapotassium EDTA", "Sodium Chloride",
                 "Toluene", "Ethylbenzene", "Naphthalene", "Caramel",
                 "Fragrance", "Pine Essential Oil", "d-Limonene", "Myrcene"],
        "source": (
            "The Clorox Company's own California Cleaning Product Right to Know "
            "Act (SB-258) disclosure for Lestoil Heavy Duty Multi-Purpose "
            "Cleaner, served through Clorox's SmartLabel pages for the 48 fl oz "
            "(044600339160) and 28 fl oz (044600339108) sizes, read 2026-10-13; "
            "both sizes carry the identical list. The page states that "
            "ingredients appearing on an SB-258 designated list or on Annex III "
            "of the EU Cosmetics Regulation are marked with the DL symbol, and "
            "the marked entries here are Light Aromatic Hydrocarbons, "
            "Trimethylbenzene, Sodium Hydroxide, Toluene, Ethylbenzene, "
            "Naphthalene, d-Limonene and Myrcene. Cross-checked against "
            "Clorox's own SDS composition section (product CLO33910), which "
            "quantifies the four components it treats as hazardous: Tall oil "
            "fatty acids, sodium salts (61790-45-2) 5-10%, Stoddard solvent "
            "(8052-41-3) 3-7%, Pine oil (8002-09-3) 1-5% and Sodium hydroxide "
            "(1310-73-2) 0.1-1%, with exact percentages withheld as trade "
            "secret. The SmartLabel term 'Light Aromatic Hydrocarbons' is the "
            "same petroleum stream the SDS calls 'Stoddard solvent'; the "
            "SmartLabel term is the one recorded, with the CAS in the "
            "ingredient note. The Canadian SDS from Clorox Company of Canada "
            "carries the same four-component composition block and adds the "
            "GHS classification Skin Irrit. 3 / Eye Irrit. 2A / Muta. 1B for "
            "the mixture as sold."),
        "source_url": LESTOIL_SMARTLABEL,
        "note": (
            "A dilutable heavy-duty cleaner built on a pine-oil soap and a "
            "petroleum solvent, and the largest disclosed aromatic load in the "
            "corpus. The cleaning system is sodium tallate (a tall-oil soap) "
            "with sodium linoleate and sodium oleate, carried by light aromatic "
            "hydrocarbons (the Stoddard-solvent stream) and boosted by C10-12 "
            "alcohol ethoxylates; pine essential oil and its terpenes "
            "(d-limonene, myrcene) supply the scent, and the formula is "
            "stabilised with xanthan gum, trimethylpentanediol, tetrapotassium "
            "EDTA and sodium hydroxide, coloured with caramel, and preserved "
            "with fragrance chemistry. What makes the record worth carrying is "
            "the tail: the disclosure names toluene, ethylbenzene and "
            "naphthalene as intentionally added components, all three flagged "
            "on California's SB-258 designated list, and the SDS quantifies "
            "the Stoddard solvent at 3-7% of the formula. Those three "
            "substances are also the reason the owner registry matters here -- "
            "this is a Clorox product, and the same company sells the "
            "chlorine-bleach shelf."),
        "owner": "Clorox", "owner_ev": "verified",
        "owner_src": "https://www.thecloroxcompany.com/brands/",
        "tier": "mass", "tier_ev": "reported",
        "tier_src": "https://www.lestoil.com/",
        "tier_note": (
            "Sold at mass grocery, hardware and home-center retailers; "
            "recorded as mass. Channel evidence is the brand's own retail "
            "placement, not a per-SKU page."),
        "substitutes": [],
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A dilutable heavy-duty cleaner in the mass channel."),
    },
    {
        "name": "Lemi Shine Dish Detergent Booster",
        "brand": "Lemi Shine",
        "cat": "Dishwasher",
        "ings": ["Citric Acid", "Fragrance"],
        "source": (
            "The maker's own ingredient page, read 2026-10-13, which publishes "
            "a separate table per Lemi Shine formula with ingredient, "
            "description and CAS number. The Booster table lists CITRIC ACID "
            "(77-92-9) and FRAGRANCE (CAS withheld as proprietary), and states "
            "that the fragrance's sensitizer components are Citral "
            "(5392-40-5), D-Limonene (5989-27-5) and benzyl benzoate "
            "(120-51-4). The same page lists the Booster among the products "
            "currently certified under the US EPA Safer Choice program, and "
            "carries the EPA's own disclaimer that the certification rests on "
            "the company's representations rather than on EPA analysis."),
        "source_url": LEMISHINE_ING,
        "note": (
            "A single-active dishwasher booster: citric acid, which chelates "
            "the hard-water calcium that causes spotting and filming, plus a "
            "fragrance. It is the shortest disclosed formula in the corpus, and "
            "that is the point of carrying it -- the product is sold on the "
            "strength of its ingredient list, and the list is two lines. The "
            "fragrance is the only part of the formula that is not fully "
            "specified: the maker names its three sensitizer components but "
            "withholds the rest of the blend as proprietary, so the record "
            "carries the database's generic Fragrance entry and the named "
            "sensitizers are visible through the Citral and Limonene records "
            "that other products in the corpus already reference. The brand "
            "already appears in the corpus through its dishwasher pods; this "
            "adds the booster, which is the product the brand was built on."),
        "owner": "AlEn USA", "owner_ev": "reported",
        "owner_src": "https://lemishine.com/pages/our-story",
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": "https://lemishine.com/pages/ingredients",
        "tier_note": (
            "Sold at grocery, mass and online retailers; recorded as grocery. "
            "Channel evidence is the brand's own retail placement, not a "
            "per-SKU page."),
        "substitutes": [],
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A dishwasher booster in the grocery channel."),
    },
    {
        "name": "DampRid Fragrance Free Moisture Absorber",
        "brand": "DampRid",
        "cat": "Specialty",
        "ings": ["Calcium Chloride", "Sodium Chloride", "Potassium Chloride"],
        "source": (
            "W.M. Barr's own SDS composition section for DampRid Moisture "
            "Absorbers, read 2026-10-13, in two revisions. The fragrance-free "
            "moisture-absorber SDS (product codes FG60LVW, FG83LVW, FG8360WS, "
            "FG84HDWS, FG301, FG80FFAZ, FG50FSMTL, FG6030FSMTL, FG83HDWS) "
            "gives Calcium chloride (10043-52-4) 70.0-100.0%, Sodium chloride "
            "(7647-14-5) <3.0% and Potassium chloride (7447-40-7) <3.0%, with "
            "the note that specific concentration may vary. The Lo-Profile "
            "fragrance and fragrance-free SDS (FG44, FG45, FG46, FG47, "
            "FG4445, FG4445CC, FG44HDWS, FG45W, FG46W) gives Calcium chloride "
            "50.0-70.0%, Starch (9005-25-8) 10.0-30.0%, Urea (57-13-6) <5.0%, "
            "Sodium chloride <3.0% and Potassium chloride <3.0%. The three "
            "components common to both revisions are the ones recorded here; "
            "the Lo-Profile variant's starch and urea are noted as a "
            "variant-specific difference rather than folded into the record."),
        "source_url": DAMPRID_SDS,
        "note": (
            "A moisture absorber, not a cleaner: calcium chloride draws water "
            "vapour out of the air and the two minor salts (sodium and "
            "potassium chloride) come with it. It is carried because it fills "
            "a function the corpus had zero products for -- indoor humidity "
            "control -- and because it is the clearest case in the corpus of a "
            "product whose hazard is physical rather than chemical: calcium "
            "chloride is a severe eye irritant (the database's own Calcium "
            "Chloride record is graded derm C on H319 at 99.7% notifier "
            "consensus) and its dissolution is strongly exothermic, which is "
            "why the maker's label warns against contact with eyes and skin. "
            "The maker's SDS also flags calcium chloride as an AOEC asthmagen "
            "in the refill product's ingredient table. Nothing here is a "
            "cleaning active, so the record carries no substitute links. The "
            "Lo-Profile variant adds starch and urea; both are recorded as "
            "variant differences in the source field rather than as separate "
            "products, because the maker publishes one SDS covering both."),
        "owner": "W.M. Barr", "owner_ev": "verified",
        "owner_src": DAMPRID_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": "https://damprid.com/",
        "tier_note": (
            "Sold at mass grocery, hardware and home-center retailers; "
            "recorded as mass. Channel evidence is the brand's own retail "
            "placement, not a per-SKU page."),
        "substitutes": [],
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A household moisture absorber in the mass channel."),
    },
    {
        "name": "Ozium Air Sanitizer Spray, Original",
        "brand": "Ozium",
        "cat": "Specialty",
        "ings": ["Isopropanol", "Petroleum gases, liquefied, sweetened",
                 "1,1-Difluoroethane", "Propylene Glycol", "Citral",
                 "Orange, sweet, ext.", "Cymbopogon Schoenanthus Oil"],
        "source": (
            "Niteo Products' own SDS composition section for Ozium Air "
            "Sanitizer Spray Original (product code OZ-1, AC OZIUM .8OZ ORIG "
            "48/6), read 2026-10-13. The SDS gives the hazardous components as "
            "Isopropanol (67-63-0) >=30 to <50%, Petroleum gases, liquefied, "
            "sweetened (68476-86-8) >=20 to <30%, 1,1-Difluoroethane (75-37-6) "
            ">=5 to <10%, Propylene glycol (57-55-6) >=1 to <5%, Citral "
            "(5392-40-5) >=0.1 to <1%, Orange, sweet, ext. (8028-48-6) >=0.1 to "
            "<1% and Cymbopogon schoenanthus oil (8007-02-1) >=0.1 to <1%, with "
            "the note that ranges protect confidentiality or reflect batch "
            "variation. The product is an EPA-registered sanitizer, EPA Reg. "
            "No. 51838-2, and the SDS classifies it as a flammable aerosol "
            "that causes serious eye irritation, may cause allergic skin "
            "reaction and may cause drowsiness or dizziness."),
        "source_url": OZIUM_SDS,
        "note": (
            "An EPA-registered air sanitizer, and the corpus's first product "
            "whose own SDS is mostly propellant and alcohol by weight: "
            "isopropanol at 30-50% and liquefied petroleum gas at 20-30% "
            "together account for well over half the can. The two fragrance "
            "components (sweet orange extract and lemongrass oil) sit at "
            "0.1-1% each, and the label term 'Petroleum gases, liquefied, "
            "sweetened' is aliased to the database's existing 'Liquefied "
            "Petroleum Gas' key rather than re-minted. The record is worth "
            "carrying for a second reason: this product has a real US "
            "enforcement history. The California Air Resources Board settled "
            "with Niteo Products over Ozium Air Sanitizer exceeding the state's "
            "20% by weight VOC limit for the air-freshener (double phase "
            "aerosol) category, a $160,000 penalty premised on 13.32 tons of "
            "excess VOC emissions, with the company reformulating to comply. "
            "That settlement is recorded as this run's regulatory-watch entry."),
        "owner": "NiTEO Products, LLC", "owner_ev": "verified",
        "owner_src": OZIUM_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": "https://www.ozium.com/",
        "tier_note": (
            "Sold at grocery, mass, convenience, hardware and automotive "
            "retailers; recorded as mass. Channel evidence is the acquirer's "
            "own statement of the brand's retail channels, not a per-SKU page."),
        "substitutes": [],
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("An aerosol air sanitizer in the mass channel."),
    },
]

BRAND_ADDITIONS = {
    "Clorox": "Lestoil",
    "NiTEO Products, LLC": "Ozium",
}

NEW_OWNERS = {
    "W.M. Barr": {
        "type": "private, employee-owned (ESOP)",
        "detail": (
            "Memphis, Tennessee. Founded 1946 by William M. Barr and sold to "
            "its employees in 1996; the company's own 'About WM Barr' page "
            "names DampRid as one of its brands and describes it as the "
            "largest national manufacturer of solvents, removers, fuels, and "
            "cleaning and surface prep products. The maker's own SDS for "
            "DampRid names W. M. Barr, 2105 Channel Avenue, Memphis, TN as the "
            "company. Recorded at verified: the evidence is the maker's own "
            "corporate and SDS pages, not a register or a corporate filing."),
        "ev": "verified",
        "src": DAMPRID_OWNER_SRC,
        "brands": ["DampRid"],
    },
}

# Regulatory watch: a US state enforcement action, which is the one US rule
# that directly caps the volatile load of an aerosol air care product.
WATCHLIST_ENTRY = {
    "name": "Air freshener VOCs (CARB)",
    "region": "us",
    "status": "enforced",
    "since": "2023",
    "rule": (
        "California's consumer-products regulation caps air fresheners in the "
        "'double phase aerosol' category at 20 percent VOC by weight (17 CCR "
        "94509(a)). CARB settled with Niteo Products in 2023 over Ozium Air "
        "Sanitizer exceeding that limit -- a $160,000 penalty premised on 13.32 "
        "tons of excess VOC emissions, with the company modifying the product "
        "to comply. There is no federal equivalent: the US caps VOCs in "
        "consumer products only through state rules, of which California's is "
        "the strictest and the most actively enforced."),
    "reason": (
        "Aerosol air fresheners and sanitizers are mostly propellant and "
        "alcohol by weight -- Ozium's own SDS is 30-50% isopropanol plus 20-30% "
        "liquefied petroleum gas -- so the VOC cap is the one rule that "
        "directly limits that load, and it is enforced against the product "
        "rather than against a named ingredient. Carried because the corpus "
        "now holds the product the action was taken against."),
    "src": CARB_SETTLEMENT,
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


def main():
    products = load(os.path.join(DATA, "products.json"))
    ingredients = load(os.path.join(DATA, "ingredients.json"))
    owners = load(os.path.join(DATA, "owners.json"))
    changelog = load(os.path.join(DATA, "changelog.json"))
    reg = load(os.path.join(DATA, "reg.json"))

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

    for name, rec in NEW_OWNERS.items():
        if name in owners["owners"]:
            print(f"owner already present, not re-minting: {name}")
            continue
        owners["owners"][name] = rec
        print(f"new owner: {name}")

    watch_names = {w.get("name") for w in reg["watchlist"]}
    if WATCHLIST_ENTRY["name"] in watch_names:
        print(f"watchlist entry already present: {WATCHLIST_ENTRY['name']}")
    else:
        reg["watchlist"].append(WATCHLIST_ENTRY)
        print(f"watchlist entry added: {WATCHLIST_ENTRY['name']}")

    for r in products:
        for k in r["ings"]:
            if k not in ingredients:
                raise SystemExit(f"record {r['name']!r} references missing key {k!r}")

    if DRY:
        print(f"\nDRY RUN: would add {added} products, "
              f"{len(added_keys)} ingredient keys.")
        return

    dump(os.path.join(DATA, "products.json"), products, 1)
    dump(os.path.join(DATA, "ingredients.json"), ingredients, 1)
    dump(os.path.join(DATA, "owners.json"), owners, 1)
    dump(os.path.join(DATA, "reg.json"), reg, 1)

    if added and not NO_CHANGELOG:
        changelog.insert(0, {
            "date": TODAY,
            "text": (
                "Gather lane: 4 products added from maker disclosures read "
                "2026-10-13, each filling a function the corpus did not carry "
                "-- Lestoil Heavy Duty Multi-Purpose Cleaner (Clorox's own "
                "California SB-258 SmartLabel disclosure, cross-checked against "
                "Clorox's SDS composition), the classic dilutable "
                "petroleum-solvent cleaner and the largest disclosed aromatic "
                "load in the corpus: it names toluene, ethylbenzene and "
                "naphthalene as intentionally added, all three flagged on "
                "California's SB-258 designated list, plus a Stoddard-solvent "
                "stream the SDS quantifies at 3-7%; Ozium Air Sanitizer Spray "
                "Original (Niteo Products' own SDS, EPA Reg. No. 51838-2), the "
                "first EPA-registered air sanitizer here and the first product "
                "whose SDS is mostly propellant and alcohol by weight "
                "(isopropanol 30-50%, liquefied petroleum gas 20-30%); DampRid "
                "Fragrance Free Moisture Absorber (W.M. Barr's own SDS "
                "composition, two revisions), the first product in the corpus "
                "for indoor humidity control -- a function with zero "
                "representation before this run -- whose hazard is physical "
                "rather than chemical (calcium chloride 70-100%, an eye "
                "irritant whose dissolution is strongly exothermic); and Lemi "
                "Shine Dish Detergent Booster (the maker's own per-formula "
                "ingredient table), the first dishwasher booster and the "
                "shortest disclosed formula in the corpus at two lines (citric "
                "acid plus a fragrance whose three sensitizer components the "
                "maker names). Eleven new ingredient keys: eight graded "
                "(Sodium Linoleate, CID 23676150, H315 100% -> derm C; "
                "Trimethylpentanediol, CID 8946, H319 96.3% -> derm C, H335 "
                "59.4% -> resp C; Nonane, CID 8141, H226 65.8% / H304 65.3% / "
                "H315 55% / H319 53.4% / H336 55.3%; Trimethylbenzene, CID "
                "10686, H226 96.1% / H315 91.7% / H319 81.5% / H312 77.8% / "
                "H302 66.4%, recorded Medium because PubChem resolves the "
                "mixed-isomer label term to one isomer; Toluene, CID 1140, "
                "H225 / H304 / H315 / H336 / H361 / H373, all at 95-100% "
                "consensus; Ethylbenzene, CID 7500, H225 and H332 at >99.9% "
                "with H304 and H373 carried from the harmonized "
                "classification; Naphthalene, CID 931, H302 99.8% / H351 "
                "98.9% -> canc C / H400 99.6% / H410 99.9% -> env F; and "
                "1,1-Difluoroethane, CID 6368, H220 95% / H280 77.9%, physical "
                "hazard only) and three recorded without a grade with an "
                "explicit sourcing note (Light Aromatic Hydrocarbons and "
                "Caramel are UVCBs whose PubChem PUG REST lookups return 404; "
                "Cymbopogon Schoenanthus Oil has no direct PubChem record and "
                "is extrapolated from the essential-oil class). One name lookup "
                "was REJECTED for returning a different compound: PubChem's "
                "'Caramel' resolves to CID 61634, '3,5-Dimethyl-1,2-"
                "cyclopentanedione', a flavour substance rather than caramel "
                "colour -- the record states the rejection rather than "
                "accepting the CID. Three label terms were ALIASED to existing "
                "keys rather than re-minted (C10-12 Alcohol Ethoxylates -> "
                "Alcohol Ethoxylate; Orange, sweet, ext. -> Orange Oil; "
                "Petroleum gases, liquefied, sweetened -> Liquefied Petroleum "
                "Gas). Owner registry: Clorox gains Lestoil, NiTEO Products "
                "gains Ozium, and one new record is minted -- W.M. Barr "
                "(Memphis, employee-owned, the DampRid maker), which the "
                "registry did not carry. REGULATORY WATCH: a new watchlist "
                "entry records California's CARB enforcement against aerosol "
                "air care -- the 2023 settlement with Niteo Products over "
                "Ozium Air Sanitizer exceeding the state's 20 percent VOC cap "
                "for the air-freshener (double phase aerosol) category, a "
                "$160,000 penalty premised on 13.32 tons of excess VOC "
                "emissions. It is carried because the corpus now holds the "
                "product the action was taken against, and because it is the "
                "one US rule that directly caps an aerosol's volatile load "
                "with no federal equivalent."),
        })
        dump(os.path.join(DATA, "changelog.json"), changelog, 2)

    print(f"\nwrote {added} products, {len(added_keys)} new ingredient keys.")


if __name__ == "__main__":
    main()
