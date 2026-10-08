#!/usr/bin/env python3
"""Daily gather (2026-10-08, 10:00Z maintenance lane): four high-volume US
cleaning products that were missing from the database, plus the ingredient
records and owner-registry entries they need.

Sources read on 2026-10-08:

  - Static Guard Original Anti-Static Spray. B&G Foods' own ingredient list on
    the brand's product page, plus the same company's GHS safety data sheet
    (section 3) for the fuller chemical names and ranges.
    https://bgfoods.com/brands/static-guard/product/original-scent/
    https://msdsdigital.com/system/files/STATIC%20GUARD%20-%20B%26G%20FOODS%20-%20SDS.pdf
  - Downy WrinkleGuard Wrinkle Releaser Fabric Spray, Fresh. P&G's own
    SmartLabel disclosure (information last updated 2021-04-14 by Downy).
    https://smartlabel.pg.com/en-us/00037000524083.html
  - Babyganics Foaming Dish + Bottle Soap, Fragrance Free. The manufacturer's
    own per-SKU ingredient list on its product page, plus the same company's
    California SB-258 disclosure PDF, which carries the CAS numbers.
    https://babyganics.com/products/foaming-dish-bottle-soap-fragrance-free.html
    https://babyganics.com/content/sds/BGX-dish_bottle-soap-citrus_CA-Disclosure_110419.pdf
  - Cerama Bryte Cooktop Cleaner. The manufacturer's own ingredient table on
    its product page (with CAS numbers), plus its GHS safety data sheet.
    https://ceramabryte.com/product/cerama-bryte-cooktop-cleaner/
    https://ceramabryte.com/wp-content/uploads/2023/05/SDS-Cooktop-Cleaner-rev-7-29Mar22.pdf

Why these four. The corpus is deep in the bleach/bathroom cluster and thin in
three places, and two of these four are functions it does not carry at all:

  - Laundry holds 48 products and NOT ONE fabric-care product that is not a
    detergent, softener, sheet, booster or bleach. Static Guard is a different
    function again: an aerosol anti-static spray applied to a garment after
    drying, whose active is a quaternary ammonium anti-static agent rather than
    a surfactant. It is also the only product in the corpus whose propellant
    package is the majority of the formula.
  - The same gap in the other direction: no wrinkle releaser. Downy WrinkleGuard
    is a spray-on fabric relaxer (a silicone/polymer wrinkle-relaxing agent plus
    a cyclodextrin odour neutraliser), a delivery form the corpus does not carry.
  - Dish Soap holds 25 products and no BABY/BOTTLE line. Babyganics is the
    leading US baby-safe cleaning brand and the brand family is entirely absent
    from the corpus; it is also the only dish soap here whose surfactant set is
    a hydroxysultaine + amine oxide + two glucosides + a sarcosinate, with no
    sulfate and no betaine.
  - Specialty holds 31 products and no COOKTOP cleaner. Cerama Bryte is the
    category leader for glass-ceramic cooktops (recommended by GE Appliances,
    tested and approved for CERAN by SCHOTT) and its formula is a feldspar/quartz
    abrasive paste, a function the corpus does not carry.

Disclosure quality, stated honestly:
  - Static Guard, Downy WrinkleGuard and Babyganics publish a FULL
    intentionally-added list.
  - Cerama Bryte publishes a full ingredient table with CAS numbers on its own
    product page; ONE line ('Thickening Aid') has its CAS withheld and is
    recorded as a class term with the gap stated.

Grading follows the house rule (docs/source-policy.md, docs/scoring-rubric.md):
only H-codes at >=40% ECHA C&L notifier consensus drive a dimension grade, read
from the headline (largest company-count) block of PubChem PUG View. Every
returned PubChem title was checked against the intended substance before the
record was accepted, and every label term was checked against the existing
registry before a new key was minted.

  - Seven new keys are minted this run. ONE is graded: Hydrofluorocarbon 152A
    (CID 6368, returned title '1,1-Difluoroethane' -- the substance HFC-152a,
    CAS 75-37-6) carries H220 at 95% and H280 at 77.9% consensus, and is
    recorded with the same shape as the DB's existing Propane and Isobutane
    records (g 'H220,H280', work C) because the hazard is the physical
    propellant, not a health endpoint. The other six are recorded Not Classified
    with an explicit sourcing note: Quaternium-18, PEG/PPG-18/18 Dimethicone,
    Butyl Acrylate Methacrylic Acid Copolymer, Polyethylene-polypropylene glycol
    and Thickening Aid resolve to no PubChem CID at all (UVCB/polymer/class
    term), and Ammonium Acetate resolves to CID 517165 whose record reports not
    meeting GHS hazard criteria by 2441 of 2536 notifying companies. No grade is
    minted from a guess.
  - Three label terms are ALIASED to keys the DB already carries rather than
    re-minted: 'Quartz' -> 'Silica' (the DB's Silica key is explicitly the
    crystalline form, and quartz is the common crystalline polymorph, CAS
    14808-60-7); 'D-Limonene' -> 'Limonene' (same substance, CAS 5989-27-5,
    already graded derm D / env F under a 2026-09-27 ruling); and
    'Lemon Fragrance' -> 'Fragrance'.

Nothing here is product-graded. Product grading is the Sifter lane; a blank
as-sold grade is the honest state, and substitutes[] is left empty for the same
reason (the substitute rule binds on a D/F grade, and none of these carries one
yet).

Run: python3 tools/gather_2026_10_08.py
Then: python3 build.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-08"

DRY = "--dry-run" in sys.argv
NO_CHANGELOG = "--no-changelog" in sys.argv

STATICGUARD_URL = "https://bgfoods.com/brands/static-guard/product/original-scent/"
STATICGUARD_SDS = ("https://msdsdigital.com/system/files/STATIC%20GUARD%20-%20"
                   "B%26G%20FOODS%20-%20SDS.pdf")
BG_OWNER_SRC = "https://bgfoods.com/about/history/acquisition-history/"
DOWNY_URL = "https://smartlabel.pg.com/en-us/00037000524083.html"
PG_OWNER_SRC = "https://us.pg.com/brands/"
BABYGANICS_URL = ("https://babyganics.com/products/foaming-dish-bottle-soap-"
                  "fragrance-free.html")
BABYGANICS_CA = ("https://babyganics.com/content/sds/BGX-dish_bottle-soap-"
                 "citrus_CA-Disclosure_110419.pdf")
SCJ_OWNER_SRC = ("https://www.prnewswire.com/news-releases/sc-johnson-signs-"
                 "agreement-to-acquire-babyganics-300293228.html")
CERAMA_URL = "https://ceramabryte.com/product/cerama-bryte-cooktop-cleaner/"
CERAMA_SDS = ("https://ceramabryte.com/wp-content/uploads/2023/05/"
              "SDS-Cooktop-Cleaner-rev-7-29Mar22.pdf")
GOLDEN_OWNER_SRC = CERAMA_URL

# --------------------------------------------------------------------------
# Ingredient key resolution. Label wording -> existing canonical key, where the
# substance is the same and a second key would be a synonym for one CAS.
# --------------------------------------------------------------------------
ALIASES = {
    # Cerama Bryte prints the mineral name; the DB key is the same substance
    # (crystalline silica, CAS 14808-60-7) and its note already says so.
    "Quartz": "Silica",
    # Cerama Bryte prints the terpene's stereo descriptor; the DB already
    # carries the same substance (CAS 5989-27-5) as "Limonene", graded derm D /
    # env F under the 2026-09-27 ruling.
    "D-Limonene": "Limonene",
    # Cerama Bryte prints the fragrance as a named blend; the DB carries the
    # generic key.
    "Lemon Fragrance": "Fragrance",
}

# New keys minted this fire. Shape follows the registry: ungraded is recorded as
# ev "Low"/"Medium" with g "Not Classified" (or null) and an explicit sourcing
# note, never a guess.
NEW_KEYS = {
    "Hydrofluorocarbon 152A": {
        "s": "1,1-Difluoroethane (HFC-152a, CAS 75-37-6); a liquefied "
             "propellant gas and the majority of the Static Guard aerosol.",
        "ev": "High", "g": "H220,H280", "gr": {"work": "C"}, "impacts": [],
        "note": "Graded from PubChem GHS (CID 6368, returned title "
                "'1,1-Difluoroethane' -- the substance HFC-152a, CAS 75-37-6; "
                "the name was confirmed against the CAS before the record was "
                "accepted). H220 (extremely flammable gas) sits at 95% "
                "notifier consensus and H280 (contains gas under pressure) at "
                "77.9%. A single H336 (may cause drowsiness or dizziness) "
                "appears without a notifier percentage, so it is not carried "
                "into a grade. Recorded with the same shape as the DB's "
                "existing Propane and Isobutane records (g 'H220,H280', "
                "work C): the hazard is the physical propellant, not a health "
                "endpoint. Named on B&G Foods' own ingredient list for Static "
                "Guard Original.",
    },
    "Quaternium-18": {
        "s": "A dialkyl dimethyl quaternary ammonium chloride (CAS "
             "61789-80-8); the anti-static active in the spray.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on B&G Foods' own ingredient list for Static Guard "
                "Original as 'Quaternium-18'; the same company's SDS names it "
                "more fully as 'Quaternary ammonium compounds, "
                "bis(hydrogenated tallow alkyl)dimethyl, chlorides' (CAS "
                "61789-80-8, 3-7%). PubChem PUG REST returns 404 for both the "
                "name and the CAS number: this is a UVCB (a mixture of "
                "quaternary ammonium chlorides derived from hydrogenated "
                "tallow), so no discrete CID resolves and no GHS "
                "classification is available. Recorded Not Classified rather "
                "than guessed, the same way the DB carries other UVCB class "
                "keys. Distinct from the DB's discrete quaternary ammonium "
                "keys (the dialkyl dimethyl ammonium chlorides carried from "
                "the disinfectant filings).",
    },
    "Ammonium Acetate": {
        "s": "No GHS hazard criteria met (majority not-classified per ECHA "
             "C&L via PubChem)",
        "ev": "Medium", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Graded from PubChem GHS classifications (CID 517165, returned "
                "title 'Ammonium Acetate'; the name was confirmed against CAS "
                "631-61-8 before the record was accepted). The record reports "
                "not meeting GHS hazard criteria by 2441 of 2536 notifying "
                "companies; no H-code reaches the 40% house bar, so the key is "
                "recorded Not Classified. Named on B&G Foods' own ingredient "
                "list for Static Guard Original.",
    },
    "PEG/PPG-18/18 Dimethicone": {
        "s": "A silicone polyether copolymer (CAS 68937-54-2); the "
             "wrinkle-relaxing agent.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on P&G's own SmartLabel for Downy WrinkleGuard Wrinkle "
                "Releaser Fabric Spray. PubChem PUG REST returns 400 for the "
                "name and 404 for the CAS number 68937-54-2: this is a "
                "silicone/polyether block copolymer (a UVCB), so no discrete "
                "CID resolves and no GHS classification is available. Recorded "
                "Not Classified rather than guessed. Distinct from the DB's "
                "discrete dimethicone and PEG keys.",
    },
    "Butyl Acrylate Methacrylic Acid Copolymer": {
        "s": "An acrylic copolymer (a film-forming softening agent); no "
             "discrete PubChem CID.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on P&G's own SmartLabel for Downy WrinkleGuard Wrinkle "
                "Releaser Fabric Spray. PubChem PUG REST returns 404 for the "
                "name -- no discrete CID resolves for this polymer -- so no "
                "GHS classification is available. Recorded Not Classified "
                "rather than guessed, the same way the DB already carries "
                "other polymer class keys (Acrylic Copolymer, Styrene/"
                "Acrylates Copolymer and so on).",
    },
    "Polyethylene-polypropylene glycol": {
        "s": "A poloxamer (a polyoxyethylene-polyoxypropylene block copolymer, "
             "CAS 9003-11-6); a nonionic cleaning agent.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Cerama Bryte's own ingredient table for Cook Top "
                "Cleaner with CAS 9003-11-6. PubChem PUG REST returns 404 for "
                "both the name and the CAS number: this is the poloxamer "
                "polymer family, so no discrete CID resolves and no GHS "
                "classification is available. Recorded Not Classified rather "
                "than guessed. Distinct from the DB's 'Poloxamer 124', which "
                "is a single numbered grade of the same family.",
    },
    "Thickening Aid": {
        "s": "A thickener named only as a class term on the manufacturer's own "
             "ingredient table; CAS withheld.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Cerama Bryte's own ingredient table for Cook Top "
                "Cleaner as 'Thickening Aid' with the CAS withheld. No "
                "substance identity is published, so no CID resolves and no "
                "GHS classification is available. Recorded Not Classified with "
                "the gap stated rather than guessed -- the same treatment the "
                "DB gives its other class-term keys (Proprietary Chelating "
                "Agent, Proprietary Surfactant, Proprietary Polymer Solution).",
    },
}

# --------------------------------------------------------------------------
# Owners. B&G Foods and Golden Ventures are both new to the registry; SC Johnson
# and Procter & Gamble are already recorded (SC Johnson's brand list already
# names Babyganics).
# --------------------------------------------------------------------------
NEW_OWNERS = {
    "B&G Foods, Inc.": {
        "type": "public (BGS)",
        "detail": ("B&G Foods, Inc., headquartered in Parsippany, New Jersey; "
                   "trades on the New York Stock Exchange as BGS. Primarily a "
                   "packaged-foods company that has acquired and integrated "
                   "more than 50 brands since 1996, it also carries one "
                   "household brand. It acquired Static Guard from Unilever as "
                   "part of the Culver Specialty Brands purchase, completed "
                   "1 December 2011 for $325 million in cash (the package also "
                   "included Mrs. Dash, Molly McButter, Sugar Twin, Baker's "
                   "Joy and Kleen Guard). The company's own 10-K describes the "
                   "brand as 'the number one brand name in static elimination "
                   "sprays' and says it 'created the anti-static spray "
                   "category when it was launched in 1978'. B&G Foods sells "
                   "Static Guard through the same food-channel distribution "
                   "system it uses for its food brands. Acquisition facts from "
                   "B&G Foods' own acquisition history and its 10-K; the brand "
                   "page and the SDS both name B&G Foods, Inc. as supplier."),
        "ev": "verified",
        "src": BG_OWNER_SRC,
        "brands": ["Static Guard"],
    },
    "Golden Ventures, Inc.": {
        "type": "private",
        "detail": ("Golden Ventures, Inc., a privately held homecare-products "
                   "company headquartered at 7687 Winton Drive, Indianapolis, "
                   "Indiana. It owns the Cerama Bryte brand -- the CERAMA "
                   "BRYTE word mark was filed by Golden Ventures, Inc. in 2016 "
                   "-- and sells cooktop, stainless-steel and appliance "
                   "cleaners under it. The company's own product page states "
                   "that Cerama Bryte Cooktop Cleaner is recommended by GE "
                   "Appliances and has been tested and approved for CERAN by "
                   "SCHOTT, the manufacturer of the glass used on most "
                   "smooth-top ranges."),
        "ev": "verified",
        "src": GOLDEN_OWNER_SRC,
        "brands": ["Cerama Bryte"],
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
# list, read 2026-10-08.
# --------------------------------------------------------------------------
PRODUCTS = [
    {
        "name": "Static Guard Original Anti-Static Spray",
        "brand": "Static Guard",
        "cat": "Laundry",
        "ings": ["Alcohol Denat.", "Hydrofluorocarbon 152A", "Isobutane",
                 "Propane", "Quaternium-18", "Isopropyl Alcohol",
                 "Ammonium Acetate", "Fragrance"],
        "source": ("Manufacturer ingredient list (B&G Foods, Static Guard "
                   "Original Scent, bgfoods.com product page, read "
                   "2026-10-08): Alcohol Denat., Hydrofluorocarbon 152A, "
                   "Isobutane, Propane, Quaternium-18, Isopropyl Alcohol, "
                   "Ammonium Acetate, Fragrance (Parfum). The same company's "
                   "GHS safety data sheet (section 3) names the same package "
                   "with ranges: Alcohol (64-17-5, 60-100%), Isobutane "
                   "(75-28-5), Propane (74-98-6), Quaternary ammonium "
                   "compounds, bis(hydrogenated tallow alkyl)dimethyl, "
                   "chlorides (61789-80-8, 3-7%) and Fragrance (1-5%), and "
                   "states the exact percentages are a trade secret."),
        "source_url": STATICGUARD_URL,
        "note": ("A full intentionally-added list, published by the maker on "
                 "its own brand page. This is the first FABRIC-CARE product in "
                 "the corpus that is not a detergent, softener, sheet, booster "
                 "or bleach, and the only product here whose propellant "
                 "package is most of the formula: the alcohol/HFC-152a/"
                 "isobutane/propane blend is the carrier that flashes off, and "
                 "the quaternary ammonium anti-static agent (Quaternium-18) is "
                 "the small active that remains on the fabric. The label's own "
                 "precaution is 'CAUTION: EYE IRRITANT', and the SDS adds 'May "
                 "cause an allergic skin reaction' from the fragrance. The "
                 "product is an aerosol, so the propellant hazard is real: "
                 "extremely flammable, contains gas under pressure. B&G Foods' "
                 "own 10-K calls the brand the category creator (1978)."),
        "owner": "B&G Foods, Inc.", "owner_ev": "verified",
        "owner_src": BG_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": STATICGUARD_URL,
        "tier_note": ("Sold at mass, grocery, drug and dollar retailers; "
                      "recorded as mass. Channel evidence is the brand's own "
                      "retail placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("An aerosol anti-static fabric spray in the mass "
                       "channel."),
    },
    {
        "name": "Downy WrinkleGuard Wrinkle Releaser Fabric Spray, Fresh",
        "brand": "P&G",
        "cat": "Laundry",
        "ings": ["Water", "Alcohol", "PEG/PPG-18/18 Dimethicone",
                 "Butyl Acrylate Methacrylic Acid Copolymer",
                 "Hydroxypropyl Cyclodextrin", "Fragrance",
                 "Benzisothiazolinone", "Nitrogen"],
        "source": ("Manufacturer ingredient disclosure (Procter & Gamble, "
                   "Downy WrinkleGuard Wrinkle Releaser Fabric Spray, Fresh, "
                   "9.7 oz, SmartLabel, information last updated 2021-04-14 by "
                   "Downy): Water, Alcohol, PEG/PPG-18/18 Dimethicone, Butyl "
                   "Acrylate Methacrylic Acid Copolymer, Hydroxypropyl "
                   "Cyclodextrin, Fragrance, Benzisothiazolinone, Nitrogen. "
                   "The same brand's product page for the current Wrinkle "
                   "Releaser spray prints the identical set with functional "
                   "labels (alcohol as process aid, the dimethicone as "
                   "wrinkle-relaxing agent, the acrylic copolymer as softening "
                   "agent, the cyclodextrin as odour-removing agent)."),
        "source_url": DOWNY_URL,
        "note": ("A full intentionally-added list, published by the maker on "
                 "its own SmartLabel page. This is the first WRINKLE RELEASER "
                 "in the corpus and a different function from every laundry "
                 "product already recorded: it is sprayed on a garment and "
                 "tugged, so the formula is a fabric-relaxing silicone, a "
                 "film-forming acrylic copolymer, an alcohol process aid and a "
                 "cyclodextrin odour neutraliser, with no surfactant and no "
                 "builder. Nitrogen is the propellant. Benzisothiazolinone is "
                 "the preservative; the DB already carries it and grades it "
                 "derm D (H317) from other filings. The fragrance is disclosed "
                 "as a single 'Fragrance' entry, which is P&G's SmartLabel "
                 "convention for this product; the DB carries that under its "
                 "existing 'Fragrance' key."),
        "owner": "Procter & Gamble", "owner_ev": "verified",
        "owner_src": PG_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": DOWNY_URL,
        "tier_note": ("Sold at mass, grocery and club retailers; recorded as "
                      "mass. Channel evidence is the brand's own retail "
                      "placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A spray-on fabric wrinkle releaser in the mass "
                       "channel."),
    },
    {
        "name": "Babyganics Foaming Dish + Bottle Soap, Fragrance Free",
        "brand": "Babyganics",
        "cat": "Dish Soap",
        "ings": ["Water", "Cocamidopropyl Hydroxysultaine", "Lauramine Oxide",
                 "Decyl Glucoside", "Lauryl Glucoside",
                 "Sodium Lauroyl Sarcosinate", "Glycerin",
                 "Methylisothiazolinone"],
        "source": ("Manufacturer ingredient list (Babyganics, foaming dish + "
                   "bottle soap, fragrance free, 16 oz, babyganics.com product "
                   "page, read 2026-10-08): water, cocamidopropyl "
                   "hydroxysultaine, lauramine oxide, decyl glucoside, lauryl "
                   "glucoside, sodium lauroyl sarcosinate, glycerin, "
                   "methylisothiazolinone. The same company's California "
                   "Cleaning Product Right to Know (SB-258) disclosure PDF for "
                   "the dish & bottle soap carries the same substances with "
                   "CAS numbers (cocamidopropyl hydroxysultaine 68139-30-0, "
                   "decyl glucoside 68515-73-1, lauramine oxide 1643-20-5, "
                   "sodium lauroyl sarcosinate 137-16-6, glycerin 56-81-5, "
                   "methylisothiazolinone 2682-20-4, water 7732-18-5)."),
        "source_url": BABYGANICS_URL,
        "note": ("A full intentionally-added list, published by the maker on "
                 "its own product page and repeated with CAS numbers in its "
                 "California SB-258 filing. This is the first BABY/BOTTLE dish "
                 "soap in the corpus and the first Babyganics product of any "
                 "kind: the brand family was entirely absent, and it is the "
                 "leading US baby-safe cleaning brand. The surfactant set is "
                 "distinct from every other dish soap here -- a mild "
                 "hydroxysultaine, an amine oxide, two alkyl glucosides and a "
                 "sarcosinate, with no sulfate and no betaine -- and the brand "
                 "positions on being free of phosphates, phthalates, "
                 "fragrances and dyes, which the list bears out (this is the "
                 "fragrance-free SKU). The preservative is "
                 "methylisothiazolinone, which the DB already carries and "
                 "grades; it is the one line in the formula that carries a "
                 "sensitisation concern, and it is disclosed rather than "
                 "hidden."),
        "owner": "SC Johnson", "owner_ev": "verified",
        "owner_src": SCJ_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": BABYGANICS_URL,
        "tier_note": ("Sold at mass, grocery, drug and baby retailers and "
                      "direct from the brand; recorded as mass. Channel "
                      "evidence is the brand's own retail placement, not a "
                      "per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A baby/bottle dish soap in the mass channel."),
    },
    {
        "name": "Cerama Bryte Cooktop Cleaner",
        "brand": "Cerama Bryte",
        "cat": "Specialty",
        "ings": ["Water", "Feldspar", "Thickening Aid", "Quartz",
                 "Polyethylene-polypropylene glycol",
                 "Diethylene Glycol Monobutyl Ether", "Citric Acid",
                 "Xanthan Gum", "Sodium Benzoate", "Lemon Fragrance",
                 "D-Limonene", "Citral"],
        "source": ("Manufacturer ingredient table (Golden Ventures, Inc., "
                   "Cerama Bryte Cooktop Cleaner, ceramabryte.com product "
                   "page, read 2026-10-08): Water (7732-18-5), Feldspar "
                   "(68479-25-5), Thickening Aid (CAS withheld), Quartz "
                   "(14808-60-7), Polyethylene-polypropylene glycol "
                   "(9003-11-6), Diethylene Glycol Monobutyl Ether "
                   "(112-34-5), Citric Acid (77-92-9), Xanthan Gum "
                   "(11138-66-2), Sodium Benzoate (532-32-1), Lemon Fragrance "
                   "(unknown), D-Limonene (5989-27-5), Citral (226-394-6). The "
                   "same company's GHS safety data sheet (section 3) lists the "
                   "hazardous components only: Feldspar (68476-25-5), Quartz "
                   "(14808-60-7), Glycol Ether DB (112-34-5) and Citric Acid "
                   "(77-92-9), with the balance (65-75%) recorded as "
                   "non-hazardous ingredients below reportable levels. Note "
                   "the two documents disagree on the Feldspar CAS "
                   "(68479-25-5 on the page, 68476-25-5 on the SDS); both are "
                   "recorded here rather than silently reconciled."),
        "source_url": CERAMA_URL,
        "note": ("A full ingredient table with CAS numbers, published by the "
                 "maker on its own product page; one line ('Thickening Aid') "
                 "has its CAS withheld and is recorded as a class term with "
                 "the gap stated. This is the first COOKTOP cleaner in the "
                 "corpus and a function it does not carry: a feldspar/quartz "
                 "abrasive paste, buffed off dry, rather than a spray. The "
                 "maker's own page states the product is recommended by GE "
                 "Appliances and tested and approved for CERAN by SCHOTT, and "
                 "that it deliberately contains no silicone (which would leave "
                 "an oily film and can lift the cooktop pattern under heat). "
                 "The two abrasives are the reason the entry matters: quartz "
                 "is crystalline silica, which the DB already carries and "
                 "grades for the dust-inhalation hazard, and the maker's own "
                 "SDS notes the silica is present in a non-respirable form and "
                 "that silica dust is not generated with use. The solvent is "
                 "the glycol ether the DB already carries and grades "
                 "(Diethylene Glycol Monobutyl Ether); the fragrance is "
                 "carried by the DB's existing Limonene key, which already "
                 "carries the 2026-09-27 dermal-sensitisation ruling."),
        "owner": "Golden Ventures, Inc.", "owner_ev": "verified",
        "owner_src": GOLDEN_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": CERAMA_URL,
        "tier_note": ("Sold at home-improvement, hardware and appliance "
                      "retailers and online; recorded as mass. Channel "
                      "evidence is the brand's own retail placement, not a "
                      "per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A glass-ceramic cooktop cleaner in the mass channel."),
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

    for r in products:
        for k in r["ings"]:
            if k not in ingredients:
                raise SystemExit(f"record {r['name']!r} references missing key {k!r}")

    if added and not NO_CHANGELOG:
        changelog.insert(0, {
            "date": TODAY,
            "text": ("Gather lane: 4 products added from manufacturer "
                     "disclosures read 2026-10-08 -- Static Guard Original "
                     "Anti-Static Spray (full list, bgfoods.com, with the "
                     "company's own SDS for the fuller chemical names and "
                     "ranges), Downy WrinkleGuard Wrinkle Releaser Fabric "
                     "Spray Fresh (full SmartLabel list, smartlabel.pg.com), "
                     "Babyganics Foaming Dish + Bottle Soap Fragrance Free "
                     "(full per-SKU list, babyganics.com, repeated with CAS "
                     "numbers in the company's California SB-258 filing) and "
                     "Cerama Bryte Cooktop Cleaner (full ingredient table with "
                     "CAS, ceramabryte.com, one line 'Thickening Aid' with the "
                     "CAS withheld). Two brand families new to the corpus: "
                     "Babyganics (owner SC Johnson, already recorded, whose "
                     "brand list already named it) and Golden Ventures, Inc. "
                     "(owner-registry entry added for the Cerama Bryte brand); "
                     "B&G Foods, Inc. is also added as the owner of Static "
                     "Guard, acquired from Unilever in 2011. Fills three "
                     "functional gaps the corpus did not carry at all: the "
                     "first fabric-care product that is not a detergent, "
                     "softener, sheet, booster or bleach (an aerosol "
                     "anti-static spray), the first WRINKLE RELEASER, and the "
                     "first COOKTOP cleaner. Seven new ingredient keys: one "
                     "graded (Hydrofluorocarbon 152A, CID 6368 "
                     "'1,1-Difluoroethane', H220 at 95% and H280 at 77.9% "
                     "consensus, recorded with the same shape as the existing "
                     "Propane and Isobutane records) and six recorded Not "
                     "Classified with an explicit sourcing note -- "
                     "Quaternium-18, PEG/PPG-18/18 Dimethicone, Butyl Acrylate "
                     "Methacrylic Acid Copolymer, Polyethylene-polypropylene "
                     "glycol and Thickening Aid resolve to no PubChem CID at "
                     "all (UVCB/polymer/class term), and Ammonium Acetate "
                     "resolves to CID 517165 whose record reports not meeting "
                     "GHS hazard criteria by 2441 of 2536 notifying companies. "
                     "Three label terms were ALIASED to keys the DB already "
                     "carries instead of being re-minted: Quartz -> Silica "
                     "(the DB's Silica key is explicitly the crystalline form, "
                     "CAS 14808-60-7), D-Limonene -> Limonene (same CAS "
                     "5989-27-5, already graded derm D / env F under the "
                     "2026-09-27 ruling) and Lemon Fragrance -> Fragrance."),
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
