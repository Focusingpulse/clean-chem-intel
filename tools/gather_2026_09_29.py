#!/usr/bin/env python3
"""Daily gather (2026-09-29, 10:00Z maintenance lane): four high-volume US
products that were missing from the database, plus the ingredient records they
need.

Sources read on 2026-09-29:

  - Mr. Clean Clean Freak All Purpose Cleaner Spray, Deep Cleaning Mist, Lemon
    Zest — the P&G SmartLabel ingredient disclosure for UPC 00037000791294
    (updated 2024-12-18). A distributor spec sheet (maloneoffice.com, P&G part
    79129) lists a slightly longer set including alcohol ethoxylate and
    benzisothiazolinone; the SmartLabel is the manufacturer's own current
    disclosure and is used here.
    https://smartlabel.pg.com/00037000791294.html
  - Clorox Scentiva Disinfecting Multi-Surface Cleaner, Spray Bottle, Bleach
    Free, Tuscan Lavender & Jasmine — the Clorox SmartLabel ingredient
    disclosure for UPC 044600313870 (updated 2025-04-09).
    https://smartlabel.labelinsight.com/product/6096788/ingredients
  - Cascade Platinum Plus ActionPacs Dishwasher Detergent Pods, Fresh — the
    P&G SmartLabel ingredient disclosure (updated 2026-03-30).
    https://smartlabel.pg.com/en-us/00030772064726.html
  - Mean Green Super Strength Cleaner & Degreaser — the Rust-Oleum GHS SDS,
    product identifier 932, revision 2026-03-31, plus the Rust-Oleum technical
    data sheet (ARJ-1954). The SDS names only two hazardous substances and withholds
    the balance as trade secret; the TDS describes the remainder only as a
    "proprietary blend of biodegradable surfactants, biodegradable solvent,
    detergents and dye".
    https://www.rustoleum.com/MSDS/ENGLISH/932.pdf

Canonical-key mappings (no new keys minted) are recorded per product in
`disclosure_note`:
  - "Perfume" / "Fragrances" -> Fragrance
  - "d-Limonene" -> Limonene
  - "Acid Red 33" -> Red 33
  - "PEG/PPG Propylheptyl Ether" -> PEG/PPG/Propylheptyl Ether
  - "Alanine, N,N-bis(carboxymethyl)-, trisodium salt" -> Trisodium Dicarboxymethyl Alaninate

Grading follows the house rule (docs/source-policy.md, docs/methodology.md):
only H-codes at >=40% ECHA C&L notifier consensus drive a dimension grade, read
from PubChem PUG View. UVCB / polymer / botanical substances with no discrete
PubChem CID are recorded "Extrapolated" with an explicit sourcing note, never
graded. Every returned PubChem title was checked against the intended substance
before the record was accepted.

Run: python3 tools/gather_2026_09_29.py
Then: python3 build.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
TODAY = "2026-09-29"

MR_CLEAN = "https://smartlabel.pg.com/00037000791294.html"
SCENTIVA = "https://smartlabel.labelinsight.com/product/6096788/ingredients"
CASCADE = "https://smartlabel.pg.com/en-us/00030772064726.html"
MEANGREEN = "https://www.rustoleum.com/MSDS/ENGLISH/932.pdf"

BASE_BASIS = ("searched for a published per-product US household penetration figure; none "
              "exists in the open literature, so the estimate is derived from category "
              "penetration times the brand's share of its channel. Rounded to one "
              "significant figure. ")


# ---------------------------------------------------------------- ingredients
NEW_INGS = {
    "Lauryl Betaine": {
        "g": "H302,H312,H315,H318",
        "s": "Betaine surfactant. Harmful if swallowed or in contact with skin; causes skin "
             "irritation and serious eye damage.",
        "ev": "High",
        "gr": {"derm": "D", "work": "D"},
        "impacts": ["derm"],
        "note": "Graded from PubChem GHS (CID 4292413, returned title 'Lauryldimethylbetaine' - "
                "the systematic name for the C12 alkylbetaine the disclosure calls 'Lauryl "
                "betaine', CAS 683-10-3). Dominant ECHA C&L block (935 reports, 13 "
                "notifications): H318 86.8% -> derm D; H315 88.4% -> derm C (subsumed); H302 53% "
                "and H312 57.6% -> work D. H317 22.6% (skin sensitization) and H319 13.6% fall "
                "below the house >=40% consensus bar and are noted, not graded. PubChem's "
                "aggregated view also lists H371/H373/H400/H401/H412 without notifier "
                "percentages - noted, not graded. Disclosed by the P&G SmartLabel for Mr. Clean "
                "Clean Freak Deep Cleaning Mist, Lemon Zest.",
    },
    "PEG PPG Ethylhexyl Ether": {
        "g": "Extrapolated",
        "s": "Polymeric alkoxylated ether (PEG/PPG ethylhexyl ether). Polymer; no discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "Polymeric alkoxylated ether. PubChem PUG REST returns no CID for the name (404), "
                "so no ECHA C&L consensus can be read. Recorded extrapolated by the PEG/PPG ether "
                "class rather than invented; the sibling 'PEG/PPG/Propylheptyl Ether' entry is "
                "likewise ungraded. Disclosed by the P&G SmartLabel for Mr. Clean Clean Freak "
                "Deep Cleaning Mist, Lemon Zest.",
    },
    "PEG": {
        "g": "Extrapolated",
        "s": "Polyethylene glycol (PEG). Polymer family; no discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "Polyethylene glycol. PubChem PUG REST returns no CID for the bare name (404); PEG "
                "is a polymer family, not a discrete substance. Recorded extrapolated by the PEG "
                "class rather than invented; the DB's 'PEG-150' entry is likewise ungraded. "
                "Disclosed by the P&G SmartLabel for Mr. Clean Clean Freak Deep Cleaning Mist, "
                "Lemon Zest.",
    },
    "Tetrapotassium EDTA": {
        "g": "H302,H318,H319,H332,H361,H373",
        "s": "Chelating agent (tetrapotassium salt of EDTA). Harmful if swallowed or inhaled; "
             "serious eye damage; suspected reproductive toxicity; organ damage on prolonged exposure.",
        "ev": "Medium",
        "gr": {"derm": "D", "resp": "C", "organ": "C", "work": "D", "repro": "C"},
        "impacts": ["derm", "repro", "resp"],
        "note": "Graded from PubChem GHS (CID 62595, returned title 'Edetate tetrapotassium' - "
                "matches; CAS 2001-91-0). Dominant ECHA C&L block (241 reports, 9 notifications): "
                "H302 66.4% -> work D; H318 46.5% -> derm D; H332 45.2% -> resp C; H373 45.2% -> "
                "organ C; H319 54.4% (subsumed by H318); H302+H332 43.2%. A second ECHA C&L block "
                "on the same CID (129 reports, 2 notifications) reports H361 80.6% (suspected "
                "reproductive toxicity) -> repro C and H319 100%; both blocks are ECHA C&L "
                "consensus, so the reproductive code is graded and its provenance named here. "
                "Disclosed by the Clorox SmartLabel for Scentiva Disinfecting Multi-Surface "
                "Cleaner, Tuscan Lavender & Jasmine.",
    },
    "Copolymer of Acrylic and Sulphonic Acids": {
        "g": "Extrapolated",
        "s": "Polymeric antiredeposition agent (acrylic/sulphonic acid copolymer). Polymer; no "
             "discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "Polymeric antiredeposition agent. PubChem PUG REST returns no CID for the name "
                "(404). Recorded extrapolated by polymer class rather than invented, matching the "
                "existing 'Copolymer of Acrylic Maleic and Sulphonic Acids' entry, which is "
                "likewise ungraded. Disclosed by the P&G SmartLabel for Cascade Platinum Plus "
                "ActionPacs, Fresh.",
    },
    "Tolyltriazole": {
        "g": "Extrapolated",
        "s": "Metal corrosion inhibitor (mixture of methylbenzotriazole isomers). UVCB; no "
             "discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "Tolyltriazole (CAS 29385-43-1) is a UVCB mixture of methylbenzotriazole isomers; "
                "PubChem PUG REST returns no CID for the name (404). Recorded extrapolated by the "
                "benzotriazole class rather than invented; the sibling 'Benzotriazole' entry is "
                "graded derm C / work C (H302 96.7%, H319 87.8%). Disclosed by the P&G SmartLabel "
                "for Cascade Platinum Plus ActionPacs, Fresh.",
    },
    "Acid Yellow 17": {
        "g": "Not Classified",
        "s": "Azo dye (CI 18965). No GHS hazard criteria met by the notifier majority.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "Graded from PubChem GHS (CID 22842, returned title 'benzenesulfonic acid, "
                "2,5-dichloro-4-(4,5-dihydro-3-methyl-5-oxo-4-((4-sulfophenyl)azo)-1h-pyrazol-1-"
                "yl)-, disodium salt' - the IUPAC name for the dye the disclosure calls 'Acid "
                "Yellow 17', CAS 6359-98-4). ECHA C&L: 2269 of 2296 reports (98.8%) report not "
                "meeting hazard criteria; only 2 notifications of 2296 carry hazard codes, all "
                "below the house 40% bar, so no dimension grade is justified. Disclosed by the "
                "P&G SmartLabel for Cascade Platinum Plus ActionPacs, Fresh.",
    },
    "Acid Blue 3": {
        "g": "Not Classified",
        "s": "Triarylmethane dye (CI 42051, Patent Blue V). No GHS hazard criteria met.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "Graded from PubChem GHS (CID 77073, returned title 'Acid Blue 3' - matches; CAS "
                "3536-49-0). ECHA C&L: 182 of 182 reports (100%) report not meeting hazard "
                "criteria; 0 notifications carry hazard codes, so no dimension grade is "
                "justified. Disclosed by the P&G SmartLabel for Cascade Platinum Plus ActionPacs, "
                "Fresh.",
    },
}


# ------------------------------------------------------------------ products
def prod(name, brand, cat, ings, tier, tier_ev, tier_src, exposure, exposure_ev,
         exposure_src, exposure_basis, subs=None, no_sub=None, tier_note=None,
         heritage=None, owner=None, owner_ev="untested", owner_src=None,
         disclosure_note=None, source=None, source_url=None):
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
    if source:
        p["source"] = source
    if source_url:
        p["source_url"] = source_url
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
    prod("Mr. Clean Clean Freak Deep Cleaning Mist, Lemon Zest", "Mr. Clean", "All-Purpose",
         ["Water", "Triethanolamine", "Lauryl Betaine", "PEG PPG Ethylhexyl Ether",
          "Dipropylene Glycol Butyl Ether", "Sodium Carbonate", "Ethanolamine", "Xanthan Gum",
          "PEG", "Fragrance"],
         "mass", "reported", MR_CLEAN,
         6, "extrapolated", MR_CLEAN,
         BASE_BASIS + "Clean Freak is a line extension of Mr. Clean, the leading US "
                      "all-purpose spray brand (the base Mr. Clean record carries an extrapolated "
                      "exposure of 10); the mist line is a fraction of the brand's total spray "
                      "volume, so the estimate stops at the brand's share of the category rather "
                      "than a measured product share.",
         subs=[{"name": "Mr. Clean",
                "tier": "mass",
                "note": "The base Mr. Clean multi-surface spray from the same brand; a similar "
                        "surfactant/solvent base without the mist delivery."},
               {"name": "Seventh Gen All-Purpose",
                "tier": "natural",
                "note": "Plant-derived surfactant base, fragrance disclosed by component. Avoids "
                        "the undisclosed perfume."}],
         owner="Procter & Gamble", owner_ev="reported", owner_src=MR_CLEAN,
         disclosure_note="Source spelling mapped to canonical key: 'Perfume' -> Fragrance. The "
                         "P&G SmartLabel for UPC 00037000791294 is the manufacturer's own current "
                         "disclosure; a distributor spec sheet (P&G part 79129) lists a longer set "
                         "that also names alcohol ethoxylate, benzisothiazolinone and C10-16 "
                         "alkyldimethylamine oxide.",
         source="Procter & Gamble SmartLabel ingredient disclosure",
         source_url=MR_CLEAN,
         tier_note="A mainstream all-purpose cleaning spray. The disclosure lists triethanolamine "
                   "and ethanolamine (amines used to cut grease) plus an undisclosed perfume; the "
                   "finished product is not a disinfectant."),

    prod("Clorox Scentiva Disinfecting Multi-Surface Cleaner, Tuscan Lavender & Jasmine",
         "Clorox", "Disinfectant",
         ["Water", "Lauramine Oxide", "Ethanolamine",
          "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride", "Myristamine Oxide",
          "Tetrapotassium EDTA", "Ethanol", "Fragrance", "Limonene",
          "Butylphenyl Methylpropional", "Citronellol"],
         "mass", "reported", SCENTIVA,
         6, "extrapolated", SCENTIVA,
         BASE_BASIS + "Scentiva is a line extension of Clorox, the leading US bleach brand (the "
                      "Clorox Bleach record carries an extrapolated exposure of 15); the "
                      "bleach-free multi-surface spray is a fraction of the brand's total "
                      "disinfecting volume, so the estimate stops at the brand's share of the "
                      "category rather than a measured product share.",
         subs=[{"name": "Clorox Clean-Up All Purpose Cleaner with Bleach, Original",
                "tier": "mass",
                "note": "Same brand, bleach-based disinfectant; a different active (sodium "
                        "hypochlorite) and no quaternary ammonium compound."},
               {"name": "Seventh Generation All-Purpose Cleaner, Free & Clear",
                "tier": "natural",
                "note": "Fragrance-free, no quaternary ammonium active; a weaker disinfecting "
                        "claim."}],
         owner="The Clorox Company", owner_ev="reported", owner_src=SCENTIVA,
         disclosure_note="Source spelling mapped to canonical key: 'd-Limonene' -> Limonene. The "
                         "Clorox SmartLabel for UPC 044600313870 is the manufacturer's own "
                         "disclosure (updated 2025-04-09) and names the fragrance allergens "
                         "individually.",
         source="Clorox SmartLabel ingredient disclosure",
         source_url=SCENTIVA,
         tier_note="A bleach-free disinfecting multi-surface spray. The active is a C12-16 alkyl "
                   "dimethylbenzyl ammonium chloride (a quaternary ammonium compound); the label "
                   "also names three fragrance allergens individually (d-limonene, butylphenyl "
                   "methylpropional, citronellol)."),

    prod("Cascade Platinum Plus ActionPacs, Fresh", "Cascade", "Dishwasher",
         ["Trisodium Dicarboxymethyl Alaninate", "Sodium Carbonate", "Sodium Sulfate",
          "Sodium Carbonate Peroxide", "Isotridecanol Ethoxylated",
          "Copolymer of Acrylic and Sulphonic Acids", "Water", "PEG/PPG/Propylheptyl Ether",
          "Dipropylene Glycol", "Tolyltriazole", "Subtilisin", "Fragrance", "Glycerin",
          "Amylase Enzyme", "Benzotriazole", "Transition Metal Catalyst", "Acid Yellow 17",
          "Acid Blue 182", "Acid Blue 3", "Red 33", "Polyvinyl Alcohol Polymer"],
         "mass", "reported", CASCADE,
         10, "extrapolated", CASCADE,
         BASE_BASIS + "Cascade is the leading US automatic-dishwasher detergent brand (the base "
                      "Cascade record carries an extrapolated exposure of 15); Platinum Plus is "
                      "the brand's premium tier, so the estimate stops at the brand's share of "
                      "the category rather than a measured product share.",
         subs=[{"name": "Finish",
                "tier": "mass",
                "note": "The other leading dishwasher-tab brand; a different builder and enzyme "
                        "package."},
               {"name": "Seventh Generation Dishwasher Pacs, Free & Clear",
                "tier": "natural",
                "note": "Fragrance-free and dye-free; no bleach activator."}],
         owner="Procter & Gamble", owner_ev="reported", owner_src=CASCADE,
         disclosure_note="Source spellings mapped to canonical keys: 'Fragrances' -> Fragrance; "
                         "'PEG/PPG Propylheptyl Ether' -> PEG/PPG/Propylheptyl Ether; 'Acid Red "
                         "33' -> Red 33; 'Acid Blue 182' kept as the DB's existing key.",
         source="Procter & Gamble SmartLabel ingredient disclosure",
         source_url=CASCADE,
         tier_note="A premium dishwasher pod. The disclosure lists a percarbonate bleach system "
                   "with a TAED-type activator, two enzymes (subtilisin protease and amylase), a "
                   "benzotriazole/tolyltriazole corrosion-inhibitor pair and five dyes; the pod "
                   "film is polyvinyl alcohol."),

    prod("Mean Green Super Strength Cleaner & Degreaser", "Mean Green", "All-Purpose",
         ["Potassium Hydroxide", "Trisodium Dicarboxymethyl Alaninate"],
         "dollar-store", "reported", MEANGREEN,
         5, "extrapolated", MEANGREEN,
         BASE_BASIS + "Mean Green is a long-standing dollar-store and mass degreaser sold under "
                      "the Rust-Oleum umbrella; no per-product US penetration figure exists, so "
                      "the estimate stops at the brand's share of its channel rather than a "
                      "measured product share.",
         subs=[{"name": "Simple Green",
                "tier": "mass",
                "note": "The original concentrate-and-dilute degreaser; discloses its surfactant "
                        "and solvent classes and carries EPA Safer Choice certification on some "
                        "SKUs."},
               {"name": "LA's Totally Awesome All-Purpose Cleaner",
                "tier": "dollar-store",
                "note": "Same dollar-store channel and price point; discloses a fuller ingredient "
                        "list."}],
         owner="Rust-Oleum Corporation", owner_ev="reported", owner_src=MEANGREEN,
         disclosure_note="Disclosure gap: the Rust-Oleum GHS SDS (product 932, rev. 2026-03-31) "
                         "names only two hazardous substances and states that actual "
                         "concentrations are withheld as trade secret; the technical data sheet "
                         "describes the balance only as a 'proprietary blend of biodegradable "
                         "surfactants, biodegradable solvent, detergents and dye'. The record "
                         "carries the two disclosed components and the gap, not a guess. Source "
                         "spelling mapped to canonical key: 'Alanine, N,N-bis(carboxymethyl)-, "
                         "trisodium salt' -> Trisodium Dicarboxymethyl Alaninate.",
         source="Rust-Oleum GHS SDS (product 932) + technical data sheet",
         source_url=MEANGREEN,
         tier_note="A concentrate-and-dilute alkaline degreaser (pH 12.5-13.0) sold through "
                   "dollar stores and mass retail. The label markets it 'Non-Toxic', but the SDS "
                   "names potassium hydroxide (corrosive; H314/H318/H301) at 0.1-1.0% and "
                   "withholds the rest of the formula as trade secret - a product whose marketing "
                   "claim and disclosure both point away from its own SDS."),
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
