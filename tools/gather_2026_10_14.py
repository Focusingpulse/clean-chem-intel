#!/usr/bin/env python3
"""Daily gather + repair (2026-10-14, 10:00Z maintenance lane).

Two genuinely missing US cleaning products, the ingredient keys they need,
two owner records, and one REPAIR: a duplicate product pair the dedupe guard
cannot see.

Sources read on 2026-10-14:

  - Purple Power Industrial Strength Cleaner/Degreaser. Aiken Chemical Co.'s
    own California Cleaning Product Right to Know Act (SB-258) ingredient
    disclosure, which lists each ingredient with its CAS number and function,
    cross-checked against Aiken's own SDS composition section (which
    quantifies sodium silicate at 1-5%).
    https://prosourcediesel.com/wp-content/uploads/2022/04/Purple-Power-Cleaner-Degreaser.pdf
    https://eunoffgsnusqmqgzpigj.supabase.co/storage/v1/object/public/product-media/sds/purple-power-industrial-cleaner-degreaser.pdf
  - Citra Solv Concentrated Cleaner & Degreaser. The maker's own product page,
    which publishes a per-ingredient table with CAS numbers and the
    designated lists each ingredient appears on.
    https://citrasolv.com/products/citra-solv-concentrated-cleaner-degreaser

Why these two. The corpus is deep in bleach / bathroom / disinfectant and in
the mass laundry aisle, and it is thin in the solvent-degreaser shelf -- the
one shelf a transparency engine should be best at, because it is where the
disclosed aromatic and glycol-ether loads actually are. Purple Power is the
mass-market purple degreaser (sodium hydroxide + diethylene glycol monobutyl
ether + tetrasodium EDTA + sodium silicate) and carries the first disclosed
"proprietary corrosion inhibitor" in the corpus. Citra Solv is the
plant-based citrus solvent that competes with it on the same shelf, and it is
the first product here whose whole solvent system is d-limonene plus a
laureth surfactant pair.

Grading method (stated because it is not the raw tool output). The house rule
is the strict >=40% ECHA C&L notifier consensus, UNION the EU harmonized
classification codes when PubChem lists them in a block without percentages,
applied via tools/ghs_lookup.py and tools/grade_batch.py. Every CID below was
checked against the returned title before the record was accepted. Dimension
grades use the database's existing mapping (H314 -> derm F, H318/H317 -> derm
D, H315/H319 -> derm C, H332/H335/H336 -> resp C, H373 -> organ C, H351 ->
canc C, H361 -> repro C, H400 -> env F, H410/H411 -> env D). Allergenicity
goes in impacts[], never as a grade dimension.

REPAIR (the reason this run is worth reading). The corpus carried the same
product twice: "Bon Ami" (brand "Faultless") and "Powder Cleanser" (brand
"Bon Ami"), same owner (Faultless Brands), same category (Abrasive Cleanser),
same substance -- one listed calcium carbonate, the other its mineral synonym
limestone, both CAS 1317-65-3. The dedupe guard keys on normalized
name+brand, so a pair whose name AND brand are both different is invisible to
it; the guard correctly reported "no duplicates". This run merges the pair
into one canonical record and completes the disclosure, because BOTH copies
omitted the surfactant the maker lists on its own ingredient page and in its
SDS (benzenesulfonic acid, C10-16-alkyl derivs., CAS 68584-22-5, <1%).
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-14"

DRY = "--dry-run" in sys.argv
NO_CHANGELOG = "--no-changelog" in sys.argv

PP_SB258 = ("https://prosourcediesel.com/wp-content/uploads/2022/04/"
            "Purple-Power-Cleaner-Degreaser.pdf")
PP_SDS = ("https://eunoffgsnusqmqgzpigj.supabase.co/storage/v1/object/public/"
          "product-media/sds/purple-power-industrial-cleaner-degreaser.pdf")
CS_PAGE = ("https://citrasolv.com/products/"
           "citra-solv-concentrated-cleaner-degreaser")
BONAMI_ING = "https://www.bonami.com/products/bon-ami-powder-cleanser/"
BONAMI_SDS = ("https://corporate.faultless.com/SDSfiles/Bon%20Ami%20Products/"
              "Bon%20Ami%20Cleanser.pdf")

# --------------------------------------------------------------------------
# New ingredient keys. Grades are the de-duplicated >=40% ECHA consensus set
# (see the module docstring for the method).
# --------------------------------------------------------------------------
NEW_KEYS = {
    "Laureth-3": {
        "ev": "High",
        "g": "H302,H315,H318,H319,H400",
        "gr": {"derm": "D", "env": "F"},
        "impacts": ["derm", "aqua"],
        "note": (
            "Graded from PubChem GHS (CID 76458, returned title "
            "'2-(2-(2-(Dodecyloxy)ethoxy)ethoxy)ethanol'; the returned title "
            "was confirmed against the intended substance -- laureth-3 is the "
            "3-EO-unit ethoxylate of lauryl alcohol, and the returned "
            "structure is exactly that -- before the record was accepted). "
            "PubChem lists two ECHA blocks. The notifier-consensus block "
            "(80 reports / 4 notifications) gives H318 (serious eye damage) "
            "48.8% -> derm D, H319 (eye irritation) 51.2% -> derm C, and H400 "
            "(very toxic to aquatic life) 47.5% -> env F. The second block, "
            "listed without percentages (the harmonized classification), adds "
            "H302 (harmful if swallowed), H315 (skin irritation) -> derm C, "
            "and H318 -> derm D; those are carried per the house rule. H318 "
            "and H319 are mutually exclusive in GHS and both clear the 40% "
            "bar here because the notifier pool splits between them; both are "
            "recorded rather than picking one. Disclosed by Citra Solv on its "
            "own product page as 'Laureth-3' with CAS 68439-50-9, flagged "
            "there as a California PBT-list entry."),
        "s": ("Ethoxylated lauryl alcohol (average 3 EO units); nonionic "
              "surfactant. Serious eye damage, skin irritation, very toxic to "
              "aquatic life."),
        "added": TODAY,
    },
    "PEG-10 Dioleate": {
        "ev": "Low",
        "g": "Not Classified",
        "gr": {},
        "impacts": [],
        "note": (
            "The maker discloses the label term 'PEG-10 Dioleate' with CAS "
            "9005-07-6. PubChem's NAME lookup returns 404 for the label term; "
            "the CAS lookup resolves to CID 5378708, returned title "
            "'Polyoxyethylene dioleate' -- the correct class for a "
            "polyethylene-glycol diester of oleic acid, so the CAS is the "
            "anchor here rather than the trade name. That record's GHS block "
            "reads 'Not Classified', with the ECHA summary noting 670 of 711 "
            "reporting companies provided no hazard criteria. Recorded as Not "
            "Classified with confidence Low, because the record is a "
            "class-level polymer entry rather than a single discrete "
            "substance and the trade name and the CID are not the same string. "
            "Disclosed by Citra Solv on its own product page as 'PEG-10 "
            "Dioleate' with CAS 9005-07-6."),
        "s": ("Polyethylene glycol dioleate (PEG diester of oleic acid); "
              "emulsifier. No GHS hazard criteria reported."),
        "added": TODAY,
    },
    "Proprietary Corrosion Inhibitor": {
        "ev": "Low",
        "g": "Not Classified",
        "gr": {},
        "impacts": [],
        "note": (
            "Named only by function on Aiken Chemical's California SB-258 "
            "disclosure for Purple Power, with no CAS number and no chemical "
            "identity. No PubChem record exists for a functional description, "
            "so no grade is assigned and the entry is recorded unclassified "
            "rather than guessed -- the same convention already used here for "
            "'Proprietary Surfactant' and 'Proprietary Chelating Agent'. This "
            "is NOT a finding that the substance is non-hazardous; it is a "
            "finding that the maker does not disclose it. The product's own "
            "SDS names only sodium silicate as a hazardous component, so the "
            "inhibitor is not among the components Aiken treats as hazardous."),
        "s": ("Corrosion inhibitor named only by function; identity withheld "
              "as proprietary, CAS not available."),
        "added": TODAY,
    },
}

# --------------------------------------------------------------------------
# Label terms aliased to existing keys rather than re-minted.
# --------------------------------------------------------------------------
ALIASES = {
    # The maker's term for orange peel oil (CAS 8028-48-6). The corpus already
    # carries TWO keys for this one substance -- "Orange Oil" (graded, CID
    # 62161) and "Citrus Aurantium Dulcis (Orange) Peel Oil" (ungraded, no CID
    # resolved). Aliasing to the GRADED key rather than minting a third, and
    # flagging the split in the changelog instead of deepening it.
    "Citrus Aurantium Dulcis Peel Extract": "Orange Oil",
}

# --------------------------------------------------------------------------
# Products. Every ingredient list below is the maker's own published list or
# the maker's own SDS composition section, read 2026-10-14.
# --------------------------------------------------------------------------
PRODUCTS = [
    {
        "name": "Purple Power Industrial Strength Cleaner/Degreaser",
        "brand": "Purple Power",
        "cat": "Specialty",
        "ings": ["Water", "Proprietary Corrosion Inhibitor", "Sodium Hydroxide",
                 "Tetrasodium EDTA", "Diethylene Glycol Monobutyl Ether",
                 "Proprietary Surfactant",
                 "Polyoxyalkylene Substituted Chromophore", "Sodium Silicate"],
        "source": (
            "Aiken Chemical Co.'s own California Cleaning Product Right to "
            "Know Act (SB-258) ingredient disclosure for Purple Power "
            "Industrial Strength Cleaner/Degreaser (part numbers 4302P, "
            "4315PS, 4332PS, 4319PS, 4320P, 4322P, 4325P, 4390S, 4340, PP275, "
            "PP330), read 2026-10-14, which lists each ingredient with its CAS "
            "number and function. The disclosure names three surfactant "
            "entries (two 'Proprietary Surfactant Blend' and one 'Proprietary "
            "Surfactant') and two colorant entries ('Polyoxyalkylene "
            "Substituted Chromophore (Dye)'); each group is recorded here as "
            "one key because the maker gives them the same name and no CAS. "
            "Cross-checked against Aiken's own SDS composition section "
            "(version 2.0, 2024-03-29), which quantifies sodium silicate "
            "(1344-09-8) at 1-5% as the only component it treats as "
            "hazardous, and whose New Jersey / Pennsylvania Right-to-Know "
            "blocks list water and diethylene glycol monobutyl ether "
            "(112-34-5). Exact percentages are withheld as trade secret."),
        "source_url": PP_SB258,
        "note": (
            "The mass-market purple degreaser, and the first product in the "
            "corpus built on a caustic-plus-glycol-ether solvent pair. The "
            "cleaning system is sodium hydroxide as the alkaline agent, "
            "diethylene glycol monobutyl ether (a glycol ether solvent) "
            "carrying the grease, tetrasodium EDTA chelating hard-water "
            "metals, and sodium silicate as the corrosion inhibitor and "
            "alkalinity buffer; the surfactant package is disclosed only by "
            "function, and the purple colour comes from a polymeric "
            "chromophore the maker also declines to name. Two things make the "
            "record worth carrying. First, it is the corpus's first disclosed "
            "'proprietary corrosion inhibitor' -- a functional disclosure with "
            "no identity at all, which is the transparency engine's whole "
            "subject in one line. Second, the maker's own SDS treats exactly "
            "one component as hazardous (sodium silicate, 1-5%), while the "
            "SB-258 list names the glycol ether and the EDTA that the SDS "
            "does not classify -- the two documents disagree about which "
            "components matter, and both are recorded here."),
        "owner": "Aiken Chemical Co., Inc.", "owner_ev": "verified",
        "owner_src": "https://www.clean-rite.com/",
        "tier": None, "tier_ev": "untested",
        "substitutes": [],
        "strength_disclosure": "full",
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
            "gap rather than estimated. A heavy-duty degreaser sold through "
            "auto-parts and hardware channels rather than grocery."),
    },
    {
        "name": "Citra Solv Concentrated Cleaner & Degreaser",
        "brand": "Citra Solv",
        "cat": "Specialty",
        "ings": ["Limonene", "Laureth-3", "Laureth-4", "PEG-10 Dioleate",
                 "Citrus Aurantium Dulcis Peel Extract"],
        "source": (
            "The maker's own product page for Citra Solv Concentrated Cleaner "
            "& Degreaser (Valencia Orange), read 2026-10-14, which publishes a "
            "per-ingredient table with CAS numbers and the designated lists "
            "each ingredient appears on: Limonene (5989-27-5, solvent, EU "
            "Fragrance Allergen), Laureth-3 (68439-50-9, surfactant, CA PBTs), "
            "Laureth-4 (68551-12-2, surfactant), PEG-10 Dioleate (9005-07-6, "
            "emulsifier) and Citrus Aurantium Dulcis Peel Extract (8028-48-6, "
            "fragrance). The maker's older concentrate page lists a shorter "
            "set (limonene, C10-16 pareth-1, orange peel oil); the current "
            "product page is the one recorded, and the difference is noted "
            "rather than silently resolved."),
        "source_url": CS_PAGE,
        "note": (
            "The plant-based citrus solvent that competes with Purple Power on "
            "the same degreaser shelf, and the corpus's first product whose "
            "entire solvent system is d-limonene. The formula is short and "
            "fully disclosed: limonene as the solvent, a laureth-3 / laureth-4 "
            "surfactant pair, a PEG dioleate emulsifier and orange peel oil "
            "for scent. What makes it worth carrying next to Purple Power is "
            "the contrast -- the two products sit on the same shelf and "
            "disclose at opposite ends of the spectrum. Purple Power names "
            "three surfactant entries by function only and a colorant by "
            "function only; Citra Solv names every ingredient with a CAS "
            "number and, unusually, publishes which regulatory lists each one "
            "appears on. The corpus should be able to show a reader both. Note "
            "that 'plant-based' here is a solvent claim, not a hazard claim: "
            "limonene itself is graded derm D / env F with a sensitization "
            "tag, and the maker's own page flags it as an EU fragrance "
            "allergen and flags laureth-3 as a California PBT-list entry."),
        "owner": "Citra Solv LLC", "owner_ev": "verified",
        "owner_src": "https://citrasolv.com/pages/about-us",
        "tier": None, "tier_ev": "untested",
        "substitutes": [],
        "strength_disclosure": "full",
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
            "gap rather than estimated. A concentrated citrus degreaser sold "
            "through natural-grocery and direct channels."),
    },
]

# --------------------------------------------------------------------------
# Owner records the registry does not carry.
# --------------------------------------------------------------------------
NEW_OWNERS = {
    "Aiken Chemical Co., Inc.": {
        "type": "private",
        "detail": (
            "Aiken Chemical Co., Inc. (Greenville, South Carolina) makes the "
            "Purple Power and Clean-Rite brands; the SDS and the SB-258 "
            "disclosure both name it as the responsible party, and its "
            "customer-service contact is served from clean-rite.com. The "
            "company states on its own SDS that it performs no animal "
            "testing."),
        "ev": "verified",
        "src": "https://www.clean-rite.com/",
        "brands": ["Purple Power", "Clean-Rite"],
    },
    "Citra Solv LLC": {
        "type": "private",
        "detail": (
            "Citra Solv LLC makes the Citra Solv line of citrus-solvent "
            "cleaners; the maker's own product page names the company and "
            "publishes the per-ingredient disclosure used for this record. The "
            "brand is sold direct and through natural-grocery and online "
            "channels."),
        "ev": "verified",
        "src": "https://citrasolv.com/pages/about-us",
        "brands": ["Citra Solv"],
    },
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


def merge_bon_ami(products):
    """Collapse the duplicate Bon Ami pair into one canonical record.

    Returns (merged_record_or_None, detail_string).
    """
    matches = [p for p in products
               if p.get("name") == "Bon Ami" and p.get("brand") == "Faultless"]
    matches += [p for p in products
                if p.get("name") == "Powder Cleanser" and p.get("brand") == "Bon Ami"]
    if len(matches) != 2:
        return None, f"expected 2 duplicate records, found {len(matches)}"

    # The richer of the two is the heritage/exposure record; carry its fields
    # and take `safe` from the other so the merge loses nothing.
    rich = next((m for m in matches if m.get("heritage")), matches[0])
    other = next(m for m in matches if m is not rich)

    rec = dict(rich)
    rec["name"] = "Bon Ami Powder Cleanser"
    rec["brand"] = "Bon Ami"
    rec["updated"] = TODAY
    if other.get("safe") and not rec.get("safe"):
        rec["safe"] = other["safe"]
    # Complete the disclosure: the maker's own ingredient page and SDS both
    # list the C10-16 alkylbenzene sulfonic acid surfactant, which NEITHER
    # copy carried.
    if "Alkylbenzene Sulfonic Acid" not in rec["ings"]:
        rec["ings"] = list(rec["ings"]) + ["Alkylbenzene Sulfonic Acid"]
    rec["source_url"] = BONAMI_ING

    for m in matches:
        products.remove(m)
    products.append(rec)
    return rec, (f"merged 2 records -> '{rec['name']}' (brand {rec['brand']}), "
                 f"carried safe={other.get('safe')!r}, "
                 f"added the disclosed surfactant")


def main():
    products = load(os.path.join(DATA, "products.json"))
    ingredients = load(os.path.join(DATA, "ingredients.json"))
    owners = load(os.path.join(DATA, "owners.json"))
    changelog = load(os.path.join(DATA, "changelog.json"))

    names = {r["name"] for r in products}
    lower = {k.lower(): k for k in ingredients}

    # ---- REPAIR: merge the duplicate Bon Ami pair ------------------------
    merged, merge_detail = merge_bon_ami(products)
    print(f"repair: {merge_detail}")

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
            print(f"owner already present, not re-minting: {name}")
            continue
        owners["owners"][name] = rec
        print(f"new owner: {name}")

    for r in products:
        for k in r["ings"]:
            if k not in ingredients:
                raise SystemExit(f"record {r['name']!r} references missing key {k!r}")

    if DRY:
        print(f"\nDRY RUN: would add {added} products, "
              f"{len(added_keys)} ingredient keys, merge {merge_detail}")
        return

    dump(os.path.join(DATA, "products.json"), products, 1)
    dump(os.path.join(DATA, "ingredients.json"), ingredients, 1)
    dump(os.path.join(DATA, "owners.json"), owners, 1)

    if not NO_CHANGELOG:
        changelog.insert(0, {
            "date": TODAY,
            "text": (
                "Gather + repair lane: 2 products added and 1 duplicate pair "
                "merged. NEW PRODUCTS, each from the maker's own disclosure "
                "read 2026-10-14: Purple Power Industrial Strength "
                "Cleaner/Degreaser (Aiken Chemical's own California SB-258 "
                "ingredient disclosure, cross-checked against Aiken's own SDS "
                "composition), the mass-market caustic-plus-glycol-ether "
                "degreaser and the corpus's first disclosed 'proprietary "
                "corrosion inhibitor' -- a functional disclosure with no "
                "chemical identity at all; and Citra Solv Concentrated "
                "Cleaner & Degreaser (the maker's own per-ingredient table "
                "with CAS numbers and designated lists), the plant-based "
                "citrus solvent that competes with it on the same shelf and "
                "the corpus's first product whose whole solvent system is "
                "d-limonene. Three new ingredient keys: Laureth-3 (CID 76458, "
                "returned title confirmed against the intended substance; "
                "notifier consensus H318 48.8% -> derm D, H319 51.2% -> derm "
                "C, H400 47.5% -> env F, unioned with the harmonized H302 / "
                "H315 / H318 block) and two recorded without a grade with an "
                "explicit sourcing note (PEG-10 Dioleate, whose trade name "
                "404s in PubChem and whose CAS 9005-07-6 resolves to the "
                "class-level CID 5378708 'Polyoxyethylene dioleate' reading "
                "Not Classified; and Proprietary Corrosion Inhibitor, named "
                "only by function with no CAS). One label term ALIASED to an "
                "existing key rather than re-minted (Citrus Aurantium Dulcis "
                "Peel Extract -> Orange Oil). Two owner records minted (Aiken "
                "Chemical Co., Inc.; Citra Solv LLC). REPAIR: the corpus "
                "carried the SAME PRODUCT TWICE -- 'Bon Ami' (brand "
                "'Faultless') and 'Powder Cleanser' (brand 'Bon Ami'), same "
                "owner (Faultless Brands), same category (Abrasive Cleanser), "
                "same substance (one listed calcium carbonate, the other its "
                "mineral synonym limestone, both CAS 1317-65-3). The dedupe "
                "guard keys on normalized name+brand, so a pair whose name AND "
                "brand are BOTH different is invisible to it -- it correctly "
                "reported 'no duplicates', and the cause is the guard's key, "
                "not the data. The pair is merged into one canonical record "
                "('Bon Ami Powder Cleanser', brand 'Bon Ami', owner Faultless "
                "Brands) and the disclosure is completed, because BOTH copies "
                "omitted the surfactant the maker lists on its own ingredient "
                "page and in its SDS (benzenesulfonic acid, C10-16-alkyl "
                "derivs., CAS 68584-22-5, <1%). FLAGGED, NOT FIXED: the "
                "corpus carries two keys for one substance -- 'Orange Oil' "
                "(graded, CID 62161) and 'Citrus Aurantium Dulcis (Orange) "
                "Peel Oil' (ungraded, no CID resolved), both CAS 8028-48-6; "
                "the new record aliases to the graded key rather than minting "
                "a third, and the key-level split is left for a lane that can "
                "re-point the existing references."),
        })
        dump(os.path.join(DATA, "changelog.json"), changelog, 2)

    print(f"\nwrote {added} products, {len(added_keys)} new ingredient keys.")


if __name__ == "__main__":
    main()
