#!/usr/bin/env python3
"""Gather run 2026-09-24: four popular US cleaning products with public disclosures,
plus resolution of four unknown-ingredient validation errors inherited from the
spectrum lane.

Every ingredient list below is transcribed from a manufacturer SDS or a California
Cleaning Product Right to Know disclosure. No grade is invented; grades come from
PubChem PUG View (ECHA C&L notifier consensus) via tools/ghs_lookup.py with the >=40%
house threshold applied. UVCB/polymer substances with no PubChem CID are recorded
Not Classified / Extrapolated with an explicit sourcing note.

Two classes of unknown-ingredient error are resolved differently:
  (A) the substance is genuinely absent -> add it, honestly graded;
  (B) the product references a SPELLING VARIANT of an ingredient we already carry
      -> point the product at the canonical key and record the source's spelling in
      the product note. Minting a second key for one substance inflates the index and
      drifts (the repo already carries case-duplicate mirrors); it is not done here.

Run: python3 tools/gather_2026_09_24.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
TODAY = "2026-09-24"

# ------------------------------------------------------------------ new ingredients
NEW_ING = {
    "Compound Based on Anionic and Nonionic Surfactants": {
        "g": "Extrapolated",
        "s": "Undisclosed surfactant class - the disclosure names a category, not a substance.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "Disclosed by Delta Brands for PowerHouse All Purpose Cleaner with Bleach as the literal string 'Compound Based on Anionic and Nonionic Surfactants' - a class descriptor, not a chemical name, so no CAS and no PubChem entry exist to grade. Recorded extrapolated, not graded. Class hazards for an anionic/nonionic surfactant blend are skin/eye irritation and aquatic toxicity. The class-level disclosure is itself the finding: the product names its bleach and its caustic but not its surfactant.",
    },
    "Benzenesulfonic acid, C10-16-alkyl derivs., magnesium salts": {
        "g": "Not Classified",
        "s": "Magnesium salt of linear alkylbenzene sulfonate (LAS). Sub-threshold notifier consensus.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "UVCB (CAS 68584-26-9) with no discrete PubChem record; looked up by the class analog 'Magnesium dodecyl benzene sulfonate' (CID 168704, returned title matches the class), whose ECHA C&L notifier block reports H302, H315 and H319 each at 16.7% - all below the house >=40% consensus threshold, so no dimension grade is justified. Class-analogous to the existing 'Sodium Dodecylbenzenesulfonate' entry (derm D, env C). Disclosed by Colgate-Palmolive for Ajax Dishwashing Liquid.",
    },
    "C12-14 Alcohol EO 3:1 Sodium Sulfate": {
        "g": "Extrapolated",
        "s": "Alcohol ethoxylate sulfate (C12-14, 3 EO) sodium salt. UVCB; class hazards: skin/eye irritant, aquatic toxicity.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "UVCB - PubChem name lookup resolves no CID (PUG REST 404). Class-analogous to the existing 'Sodium Laureth Sulfate' and 'Ethoxylated Alcohol' entries (derm C, env C; trace 1,4-dioxane from ethoxylation). Recorded extrapolated, not graded. Disclosed by Colgate-Palmolive for Ajax Dishwashing Liquid.",
    },
    "TEA Dodecylbenzene Sulfonate": {
        "g": "H315,H319",
        "s": "Triethanolamine salt of linear alkylbenzene sulfonate. Causes skin and serious eye irritation.",
        "ev": "Medium",
        "gr": {"derm": "D"},
        "impacts": ["derm"],
        "note": "Graded from PubChem GHS (CID 33782, returned title 'dodecylbenzenesulfonic acid, triethanolamine salt' - matches the disclosed substance). ECHA C&L notifier consensus: H315 87.1% (skin irritation -> derm D) and H319 55.2% (serious eye irritation -> derm D). H301 15.2%, H302 20.6% and H318 26.3% all fall below the house >=40% threshold and are not graded. Disclosed by Colgate-Palmolive for Ajax Dishwashing Liquid.",
    },
    "Acrylic Polymer": {
        "g": "Not Classified",
        "s": "Polymeric soil-suspension agent. No discrete PubChem CID.",
        "ev": "Low",
        "gr": {},
        "impacts": [],
        "note": "Polymer - PubChem name lookup resolves no CID (PUG REST 404) and therefore no GHS classification. Recorded unclassified rather than assigned an unsourced grade; high-MW polymers are generally not bioavailable. The California disclosure states the polymer carries no free acrylic acid. Disclosed by Folex for Instant Carpet Spot Remover.",
    },
    "Primary Amine": {
        "g": "Extrapolated",
        "s": "Undisclosed primary amine used as a pH buffer - the disclosure names a class, not a substance.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "Disclosed by Folex on its California Ingredient Disclosure as 'Primary Amine (No DEA)' with the CAS withheld - a class descriptor, so no specific substance can be graded. Recorded extrapolated, not graded; class hazards for a primary amine buffer are skin/eye irritation. The '(No DEA)' qualifier is the manufacturer ruling out one specific member of the class, not identifying the one used.",
    },
    "Distillates (petroleum), hydrotreated middle": {
        "g": "Not Classified",
        "s": "Hydrotreated middle petroleum distillate (UVCB). Current manufacturer SDS reports no hazardous components requiring reporting.",
        "ev": "Low",
        "gr": {},
        "impacts": [],
        "note": "UVCB (CAS 64742-46-7) - no discrete PubChem record to grade. The current Reckitt SDS for Old English Lemon Oil reports this as the only component (>60%) and states no additional ingredients are classified as hazardous. Recorded unclassified per the current SDS. An earlier (2008) SDS for the same product line carried 'DANGER: HARMFUL OR FATAL IF SWALLOWED - contains petroleum distillates greater than 10%', an aspiration-hazard warning that does not map to any of the house grade dimensions; the two SDS versions disagree and both are noted rather than reconciled.",
    },
}

# ------------------------------------------------------------------ new products
NEW_PRODUCTS = [
    {
        "name": "Liquid-Plumr Pro-Strength Clog Destroyer Gel with Pipeguard",
        "brand": "Clorox",
        "cat": "Drain",
        "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide", "Surfactant"],
        "source": "Manufacturer SDS (The Clorox Company, document US001283, issued 28-May-2021)",
        "source_url": "https://www.thecloroxcompany.com/wp-content/uploads/2021/07/USA001283-Pro-Strength-Liquid-Plumr-Clog-Destroyer-Gel-with-Pipeguard_1.pdf",
        "note": "The best-selling gel drain opener, and a two-active product: sodium hypochlorite at 5-10% and sodium hydroxide at 1-5%, with the rest water and an unspecified 'biodegradable surfactants' line. The label states the ingredients plainly ('CONTAINS: Sodium hypochlorite, sodium hydroxide and biodegradable surfactants'). The hazard is the combination, not either part alone: the SDS carries DANGER for skin corrosion and serious eye damage, and warns explicitly against use with ammonia, toilet-bowl cleaners or any other drain opener because of hazardous gas release. The SDS is written for workplace and emergency use and states it is not applicable to consumer use.",
    },
    {
        "name": "Ajax Dishwashing Liquid, Lemon",
        "brand": "Colgate-Palmolive",
        "cat": "Dish Soap",
        "ings": [
            "Water",
            "Benzenesulfonic acid, C10-16-alkyl derivs., magnesium salts",
            "C12-14 Alcohol EO 3:1 Sodium Sulfate",
            "Sodium Dodecylbenzenesulfonate",
            "TEA Dodecylbenzene Sulfonate",
        ],
        "source": "Manufacturer SDS (Colgate-Palmolive, SDS 660000000049, revision 2016-03-21)",
        "source_url": "https://sanjacinto-keenan.safeschoolssds.com/document/repo/dc65a07f-0279-49fe-a43b-b9e9fcd37713",
        "note": "A top-selling value dish liquid that had no entry in the database. The SDS is unusual for the category in that it is CAS-numbered and gives percentage bands: water 70-90%, a magnesium LAS 5-10%, a C12-14 alcohol ethoxylate sulfate 5-10%, and two LAS salts at 1-5% each. Colgate classifies the finished product as 'Not a hazardous substance or mixture' under GHS, and separately notes that the LAS component alone causes severe skin irritation and eye irritation reversing within 21 days - the finished-product call rests on dilution, not on the ingredients being mild. The product has not been tested as a whole; the manufacturer states the formula was reviewed by its own toxicologists.",
    },
    {
        "name": "Folex Instant Carpet Spot Remover",
        "brand": "Folex",
        "cat": "Carpet",
        "ings": [
            "Water",
            "Acrylic Polymer",
            "Trisodium Dicarboxymethyl Alaninate",
            "Ethoxylated Alcohol",
            "Primary Amine",
        ],
        "source": "California Ingredient Disclosure (Folex Company, all-sized containers)",
        "source_url": "https://folexcompany.com/wp-content/uploads/Ingredient-Disclosure-Instant-Carpet-Spot-Remover.pdf",
        "note": "A widely recommended carpet spotter, and a study in how much a 'California Ingredient Disclosure' actually discloses. Five lines: water, an acrylic polymer, a chelant, a surfactant and a pH buffer - and the CAS number is withheld for four of the five. The disclosure spells the chelant 'Trisodium Dicarboxy Alaninate'; it is recorded here under the canonical key for the same chelant family already in the database, and the surfactant under the canonical 'Ethoxylated Alcohol' key (the disclosure writes 'Ethoxylate Alcohol'). The manufacturer's own SDS classifies the product as non-hazardous with no components requiring reporting under 29 CFR 1910.1200, which is why the ingredient table is the only place the composition appears at all.",
        "disclosure_note": "Source spellings mapped to canonical keys: 'Trisodium Dicarboxy Alaninate' -> Trisodium Dicarboxymethyl Alaninate; 'Ethoxylate Alcohol' -> Ethoxylated Alcohol.",
    },
    {
        "name": "Old English Lemon Oil Furniture Polish",
        "brand": "Reckitt",
        "cat": "Polish",
        "ings": ["Distillates (petroleum), hydrotreated middle"],
        "source": "Manufacturer SDS (Reckitt, published via rbnainfo.com)",
        "source_url": "https://www.rbnainfo.com/productpro/getmsds/4000c754-a650-4bec-ac2c-e7449460b656",
        "note": "The classic lemon-oil furniture polish, and the clearest case in the database of a product named for something it does not primarily contain: the current SDS lists a single component, a hydrotreated middle petroleum distillate at >60%, and states that no other ingredient is classified as hazardous and therefore none is reported. There is no citrus oil in the disclosed composition. An earlier SDS for the same product line listed white mineral oil at 90-100% instead, so the carrier has changed across reformulations and both versions are on the record. The SDS carries no hazard classification for the distillate; the 2008 version of the same product line carried a 'harmful or fatal if swallowed' aspiration warning.",
    },
]


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def save(name, obj):
    (DATA / name).write_text(
        json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )


# Unknown-ingredient errors inherited from the spectrum lane, split by cause.
# (B) spelling variants of a key we already carry -> repoint the product reference.
VARIANT_REPOINT = {
    "Sodium C10-16 Alkylbenzenesulfonate": "Sodium (C10-16) Alkylbenzenesulfonate",
    "Sodium Xylene Sulfonate": "Sodium Xylenesulfonate",
    "Orange Oil Blend": "Orange Oil",
}


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

    # (B) repoint spelling variants to the canonical key
    repointed = []
    for p in prod:
        new_ings = []
        for i in p["ings"]:
            if i in VARIANT_REPOINT:
                repointed.append((p["name"], i, VARIANT_REPOINT[i]))
                new_ings.append(VARIANT_REPOINT[i])
            else:
                new_ings.append(i)
        p["ings"] = new_ings

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
            "exposure_basis": "searched for a published per-product US household penetration figure; none exists in the open literature. Left as a research gap rather than estimated.",
        }
        if "disclosure_note" in p:
            rec["disclosure_note"] = p["disclosure_note"]
        prod.append(rec)
        added_prod.append(p["name"])

    # every ingredient a product references must exist
    missing = sorted({i for p in prod for i in p["ings"] if i not in ing})

    save("ingredients.json", ing)
    save("products.json", prod)

    print(json.dumps({
        "added_ingredients": added_ing,
        "skipped_ingredients": skipped_ing,
        "repointed_variant_refs": repointed,
        "added_products": added_prod,
        "skipped_products": skipped_prod,
        "products": len(prod),
        "ingredients": len(ing),
        "unresolved_ingredient_refs": missing,
    }, indent=1))


if __name__ == "__main__":
    main()
