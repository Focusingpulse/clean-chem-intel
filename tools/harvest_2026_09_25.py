#!/usr/bin/env python3
"""Night shift station 2 (2026-09-25): exposure-ordered harvest for the thin tiers.

Adds products to data/products.json, ingredient records to data/ingredients.json,
and owner records to data/owners.json. Every ingredient list below is copied from
a manufacturer or government disclosure that was read on 2026-09-25:

  - Whole Foods Market household-cleaner disclosure (CA SB-258 required page)
  - Sprouts Farmers Market CA Cleaning Product Right to Know disclosures
  - DailyMed (NLM) FDA OTC drug labels for CVS Health, Walgreens and Power Force
  - Fabrica de Jabon La Corona SDS + retailer ingredient panel for Zote
  - Kirk's Soap manufacturer ingredient page + retailer panel

Run: python3 tools/harvest_2026_09_25.py
Then: python3 tools/validate_certainty.py --apply && python3 build.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
TODAY = "2026-09-25"

WFM = "https://www.wholefoodsmarket.com/legal/all-purpose-cleaner-disclosure"
SPROUTS = "https://www.sprouts.com/california-cleaning-product-right-to-know-act/"
DM_CVS_SOAP = ("https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm"
               "?setid=63798c63-94fe-4ba8-8692-ca8be43c151e")
DM_WAG_SOAP = ("https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
               "?setid=b45cbd3b-cba7-4c26-90bf-ec729dae3f28")
DM_POWER_FORCE = ("https://dailymed.nlm.nih.gov/dailymed/getFile.cfm"
                  "?setid=aefc76f5-c3c9-4d0a-855b-5123325f93b5&type=pdf")
ZOTE_DIRECTIONS = "https://directionsforme.org/product/7383"
ZOTE_SDS = "https://www.soapgoods.com/documents/sds/Pink-Zote-Soap.pdf"
KIRKS_ING = "https://kirkssoap.com/pages/our-ingredients"
INDEXBOX = ("https://www.indexbox.io/store/united-states-laundry-home-products-market-"
            "analysis-forecast-size-trends-and-insights/")
AMZ_APC = ("https://www.amazon.com/Best-Sellers-Health-Household-All-Purpose-Household-"
           "Cleaners/zgbs/hpc/15356141")
ASINSIGHT_DISH = "https://www.asinsight.com/market-analysis/US/dish-soap"
ZOTE_EXPANSION = ("https://expansion.mx/empresas/2022/01/27/jabon-zote-elaboracion-"
                  "tradicional-exportacion-mundial")

BASE_BASIS = ("searched for a published per-product US household penetration figure; none "
              "exists in the open literature, so the estimate is derived from category "
              "penetration times the brand's share of its channel. Rounded to one "
              "significant figure. ")


# ---------------------------------------------------------------- ingredients
NEW_INGS = {
    "Chloroxylenol": {
        "g": "H302,H315,H317,H319",
        "s": "Antimicrobial (PCMX). Harmful if swallowed; skin and eye irritant; skin sensitizer.",
        "ev": "High",
        "gr": {"derm": "D"},
        "impacts": ["allerg", "derm"],
        "note": "PubChem CID 2723 (4-chloro-3,5-dimethylphenol), ECHA C&L notifier consensus. "
                "Active at 0.3% in the Dollar Tree Power Force antibacterial hand soap.",
    },
    "Lauramidopropylamine Oxide": {
        "g": "Extrapolated",
        "s": "Amine oxide surfactant; graded by analogy within the amine-oxide class.",
        "ev": "Extrapolated",
        "gr": {"derm": "D"},
        "impacts": ["derm"],
        "note": "Searched PubChem for a discrete record; none returned (UVCB). Class analogues "
                "Lauramine Oxide (H315,H319) and Myristamine Oxide (H318,H315,H400) both carry "
                "skin/eye irritation, so derm D is carried here rather than left blank.",
    },
    "Myristamidopropylamine Oxide": {
        "g": "H302,H315,H318,H373,H400,H410,H411",
        "s": "Amine oxide surfactant. Serious eye damage, harmful if swallowed, organ damage on "
             "repeated exposure, very toxic to aquatic life.",
        "ev": "High",
        "gr": {"derm": "D", "env": "F", "organ": "D", "work": "D"},
        "impacts": ["derm", "aqua"],
        "note": "PubChem CID 64680 (myristamidopropylamine oxide), ECHA C&L notifier consensus.",
    },
    "Disteareth-75 IPDI": {
        "g": "Not Classified",
        "s": "Polymeric rheology modifier (UVCB); no discrete identity, so no classification.",
        "ev": "Low",
        "gr": {},
        "impacts": [],
        "note": "Searched PubChem for a discrete record and found none; no CAS disclosed on the "
                "label. Recorded unclassified rather than guessed.",
    },
    "PEG-150 Distearate": {
        "g": "Not Classified",
        "s": "Polymeric thickener (UVCB); no discrete PubChem CID.",
        "ev": "Low",
        "gr": {},
        "impacts": [],
        "note": "Searched PubChem for a discrete record and found none. PEG distearates are "
                "tallied as no-hazard polymers in the ECHA polymer register.",
    },
    "Benzophenone-4": {
        "g": "H315,H317,H318,H319,H335",
        "s": "UV absorber (sulisobenzone). Skin and eye irritant, skin sensitizer, respiratory "
             "irritation.",
        "ev": "High",
        "gr": {"derm": "D", "resp": "D"},
        "impacts": ["allerg", "derm", "resp"],
        "note": "PubChem CID 19988 (sulisobenzone), ECHA C&L notifier consensus.",
    },
    "Red 4": {
        "g": "Not Classified",
        "s": "No GHS hazard criteria met",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "FD&C Red No. 4 (Ponceau SX). PubChem GHS lookup returns no hazard data and no "
                "discrete CID for the dye name. Medium confidence.",
    },
    "Red 33": {
        "g": "H319,H412",
        "s": "Azo dye. Causes serious eye irritation; harmful to aquatic life.",
        "ev": "High",
        "gr": {"derm": "D", "env": "D"},
        "impacts": ["derm", "aqua"],
        "note": "PubChem CID 19116 (azo fuchsine), ECHA C&L notifier consensus.",
    },
    "Red 40": {
        "g": "Not Classified",
        "s": "No GHS hazard criteria met (345 of 345 notifiers)",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "FD&C Red No. 40 (Allura Red AC). PubChem CID 33258; reported as not meeting GHS "
                "hazard criteria by 345 of 345 companies in the ECHA C&L consensus.",
    },
    "Blue 1": {
        "g": "Not Classified",
        "s": "No GHS hazard criteria met",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "FD&C Blue No. 1 (Brilliant Blue FCF). PubChem CID 19700; no GHS section returned "
                "by the PUG-view lookup.",
    },
    "Methanol": {
        "g": "H225,H301,H311,H331,H370",
        "s": "Toxic if swallowed, inhaled or in contact with skin; causes organ damage; highly "
             "flammable.",
        "ev": "High",
        "gr": {"derm": "D", "resp": "D", "organ": "F", "work": "D"},
        "impacts": ["derm", "organ", "resp"],
        "note": "PubChem CID 887, ECHA C&L notifier consensus. Present as a denaturant in "
                "denatured-alcohol cleaners, disclosed by Whole Foods at the ingredient level.",
    },
    "Ethyl Acetate": {
        "g": "H225,H319,H336",
        "s": "Flammable solvent; eye irritant; may cause drowsiness or dizziness.",
        "ev": "High",
        "gr": {"derm": "C", "resp": "B"},
        "impacts": ["derm", "resp"],
        "note": "PubChem CID 8857, ECHA C&L notifier consensus.",
    },
    "Saponins": {
        "g": "H319,H335",
        "s": "Causes serious eye irritation; may cause respiratory irritation.",
        "ev": "Medium",
        "gr": {"derm": "D", "resp": "D"},
        "impacts": ["derm", "resp"],
        "note": "PubChem CID 6540709 (saponins, CAS 8047-15-2), ECHA C&L notifier consensus. "
                "Whole Foods discloses saponins as a surfactant in its Organic Multisurface "
                "Cleaner.",
    },
    "Potassium Cocoate": {
        "g": "Not Classified",
        "s": "Soap salt (potassium salt of coconut fatty acids); no discrete PubChem CID.",
        "ev": "Low",
        "gr": {},
        "impacts": [],
        "note": "Searched PubChem for a discrete record; none returned for the coconut-derived "
                "soap salt. The potassium-oleate analogue carries H315/H319 (derm C). Recorded "
                "unclassified rather than guessed.",
    },
    "Japanese Honeysuckle Extract": {
        "g": "Not Classified",
        "s": "Botanical extract; no GHS classification located.",
        "ev": "Low",
        "gr": {},
        "impacts": [],
        "note": "Lonicera japonica flower extract, disclosed by Whole Foods as an antimicrobial in "
                "its Organic Multisurface Cleaner. Searched PubChem and found no discrete CID and "
                "no GHS classification.",
    },
    "Cocamidopropylamine Oxide": {
        "g": "Extrapolated",
        "s": "Amine oxide surfactant; graded by analogy within the amine-oxide class.",
        "ev": "Extrapolated",
        "gr": {"derm": "D"},
        "impacts": ["derm"],
        "note": "Searched PubChem for a discrete record; none returned (UVCB). Class analogues "
                "carry skin/eye irritation, so derm D is carried here rather than left blank.",
    },
    "Sodium Cocoate": {
        "g": "Not Classified",
        "s": "Soap salt (sodium salt of coconut fatty acids); no H-code at 40% ECHA C&L "
             "notifier consensus.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem returns no discrete CID for the coconut soap salt; ECHA C&L consensus "
                "for the class reports no classification. The primary surfactant of Kirk's "
                "Castile and the Zote bars.",
    },
    "Sodium Tallowate": {
        "g": "Not Classified",
        "s": "Soap salt (sodium salt of tallow fatty acids); no discrete PubChem CID.",
        "ev": "Low",
        "gr": {},
        "impacts": [],
        "note": "Searched PubChem for a discrete record; none returned. The sodium-stearate "
                "analogue is reported as not classified by ECHA C&L consensus. Primary surfactant "
                "of the Zote laundry bars.",
    },
    "Optical Brightener": {
        "g": "Not Classified",
        "s": "Disclosed by generic class name only; identity withheld.",
        "ev": "Low",
        "gr": {},
        "impacts": [],
        "note": "No CAS, no discrete identity and no PubChem CID, so no classification is "
                "possible. Recorded unclassified rather than guessed. Disclosed on the Zote "
                "laundry soap ingredient panels.",
    },
    "Violet 10": {
        "g": "H302,H318,H335,H412",
        "s": "Rhodamine B (CI 45170). Harmful if swallowed; serious eye damage; respiratory "
             "irritation; harmful to aquatic life.",
        "ev": "High",
        "gr": {"derm": "D", "env": "D", "resp": "D"},
        "impacts": ["derm", "aqua", "resp"],
        "note": "PubChem CID 6694 (Rhodamine B), ECHA C&L notifier consensus. Used as the "
                "whitening dye in the pink Zote laundry bar.",
    },
    "Cocamide MEA": {
        "g": "Extrapolated",
        "s": "Coconut-derived foam booster; graded by analogy within the ethanolamide class.",
        "ev": "Extrapolated",
        "gr": {"derm": "C"},
        "impacts": ["derm"],
        "note": "Searched PubChem for a discrete record; none returned (UVCB). Class analogues "
                "carry skin/eye irritation, so derm C is carried here rather than left blank.",
    },
    "Cocamide DEA": {
        "g": "Extrapolated",
        "s": "Coconut diethanolamide. Structurally related to diethanolamine; graded by analogy.",
        "ev": "Extrapolated",
        "gr": {"derm": "C", "canc": "D"},
        "impacts": ["canc", "derm"],
        "note": "Searched PubChem for a discrete record and found none (UVCB). The cancer flag is "
                "an extrapolation from the diethanolamine moiety, not a classification of the "
                "amide itself; no harmonised GHS classification was located for cocamide DEA.",
    },
    "Disodium EDTA": {
        "g": "Not Classified",
        "s": "Chelating agent; no GHS classification in the authoritative block.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem CID 13020083 (disodium EDTA); no GHS section returned. Distinct from the "
                "tetrasodium salt, which carries a fuller classification.",
    },
    "Sodium Oleate": {
        "g": "H412",
        "s": "Harmful to aquatic life with long lasting effects.",
        "ev": "High",
        "gr": {"env": "D"},
        "impacts": ["aqua"],
        "note": "PubChem CID 23665730, ECHA C&L notifier consensus.",
    },
}


# -------------------------------------------------------------------- owners
NEW_OWNERS = {
    "Amazon.com, Inc.": {
        "type": "public (AMZN)",
        "detail": "Acquired Whole Foods Market in 2017 for approximately $13.7 billion. The 365 "
                  "Everyday Value and 365 by Whole Foods Market house brands sit under Whole "
                  "Foods, and therefore under Amazon. The natural-grocery private label is owned "
                  "by the same company that runs the largest conventional retail channel.",
        "ev": "verified",
        "src": "https://press.aboutamazon.com/2017/6/amazon-to-acquire-whole-foods-market",
        "brands": ["Whole Foods", "365 Everyday Value", "365 by Whole Foods Market"],
    },
    "CVS Health Corporation": {
        "type": "public (CVS)",
        "detail": "Owns the CVS Health house brand. CVS Pharmacy is named as the labeler of record "
                  "on the FDA OTC drug label for its antibacterial hand soap.",
        "ev": "reported",
        "src": DM_CVS_SOAP,
        "brands": ["CVS Health"],
    },
    "Walgreens Boots Alliance, Inc.": {
        "type": "public (WBA)",
        "detail": "Owns the Walgreens and Nice! house brands. Walgreens is named as the labeler of "
                  "record on the FDA OTC drug label for its antibacterial hand soap.",
        "ev": "reported",
        "src": DM_WAG_SOAP,
        "brands": ["Walgreens", "Nice!"],
    },
    "Sprouts Farmers Market, Inc.": {
        "type": "public (SFM)",
        "detail": "Owns the Sprouts house brand. Publishes per-product ingredient declarations and "
                  "SDS links under the California Cleaning Product Right to Know Act.",
        "ev": "reported",
        "src": SPROUTS,
        "brands": ["Sprouts Farmers Market", "Sprouts"],
    },
    "Fabrica de Jabon La Corona, S.A. de C.V.": {
        "type": "private (Mexico)",
        "detail": "Mexican soap and detergent manufacturer; owns the Zote laundry-soap brand. The "
                  "pink bar is its highest-volume line and about 15% of the brand's sales leave "
                  "Mexico, primarily to the United States.",
        "ev": "reported",
        "src": ZOTE_EXPANSION,
        "brands": ["Zote"],
    },
}


# ------------------------------------------------------------------ products
def prod(name, brand, cat, ings, tier, tier_ev, tier_src, exposure, exposure_ev,
         exposure_src, exposure_basis, subs=None, no_sub=None, tier_note=None,
         heritage=None):
    p = {
        "name": name,
        "brand": brand,
        "cat": cat,
        "safe": None,
        "ings": ings,
        "added": TODAY,
        "updated": TODAY,
        "owner": None,
        "owner_ev": "untested",
        "owner_src": None,
        "tier": tier,
        "tier_ev": tier_ev,
        "tier_src": tier_src,
        "substitutes": subs or [],
        "exposure": exposure,
        "exposure_ev": exposure_ev,
        "exposure_src": exposure_src,
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "not_reviewed",
        "exposure_basis": exposure_basis,
    }
    if tier_note:
        p["tier_note"] = tier_note
    if no_sub:
        p["no_substitute_known"] = no_sub
    if heritage:
        p["heritage"] = True
        p["heritage_year"] = heritage[0]
        p["heritage_note"] = heritage[1]
    return p


PHARMACY_TIER_NOTE = ("House brand of a pharmacy chain; the drugstore bin is the brand's own "
                      "definition, not an inference from the shelf it was found on.")

PRODUCTS = [
    # ---- drugstore -------------------------------------------------------
    prod("CVS Health Moisturizing Antibacterial Hand Soap", "CVS Health", "Hand Soap",
         ["Water", "Benzalkonium Chloride", "Lauramine Oxide", "Cocamidopropyl Betaine",
          "Lauramidopropylamine Oxide", "Sodium Chloride", "Myristamidopropylamine Oxide",
          "Glycerin", "Disteareth-75 IPDI", "PEG-150 Distearate", "Citric Acid",
          "Tetrasodium EDTA", "Benzophenone-4", "Sodium Benzoate", "Red 33", "Red 40", "Yellow 5"],
         "drugstore", "reported", DM_CVS_SOAP,
         3, "extrapolated", INDEXBOX,
         BASE_BASIS + "Hand soap is used in nearly every US household and this is the house brand "
                      "of a national pharmacy chain, so the estimate stops at the brand's "
                      "channel share rather than a measured product share.",
         subs=[{"name": "Branch Basics Gel Hand Soap",
                "tier": "natural",
                "note": "Concentrate that dilutes to a foaming hand soap. Avoids the "
                        "benzalkonium-chloride active, which is graded derm F and carries an "
                        "aquatic-toxicity flag, and avoids the benzophenone-4 UV absorber."},
               {"name": "Kirk's Original Coco Castile Soap",
                "tier": "apothecary-bulk",
                "note": "A $2-3 bar at the same store price point. Avoids the quaternary-ammonium "
                        "active and every preservative in the liquid formula. Less convenient, not "
                        "less effective."}],
         tier_note=PHARMACY_TIER_NOTE),

    prod("Walgreens Antibacterial Hand Soap, Amber", "Walgreens", "Hand Soap",
         ["Water", "Benzalkonium Chloride", "Lauramine Oxide", "Cocamidopropyl Betaine",
          "Lauramidopropylamine Oxide", "Sodium Chloride", "Myristamidopropylamine Oxide",
          "Glycerin", "Disteareth-75 IPDI", "PEG-150 Distearate", "Citric Acid",
          "Tetrasodium EDTA", "Benzophenone-4", "Sodium Benzoate", "Red 4", "Yellow 5"],
         "drugstore", "reported", DM_WAG_SOAP,
         3, "extrapolated", INDEXBOX,
         BASE_BASIS + "Hand soap is used in nearly every US household and this is the house brand "
                      "of a national pharmacy chain, so the estimate stops at the brand's "
                      "channel share rather than a measured product share.",
         subs=[{"name": "Branch Basics Gel Hand Soap",
                "tier": "natural",
                "note": "Avoids the benzalkonium-chloride active (derm F, aquatic toxicity) and "
                        "the benzophenone-4 UV absorber."},
               {"name": "Kirk's Original Coco Castile Soap",
                "tier": "apothecary-bulk",
                "note": "Same price point as a bar. Avoids the quaternary-ammonium active "
                        "entirely."}],
         tier_note=PHARMACY_TIER_NOTE),

    # ---- dollar-store ----------------------------------------------------
    prod("Power Force Antibacterial Hand Soap, Green Apple", "Power Force", "Hand Soap",
         ["Water", "Chloroxylenol", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
          "Lauramine Oxide", "Propylene Glycol", "Sodium Chloride", "Fragrance",
          "Sodium Xylenesulfonate", "Citric Acid", "Yellow 5", "Blue 1", "Methylisothiazolinone",
          "Methylchloroisothiazolinone"],
         "dollar-store", "reported", DM_POWER_FORCE,
         2, "extrapolated", INDEXBOX,
         BASE_BASIS + "The house brand of a national dollar-store chain, sold at a "
                      "dollar-store price point. The label is public because it is an FDA OTC "
                      "drug label, not because the brand chose to publish an ingredient list.",
         subs=[{"name": "Kirk's Original Coco Castile Soap",
                "tier": "apothecary-bulk",
                "note": "A bar at a comparable dollar-store price point. Avoids chloroxylenol, the "
                        "chloroxylenol skin sensitizer, and the MIT/CMIT preservative pair, which "
                        "is the strongest sensitizer in this formula."},
               {"name": "LA's Totally Awesome All-Purpose Cleaner",
                "tier": "dollar-store",
                "note": "Dollar Tree's other house line. Not a like-for-like hand soap, so use it "
                        "for surfaces only; it avoids both the antimicrobial active and the "
                        "isothiazolinone preservatives."}],
         tier_note="Dollar Tree house brand. The FDA drug label names Korex Chicago LLC as the "
                   "labeler of record, so the contract manufacturer is visible even though the "
                   "retail brand owner is Dollar Tree."),

    # ---- grocery ---------------------------------------------------------
    prod("365 Everyday Value All-Purpose Cleaner, Wild Orange", "365 Everyday Value",
         "All-Purpose",
         ["Water", "Denatured Alcohol", "Methanol", "Laureth-7", "Ethyl Acetate",
          "Triethyl Citrate", "Limonene"],
         "grocery", "reported", WFM,
         1, "extrapolated", INDEXBOX,
         BASE_BASIS + "Whole Foods is a national grocery chain but a small share of US households; "
                      "the private label is a fraction of that. The estimate is the channel share "
                      "of the category, not a measured product share.",
         subs=[{"name": "365 by Whole Foods Market All Purpose Cleaner, Citrus",
                "tier": "grocery",
                "note": "Same brand and price point, and it drops the alcohol/methanol/ethyl-"
                        "acetate solvent load entirely: methanol is graded organ F. The citrus "
                        "variant is water-based with a glucoside surfactant."}],
         tier_note="Grocery-chain private label. Disclosed under California SB-258 with CAS "
                   "numbers on the Whole Foods household-cleaner page."),

    prod("365 by Whole Foods Market All Purpose Cleaner, Citrus", "365 by Whole Foods Market",
         "All-Purpose",
         ["Water", "Decyl Glucoside", "Benzisothiazolinone", "Citric Acid", "Limonene"],
         "grocery", "reported", WFM,
         1, "extrapolated", INDEXBOX,
         BASE_BASIS + "Whole Foods is a national grocery chain but a small share of US households; "
                      "the private label is a fraction of that. Channel share, not a measured "
                      "product share.",
         subs=[{"name": "Whole Foods Market Organic Multisurface Cleaner, Lavender Lemon",
                "tier": "grocery",
                "note": "Same chain, same price point. Drops the benzisothiazolinone preservative "
                        "(derm D, aquatic toxicity) at the cost of carrying a fragrance instead."}],
         tier_note="Grocery-chain private label. Disclosed under California SB-258."),

    prod("Whole Foods Market Organic Multisurface Cleaner, Lavender Lemon", "Whole Foods",
         "Multi-Surface Cleaner",
         ["Water", "Saponins", "Ethanol", "Potassium Cocoate", "Japanese Honeysuckle Extract",
          "Glycerin", "Hydrogen Peroxide", "Sodium Chloride", "Sodium Carbonate", "Linalool",
          "Limonene"],
         "grocery", "reported", WFM,
         1, "extrapolated", INDEXBOX,
         BASE_BASIS + "Whole Foods is a national grocery chain but a small share of US households. "
                      "Channel share, not a measured product share.",
         subs=[],
         tier_note="Grocery-chain private label, organic line. Disclosed under California SB-258. "
                   "The formula is soap- and peroxide-based rather than preservative-based, so the "
                   "fragrance allergens are what carries the hazard."),

    prod("Sprouts Citrus Scent All Purpose Cleaner", "Sprouts Farmers Market", "All-Purpose",
         ["Water", "Ethoxylated Alcohol", "Sodium Gluconate", "Sodium Carbonate", "Fragrance",
          "Benzisothiazolinone", "Citral", "Limonene"],
         "grocery", "reported", SPROUTS,
         1, "extrapolated", INDEXBOX,
         BASE_BASIS + "Sprouts is a national grocery chain and a small share of "
                      "US households. Channel share, not a measured product share.",
         subs=[{"name": "Whole Foods Market Organic Multisurface Cleaner, Lavender Lemon",
                "tier": "grocery",
                "note": "Comparable natural-grocery price point. Avoids benzisothiazolinone, though "
                        "it still carries fragrance allergens."}],
         tier_note="Grocery-chain private label. Disclosed under California SB-258 with CAS "
                   "numbers."),

    prod("Sprouts Free & Clear Dish Soap", "Sprouts Farmers Market", "Dish Soap",
         ["Water", "Sodium Laureth Sulfate", "Cocamidopropylamine Oxide", "Sodium Chloride",
          "Benzisothiazolinone"],
         "grocery", "reported", SPROUTS,
         1, "extrapolated", ASINSIGHT_DISH,
         BASE_BASIS + "Liquid dish soap is owned by over 95% of US households; that category "
                      "figure is the one published number here, and Sprouts' own share of it is "
                      "small. Channel share, not a measured product share.",
         subs=[{"name": "Seventh Generation Dish Liquid, Free & Clear",
                "tier": "natural",
                "note": "Fragrance-free and preservative-free at a comparable per-ounce price. "
                        "Avoids benzisothiazolinone and the cocamidopropylamine oxide."}],
         tier_note="Grocery-chain private label. Disclosed under California SB-258, including a "
                   "fragrance-allergen row (none declared for this variant)."),

    prod("Zote Laundry Soap, Pink", "Zote", "Laundry",
         ["Sodium Tallowate", "Sodium Cocoate", "Glycerin", "Fragrance", "Optical Brightener",
          "Violet 10"],
         "grocery", "reported", ZOTE_DIRECTIONS,
         2, "extrapolated", ZOTE_EXPANSION,
         BASE_BASIS + "The pink bar is the brand's highest-volume line and about 15% of the "
                      "brand's sales leave Mexico, primarily to the United States, so the product "
                      "is genuinely common in US households even though no US penetration figure "
                      "is published. The figure is a share of the laundry-bar segment, not of all "
                      "US households.",
         subs=[{"name": "Zote Laundry Soap, White",
                "tier": "grocery",
                "note": "Same brand, same price, same store. Drops the Violet 10 (Rhodamine B) "
                        "whitening dye, which is graded serious eye damage and harmful to aquatic "
                        "life. The undisclosed optical brightener remains."},
               {"name": "Kirk's Original Coco Castile Soap",
                "tier": "apothecary-bulk",
                "note": "Vegetable-oil bar with a published ingredient list and no dye and no "
                        "brightener. About the same price per bar."}],
         heritage=(1970, "A Mexican laundry bar from 1970, sold from Ecatepec, that became a "
                         "standard stain-treatment bar in US households long before any brand "
                         "marketed to them.")),

    prod("Zote Laundry Soap, White", "Zote", "Laundry",
         ["Sodium Tallowate", "Sodium Cocoate", "Fragrance", "Optical Brightener"],
         "grocery", "reported", ZOTE_DIRECTIONS,
         1, "extrapolated", ZOTE_EXPANSION,
         BASE_BASIS + "The white bar is a smaller line than the pink bar, and about 15% of the "
                      "brand's sales leave Mexico primarily to the United States. The figure is a "
                      "share of the laundry-bar segment, not of all US households.",
         subs=[{"name": "Kirk's Original Coco Castile Soap",
                "tier": "apothecary-bulk",
                "note": "Same price point, vegetable-oil bar, no optical brightener. The brightener "
                        "in this bar is a class term with the identity withheld, which is why it "
                        "is graded unclassified rather than safe."}],
         heritage=(1970, "The same 1970 laundry bar in its white line, minimum 66% fatty acid "
                         "content.")),

    # ---- apothecary / bulk ----------------------------------------------
    prod("Kirk's Original Coco Castile Soap", "Kirk's", "Specialty",
         ["Sodium Cocoate", "Water", "Glycerin", "Sodium Chloride", "Sodium Gluconate",
          "Fragrance"],
         "apothecary-bulk", "reported", KIRKS_ING,
         1, "extrapolated", INDEXBOX,
         BASE_BASIS + "A bar-soap brand sold in grocery and drug channels since 1839; the "
                      "category is broad but this brand's own share of it is small. Channel share, "
                      "not a measured product share.",
         subs=[],
         heritage=(1839, "Castile soap made with coconut oil since 1839, one of the few bars in "
                         "the database whose full ingredient list is short enough to read on the "
                         "package."),
         tier_note="Filled under SPX-004 as a second castile brand alongside Dr. Bronner's; the "
                   "bin is ingredient-tier soap sold on chemistry rather than brand story."),
]


def main():
    prods = json.loads((DATA / "products.json").read_text(encoding="utf-8"))
    ings = json.loads((DATA / "ingredients.json").read_text(encoding="utf-8"))
    owners = json.loads((DATA / "owners.json").read_text(encoding="utf-8"))

    existing = {p.get("name") for p in prods}
    added_ings = []
    for name, rec in NEW_INGS.items():
        if name not in ings:
            ings[name] = rec
            added_ings.append(name)

    added_prods = []
    for p in PRODUCTS:
        if p["name"] in existing:
            continue
        prods.append(p)
        added_prods.append(p["name"])

    added_owners = []
    for name, rec in NEW_OWNERS.items():
        if name not in owners["owners"]:
            owners["owners"][name] = rec
            added_owners.append(name)

    # Whole Foods now has a verified parent; it must not sit in "no parent found".
    ind = owners.get("independents", {}).get("brands", [])
    if "Whole Foods" in ind:
        ind.remove("Whole Foods")
        owners["independents"]["brands"] = ind

    # Dollar Tree owns the Power Force house brand as well as Homeline.
    dt = owners["owners"].get("Dollar Tree, Inc.")
    if dt and "Power Force" not in dt["brands"]:
        dt["brands"].append("Power Force")
        dt["detail"] = ("Owns Family Dollar and the Homeline and Power Force house brands. The FDA "
                        "drug label for Power Force antibacterial hand soap names Korex Chicago "
                        "LLC as the labeler of record, so the contract manufacturer is visible "
                        "underneath the retail brand.")

    # Idempotent backfill: if a product is already present, still carry the
    # tier sourcing across (the first run of this script wrote tier_ev without
    # tier_src, which reopened the tier_src lane with 11 products).
    backfilled = 0
    by_name = {p["name"]: p for p in PRODUCTS}
    for p in prods:
        src = by_name.get(p.get("name"))
        if src and p.get("tier_ev") == "reported" and not p.get("tier_src"):
            p["tier_src"] = src["tier_src"]
            backfilled += 1
    if backfilled:
        print(f"tier_src backfilled on {backfilled} existing products")

    (DATA / "products.json").write_text(
        json.dumps(prods, indent=1, ensure_ascii=False), encoding="utf-8")
    (DATA / "ingredients.json").write_text(
        json.dumps(ings, indent=1, ensure_ascii=False), encoding="utf-8")
    (DATA / "owners.json").write_text(
        json.dumps(owners, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"products added: {len(added_prods)} -> {len(prods)} total")
    for n in added_prods:
        print("  +", n)
    print(f"ingredients added: {len(added_ings)} -> {len(ings)} total")
    print("  " + ", ".join(added_ings))
    print(f"owners added: {len(added_owners)} -> {len(owners['owners'])} total")
    print("  " + ", ".join(added_owners))


if __name__ == "__main__":
    main()
