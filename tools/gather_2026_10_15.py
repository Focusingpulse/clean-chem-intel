#!/usr/bin/env python3
"""Daily gather (2026-10-15, 10:00Z maintenance lane).

Two genuinely missing US cleaning products, the ingredient keys they need,
one owner record, and one regulatory-watch addition.

Sources read on 2026-10-15:

  - Scotchgard Fabric Water Shield (3M). 3M's own US Safety Data Sheet,
    Section 3 (Composition/information on ingredients), which itemizes each
    component with its CAS number and weight range.
    https://multimedia.3m.com/mws/mediawebserver?mwsId=SSSSSuUn_zu8l_gIMYten8_vmv70k17zHvu9lxtD7SSSSSS--
  - Concrobium Mold Control (Siamons International Inc.). The maker's own
    Safety Data Sheet, Section 3, which itemizes the hazardous components with
    CAS numbers and weight ranges.
    https://assets.unilogcorp.com/187/ITEM/DOC/Concrobium_100041600_SDS.pdf

Why these two. The corpus is deep in the bleach / bathroom / laundry aisles
and thin in the "treat the surface rather than wash it" shelf -- fabric
protectors, mold remediation, the products a homeowner reaches for when the
problem is a material rather than a stain. Both of these are mass-market US
staples that were absent, and both disclose in a way worth carrying: Scotchgard
names four of seven components with CAS numbers and one only by chemical class
marked trade secret; Concrobium's whole disclosed composition is two salts.

Grading method (stated because it is not the raw tool output). The house rule
is the strict >=40% ECHA C&L notifier consensus, UNION the EU harmonized
classification codes when PubChem lists them in a block without percentages,
applied via tools/ghs_lookup.py and tools/grade_batch.py. Every CID below was
checked against the returned title before the record was accepted. Where a
substance has no PubChem CID at all (a UVCB, a polymer, or a functional
trade-secret description) it is recorded as "Not Classified" with an explicit
sourcing note -- never invented. Allergenicity goes in impacts[], never as a
grade dimension.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-15"

SCOTCHGARD_SDS = ("https://multimedia.3m.com/mws/mediawebserver?mwsId="
                  "SSSSSuUn_zu8l_gIMYten8_vmv70k17zHvu9lxtD7SSSSSS--")
CONCROBIUM_SDS = ("https://assets.unilogcorp.com/187/ITEM/DOC/"
                  "Concrobium_100041600_SDS.pdf")

# --------------------------------------------------------------------------
# Ingredient keys the corpus does not carry.
# --------------------------------------------------------------------------
NEW_KEYS = {
    "Petroleum Gases, Liquified, Sweetened": {
        "ev": "Low",
        "g": "Not Classified",
        "gr": {},
        "impacts": [],
        "note": (
            "Disclosed by 3M in the SDS composition section for Scotchgard "
            "Fabric Water Shield at 3-7% by weight, with CAS 68476-86-8. "
            "PubChem returns 404 for both the name and the CAS, because this "
            "is a UVCB -- a liquefied petroleum gas fraction, not a single "
            "discrete substance -- so no discrete GHS record exists to grade. "
            "Recorded unclassified with confidence Low rather than guessed, "
            "the same convention already used here for 'Proprietary "
            "Surfactant' and 'Proprietary Corrosion Inhibitor'. This is NOT a "
            "finding that the substance is non-hazardous; it is a finding "
            "that there is no discrete record. The fraction is a short-chain "
            "alkane mix whose individual components are flammable gases; the "
            "product's other propellant, 1,1-difluoroethane, does carry a GHS "
            "record and is graded separately in this same product."),
        "s": ("Liquefied petroleum gas fraction (UVCB, CAS 68476-86-8); "
              "aerosol propellant. No discrete GHS record exists to grade."),
        "added": TODAY,
    },
    "Styrene Maleic Anhydride Copolymer": {
        "ev": "Low",
        "g": "Not Classified",
        "gr": {},
        "impacts": [],
        "note": (
            "Disclosed by 3M in the SDS composition section for Scotchgard "
            "Fabric Water Shield at 1-5% by weight, with CAS 52720-34-0. "
            "PubChem returns 404 for both the name and the CAS: this is a "
            "polymer and PubChem carries no discrete GHS classification "
            "record for it. Recorded unclassified with confidence Low rather "
            "than guessed. The polymer is the film-forming soil-release agent "
            "the treatment leaves on the fabric; its hazard profile is "
            "governed by residual monomer content, which the SDS does not "
            "disclose."),
        "s": ("Styrene/maleic anhydride copolymer (CAS 52720-34-0); "
              "film-forming soil-release polymer. No discrete GHS record."),
        "added": TODAY,
    },
    "Organic Acid Ester Salt": {
        "ev": "Low",
        "g": "Not Classified",
        "gr": {},
        "impacts": [],
        "note": (
            "Disclosed by 3M in the SDS composition section for Scotchgard "
            "Fabric Water Shield at 1-5% by weight, and named ONLY by chemical "
            "class -- the SDS marks the entry 'Trade Secret' with no CAS "
            "number and no identity. No PubChem record can exist for a class "
            "description, so no grade is assigned and the entry is recorded "
            "unclassified rather than guessed. This is a functional "
            "disclosure with no identity at all, the same shape as "
            "'Proprietary Surfactant' elsewhere in the corpus, and it is the "
            "transparency engine's whole subject in one line: a component "
            "present at up to 5% that the maker declines to name."),
        "s": ("Organic acid ester salt; identity withheld as trade secret, "
              "CAS not available."),
        "added": TODAY,
    },
    "Trisodium Phosphate": {
        "ev": "High",
        "g": "H314,H318,H315,H319,H335",
        "gr": {"derm": "F", "resp": "C"},
        "impacts": [],
        "note": (
            "Graded from PubChem GHS (CID 24243, returned title 'Trisodium "
            "Phosphate'; the returned title was confirmed against the "
            "intended substance before the record was accepted). ECHA C&L "
            "notifier consensus: H315 (90.2%) and H319 (90.1%) -> derm C, "
            "H335 (85.1%) -> resp C; unioned with the harmonized "
            "classification block, listed without percentages, which adds "
            "H314 (skin corrosion) -> derm F and H318 (serious eye damage) -> "
            "derm D, per the house rule. H314 and H318 both clear the bar and "
            "are carried. Disclosed by Siamons International in the SDS "
            "composition section for Concrobium Mold Control at 1-5% by "
            "weight (CAS 7601-54-9)."),
        "s": ("Trisodium phosphate (TSP); alkaline builder. Causes severe skin "
              "burns and serious eye damage, respiratory irritation."),
        "added": TODAY,
    },
}

# --------------------------------------------------------------------------
# Label terms aliased to existing keys rather than re-minted.
# --------------------------------------------------------------------------
ALIASES = {
    # 3M's SDS names this component "2-Butoxyethanol" with CAS 111-76-2. The
    # corpus already carries the same substance under the key
    # "Butyloxyethanol" (graded from PubChem CID 8133, whose returned title is
    # "2-Butoxyethanol"), merged there on 2026-10-04 from a second spelling.
    # Aliasing to the existing graded key rather than minting a third spelling
    # for one substance.
    "2-Butoxyethanol": "Butyloxyethanol",
}

# --------------------------------------------------------------------------
# Products. Every ingredient list below is the maker's own SDS composition
# section, read 2026-10-15.
# --------------------------------------------------------------------------
PRODUCTS = [
    {
        "name": "Scotchgard Fabric Water Shield",
        "brand": "3M",
        "cat": "Specialty",
        "ings": ["Water", "Petroleum Gases, Liquified, Sweetened",
                 "Sodium Lauryl Sulfate", "Styrene Maleic Anhydride Copolymer",
                 "Organic Acid Ester Salt", "1,1-Difluoroethane",
                 "2-Butoxyethanol"],
        "source": (
            "3M's own US Safety Data Sheet for Scotchgard Fabric Water Shield, "
            "Section 3 (Composition/information on ingredients), read "
            "2026-10-15, which itemizes each component with its CAS number and "
            "weight range: water (7732-18-5) 85-90%, petroleum gases, "
            "liquefied, sweetened (68476-86-8) 3-7%, sodium lauryl sulfate "
            "(151-21-3) 1-5%, styrene maleic anhydride copolymer (52720-34-0) "
            "1-5%, organic acid ester salt (trade secret, no CAS) 1-5%, "
            "1,1-difluoroethane (75-37-6) 1-3% and 2-butoxyethanol (111-76-2) "
            "<0.5%. The maker's separate EU/Canada SDS for the same product "
            "line lists a different propellant set (hydrocarbons C9-C11 plus "
            "butane and propane) because the aerosol formulation differs by "
            "market; the US composition is the one recorded, and the "
            "difference is noted rather than silently resolved."),
        "source_url": SCOTCHGARD_SDS,
        "note": (
            "3M's consumer fabric protector -- the spray that made "
            "'Scotchgard' a verb for stain-proofing upholstery. The disclosed "
            "formula is short and mostly named: water as the carrier, a "
            "styrene/maleic anhydride copolymer as the film-forming "
            "soil-release agent, plain sodium lauryl sulfate as the "
            "surfactant, and two propellants. What the maker does NOT name is "
            "the component that does the water-repelling -- it appears only as "
            "'organic acid ester salt', marked trade secret, at up to 5%. That "
            "is the transparency engine's subject in one line: the functional "
            "ingredient is the one withheld. Note also that no perfluorinated "
            "component appears anywhere in the disclosed composition, while "
            "one of the two propellants (1,1-difluoroethane, HFC-152a) is a "
            "fluorinated greenhouse gas -- so the fluorochemistry in this can "
            "is in the propellant, not the repellent, and the two have very "
            "different regulatory trajectories. The same brand is a different "
            "formulation in the EU and Canada, where the SDS lists a "
            "hydrocarbon propellant set instead."),
        "owner": "3M Company", "owner_ev": "verified",
        "owner_src": SCOTCHGARD_SDS,
        "tier": "mass", "tier_ev": "untested",
        "tier_basis": (
            "Searched for a citable source for the tier and found none "
            "reachable from this environment: 3M's own consumer product pages "
            "(3m.com, scotchgard.com) do not resolve from the sandbox, and no "
            "third-party certification covers this product. The tier was "
            "assigned by exclusion rather than by a source, so it is "
            "downgraded to untested rather than left marked reported with "
            "nothing to point at. A guessed tier is worse than no tier."),
        "substitutes": [],
        "strength_disclosure": "partial",
        "added": TODAY, "updated": TODAY,
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
            "gap rather than estimated. A mass-market aerosol sold through "
            "grocery, hardware and home channels."),
    },
    {
        "name": "Concrobium Mold Control",
        "brand": "Concrobium",
        "cat": "Specialty",
        "ings": ["Water", "Trisodium Phosphate", "Sodium Carbonate"],
        "source": (
            "The maker's own Safety Data Sheet for Concrobium Mold Control "
            "(Siamons International Inc., Toronto), Section 3 "
            "(Composition/information on ingredients), read 2026-10-15, which "
            "itemizes the hazardous components with CAS numbers and weight "
            "ranges: trisodium phosphate (7601-54-9) 1-5% and sodium carbonate "
            "(497-19-8) less than 1%. The SDS states the product is not "
            "classified as hazardous under the OSHA Hazard Communication "
            "Standard and lists no GHS pictogram, signal word or precautionary "
            "statement. Note that the maker's SDS itemizes only the hazardous "
            "components; the balance of the water-based formula is not "
            "itemized, and a later distributor SDS for the aerosolized pack "
            "(Rust-Oleum, 2023) gives the same two components at different "
            "ranges (sodium carbonate 1.0-2.5%, trisodium phosphate 0.1-1.0%) "
            "-- both are recorded here as a range disagreement rather than "
            "silently picking one."),
        "source_url": CONCROBIUM_SDS,
        "note": (
            "The mass-market mold-remediation spray, sold through hardware and "
            "home channels, and the corpus's first product whose entire "
            "disclosed actives are two alkaline salts -- trisodium phosphate "
            "and sodium carbonate -- with no bleach, no quaternary ammonium "
            "and no registered pesticide active. That is the interesting part: "
            "the product is marketed as a mold treatment rather than a "
            "disinfectant, and its disclosed composition is a pH-raiser rather "
            "than a biocide, which is a different mechanism from every other "
            "mold product the corpus carries (Tilex and the bleach cleaners "
            "work by oxidation, the quat sprays by membrane disruption). The "
            "SDS treats the product as non-hazardous while the trisodium "
            "phosphate it contains is itself graded derm F / resp C on its own "
            "record -- the mixture is below the concentration that triggers "
            "classification, which is a real and ordinary outcome, not a "
            "contradiction, and both facts are carried. The maker's SDS "
            "itemizes only hazardous components, so the ingredient list here "
            "is a floor, not a full disclosure."),
        "owner": "Siamons International Inc.", "owner_ev": "verified",
        "owner_src": "https://www.concrobium.com/",
        "tier": "mass", "tier_ev": "reported",
        "tier_src": "https://www.concrobium.com/",
        "tier_note": ("Tier rests on the maker's own US product site "
                      "(Concrobium), which sells direct and through hardware "
                      "and home channels."),
        "substitutes": [],
        "strength_disclosure": "partial",
        "added": TODAY, "updated": TODAY,
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
            "gap rather than estimated. A mass-market mold-control product "
            "sold through hardware and home channels."),
    },
]

# --------------------------------------------------------------------------
# Owner records the registry does not carry.
# --------------------------------------------------------------------------
NEW_OWNERS = {
    "Siamons International Inc.": {
        "type": "private",
        "detail": (
            "Siamons International Inc. (Toronto, Ontario) makes the "
            "Concrobium line of mold-control and odor products; the maker's "
            "own Safety Data Sheet names it as the responsible party and gives "
            "a Toronto address. The brand is sold through hardware and home "
            "channels in the US and Canada, with an aerosolized pack "
            "distributed under a Rust-Oleum SDS."),
        "ev": "verified",
        "src": "https://www.concrobium.com/",
        "brands": ["Concrobium"],
    },
}

# --------------------------------------------------------------------------
# Regulatory watch -- a live restriction the new records touch.
# --------------------------------------------------------------------------
REG_WATCH = {
    "name": "HFC aerosol propellants (HFC-152a / 1,1-difluoroethane)",
    "region": "us",
    "status": "phasing down",
    "since": "2020",
    "rule": (
        "The US AIM Act (2020) directs EPA to phase down HFC production and "
        "consumption 85% by 2036, and the EU F-gas Regulation (517/2014) "
        "phases HFCs down on a comparable schedule; both cover HFC-152a "
        "(GWP 138) as used as an aerosol propellant. Unlike the other entries "
        "here this is a climate restriction, not a toxicity restriction -- the "
        "propellant carries no health hazard classification, but it is a "
        "fluorinated greenhouse gas being squeezed out of consumer aerosols. "
        "Recorded because Scotchgard Fabric Water Shield, added 2026-10-15, "
        "discloses it at 1-3%."),
    "reason": ("Fluorinated greenhouse gas (GWP 138); production and "
               "consumption phased down under the Kigali Amendment, the US "
               "AIM Act and the EU F-gas Regulation."),
    "src": "https://www.epa.gov/climate-hfcs-reduction",
}


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def dump(path, obj, indent):
    # Measured at head: products/ingredients/owners/reg indent=1 no trailing
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

    # ---- GATHER ----------------------------------------------------------
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

    for name, rec in NEW_OWNERS.items():
        if name in owners["owners"]:
            print(f"owner exists, not re-minting: {name}")
            continue
        owners["owners"][name] = rec
        print(f"new owner: {name}")

    # ---- REGULATORY WATCH ------------------------------------------------
    existing = {w.get("name") for w in reg["watchlist"]}
    if REG_WATCH["name"] in existing:
        print(f"reg watch exists: {REG_WATCH['name']}")
    else:
        reg["watchlist"].append(REG_WATCH)
        print(f"new reg watch: {REG_WATCH['name']}")

    # ---- WRITE -----------------------------------------------------------
    dump(os.path.join(DATA, "products.json"), products, 1)
    dump(os.path.join(DATA, "ingredients.json"), ingredients, 1)
    dump(os.path.join(DATA, "owners.json"), owners, 1)
    dump(os.path.join(DATA, "reg.json"), reg, 1)

    if added:
        changelog.insert(0, {
            "date": TODAY,
            "text": (
                "Gather: two missing mass-market US surface-treatment products "
                "added from the makers' own SDS composition sections. "
                "Scotchgard Fabric Water Shield (3M) -- seven disclosed "
                "components, four named with CAS numbers, one named only by "
                "chemical class and marked trade secret ('organic acid ester "
                "salt', 1-5%), and a propellant pair of a liquefied petroleum "
                "gas fraction plus 1,1-difluoroethane (HFC-152a); the "
                "disclosure is the product's subject, because the component "
                "that does the water-repelling is the one withheld. "
                "Concrobium Mold Control (Siamons International Inc.) -- the "
                "corpus's first mold product whose disclosed actives are two "
                "alkaline salts (trisodium phosphate 1-5%, sodium carbonate "
                "<1%) rather than a biocide, a different mechanism from every "
                "other mold product carried; its SDS itemizes only hazardous "
                "components, so its ingredient list is recorded as a floor. "
                "Four new ingredient keys: Trisodium Phosphate (CID 24243, "
                "returned title confirmed; notifier consensus H315 90.2% / "
                "H319 90.1% / H335 85.1% unioned with the harmonized H314 / "
                "H318 block -> derm F, resp C) and three recorded without a "
                "grade with explicit sourcing notes because no discrete "
                "PubChem record exists (Petroleum Gases, Liquified, Sweetened "
                "-- a UVCB, CAS 68476-86-8, 404 in PubChem; Styrene Maleic "
                "Anhydride Copolymer -- a polymer, CAS 52720-34-0, 404; "
                "Organic Acid Ester Salt -- a class description marked trade "
                "secret, no CAS). One label term ALIASED to an existing key "
                "rather than re-minted (2-Butoxyethanol -> Butyloxyethanol, "
                "same substance, CAS 111-76-2, already graded from CID 8133). "
                "One owner record minted (Siamons International Inc.; 3M "
                "Company was already held). One regulatory-watch addition: "
                "HFC aerosol propellants (HFC-152a, GWP 138) under the US AIM "
                "Act and the EU F-gas Regulation -- a climate restriction "
                "rather than a toxicity one, recorded because the Scotchgard "
                "record discloses it at 1-3%."),
        })
        dump(os.path.join(DATA, "changelog.json"), changelog, 2)

    print(f"\nwrote {added} products, {len(added_keys)} new ingredient keys.")


if __name__ == "__main__":
    main()
