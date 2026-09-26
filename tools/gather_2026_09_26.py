#!/usr/bin/env python3
"""Daily gather (2026-09-26, 10:00Z maintenance lane): four high-volume US products
that were missing from the database, plus the ingredient records they need.

Every ingredient list below is copied from a manufacturer disclosure read on
2026-09-26:

  - Clorox SmartLabel for Clorox 2 for Colors Stain Remover and Laundry Additive,
    Original, 22 fl oz (UPC 044600300368, information updated 2024-08-13)
  - Clean Control Corporation Product Right-To-Know Ingredient Disclosure
    (CA SB-258 compliant) for OdoBan Ready-to-Use (Original Eucalyptus Scent),
    item 10062, revised 2019-07-29
  - Reckitt SmartLabel for Vanish Oxi Action In-Wash Fabric Stain Remover
    (productLineId 1494, UPC 0-19200-93854-9)
  - P&G SmartLabel for the Gain Ultra Dishwashing Liquid family; the Original
    Scent variant's list is the one transcribed by two independent retailers
    (HEB, Super 1 Foods) from the P&G label, and matches the P&G SmartLabel
    sibling variant (Lavender, UPC 00037000976240) ingredient for ingredient
    apart from the colorants.

Two source spellings are mapped to canonical keys rather than minted as new
keys (see each product's `disclosure_note`): "C10-16 Alkyldimethylamine Oxide"
-> Alkyldimethylamine Oxide, and "Colorants"/"Fragrances" -> Colorant/Fragrance.

Grading follows the house rule (docs/source-policy.md, docs/methodology.md):
only H-codes at >=40% ECHA C&L notifier consensus drive a dimension grade, read
from PubChem PUG View. UVCB / polymer / undisclosed substances with no discrete
PubChem CID are recorded "Extrapolated" with an explicit sourcing note, never
graded. Fragrance components are listed individually where the disclosure lists
them individually (the DB's existing fragrance-allergen pattern).

Run: python3 tools/gather_2026_09_26.py
Then: python3 build.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
TODAY = "2026-09-26"

CLOROX2 = ("https://smartlabel.labelinsight.com/product/6096212/ingredients")
ODOBAN = ("https://odobanpro.com/wp-content/uploads/2022/05/"
          "910062-RTU-Eucalyptus-7-29-19-Ingredients-1.pdf")
VANISH = "https://www.rbnainfo.com/product.php?productLineId=1494"
GAIN = "https://www.heb.com/product-detail/gain-ultra-original-scent-dish-soap/1414999"

BASE_BASIS = ("searched for a published per-product US household penetration figure; none "
              "exists in the open literature, so the estimate is derived from category "
              "penetration times the brand's share of its channel. Rounded to one "
              "significant figure. ")


# ---------------------------------------------------------------- ingredients
NEW_INGS = {
    "Isopropyl Myristate": {
        "g": "Not Classified",
        "s": "No GHS hazard criteria met at the house threshold (skin-irritant notification below 40% consensus).",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "Graded from PubChem GHS (CID 8042, title 'Isopropyl Myristate'): the ECHA C&L "
                "notifier consensus reports H315 at only 15.6%, below the 40% house bar, so no "
                "dimension grade is justified. Recorded Not Classified rather than graded on a "
                "sub-threshold signal. Disclosed by Clorox SmartLabel for Clorox 2 for Colors "
                "(Original).",
    },
    "Confidential Stabilizer Package": {
        "g": None,
        "s": "Undisclosed stabilizer blend. Named on the manufacturer disclosure with no composition.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "Undisclosed component. Clorox SmartLabel for Clorox 2 for Colors lists "
                "'Confidential Stabilizer Package' by name only, with no CAS number and no "
                "composition, so no GHS grade can be resolved. Recorded with g null rather than a "
                "guess, matching the existing 'Colorant' entry. This is a disclosure gap, not a "
                "data gap.",
    },
    "alpha-Isomethyl Ionone": {
        "g": "H315,H317,H319,H411",
        "s": "Fragrance ketone (ionone family). Skin sensitizer; toxic to aquatic life with long lasting effects.",
        "ev": "High",
        "gr": {"derm": "D", "env": "D"},
        "impacts": ["allerg", "aqua", "derm"],
        "note": "Graded from PubChem GHS (CID 5372174, CAS 127-51-5, title "
                "'3-Methyl-4-(2,6,6-trimethyl-2-cyclohexen-1-yl)-3-buten-2-one'): ECHA C&L "
                "notifier consensus H317 88.6%, H315 78.1%, H319 70.7% -> derm D + allerg; "
                "H411 87.7% -> env D. H412 (10.2%) is below the 40% bar. An EU fragrance "
                "allergen (Reg. 1223/2009 Annex III) with no equivalent US cleaning-product "
                "labelling requirement. Disclosed as a fragrance allergen by Clean Control "
                "Corporation in the CA SB-258 declaration for OdoBan Ready-to-Use (Original "
                "Eucalyptus Scent).",
    },
    "Amyl Cinnamal": {
        "g": "H317,H411",
        "s": "Fragrance aldehyde (alpha-amyl cinnamaldehyde). Skin sensitizer; toxic to aquatic life with long lasting effects.",
        "ev": "High",
        "gr": {"derm": "D", "env": "D"},
        "impacts": ["allerg", "aqua", "derm"],
        "note": "Graded from PubChem GHS (CID 31209, CAS 122-40-7, title 'Amylcinnamaldehyde'): "
                "ECHA C&L notifier consensus H317 94.2% -> derm D + allerg; H411 98.2% -> env D. "
                "H315 and H400/H410 appear only in non-consensus blocks without a percentage and "
                "do not drive grades. An EU fragrance allergen (Reg. 1223/2009 Annex III). "
                "Disclosed as a fragrance allergen by Clean Control Corporation in the CA SB-258 "
                "declaration for OdoBan Ready-to-Use (Original Eucalyptus Scent).",
    },
    "TAED": {
        "g": "Not Classified",
        "s": "No GHS hazard criteria met (unanimous not-classified per ECHA C&L via PubChem).",
        "ev": "High",
        "gr": {},
        "impacts": [],
        "note": "Graded from PubChem GHS (CID 66347, CAS 10543-57-4, title "
                "'Tetraacetylethylenediamine'): ECHA C&L notifier consensus reports no hazard "
                "criteria met by 435 of 435 companies. Recorded Not Classified. Bleach activator "
                "in oxygen-bleach laundry products; disclosed by Reckitt SmartLabel for Vanish "
                "Oxi Action In-Wash Fabric Stain Remover.",
    },
    "Ethoxydiglycol": {
        "g": "Not Classified",
        "s": "Glycol ether (fragrance component). Not classified at the house threshold; a low-consensus organ-toxicity notification exists.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "Graded from PubChem GHS (CID 8146, CAS 111-90-0, title 'Diethylene Glycol "
                "Monoethyl Ether'): the ECHA C&L aggregate reports no hazard criteria met by 4397 "
                "of 4862 reports (90.4%). 11 notifications covering 465 of 4862 reports (9.6%) "
                "carry H227, H320 and H372 - all far below the 40% house bar, so no dimension "
                "grade is justified. H372 (organ damage on prolonged or repeated exposure) is "
                "noted here rather than graded, because a 9.6% notification ratio is not a "
                "consensus. Disclosed as a fragrance component by Reckitt SmartLabel for Vanish "
                "Oxi Action In-Wash Fabric Stain Remover; the disclosure flags it on California's "
                "toxic air contaminant list.",
    },
}


# ------------------------------------------------------------------ products
def prod(name, brand, cat, ings, tier, tier_ev, tier_src, exposure, exposure_ev,
         exposure_src, exposure_basis, subs=None, no_sub=None, tier_note=None,
         heritage=None, owner=None, owner_ev="untested", owner_src=None,
         disclosure_note=None):
    p = {
        "name": name,
        "brand": brand,
        "cat": cat,
        "safe": None,
        "ings": ings,
        "added": TODAY,
        "updated": TODAY,
        "owner": owner,
        "owner_ev": owner_ev,
        "owner_src": owner_src,
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
    if disclosure_note:
        p["disclosure_note"] = disclosure_note
    return p


PRODUCTS = [
    prod("Clorox 2 for Colors Stain Remover & Laundry Additive, Original", "Clorox",
         "Laundry",
         ["Water", "Hydrogen Peroxide", "Myristamine Oxide", "Alkylbenzene Sulfonic Acid",
          "Confidential Stabilizer Package", "Disodium Distyrylbiphenyl Disulfonate",
          "Sodium Chloride", "Dipropylene Glycol", "Isopropyl Myristate", "Colorant",
          "Polyoxyalkylene Substituted Chromophore", "Sodium Hydroxide", "Fragrance",
          "Linalool"],
         "mass", "reported", CLOROX2,
         10, "extrapolated", CLOROX2,
         BASE_BASIS + "Clorox 2 is the leading color-safe bleach/booster in US laundry and this "
                      "is its mainstream scented liquid; the estimate stops at the brand's share "
                      "of the mass channel rather than a measured product share.",
         subs=[{"name": "Clorox 2 for Colors Stain Remover and Laundry Additive, Free and Clear",
                "tier": "mass",
                "note": "Same brand and same SmartLabel family (UPC 044600314730) with no "
                        "fragrance and no colorant. Removes the fragrance block (including "
                        "linalool) and both chromophore colorants; still carries hydrogen "
                        "peroxide and the confidential stabilizer package."},
               {"name": "Hydrogen Peroxide 3% (drugstore)",
                "tier": "apothecary-bulk",
                "note": "The same active (hydrogen peroxide) at a known 3% concentration, used "
                        "as a pre-treatment. Avoids the undisclosed stabilizer package, the "
                        "optical brightener, the fragrance and the colorants; no color-boosting "
                        "or anti-redeposition function."}],
         owner="Clorox", owner_ev="reported", owner_src=CLOROX2,
         tier_note="A hydrogen-peroxide color-safe bleach. The disclosure names an undisclosed "
                   "'Confidential Stabilizer Package' with no CAS number, and lists linalool as "
                   "an EU fragrance allergen."),

    prod("OdoBan Ready-to-Use Multi-Purpose Disinfectant & Deodorizer, Original Eucalyptus Scent",
         "Clean Control Corporation", "Disinfectant",
         ["Water", "Isopropanol", "Dipropylene Glycol Butyl Ether",
          "C12-15 Alcohols Ethoxylated", "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride",
          "Lauramine Oxide", "Fragrance", "Tetrasodium EDTA", "DMDM Hydantoin",
          "alpha-Isomethyl Ionone", "Amyl Cinnamal", "Citronellol", "Geraniol", "Linalool"],
         "mass", "reported", ODOBAN,
         4, "extrapolated", ODOBAN,
         BASE_BASIS + "OdoBan is a long-standing national disinfectant/deodorizer sold through "
                      "mass, grocery and janitorial channels; the estimate stops at the brand's "
                      "share of the category rather than a measured product share.",
         subs=[{"name": "Seventh Generation All-Purpose Cleaner, Free & Clear",
                "tier": "natural",
                "note": "Fragrance-free and quat-free. Avoids the benzalkonium active, the "
                        "DMDM hydantoin formaldehyde releaser and the five fragrance allergens; "
                        "not an EPA-registered disinfectant, so it does not carry kill claims."},
               {"name": "Distilled White Vinegar (5%)",
                "tier": "apothecary-bulk",
                "note": "Diluted and used as a general acid cleaner. Avoids every disclosed "
                        "ingredient here; no disinfectant registration and no residual "
                        "antimicrobial action."}],
         owner="Clean Control Corporation", owner_ev="reported", owner_src=ODOBAN,
         tier_note="A quaternary-ammonium disinfectant/deodorizer. The disclosure lists five "
                   "fragrance allergens individually and includes DMDM hydantoin, a "
                   "formaldehyde-releasing preservative."),

    prod("Vanish Oxi Action In-Wash Fabric Stain Remover", "Reckitt", "Stain & Odor",
         ["Sodium Carbonate", "Sodium Percarbonate", "Sodium Sulfate", "Sodium Bicarbonate",
          "Sodium Silicate", "C12-15 Alcohols Ethoxylated", "TAED", "Water",
          "Protease Enzyme", "Disodium Distyrylbiphenyl Disulfonate", "Fragrance",
          "Ethoxydiglycol"],
         "mass", "reported", VANISH,
         2, "extrapolated", VANISH,
         BASE_BASIS + "Vanish is Reckitt's global in-wash stain-remover brand and is sold in the "
                      "US through mass and grocery channels, but its US household penetration is "
                      "well below the domestic stain-remover leaders; the estimate stops at the "
                      "brand's share of that channel rather than a measured product share.",
         subs=[{"name": "OxiClean Versatile Stain Remover",
                "tier": "mass",
                "note": "The US market leader in the same class (sodium percarbonate oxygen "
                        "bleach). Same active chemistry; different surfactant, enzyme and "
                        "fragrance package."},
               {"name": "Sodium Percarbonate (bulk)",
                "tier": "apothecary-bulk",
                "note": "The same bleaching active sold as a single substance, dosed by weight. "
                        "Avoids the optical brightener, the enzyme, the fragrance and the glycol "
                        "ether; no TAED activator, so it needs warmer water to perform."}],
         owner="Reckitt", owner_ev="reported", owner_src=VANISH,
         tier_note="An oxygen-bleach in-wash booster (sodium percarbonate + TAED activator). The "
                   "disclosure flags the protease enzyme as an EU respiratory sensitizer and an "
                   "AOEC asthmagen, and ethoxydiglycol on California's toxic air contaminant list."),

    prod("Gain Ultra Dishwashing Liquid, Original Scent", "P&G", "Dish Soap",
         ["Water", "Sodium Lauryl Sulfate", "Alkyldimethylamine Oxide",
          "Sodium Laureth Sulfate", "Sodium Chloride", "Phenoxyethanol",
          "PEI-14 PEG-24/PPG-16 Copolymer", "Methylisothiazolinone", "Fragrance", "Colorant"],
         "mass", "reported", GAIN,
         8, "extrapolated", GAIN,
         BASE_BASIS + "Gain is one of the largest US dish-soap brands and this is its mainstream "
                      "original-scent liquid; the estimate stops at the brand's share of the "
                      "mass channel rather than a measured product share.",
         subs=[{"name": "Dawn Ultra Dishwashing Liquid",
                "tier": "mass",
                "note": "Same manufacturer and price class, different surfactant package. Both "
                        "carry the methylisothiazolinone preservative and a fragrance."},
               {"name": "Seventh Generation Dish Liquid, Free & Clear",
                "tier": "natural",
                "note": "Fragrance-free and dye-free. Avoids the fragrance block and the "
                        "colorant; a different (plant-derived) surfactant base."}],
         owner="P&G", owner_ev="reported", owner_src=GAIN,
         disclosure_note="Source spellings mapped to canonical keys: 'C10-16 Alkyldimethylamine "
                         "Oxide' -> Alkyldimethylamine Oxide; 'Colorants' -> Colorant; "
                         "'Fragrances' -> Fragrance.",
         tier_note="A mainstream hand dish liquid. The disclosure lists a colorant and a "
                   "fragrance with no component breakdown, so the fragrance allergens are not "
                   "enumerable from this source."),
]


def main():
    prods = json.loads((DATA / "products.json").read_text(encoding="utf-8"))
    ings = json.loads((DATA / "ingredients.json").read_text(encoding="utf-8"))

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

    (DATA / "products.json").write_text(
        json.dumps(prods, indent=1, ensure_ascii=False), encoding="utf-8")
    (DATA / "ingredients.json").write_text(
        json.dumps(ings, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"products added: {len(added_prods)} -> {len(prods)} total")
    for n in added_prods:
        print("  +", n)
    print(f"ingredients added: {len(added_ings)} -> {len(ings)} total")
    print("  " + ", ".join(added_ings))


if __name__ == "__main__":
    main()
