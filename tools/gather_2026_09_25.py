#!/usr/bin/env python3
"""Daily gather (2026-09-25, 10:00Z maintenance lane): four high-volume US products
that were missing from the database, plus the ingredient records they need.

Every ingredient list below is copied from a manufacturer disclosure read on
2026-09-25:

  - Church & Dwight product ingredient disclosure form for
    Arm & Hammer Liquid Laundry Detergent - Baking Soda Fresh (material 42019452,
    disclosure dated 2026-01-27)
  - Church & Dwight product ingredient disclosure form for
    Xtra Liquid Laundry Detergent - Tropical Passion (material 42015436,
    disclosure dated 2024-03-27)
  - Reckitt SmartLabel for Glass Plus Cleaner (productLineId 316)
  - Reckitt SmartLabel for Lime-A-Way Toilet Bowl Cleaner (productLineId 320)

Grading follows the house rule (docs/source-policy.md, docs/methodology.md):
only H-codes at >=40% ECHA C&L notifier consensus drive a dimension grade, read
from PubChem PUG View. UVCB / polymer / petroleum-distillate substances with no
discrete PubChem CID are recorded "Extrapolated" with an explicit sourcing note,
never graded. Fragrance components are listed individually where the disclosure
lists them individually (the DB's existing fragrance-allergen pattern).

Run: python3 tools/gather_2026_09_25.py
Then: python3 build.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
TODAY = "2026-09-25"

CD_AH = ("https://churchdwight.com/ingredient-disclosure/laundry-fabric-care/"
         "42019452-Liquid-Laundry-Detergent%E2%80%93Baking-Soda-Fresh.aspx")
CD_XTRA = ("https://churchdwight.com/ingredient-disclosure/laundry-fabric-care/"
           "42015436-xtra-liquid-laundry-detergent-tropical-passion.aspx")
RB_GLASS = "https://www.rbnainfo.com/product.php?productLineId=316"
RB_LIME = "https://www.rbnainfo.com/product.php?productLineId=320"

BASE_BASIS = ("searched for a published per-product US household penetration figure; none "
              "exists in the open literature, so the estimate is derived from category "
              "penetration times the brand's share of its channel. Rounded to one "
              "significant figure. ")


# ---------------------------------------------------------------- ingredients
NEW_INGS = {
    "Pentasodium DTPA": {
        "g": "H332,H361",
        "s": "Chelating agent (pentasodium pentetate). Harmful if inhaled; suspected reproductive "
             "or developmental toxicant.",
        "ev": "Medium",
        "gr": {"resp": "C", "repro": "C"},
        "impacts": ["repro"],
        "note": "PubChem CID 8779, ECHA C&L notifier consensus: H332 87.7% -> resp C; H361 67.4% "
                "-> repro C. H360D (18.5%), H373 (31.3%), H315 (17.7%) and H319 (18.2%) are below "
                "the 40% house bar and do not drive grades. Disclosed by Church & Dwight as "
                "Pentasodium DTPA (CAS 140-01-2) in the Arm & Hammer and Xtra liquid laundry "
                "detergents; the disclosure itself flags it EU CMRs.",
    },
    "Nitrilotriacetic Acid": {
        "g": "H319,H351",
        "s": "Chelating agent. Eye irritant; suspected carcinogen.",
        "ev": "Medium",
        "gr": {"derm": "C", "canc": "C"},
        "impacts": ["canc"],
        "note": "PubChem CID 8758, ECHA C&L notifier consensus: H319 83% -> derm C; H351 67% -> "
                "canc C. H302 (22.4%) is below the 40% bar. Non-consensus notifier blocks also "
                "carry H340 (may cause genetic defects) and H411 (aquatic), which are recorded "
                "here but do not drive a grade. Disclosed by Church & Dwight as a non-functional "
                "constituent of Arm & Hammer liquid laundry detergent; the disclosure itself "
                "flags it California Prop 65.",
    },
    "Methoxyisopropanol": {
        "g": "H226,H336",
        "s": "Glycol-ether solvent (1-methoxy-2-propanol). Flammable; may cause drowsiness or "
             "dizziness.",
        "ev": "Medium",
        "gr": {"work": "C"},
        "impacts": [],
        "note": "PubChem CID 7900, ECHA C&L notifier consensus: H226 (>99.9%) and H336 (99%). "
                "Non-consensus notifier blocks also carry H320/H332/H316/H319, which do not drive "
                "grades under the >=40% house rule. Disclosed by Reckitt SmartLabel for Glass "
                "Plus; the disclosure flags it on California's non-cancer hazard list.",
    },
    "Methyl Salicylate": {
        "g": "H302,H319",
        "s": "Fragrance component (wintergreen). Harmful if swallowed; serious eye irritant.",
        "ev": "High",
        "gr": {"derm": "C"},
        "impacts": ["derm"],
        "note": "PubChem CID 4133, ECHA C&L notifier consensus: H302 97.5%, H319 91.1% -> derm C. "
                "Non-consensus notifier blocks also carry H317 (skin sensitizer) and H361d "
                "(suspected developmental toxicant), which are recorded here but do not drive a "
                "grade under the >=40% rule. Disclosed by Reckitt SmartLabel for Lime-A-Way "
                "Toilet Bowl Cleaner; flagged EU fragrance allergen.",
    },
    "Hexyl Salicylate": {
        "g": "H317,H400,H410",
        "s": "Fragrance component. Skin sensitizer; very toxic to aquatic life.",
        "ev": "High",
        "gr": {"derm": "D", "env": "F"},
        "impacts": ["allerg", "aqua", "derm"],
        "note": "PubChem CID 22629, ECHA C&L notifier consensus: H317 98.4% -> derm D + allerg; "
                "H400 90.2% -> env F; H410 100%. H315 (26.9%) and H319 (13.2%) are below the 40% "
                "bar. Disclosed by Church & Dwight as a fragrance component of Arm & Hammer "
                "liquid laundry detergent.",
    },
    "Tetramethyl Acetyloctahydronaphthalenes": {
        "g": "H315,H317,H410",
        "s": "Fragrance component (polycyclic musk). Skin irritant and sensitizer; toxic to "
             "aquatic life.",
        "ev": "High",
        "gr": {"derm": "D", "env": "D"},
        "impacts": ["allerg", "aqua", "derm"],
        "note": "PubChem CID 108242, ECHA C&L notifier consensus: H315 84.7%, H317 89.5% -> derm D "
                "+ allerg; H410 75.2% -> env D. H411 (24.8%) is below the 40% bar. Disclosed by "
                "Church & Dwight as a fragrance component of Arm & Hammer and Xtra liquid laundry "
                "detergents; flagged EU fragrance allergen.",
    },
    "Verdyl Acetate": {
        "g": "H412",
        "s": "Fragrance component. Harmful to aquatic life with long lasting effects.",
        "ev": "Medium",
        "gr": {"env": "C"},
        "impacts": ["aqua"],
        "note": "PubChem CID 110655, ECHA C&L notifier consensus: H412 47.7% -> env C. H226 "
                "(24.5%) is below the 40% bar. Disclosed by Church & Dwight as a fragrance "
                "component of Arm & Hammer and Xtra liquid laundry detergents.",
    },
    "Cyclamen Aldehyde": {
        "g": "H315,H317,H412",
        "s": "Fragrance component. Skin irritant and sensitizer; harmful to aquatic life.",
        "ev": "High",
        "gr": {"derm": "D", "env": "C"},
        "impacts": ["allerg", "aqua", "derm"],
        "note": "PubChem CID 517827, ECHA C&L notifier consensus: H315 98.8%, H317 95.9% -> derm D "
                "+ allerg; H412 76.6% -> env C. H361 (12.3%) and H411 (15.1%) are below the 40% "
                "bar. Disclosed by Church & Dwight as a fragrance component of Arm & Hammer "
                "liquid laundry detergent.",
    },
    "Allyl Cyclohexanepropionate": {
        "g": "H302,H312,H317,H332,H400,H410",
        "s": "Fragrance component. Harmful if swallowed or in contact with skin; skin sensitizer; "
             "harmful if inhaled; very toxic to aquatic life.",
        "ev": "High",
        "gr": {"derm": "D", "resp": "C", "env": "F"},
        "impacts": ["allerg", "aqua", "derm", "resp"],
        "note": "PubChem CID 17617, ECHA C&L notifier consensus: H302 99.9%, H312 98%, H317 83% -> "
                "derm D + allerg; H332 84% -> resp C; H400 81.9% -> env F; H410 83.2%. H315 (13%) "
                "is below the 40% bar. Disclosed by Church & Dwight as a fragrance component of "
                "Arm & Hammer liquid laundry detergent.",
    },
    "Allyl Heptanoate": {
        "g": "H302,H311,H315,H319,H373,H400,H410",
        "s": "Fragrance component. Toxic in contact with skin; harmful if swallowed; skin and eye "
             "irritant; organ effects at repeated exposure; very toxic to aquatic life.",
        "ev": "High",
        "gr": {"derm": "C", "organ": "C", "env": "F"},
        "impacts": ["aqua", "derm"],
        "note": "PubChem CID 8878, ECHA C&L notifier consensus: H302 85.4%, H311 79.9%, H315 62.5%, "
                "H319 74.7% -> derm C; H373 53.7% -> organ C; H400 58.9% -> env F; H410 69.1%. "
                "H301 (14.6%), H312 (20%) and H412 (15%) are below the 40% bar. H311 (toxic in "
                "contact with skin) is carried in the summary but has no house grade dimension. "
                "Disclosed by Church & Dwight as a fragrance component of Arm & Hammer liquid "
                "laundry detergent.",
    },
    "Dihydromyrcenol": {
        "g": "H315,H319",
        "s": "Fragrance component (2,6-dimethyl-7-octen-2-ol). Skin and eye irritant.",
        "ev": "High",
        "gr": {"derm": "C"},
        "impacts": ["derm"],
        "note": "PubChem CID 29096, ECHA C&L notifier consensus: H315 74.6%, H319 94.6% -> derm C. "
                "Disclosed by Church & Dwight as '2,6-Dimethyl-7-Octen-2-ol' (CAS 18479-58-8) in "
                "Arm & Hammer and Xtra liquid laundry detergents, and by Reckitt SmartLabel as "
                "'Dihydromyrcenol' (same CAS) in Lime-A-Way.",
    },
    "Galaxolide": {
        "g": "H400,H410",
        "s": "Fragrance component (polycyclic musk, hexamethylindanopyran). Very toxic to aquatic "
             "life; persistent.",
        "ev": "High",
        "gr": {"env": "F"},
        "impacts": ["aqua"],
        "note": "PubChem CID 91497, ECHA C&L notifier consensus: H400 97.9% -> env F; H410 100%. "
                "Non-consensus notifier blocks also carry H360/H361 (reproductive toxicity), which "
                "are recorded here but do not drive a grade under the >=40% rule; the compound is a "
                "well-documented persistent musk. Disclosed by Church & Dwight as a fragrance "
                "component of Arm & Hammer liquid laundry detergent; the disclosure flags it US "
                "EPA PBTs.",
    },
    "Hexyl Cinnamal": {
        "g": "H317,H400,H411",
        "s": "Fragrance component. Skin sensitizer; very toxic to aquatic life.",
        "ev": "High",
        "gr": {"derm": "D", "env": "F"},
        "impacts": ["allerg", "aqua", "derm"],
        "note": "PubChem CID 1550884 (alpha-hexylcinnamaldehyde), ECHA C&L notifier consensus: "
                "H317 99.6% -> derm D + allerg; H400 65.1% -> env F; H411 62.4%. One of the 26 "
                "fragrance allergens that must be declared on EU cosmetic labels (Reg. 1223/2009 "
                "Annex III). Disclosed by Church & Dwight as a fragrance component of Arm & Hammer "
                "and Xtra liquid laundry detergents.",
    },
    "Hydroxycitronellal": {
        "g": "H317,H319",
        "s": "Fragrance component. Skin sensitizer; serious eye irritant.",
        "ev": "High",
        "gr": {"derm": "D"},
        "impacts": ["allerg", "derm"],
        "note": "PubChem CID 7888, ECHA C&L notifier consensus: H317 (>99.9%) -> derm D + allerg; "
                "H319 (>99.9%). One of the 26 fragrance allergens that must be declared on EU "
                "cosmetic labels (Reg. 1223/2009 Annex III). Disclosed by Church & Dwight as a "
                "fragrance component of Xtra liquid laundry detergent.",
    },
    "Tricyclodecenyl Propionate": {
        "g": "H319,H411",
        "s": "Fragrance component. Serious eye irritant; toxic to aquatic life with long lasting "
             "effects.",
        "ev": "High",
        "gr": {"derm": "C", "env": "D"},
        "impacts": ["aqua", "derm"],
        "note": "PubChem CID 86579, ECHA C&L notifier consensus: H319 72.9% -> derm C; H411 100% -> "
                "env D. Church & Dwight lists this component under two names in two disclosures: "
                "'Hexahydro-methanoindenyl propionate' (CAS 68912-13-0) in Arm & Hammer and "
                "'Tricyclodecenyl propionate' (CAS 17511-60-3) in Xtra. Both CAS numbers resolve to "
                "the same PubChem record (CID 86579).",
    },
    "Dodecanenitrile": {
        "g": "H315,H400,H410",
        "s": "Fragrance component. Skin irritant; very toxic to aquatic life.",
        "ev": "High",
        "gr": {"derm": "C", "env": "F"},
        "impacts": ["aqua", "derm"],
        "note": "PubChem CID 17092, ECHA C&L notifier consensus: H315 86.3% -> derm C; H400 95.2% "
                "-> env F; H410 97.5%. Disclosed by Reckitt SmartLabel for Lime-A-Way Cleaner; the "
                "disclosure flags it California toxic air contaminants.",
    },
    "Fructone": {
        "g": "Not Classified",
        "s": "No GHS hazard criteria met (majority not-classified per ECHA C&L via PubChem)",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "Fragrance component (ethyl acetoacetate ethylene glycol ketal, CAS 6413-10-1). "
                "PubChem CID 80865 — no H-codes at >=40% consensus; treated as minimal hazard with "
                "Medium confidence. Disclosed by Church & Dwight as a fragrance component of Arm & "
                "Hammer liquid laundry detergent.",
    },
    "2-Methoxynaphthalene": {
        "g": "Not Classified",
        "s": "No GHS hazard criteria met (majority not-classified per ECHA C&L via PubChem)",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem CID 7119 — the only classified H-code, H411 (aquatic), sits at 18.5% "
                "consensus, below the 40% house bar, so no grade is justified. Disclosed by Church "
                "& Dwight as a fragrance component of Arm & Hammer and Xtra liquid laundry "
                "detergents.",
    },
    "Gamma-Undecalactone": {
        "g": "Not Classified",
        "s": "No GHS hazard criteria met (majority not-classified per ECHA C&L via PubChem)",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem CID 7714 — H411 (10.3%) and H412 (19.3%) are both below the 40% house "
                "bar, so no grade is justified. Disclosed by Church & Dwight as a fragrance "
                "component of Arm & Hammer liquid laundry detergent.",
    },
    "Orange Terpenes": {
        "g": "Extrapolated",
        "s": "Citrus terpene mixture (orange terpenes). UVCB; no discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "UVCB (CAS 68647-72-3) — PubChem PUG REST returns no CID. Class-analogous to the "
                "existing 'Limonene' entry (derm D, env F, allerg): the terpene class is a skin "
                "sensitizer on oxidation and is very toxic to aquatic life. Recorded extrapolated, "
                "not graded. Disclosed by Church & Dwight as a fragrance component of Arm & Hammer "
                "and Xtra liquid laundry detergents.",
    },
    "Rosin, Hydrogenated": {
        "g": "Extrapolated",
        "s": "Hydrogenated rosin (fragrance fixative). UVCB; no discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "UVCB (CAS 65997-06-0) — PubChem PUG REST returns no CID. Recorded extrapolated, "
                "not graded. Disclosed by Reckitt SmartLabel for Lime-A-Way Cleaner; the disclosure "
                "flags it on Canada's PBT list (persistent, bioaccumulative, inherently toxic).",
    },
    "Acrylic Acid Homopolymer": {
        "g": "Extrapolated",
        "s": "Polymeric dispersing agent (acrylic acid homopolymer). UVCB; no discrete PubChem "
             "CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "UVCB/polymer (CAS 66019-18-9) — no discrete PubChem entry. Class-analogous to the "
                "existing polyacrylate dispersant entries: the polymer itself is not classified; "
                "the hazard of the class is residual acrylic-acid monomer. Recorded extrapolated, "
                "not graded. Disclosed by Church & Dwight for Arm & Hammer and Xtra liquid laundry "
                "detergents.",
    },
    "C12-13 Alcohols Ethoxylated": {
        "g": "Extrapolated",
        "s": "Alcohol ethoxylate nonionic surfactant (C12-13). UVCB; no discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "UVCB (CAS 66455-14-9) — no discrete PubChem entry. Class-analogous to the existing "
                "'C10-16 Pareth' and 'C12-15 Alcohols Ethoxylated' entries (derm C, env C; trace "
                "1,4-dioxane from ethoxylation). Recorded extrapolated, not graded. Disclosed by "
                "Church & Dwight for Xtra liquid laundry detergent.",
    },
    "PEG-2 Hydrogenated Tallow Amine": {
        "g": "Extrapolated",
        "s": "Ethoxylated tallow amine thickener (PEG-2 hydrogenated tallow amine). UVCB; no "
             "discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "UVCB (CAS 61791-26-2) — no discrete PubChem entry. Class-analogous to the "
                "ethoxylated-amine surfactant class (skin/eye irritant; ethoxylated amines are the "
                "more irritating end of the nonionic class). Recorded extrapolated, not graded. "
                "Disclosed by Reckitt SmartLabel for Lime-A-Way Toilet Bowl Cleaner, whose label "
                "states 'contains sulfamic acid and ethoxylated tallow amine'.",
    },
    "C.I. Acid Blue 182": {
        "g": "Not Classified",
        "s": "No GHS hazard criteria met (majority not-classified per ECHA C&L via PubChem)",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "Colorant (CI 61585, CAS 12219-26-0). PubChem CID 20846229 — reported as not "
                "meeting GHS hazard criteria by 2155 of 2156 companies. Disclosed by Reckitt "
                "SmartLabel for Glass Plus.",
    },
    "Acid Yellow 23": {
        "g": "Not Classified",
        "s": "No GHS hazard criteria met; FDA-certified color additive (FD&C Yellow No. 5).",
        "ev": "Low",
        "gr": {},
        "impacts": [],
        "note": "Tartrazine (CI 19140, CAS 1934-21-0), PubChem CID 164825. PubChem PUG View carries "
                "no GHS classification section for this CID, so no ECHA C&L consensus exists to "
                "grade from; recorded unclassified rather than guessed. Disclosed by Reckitt "
                "SmartLabel for Lime-A-Way Toilet Bowl Cleaner.",
    },
    "Acid Blue 93": {
        "g": "Not Classified",
        "s": "No GHS hazard criteria met (majority not-classified per ECHA C&L via PubChem)",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "Colorant (CI 42780, CAS 28983-56-4; PubChem title 'Methyl Blue'). PubChem CID "
                "76956083 — reported as not meeting GHS hazard criteria by 2165 of 2210 companies. "
                "Disclosed by Reckitt SmartLabel for Lime-A-Way Toilet Bowl Cleaner; the disclosure "
                "flags it an AOEC asthmagen.",
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


FRAG_NOTE = ("Fragrance components are listed individually because the manufacturer disclosure "
             "lists them individually (Church & Dwight publishes fragrance components at or above "
             "100 ppm or on a designated list); the DB's existing fragrance-allergen pattern.")


PRODUCTS = [
    prod("Arm & Hammer Liquid Laundry Detergent, Baking Soda Fresh", "Church & Dwight",
         "Laundry Detergent",
         ["Water", "C10-16 Pareth", "C12-15 Alcohols Ethoxylated", "Sodium Laureth Sulfate",
          "Pentasodium DTPA", "Sodium Bicarbonate", "Sodium Carbonate", "Fragrance",
          "Sodium (C10-16) Alkylbenzenesulfonate", "Acrylic Acid Homopolymer",
          "Disodium Distyrylbiphenyl Disulfonate", "Sodium Hydroxide",
          "Polyoxyalkylene Substituted Chromophore", "Nitrilotriacetic Acid",
          "4-tert-Butylcyclohexyl Acetate", "Allyl Cyclohexanepropionate", "Allyl Heptanoate",
          "Citral", "Cyclamen Aldehyde", "Dihydromyrcenol", "Tricyclodecenyl Propionate",
          "Fructone", "Galaxolide", "Hexyl Cinnamal", "Hexyl Salicylate",
          "Tetramethyl Acetyloctahydronaphthalenes", "Verdyl Acetate", "Orange Terpenes",
          "Gamma-Undecalactone", "2-Methoxynaphthalene", "Limonene"],
         "mass", "reported", CD_AH,
         10, "extrapolated", CD_AH,
         BASE_BASIS + "Arm & Hammer is one of the largest US laundry brands and this is its "
                      "mainstream scented liquid; the estimate stops at the brand's share of the "
                      "mass channel rather than a measured product share.",
         subs=[{"name": "Arm & Hammer Liquid Laundry Detergent, Perfume and Dye Free",
                "tier": "mass",
                "note": "Same brand and disclosure family (C&D material 42017319) with no "
                        "fragrance and no dye. Removes the entire fragrance-component block "
                        "listed here, including the polycyclic musk and the EU fragrance "
                        "allergens, and drops the colorant."},
               {"name": "all free clear Original Concentrated Liquid Laundry Detergent",
                "tier": "mass",
                "note": "Fragrance-free and dye-free at a similar price point. Avoids the "
                        "fragrance-component block and the optical brightener."}],
         tier_note=FRAG_NOTE),

    prod("Xtra Liquid Laundry Detergent, Tropical Passion", "Church & Dwight",
         "Laundry Detergent",
         ["Water", "Sodium Carbonate", "Sodium Laureth Sulfate", "C12-13 Alcohols Ethoxylated",
          "C10-16 Pareth", "Sodium (C10-16) Alkylbenzenesulfonate", "Acrylic Acid Homopolymer",
          "Disodium Distyrylbiphenyl Disulfonate", "Sodium Chloride", "Sodium Hydroxide",
          "Pentasodium DTPA", "Polyoxyalkylene Substituted Chromophore", "Fragrance",
          "4-tert-Butylcyclohexyl Acetate", "Dipropylene Glycol", "2-Methoxynaphthalene",
          "Tetramethyl Acetyloctahydronaphthalenes", "Dihydromyrcenol", "Galaxolide",
          "Hexyl Cinnamal", "Orange Terpenes", "Verdyl Acetate", "Citronellol",
          "Hydroxycitronellal", "Linalool"],
         "mass", "reported", CD_XTRA,
         5, "extrapolated", CD_XTRA,
         BASE_BASIS + "Xtra is a value-priced laundry brand sold through mass and dollar channels; "
                      "the estimate stops at the brand's share of that channel rather than a "
                      "measured product share.",
         subs=[{"name": "Arm & Hammer Liquid Laundry Detergent, Perfume and Dye Free",
                "tier": "mass",
                "note": "Same manufacturer, fragrance- and dye-free, similar price point. Removes "
                        "the fragrance-component block and the optical brightener."},
               {"name": "Purex Free & Clear Liquid Laundry Detergent",
                "tier": "mass",
                "note": "Value-priced and fragrance-free. Avoids the fragrance components, the "
                        "optical brightener and the chelating agent."}],
         tier_note=FRAG_NOTE),

    prod("Glass Plus Cleaner", "Reckitt", "Glass Cleaner",
         ["Water", "Propylene Glycol Butyl Ether", "Methoxyisopropanol", "Propylene Glycol",
          "Ethanolamine", "C9-11 Alkyl Glucoside", "Sodium Lauryl Sulfate",
          "Sodium Laureth Sulfate", "Fragrance", "C.I. Acid Blue 182", "Eugenol", "Ethanol"],
         "mass", "reported", RB_GLASS,
         4, "extrapolated", RB_GLASS,
         BASE_BASIS + "Glass cleaner is a near-universal US household product and Glass Plus is a "
                      "long-standing national brand; the estimate stops at the brand's share of "
                      "the category rather than a measured product share.",
         subs=[{"name": "Method Glass Cleaner",
                "tier": "natural",
                "note": "Avoids the glycol-ether solvent pair and the ethanolamine; a different "
                        "surfactant base."},
               {"name": "Distilled White Vinegar (5%)",
                "tier": "apothecary-bulk",
                "note": "Diluted and used as a glass spray. Avoids every solvent and the "
                        "fragrance; the trade-off is the vinegar odor."}],
         tier_note="Glass Plus is a Reckitt mass-market glass cleaner; the disclosure flags "
                   "methoxyisopropanol on California's non-cancer hazard list and ethanolamine as "
                   "an AOEC asthmagen."),

    prod("Lime-A-Way Toilet Bowl Cleaner", "Reckitt", "Toilet Bowl Cleaner",
         ["Water", "Hydrochloric Acid", "PEG-2 Hydrogenated Tallow Amine", "C10-16 Pareth",
          "Methyl Salicylate", "Acid Yellow 23", "Acid Blue 93"],
         "mass", "reported", RB_LIME,
         4, "extrapolated", RB_LIME,
         BASE_BASIS + "Toilet-bowl cleaner is used in most US households and Lime-A-Way is a "
                      "long-standing national brand; the estimate stops at the brand's share of "
                      "the category rather than a measured product share.",
         subs=[{"name": "CLR Calcium Lime Rust Cleaner",
                "tier": "mass",
                "note": "Acid descaler without hydrochloric acid; a different acid base and no "
                        "colorants."},
               {"name": "Distilled White Vinegar (5%)",
                "tier": "apothecary-bulk",
                "note": "Used undiluted for light mineral film. Avoids the strong mineral acid, "
                        "the ethoxylated tallow amine and both dyes; weaker on heavy scale."}],
         tier_note="A hydrochloric-acid bowl cleaner. The disclosure flags Acid Blue 93 as an "
                   "AOEC asthmagen and methyl salicylate as an EU fragrance allergen."),
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
