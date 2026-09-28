#!/usr/bin/env python3
"""Daily gather (2026-09-28, 10:00Z maintenance lane): four high-volume US
products that were missing from the database, plus the ingredient records they
need.

Sources read on 2026-09-28:

  - Stardrops The Pink Stuff The Miracle Cleaning Paste — the manufacturer's EU
    detergent product-information (DPI) filing, which lists the INCI names.
    https://www.dpi.uk.net/products/stardrops-the-pink-stuff-the-miracle-cleaning-paste-850g?lang=en
    The same product's SDS (Lisam Systems, product code BLE648) reports the
    quartz fraction at >=50-60% with STOT RE 2 (H373).
  - Snuggle SuperFresh Liquid Fabric Conditioner, Original — the Henkel label
    transcription carried by directionsforme.org (products 113554 / 113509);
    the Blue Sparkle variant's label on Target lists the same eight ingredients.
  - Ultra Joy Dishwashing Liquid, Lemon Scent — the P&G label transcription
    carried by directionsforme.org (product 52982) and independently by
    Instacart; the P&G SDS (RQ1400299) covers the same Joy Ultra Lemon family.
  - Branch Basics The Concentrate — the manufacturer's own ingredient list
    (branchbasics.com product page) and the Target listing for the 8 oz
    fragrance-free bottle.

Canonical-key mappings (no new keys minted) are recorded per product in
`disclosure_note`:
  - "Quartz" -> Silica (the DB's existing crystalline-silica entry)
  - "Parfum" -> Fragrance
  - "Polydimethylsiloxane" -> Dimethicone (INCI synonym)
  - "Diethyl Ester Dimethyl Ammonium Chloride" -> Diethylester Dimethyl Ammonium Chloride
  - "Colorants" -> Colorant
  - "FD&C Yellow 5" -> Yellow 5

Grading follows the house rule (docs/source-policy.md, docs/methodology.md):
only H-codes at >=40% ECHA C&L notifier consensus drive a dimension grade, read
from PubChem PUG View. UVCB / polymer / botanical substances with no discrete
PubChem CID are recorded "Extrapolated" with an explicit sourcing note, never
graded.

Run: python3 tools/gather_2026_09_28.py
Then: python3 build.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
TODAY = "2026-09-28"

PINKSTUFF = ("https://www.dpi.uk.net/products/"
             "stardrops-the-pink-stuff-the-miracle-cleaning-paste-850g?lang=en")
SNUGGLE = "https://www.directionsforme.org/product/113554"
JOY = "https://directionsforme.org/product/52982"
JOY_SDS = "https://www.kandelandson.com/site/images/stories/sdsnew/Joy%20Dish%20Detergent.pdf"
BRANCH = "https://branchbasics.com/products/the-concentrate"

BASE_BASIS = ("searched for a published per-product US household penetration figure; none "
              "exists in the open literature, so the estimate is derived from category "
              "penetration times the brand's share of its channel. Rounded to one "
              "significant figure. ")


# ---------------------------------------------------------------- ingredients
NEW_INGS = {
    "Sodium Palmate": {
        "g": "Extrapolated",
        "s": "Soap salt (sodium salts of palm-oil fatty acids). UVCB; no discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "UVCB soap salt (sodium salts of palm fatty acids). PubChem PUG REST returns no "
                "CID for the name (404), so no ECHA C&L consensus can be read. Recorded "
                "extrapolated by soap-salt class rather than invented; the sibling 'Sodium "
                "Palmitate' entry (a single-chain soap salt) is Not Classified, its only "
                "quantified code H319 at 23.3% falling below the house 40% bar. Disclosed by the "
                "manufacturer EU detergent product-information filing for The Pink Stuff Miracle "
                "Cleaning Paste.",
    },
    "Sodium Palm Kernelate": {
        "g": "Extrapolated",
        "s": "Soap salt (sodium salts of palm-kernel fatty acids). UVCB; no discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "UVCB soap salt (sodium salts of palm-kernel fatty acids). PubChem PUG REST "
                "returns no CID for the name (404). Recorded extrapolated by soap-salt class "
                "rather than invented, matching 'Sodium Palmate' and the existing 'Sodium "
                "Palmitate' entry. Disclosed by the manufacturer EU detergent "
                "product-information filing for The Pink Stuff Miracle Cleaning Paste.",
    },
    "Polyquaternium-37": {
        "g": "Extrapolated",
        "s": "Polymeric cationic conditioner (polyquaternium). Polymer; no discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "Polymeric quaternary-ammonium conditioner. PubChem PUG REST returns no CID for "
                "the name (404). Recorded extrapolated by polyquaternium class rather than "
                "invented; the sibling 'Polyquaternium-32' entry is likewise ungraded. Disclosed "
                "by the Snuggle label for SuperFresh Liquid Fabric Conditioner, Original.",
    },
    "Laurylamine Dipropylenediamine": {
        "g": "H301,H314,H318,H373,H400,H410",
        "s": "Corrosive amine. Toxic if swallowed; causes severe skin burns and eye damage; "
             "organ damage on prolonged or repeated exposure; very toxic to aquatic life.",
        "ev": "High",
        "gr": {"derm": "F", "organ": "C", "env": "F"},
        "impacts": ["derm", "aqua"],
        "note": "Graded from PubChem GHS (CID 75407, title 'N,N-Bis(3-aminopropyl)dodecylamine', "
                "CAS 2372-82-9): ECHA C&L notifier consensus H314 96% -> derm F; H318 71.2%; "
                "H301 95.4%; H373 90.5% -> organ C; H400 90.9% and H410 90.3% -> env F. The "
                "PubChem title is the systematic name for the substance the disclosure calls "
                "'Laurylamine Dipropylenediamine' (a C12 alkyl dipropylenetriamine), verified by "
                "structure. Disclosed by the manufacturer EU detergent product-information "
                "filing for The Pink Stuff Miracle Cleaning Paste.",
    },
    "Glutaral": {
        "g": "H301,H314,H317,H331,H334,H400",
        "s": "Corrosive biocide/preservative. Toxic if swallowed or inhaled; causes severe skin "
             "burns; skin and respiratory sensitizer; very toxic to aquatic life.",
        "ev": "High",
        "gr": {"derm": "F", "resp": "D", "env": "F"},
        "impacts": ["allerg", "derm", "resp", "aqua"],
        "sens": True,
        "note": "Graded from PubChem GHS (CID 3485, title 'Glutaraldehyde', CAS 111-30-8): ECHA "
                "C&L notifier consensus H314 >99.9% -> derm F; H317 >99.9% -> allerg; H334 "
                ">99.9% and H331 82.6% -> resp D; H301 >99.9%; H400 99.9% -> env F. H330 (20.1%), "
                "H318 (18.7%), H335 (19%) and H411 (16.1%) are below the 40% bar and do not drive "
                "grades. A potent respiratory sensitizer used as a preservative/biocide; "
                "disclosed by the Snuggle label for SuperFresh Liquid Fabric Conditioner, "
                "Original.",
    },
    "Chamomilla Recutita (Matricaria) Flower Extract": {
        "g": "Extrapolated",
        "s": "Botanical (chamomile) extract. No discrete PubChem CID; graded by analogy within botanicals.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "Botanical extract (chamomile). PubChem PUG REST returns no CID for the name "
                "(404). Recorded extrapolated by botanical class rather than invented, matching "
                "the existing 'Aloe Barbadensis Leaf Juice' and 'Ginger Extract' entries. "
                "Disclosed by Branch Basics for The Concentrate.",
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
    prod("The Pink Stuff Miracle Cleaning Paste", "The Pink Stuff", "Abrasive Cleanser",
         ["Silica", "Water", "Sodium Palmate", "Sodium Palm Kernelate", "Sodium Chloride",
          "Sodium Silicate", "Fragrance", "Dimethicone", "Laurylamine Dipropylenediamine",
          "Colorant"],
         "mass", "reported", PINKSTUFF,
         5, "extrapolated", PINKSTUFF,
         BASE_BASIS + "The Pink Stuff is a viral UK-born abrasive paste sold in the US through "
                      "mass, grocery and online channels; its US household penetration is well "
                      "below the legacy US cleanser leaders, so the estimate stops at the brand's "
                      "share of its channel rather than a measured product share.",
         subs=[{"name": "Bon Ami",
                "tier": "mass",
                "note": "A traditional non-chlorine powder cleanser (feldspar/limestone abrasive). "
                        "Same abrasive-cleanser job; no quartz, no fragrance, no amine."},
               {"name": "Bar Keepers Friend",
                "tier": "mass",
                "note": "Oxalic-acid powder cleanser. Different chemistry (acid + abrasive) for "
                        "the same hard-surface job; no quartz, no fragrance."}],
         owner="Stardrops", owner_ev="reported", owner_src=PINKSTUFF,
         disclosure_note="Source spellings mapped to canonical keys: 'Quartz' -> Silica; "
                         "'Parfum' -> Fragrance; 'Polydimethylsiloxane' -> Dimethicone; "
                         "'Colorant' kept as the DB's existing Colorant key.",
         tier_note="An abrasive cleaning paste. The manufacturer filing lists quartz (crystalline "
                   "silica) as the bulk abrasive and a C12 alkyl dipropylenetriamine as a "
                   "surfactant/emulsifier; the SDS reports the quartz fraction at >=50-60% with "
                   "STOT RE 2 (H373)."),

    prod("Snuggle SuperFresh Liquid Fabric Conditioner, Original", "Snuggle", "Laundry",
         ["Water", "Diethylester Dimethyl Ammonium Chloride", "Fragrance", "Lactic Acid",
          "Glutaral", "Polyquaternium-37", "Calcium Chloride", "Colorant"],
         "mass", "reported", SNUGGLE,
         10, "extrapolated", SNUGGLE,
         BASE_BASIS + "Snuggle is one of the largest US liquid fabric-softener brands, sold "
                      "through mass, grocery and dollar channels; the estimate stops at the "
                      "brand's share of the category rather than a measured product share.",
         subs=[{"name": "Downy Ultra Free & Gentle Liquid Fabric Conditioner",
                "tier": "mass",
                "note": "Same manufacturer class (P&G) and same ester-quat softener job, but "
                        "fragrance-free and dye-free. Avoids the fragrance block and the colorant; "
                        "still an ester-quat."},
               {"name": "Distilled White Vinegar (5%)",
                "tier": "apothecary-bulk",
                "note": "Added to the rinse as a softener/anti-static agent. Avoids every "
                        "disclosed ingredient here; no lasting softness and no fragrance."}],
         owner="Henkel", owner_ev="reported", owner_src=SNUGGLE,
         disclosure_note="Source spellings mapped to canonical keys: 'Diethyl Ester Dimethyl "
                         "Ammonium Chloride' -> Diethylester Dimethyl Ammonium Chloride; "
                         "'Colorants' -> Colorant.",
         tier_note="A mainstream liquid fabric softener. The label lists glutaral (glutaraldehyde) "
                   "as a preservative - a potent skin and respiratory sensitizer - plus an "
                   "undisclosed fragrance and a colorant."),

    prod("Ultra Joy Dishwashing Liquid, Lemon Scent", "Joy", "Dish Soap",
         ["Water", "Sodium Lauryl Sulfate", "Lauramine Oxide", "Sodium Laureth Sulfate",
          "Sodium Chloride", "Propylene Glycol", "Citric Acid", "Fragrance",
          "Methylisothiazolinone", "Yellow 5"],
         "mass", "reported", JOY,
         8, "extrapolated", JOY,
         BASE_BASIS + "Joy is a long-standing US hand-dish brand now well behind Dawn in share; "
                      "the estimate stops at the brand's share of the mass channel rather than a "
                      "measured product share.",
         subs=[{"name": "Dawn Ultra Dish Soap",
                "tier": "mass",
                "note": "The US dish-soap leader. Same surfactant class and the same "
                        "methylisothiazolinone preservative; different fragrance and dye package."},
               {"name": "Seventh Gen Dish",
                "tier": "natural",
                "note": "Plant-derived surfactant base, fragrance disclosed by component. Avoids "
                        "the dye and the isothiazolinone preservative."}],
         owner="P&G", owner_ev="reported", owner_src=JOY_SDS,
         disclosure_note="Source spelling mapped to canonical key: 'FD&C Yellow 5' -> Yellow 5. "
                         "The current US retail label lists Joysuds (Greenwich, CT) as the "
                         "marketer; the P&G SDS (RQ1400299) covers the same Joy Ultra Lemon "
                         "formula family, which is the basis for the owner attribution.",
         tier_note="A mainstream hand dish liquid. The label lists methylisothiazolinone, a "
                   "contact-allergen preservative, and FD&C Yellow 5 (tartrazine), a colorant "
                   "that carries an EU warning for attention-deficit effects in children."),

    prod("Branch Basics The Concentrate", "Branch Basics", "All-Purpose",
         ["Water", "Decyl Glucoside", "Coco-Glucoside",
          "Chamomilla Recutita (Matricaria) Flower Extract", "Sodium Citrate",
          "Sodium Bicarbonate", "Sodium Gluconate"],
         "natural", "reported", BRANCH,
         2, "extrapolated", BRANCH,
         BASE_BASIS + "Branch Basics is a direct-to-consumer refillable concentrate; it is not "
                      "carried in mass retail, so its US household penetration is a small "
                      "fraction of the mass all-purpose cleaners.",
         subs=[{"name": "Dr. Bronner's Sal Suds",
                "tier": "natural",
                "note": "A concentrated plant-derived liquid cleaner diluted for multiple uses. "
                        "Same refillable-concentrate model; a different surfactant base."},
               {"name": "All-Purpose Cleaner, Free & Clear",
                "tier": "natural",
                "note": "A ready-to-use fragrance-free all-purpose spray. Avoids the dilution "
                        "step; same fragrance-free positioning."}],
         owner="Branch Basics", owner_ev="reported", owner_src=BRANCH,
         tier_note="A seven-ingredient plant- and mineral-based concentrate diluted to make "
                   "all-purpose, bathroom, glass and laundry cleaners. Fragrance-free; the "
                   "chamomile extract is listed as a botanical, not a fragrance."),
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