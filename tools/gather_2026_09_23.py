#!/usr/bin/env python3
"""Gather run 2026-09-23: four popular US cleaning products with public disclosures.

Every ingredient list below is transcribed from a manufacturer disclosure (SmartLabel,
California Cleaning Product Right to Know, or a manufacturer SDS). No grade is invented;
grades come from PubChem PUG View (ECHA C&L notifier consensus) via tools/ghs_lookup.py
with the >=40% house threshold applied. UVCB/polymer substances with no PubChem CID are
recorded Not Classified / Extrapolated with an explicit sourcing note.

Run: python3 tools/gather_2026_09_23.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
TODAY = "2026-09-23"

# ------------------------------------------------------------------ new ingredients
NEW_ING = {
    # --- the four quaternary ammonium actives shared by Lysol Laundry Sanitizer and
    # Microban 24. Keys match the spelling already referenced by the Great Value
    # products, so this also closes those unknown-ingredient validation errors.
    "Didecyldimethylammonium Chloride": {
        "g": "H302,H314,H400",
        "s": "Quaternary ammonium disinfectant active. Corrosive, harmful if swallowed, very toxic to aquatic life.",
        "ev": "High",
        "gr": {"derm": "F", "env": "F", "work": "D"},
        "impacts": ["aqua", "derm"],
        "note": "Graded from PubChem GHS (CID 23558, returned title 'Didecyldimethylammonium Chloride' - matches). Dominant ECHA C&L notifier block: H314 100% (corrosive -> derm F), H302 85.8% (harmful if swallowed -> work D), H400 47.6% (very toxic to aquatic life -> env F). H318 28.4%, H410 22.4% and H411 34.7% fall below the house >=40% consensus threshold and are not graded. PubChem's aggregated view also lists H317/H330/H370/H373 without notifier percentages - noted, not graded. Alias: also written 'Didecyl Dimethyl Ammonium Chloride' (Reckitt and P&G SmartLabel).",
    },
    "Dioctyldimethylammonium Chloride": {
        "g": "H301,H310,H314,H400",
        "s": "Quaternary ammonium disinfectant active. Corrosive, fatal in contact with skin, very toxic to aquatic life.",
        "ev": "High",
        "gr": {"derm": "F", "env": "F", "work": "F"},
        "impacts": ["aqua", "derm"],
        "note": "Graded from PubChem GHS (CID 62581, returned title 'Dioctyldimethylammonium chloride' - matches). ECHA C&L notifier consensus: H314 99.6% (corrosive -> derm F), H400 90.1% (very toxic to aquatic life -> env F), H301 62.8% (toxic if swallowed) and H310 62.4% (fatal in contact with skin) -> work F. H410 57.4% also clears the threshold but env is already F; H318 62.4% would only reach derm D against an existing F; H302 36.8% is below threshold. Alias: also written 'Dioctyl Dimethyl Ammonium Chloride' (Reckitt and P&G SmartLabel).",
    },
    "Octyl Decyl Dimethyl Ammonium Chloride": {
        "g": "Not Classified",
        "s": "Quaternary ammonium disinfectant active. ECHA C&L notifier consensus sits below the house grading threshold.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem GHS (CID 61906, returned title 'Decyl dimethyl octyl ammonium chloride' - matches the disclosed substance). ECHA C&L notifier consensus reports H302, H314 and H400 each at 31.4% - all below the house >=40% threshold, so no dimension grade is justified. The substance is a BAC-type quaternary ammonium disinfectant active whose class hazards are corrosive and aquatic toxicity. Recorded unclassified rather than extrapolated because a real CID exists.",
    },
    "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride": {
        "g": "Extrapolated",
        "s": "Quaternary ammonium disinfectant (BAC-type). Class hazards: corrosive, aquatic toxicity, respiratory/allergic sensitization.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "UVCB benzalkonium chloride blend (CAS 68424-85-1) - PubChem name lookup resolves no CID (PUG REST 404). Recorded extrapolated, not graded, matching the existing 'Alkyl C12-18 Dimethylbenzyl Ammonium Chloride' entry. Disclosed by Walmart (California Cleaning Product Right to Know) for Great Value Lemon Scent and by P&G SmartLabel for Microban 24.",
    },
    # --- surfactants / polymers
    "C12-15 Alcohols Ethoxylated": {
        "g": "Extrapolated",
        "s": "Alcohol ethoxylate nonionic surfactant (C12-15). UVCB; no discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "UVCB (CAS 68131-39-5) - no PubChem entry (PUG REST 404). Class-analogous to the existing 'C10-16 Pareth' and 'Ethoxylated Alcohol' entries (derm C, env C; trace 1,4-dioxane from ethoxylation). Recorded extrapolated, not graded. Disclosed by Henkel for all free clear.",
    },
    "Alkylbenzene Sulfonic Acid": {
        "g": "Extrapolated",
        "s": "Linear alkylbenzene sulfonic acid (LAS, acid form). UVCB; class hazards: skin/eye irritant, aquatic toxicity.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "UVCB (CAS 68584-22-5) - no PubChem entry (PUG REST 404). Class-analogous to the existing 'Sodium Dodecylbenzenesulfonate' entry (derm D, env C). Recorded extrapolated, not graded. Disclosed by KIK for Comet with Bleach Cleanser.",
    },
    "Polyethyloxazoline": {
        "g": "Not Classified",
        "s": "Polymeric additive (UVCB). No discrete PubChem CID.",
        "ev": "Low",
        "gr": {},
        "impacts": [],
        "note": "Polymer/UVCB - PubChem name lookup resolves no CID (PUG REST 404) and therefore no GHS classification. Recorded unclassified rather than assigned an unsourced grade; high-MW polymers are generally not bioavailable. Disclosed by P&G SmartLabel for Microban 24.",
    },
    "Sodium Phosphate": {
        "g": "Not Classified",
        "s": "Inorganic phosphate builder, disclosed by generic name only (mono-, di- or trisodium phosphate not specified).",
        "ev": "Low",
        "gr": {},
        "impacts": [],
        "note": "Disclosed by Walmart (California Cleaning Product Right to Know) for Great Value Clear Ammonia as 'Sodium Phosphate' - a generic name. PubChem resolves 'Trisodium Phosphate' (CID 24243) with H315 90.2%, H319 90.1%, H335 85.1%, but the disclosure does not say which sodium phosphate salt is used, so no grade is assigned to the generic name. Recorded unclassified rather than graded on a guess.",
    },
}

# ------------------------------------------------------------------ new products
NEW_PRODUCTS = [
    {
        "name": "all free clear Original Concentrated Liquid Laundry Detergent",
        "brand": "Henkel",
        "cat": "Laundry Detergent",
        "ings": [
            "Water",
            "C12-15 Alcohols Ethoxylated",
            "Sodium Laureth Sulfate",
            "Trisodium Dicarboxymethyl Alaninate",
            "Ethanol",
            "Polyethyleneimine Alkoxylated",
            "Sodium Carbonate",
            "Hydrophobically Modified Acrylate/Styrene Copolymer",
            "Fatty Acids, C8-18 and C18-Unsaturated Sodium Salts",
            "Benzisothiazolinone",
        ],
        "source": "Henkel ingredient disclosure (all-laundry.com product page, CAS-numbered)",
        "source_url": "https://www.all-laundry.com/products/concentrated-laundry-detergent/all-free-clear-concentrated-liquid-laundry-detergent-the-original.html",
        "note": "The leading US free-and-clear liquid detergent - marketed as the #1 dermatologist/allergist/pediatrician-recommended brand for sensitive skin, 100% free of perfumes and dyes, and EPA Safer Choice certified. The CAS-numbered disclosure shows what 'free and clear' does and does not mean: no fragrance and no dye, but still an alcohol-ethoxylate surfactant, sodium laureth sulfate, a polymeric anti-redeposition agent and benzisothiazolinone (a potent contact allergen and aquatic toxicant). Henkel's own SDS lists the C12-15 alcohol ethoxylate at 10-<20% and sodium laureth sulfate and sodium carbonate each at 1-<5%. Safer Choice evaluates the formula Henkel represented to it; EPA states it did not independently analyse the ingredients.",
        "exposure_basis": "searched for a published per-product US household penetration figure; none exists in the open literature. Left as a research gap rather than estimated.",
    },
    {
        "name": "Comet with Bleach Cleanser",
        "brand": "KIK",
        "cat": "Abrasive Cleanser",
        "ings": [
            "Calcium Carbonate",
            "Sodium Carbonate",
            "Alkylbenzene Sulfonic Acid",
            "Trichloroisocyanuric Acid",
            "Fragrance",
            "Pigment Green 7",
            "Water",
        ],
        "source": "KIK Consumer Products ingredient disclosure (California Cleaning Product Right to Know, 12/6/2019)",
        "source_url": "https://www.kikcorp.com/wp-content/uploads/2019/05/Comet_with-Bleach-25oz_8-10003-44005-1.pdf",
        "note": "The iconic scouring-powder cleanser, and the clearest example of the difference between 'with bleach' and 'with chlorine bleach' in a US household product. The bleaching agent here is trichloroisocyanuric acid (a chlorinated isocyanurate, CAS 87-90-1) - an oxidizer and aquatic toxicant, not sodium hypochlorite. The grit is calcium carbonate; the surfactant is a linear alkylbenzene sulfonic acid (LAS). A Canadian SDS for the same product line puts calcium carbonate at 80-100% and notes that crystalline silica may be present, with an explicit warning that long-term overexposure may produce evidence of dust in the lungs. Fragrance composition is not disclosed (listed only as 'Fragrance Ingredients - Not Available').",
        "exposure_basis": "searched for a published per-product US household penetration figure; none exists in the open literature. Left as a research gap rather than estimated.",
    },
    {
        "name": "Lysol Laundry Sanitizer, Free & Clear",
        "brand": "Reckitt",
        "cat": "Laundry",
        "ings": [
            "Water",
            "Didecyldimethylammonium Chloride",
            "Dioctyldimethylammonium Chloride",
            "Octyl Decyl Dimethyl Ammonium Chloride",
            "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride",
            "C10-16 Pareth",
            "Sodium Bicarbonate",
            "Sodium Carbonate",
            "Ethanol",
            "Isopropyl Alcohol",
        ],
        "source": "Reckitt SmartLabel public ingredient disclosure (productLineId 2504)",
        "source_url": "https://www.rbnainfo.com/smart-label.php?productLineId=2504",
        "note": "The additive category that did not exist a generation ago: a laundry sanitizer you add to the rinse, for people who wash in cold water or cannot use hot water. The 'Free & Clear' version is fragrance-free but the active ingredients are the same four quaternary ammonium compounds as the scented versions - three of the four are flagged on California's Priority Chemicals list, and two carry an AOEC asthmagen designation. Quats are not removed by rinsing the way soap is; they remain on the fabric, which is the point of the product and also the exposure. Disclosed by Reckitt on its SmartLabel in descending weight order.",
        "exposure_basis": "searched for a published per-product US household penetration figure; none exists in the open literature. Left as a research gap rather than estimated.",
    },
    {
        "name": "Microban 24 Hour Multi-Purpose Cleaner and Disinfectant Spray, Fresh Scent",
        "brand": "P&G",
        "cat": "Disinfectant",
        "ings": [
            "Water",
            "Didecyldimethylammonium Chloride",
            "Dioctyldimethylammonium Chloride",
            "Octyl Decyl Dimethyl Ammonium Chloride",
            "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride",
            "Dipropylene Glycol Butyl Ether",
            "Polyethyloxazoline",
            "Alcohols, C9-11, ethoxylated",
            "Triethanolamine",
            "Fragrance",
        ],
        "source": "P&G SmartLabel public ingredient disclosure (UPC 00037000485896, updated 2024-04-18)",
        "source_url": "https://smartlabel.pg.com/en-us/00037000485896.html",
        "note": "A disinfectant spray whose claim is residual action - it is marketed as killing 99.9% of bacteria and cold/flu viruses for up to 24 hours on a hard surface, touch after touch. The mechanism is a quaternary ammonium film left behind on the surface, so the four quat actives are the product. P&G's own FAQ is careful with the claim: the 24-hour residual is against Staphylococcus aureus and Enterobacter aerogenes only, and it explicitly does not provide 24-hour residual protection against cold and flu viruses. The fragrance blend is disclosed only as 'Fragrance'.",
        "exposure_basis": "searched for a published per-product US household penetration figure; none exists in the open literature. Left as a research gap rather than estimated.",
    },
]


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def save(name, obj):
    (DATA / name).write_text(
        json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main():
    ing = load("ingredients.json")
    prod = load("products.json")

    added_ing, skipped_ing = [], []
    for k, v in NEW_ING.items():
        if k in ing:
            skipped_ing.append(k)
            continue
        ing[k] = v
        added_ing.append(k)

    existing = {(p["name"], p["brand"]) for p in prod}
    added_prod, skipped_prod = [], []
    for p in NEW_PRODUCTS:
        if (p["name"], p["brand"]) in existing:
            skipped_prod.append(p["name"])
            continue
        rec = {
            "name": p["name"],
            "brand": p["brand"],
            "cat": p["cat"],
            "safe": None,
            "ings": p["ings"],
            "heritage": False,
            "source": p["source"],
            "source_url": p["source_url"],
            "added": TODAY,
            "updated": TODAY,
            "note": p["note"],
            "owner": None,
            "owner_ev": "untested",
            "owner_src": None,
            "tier": None,
            "tier_ev": "untested",
            "substitutes": [],
            "exposure": None,
            "exposure_ev": "untested",
            "exposure_src": None,
            "conc": None,
            "conc_src": None,
            "conc_ev": "untested",
            "grade_as_sold": None,
            "grade_as_sold_src": None,
            "strength_disclosure": "not_reviewed",
            "exposure_basis": p["exposure_basis"],
        }
        prod.append(rec)
        added_prod.append(p["name"])

    # every ingredient a product references must exist
    missing = sorted({i for p in prod for i in p["ings"] if i not in ing})

    save("ingredients.json", ing)
    save("products.json", prod)

    print(json.dumps({
        "added_ingredients": added_ing,
        "skipped_ingredients": skipped_ing,
        "added_products": added_prod,
        "skipped_products": skipped_prod,
        "products": len(prod),
        "ingredients": len(ing),
        "unresolved_ingredient_refs": missing,
    }, indent=1))


if __name__ == "__main__":
    main()
