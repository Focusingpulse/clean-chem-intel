#!/usr/bin/env python3
"""clean-chem-grow RUN A -- product additions, 2026-10-09.

Rotation state said next_run = "A" (RUN A = researched product additions).
Five products people actually buy, each with a FULL disclosed ingredient list
read from a manufacturer disclosure:

  * Glisten Dishwasher Cleaner                -- near-clean, EPA-registered
  * Glisten Washing Machine Cleaner           -- moderate
  * Plink Washer & Dishwasher Freshener & Cleaner -- simple, value tier
  * Zout Laundry Stain Remover Spray          -- BAD: boric acid, MIT, enzymes
  * Dryel At Home Dry Cleaner                 -- BAD: DMDM hydantoin, IPBC

ROUTE (new, reusable): Summit Brands publishes a single California SB-258
ingredient-disclosure index at https://summitbrands.com/ingredients/ -- one
HTML page carrying a per-product table (Ingredient Name | CAS | Functionality |
SB258 List) for 44 of its household products across Glisten, Iron OUT, Lime
OUT, Dryel, Zout, White Brite, Drain OUT, Whirl OUT, Filter Mate, Plink,
EarthStone, SeptoBac and Woolite Dry Care. Read 2026-10-09, HTTP 200,
302,814 bytes. This is the manufacturer's own publication of the filing, the
same class as the KIK and Vestacy indices already in docs/source-policy.md.

Nothing invented: every ingredient line below is copied from the served table,
and CAS numbers come from that table. No grade is assigned -- the five records
enter with safe = null and the ten new ingredient keys enter ungraded, which
is the honest state until the grading lane reaches them.

Idempotent: a product already present by name is skipped; an ingredient key
that already exists (case-insensitively, or through the alias map) is never
re-minted; a second run adds nothing and writes no changelog entry.

Usage:
  python3 tools/grow_runA_2026_10_09.py [--dry-run] [--no-changelog]
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TODAY = "2026-10-09"

OWNER = "Summit Brands"
# Summit Brands' own about page names the brand family (Glisten, Iron OUT,
# Pumie, Dryel, Zout, Plink, EarthStone) and is the record's src. The brand
# strings below are all named on that page, so the src governs them.
OWNER_BRANDS_TO_ADD = ["Glisten", "Plink", "Zout", "Dryel"]

SRC_INDEX = "https://summitbrands.com/ingredients/"
SRC_DISH = ("https://www.indexbox.io/store/united-states-dishwashing-"
            "market-analysis-forecast-size-trends-and-insights/")
SRC_LAUNDRY = ("https://www.indexbox.io/store/united-states-laundry-home-products-"
               "market-analysis-forecast-size-trends-and-insights/")

SOURCE_TEXT = (
    "Summit Brands' own California Cleaning Product Right to Know Act (SB-258) "
    "ingredient-disclosure index, https://summitbrands.com/ingredients/, read "
    "2026-10-09 (HTTP 200, 302,814 bytes). The index carries one table per product "
    "giving Ingredient Name, CAS number, Functionality and the SB-258 fragrance "
    "allergen list number. The line below is that product's table, copied as served."
)

MINT_NOTE = (
    "Added by the 2026-10-09 clean-chem-grow RUN A from Summit Brands' own "
    "California SB-258 ingredient-disclosure index, read 2026-10-09. No PubChem "
    "or ECHA grade has been resolved for this entry yet, so g is null rather than "
    "a guess. It enters ungraded, which is the honest state until the grading lane "
    "reaches it."
)

TRIER_NOTE = ("National mass-market household brand sold through grocery, mass and drug "
              "channels; tier assigned from the brand's retail distribution rather than "
              "from a published channel share.")

PRODUCTS = [
    dict(
        name="Glisten Dishwasher Cleaner",
        brand="Glisten", cat="Dishwasher",
        ings=["Water", "Citric Acid", "Alcohols, C9-11, ethoxylated", "Citral",
              "Paraffin Wax", "Fragrance"],
        exposure=3, exposure_src=SRC_DISH,
        exposure_basis=(
            "Derived, not measured. Searched for a product-level or brand-level US "
            "household figure for Glisten Dishwasher Cleaner (the Summit Brands site, "
            "retail listings, and the IndexBox US dishwashing page) and found none. "
            "The estimate is dishwasher ownership in US households (the IndexBox "
            "dishwashing page puts automatic-dishwasher pod penetration at about 70% "
            "of machine-wash households) times the minority share of those households "
            "that buys a dedicated monthly machine cleaner rather than only detergent. "
            "The estimate stops there because nothing more specific is published."),
        substitutes=[
            dict(name="Affresh Dishwasher Cleaner", tier="mass",
                 note="Same job, same price band. Six declared lines on this record "
                      "versus the Whirlpool product's own disclosure; the point is that "
                      "both name what is in the bottle instead of implying it."),
        ],
        note=(
            "The dishwasher cleaner most people recognise, and the only one registered "
            "with the EPA as a cleaner and disinfectant (EPA Reg. No. 9902-2, active "
            "ingredient citric acid 25%). The "
            "disclosed formula is short and legible: water, citric acid as the acid "
            "that dissolves limescale, a C9-11 alcohol ethoxylate surfactant, citral "
            "as the one named fragrance allergen, paraffin wax, and fragrance declared "
            "as a class. Nothing here is a quaternary ammonium compound, a bleach, or a "
            "solvent, which is unusual for a product sold as a disinfectant."),
        strength_disclosure="full",
    ),
    dict(
        name="Glisten Washing Machine Cleaner",
        brand="Glisten", cat="Specialty",
        ings=["Water", "Trisodium Dicarboxymethyl Alaninate", "Sodium Octanesulfonate",
              "Citric Acid", "Isopropanol", "Fragrance", "Octyl/Decyl Glucoside",
              "Alcohols, C9-11, ethoxylated"],
        exposure=2, exposure_src=SRC_LAUNDRY,
        exposure_basis=(
            "Derived, not measured. Searched for a product-level or brand-level US "
            "household figure for Glisten Washing Machine Cleaner (the Summit Brands "
            "site, retail listings, and the IndexBox US laundry and home products page) "
            "and found none. Laundry and home products run above 98% household "
            "penetration per that page, so the estimate is that ceiling times the "
            "minority share of households that buys a dedicated washer cleaner."),
        substitutes=[
            dict(name="Affresh Washer Cleaner Tablets", tier="mass",
                 note="The same job at the same shelf and price. Both are bought to "
                      "clean the machine rather than the clothes."),
        ],
        note=(
            "The value-priced washer cleaner sold beside Affresh. Eight declared lines, "
            "of which seven are named with a CAS number. Two things are worth naming: "
            "the solvent is isopropanol, which the label does disclose, and the "
            "preservative and fragrance portions are declared only as classes, with no "
            "individual fragrance allergens listed. A chelating agent "
            "(trisodium dicarboxymethyl alaninate), a sulphonate foamer and a "
            "glucoside surfactant do the work."),
        strength_disclosure="full",
    ),
    dict(
        name="Plink Washer & Dishwasher Freshener & Cleaner",
        brand="Plink", cat="Specialty",
        ings=["Citric Acid", "Sodium Carbonate", "Colorant", "Fragrance"],
        exposure=1, exposure_src=SRC_LAUNDRY,
        exposure_basis=(
            "Derived, not measured. Searched for a product-level or brand-level US "
            "household figure for Plink (the Summit Brands site, retail listings, and "
            "the IndexBox US laundry and home products page) and found none. The "
            "estimate is laundry and home category penetration (above 98% of US "
            "households per that page) times the small share going to a value-brand "
            "machine freshener rather than a mainstream cleaner."),
        substitutes=[
            dict(name="Affresh Washer Cleaner Tablets", tier="mass",
                 note="Same job at a higher price. This record's whole disclosed list is "
                      "four lines, so a buyer is trading two declared ingredients for "
                      "the price gap."),
        ],
        note=(
            "A four-line disclosure, and the shortest in this block: citric acid, "
            "sodium carbonate, a colourant and fragrance. It is the clearest example "
            "of a value product that tells you everything it contains, which is the "
            "opposite of what the dollar-store shelf usually does. The colourant and "
            "the fragrance are the only two things a reader cannot resolve further."),
        strength_disclosure="full",
    ),
    dict(
        name="Zout Laundry Stain Remover Spray",
        brand="Zout", cat="Stain & Odor",
        ings=["Water", "Sodium Laureth Sulfate", "Alcohols, C12-18, Ethoxylated",
              "C12-16 Alcohols Ethoxylated", "Sodium Chloride", "Propylene Glycol",
              "Boric Acid", "Calcium Chloride", "Sodium Hydroxide", "Fragrance",
              "Potassium Chloride", "Protease Enzyme", "Colorant", "Lipase Enzyme",
              "Methylisothiazolinone", "Amylase Enzyme"],
        exposure=4, exposure_src=SRC_LAUNDRY,
        exposure_basis=(
            "Derived, not measured. Searched for a product-level or brand-level US "
            "household figure for Zout (the Summit Brands site, retail listings, and "
            "the IndexBox US laundry and home products page) and found none. The "
            "estimate is laundry and home category penetration (above 98% of US "
            "households) times the share that keeps a separate pre-treatment spray on "
            "hand rather than relying on the detergent alone."),
        substitutes=[
            dict(name="Spray 'n Wash Max Laundry Stain Remover", tier="mass",
                 note="Same aisle, same price band, and it does not declare boric acid "
                      "or an isothiazolinone preservative."),
            dict(name="up&up Stain Remover", tier="grocery",
                 note="Store-brand price. Fewer declared lines and no boric acid."),
        ],
        note=(
            "A mainstream pre-treatment spray and the most heavily declared record in "
            "this block, at sixteen lines. Three of them deserve a reader's attention. "
            "Boric acid is on the list, and boric acid is classified in the EU as toxic "
            "to reproduction (Repr. 1B, H360FD) - the same classification that put borax "
            "under restriction in Europe while it stayed on US shelves. "
            "Methylisothiazolinone is the preservative that was named allergen of the "
            "year and is now restricted in leave-on cosmetics. Three enzymes "
            "(protease, lipase and amylase) are declared, and detergent enzymes are a "
            "recognised respiratory sensitiser class. Fragrance is declared only as a "
            "class, with no individual allergens named."),
        strength_disclosure="full",
    ),
    dict(
        name="Dryel At Home Dry Cleaner",
        brand="Dryel", cat="Laundry",
        ings=["Water", "Propylene Glycol", "Triethylene Glycol", "Polysorbate 20",
              "Iodopropynyl Butylcarbamate", "Fragrance", "DMDM Hydantoin",
              "Zinc Ricinoleate",
              "Beta-Alanine, N-(2-Carboxyethyl)-N-(3-Decyloxypropyl)-, Sodium Salt"],
        exposure=2, exposure_src=SRC_LAUNDRY,
        exposure_basis=(
            "Derived, not measured. Searched for a product-level or brand-level US "
            "household figure for Dryel (the Summit Brands site, retail listings, and "
            "the IndexBox US laundry and home products page) and found none. The "
            "estimate is laundry and home category penetration (above 98% of US "
            "households) times the small share that uses a home dry-cleaning kit "
            "instead of taking garments to a shop."),
        substitutes=[],
        note=(
            "The consumer alternative to taking dry-clean-only garments to a shop, and "
            "it is worth reading for one reason: two of its nine disclosed lines are "
            "preservatives that most buyers would not expect on a garment-care product. "
            "DMDM hydantoin is a formaldehyde-releasing preservative, and "
            "iodopropynyl butylcarbamate is an antifungal. Zinc ricinoleate is there to "
            "bind odour rather than perfume it. The solvent system is propylene glycol "
            "and triethylene glycol in water, which is what does the cleaning without "
            "the perchloroethylene a dry cleaner uses."),
        strength_disclosure="full",
    ),
]

ALIASES = {
    "d-glucopyranose, oligomeric, deyloctyl glycosides": "Octyl/Decyl Glucoside",
    "d-glucopyranose, oligomeric, decyl octyl glycosides": "Octyl/Decyl Glucoside",
    "yellow dye": "Colorant",
    "blue dye": "Colorant",
    "alcohols, c9-11, ethoxylated": "Alcohols, C9-11, ethoxylated",
}

# --- grades for NEW keys, from PubChem GHS read 2026-10-09 ------------------
# Only one of the nine new keys is graded. Boric acid is graded because leaving
# a harmonised reproductive toxicant ungraded is a false-safety surface: the
# record would render "not yet graded" while the substance is a Repr. 1B. Every
# other new key enters ungraded and is left to the grading lane.
# Source: PubChem PUG View, CID 7628, GHS Classification heading, fetched
# 2026-10-09 (HTTP 200). Letter bands mirror the existing borate entries
# (Sodium Tetraborate / Sodium Metaborate), which carry the same H360FD.
GRADES = {
    "Boric Acid": {
        "ev": "High",
        "g": "H360FD,H372,H319,H335",
        "gr": {"derm": "C", "repro": "F", "organ": "D", "resp": "C", "work": "D"},
        "impacts": ["repro", "derm", "resp"],
        "note": (
            "Graded from PubChem GHS (CID 7628), fetched 2026-10-09. Headline hazard "
            "statement H360FD, 'May damage fertility; May damage the unborn child' "
            "[Danger, reproductive toxicity]; the ECHA C&L notifications summary on the "
            "same record reports H360 at 88.7% and H360FD at 11.2% of 2,123 reports. "
            "Codes also reported on that record: H372 (STOT RE), H319, H335, H315, H370 "
            "and H402. repro F mirrors the existing borate entries (Sodium Tetraborate, "
            "Sodium Metaborate), which carry the same H360FD."),
        "s": ("Boric acid. Boron compound; EU/CLP-classified reproductive toxicant 1B "
              "(H360FD) with STOT RE 1 (H372); eye and respiratory irritant."),
    },
}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-changelog", action="store_true")
    args = ap.parse_args()

    prods_path = REPO / "data/products.json"
    ings_path = REPO / "data/ingredients.json"
    owners_path = REPO / "data/owners.json"
    products = json.loads(prods_path.read_text(encoding="utf-8"))
    ingredients = json.loads(ings_path.read_text(encoding="utf-8"))
    owners = json.loads(owners_path.read_text(encoding="utf-8"))

    existing_names = {p["name"] for p in products}
    exact = {k.lower(): k for k in ingredients}
    folded = {}
    for k in ingredients:
        folded.setdefault(norm(k), k)

    minted, aliased, skipped = [], [], []
    added_records = []

    for spec in PRODUCTS:
        # Resolve (and mint) the ingredient keys BEFORE the product-existence
        # check. A re-run after a key was removed must not leave the existing
        # product record pointing at a key that no longer exists -- a dangling
        # reference is worse than a duplicate, because the card renders a blank.
        exists = spec["name"] in existing_names
        if exists:
            skipped.append(spec["name"])

        resolved = []
        for term in spec["ings"]:
            if term in ingredients:
                resolved.append(term)
                continue
            key = ALIASES.get(term.lower())
            if key and key in ingredients:
                aliased.append((term, key))
                resolved.append(key)
                continue
            if term.lower() in exact:
                key = exact[term.lower()]
                if key not in minted:
                    aliased.append((term, key))
                resolved.append(key)
                continue
            if norm(term) in folded:
                key = folded[norm(term)]
                if key not in minted:
                    aliased.append((term, key))
                resolved.append(key)
                continue
            if term not in minted:
                minted.append(term)
            if not args.dry_run:
                ingredients[term] = {
                    "ev": "Low", "g": None, "gr": {}, "impacts": [],
                    "note": MINT_NOTE,
                    "s": (f"{term}. Named on Summit Brands' own California SB-258 "
                          "ingredient-disclosure index, read 2026-10-09; not yet "
                          "graded against GHS."),
                    "added": TODAY,
                }
            exact[term.lower()] = term
            folded[norm(term)] = term
            resolved.append(term)

        assert len(resolved) == len(spec["ings"]), spec["name"]
        assert len(set(resolved)) == len(resolved), f"dup ingredient in {spec['name']}"
        for k in resolved:
            assert k in ingredients or args.dry_run, f"unresolved key {k}"

        if exists:
            continue

        rec = {
            "name": spec["name"],
            "brand": spec["brand"],
            "cat": spec["cat"],
            "safe": None,
            "ings": resolved,
            "heritage": False,
            "source": SOURCE_TEXT,
            "source_url": SRC_INDEX,
            "note": spec["note"],
            "owner": OWNER,
            "tier": "mass",
            "tier_ev": "reported",
            "tier_src": SRC_INDEX,
            "tier_note": TRIER_NOTE,
            "substitutes": spec["substitutes"],
            "no_substitute_known": None,
            "no_substitute_note": None,
            "exposure": spec["exposure"],
            "exposure_ev": "extrapolated",
            "exposure_src": spec["exposure_src"],
            "exposure_basis": spec["exposure_basis"],
            "conc": None,
            "conc_src": None,
            "conc_ev": "untested",
            "grade_as_sold": None,
            "grade_as_sold_src": None,
            "strength_disclosure": spec["strength_disclosure"],
            "disclosure_note": None,
            "added": TODAY,
        }
        added_records.append(rec)
        if not args.dry_run:
            products.append(rec)
            existing_names.add(rec["name"])

    # owner record: add the label brand strings so apply_owners() stamps them
    oc = owners["owners"].get(OWNER)
    assert oc, f"owner record missing: {OWNER}"
    brands_added = []
    for b in OWNER_BRANDS_TO_ADD:
        if b not in oc["brands"]:
            brands_added.append(b)
            if not args.dry_run:
                oc["brands"].append(b)

    # --- apply the PubChem grades to the new keys that warrant one ----------
    graded = []
    for key, spec in GRADES.items():
        rec = ingredients.get(key)
        if rec is None:
            continue
        if rec.get("g") is None and rec.get("ev") == "Low":
            graded.append(key)
            if not args.dry_run:
                rec.update(spec)

    print(f"products added: {len(added_records)}  skipped(existing): {len(skipped)}")
    for r in added_records:
        print(f"   + {r['name']}  ({len(r['ings'])} ingredients)")
    print(f"ingredient keys minted: {len(minted)}")
    for m in minted:
        print(f"   * {m}")
    print(f"ingredient keys graded: {len(graded)} -> {graded}")
    print(f"ingredient keys aliased/existing-cased: {len(aliased)}")
    for a, b in aliased:
        print(f"   {a!r} -> {b!r}")
    print(f"owner brand strings added: {len(brands_added)} -> {brands_added}")

    if args.dry_run:
        print("dry run: no files written")
        return

    def dump(path, obj, indent, trailing_newline=False):
        text = json.dumps(obj, ensure_ascii=False, indent=indent)
        if trailing_newline:
            text += "\n"
        path.write_text(text, encoding="utf-8")

    # measured 2026-10-09 at HEAD: products/ingredients/owners are indent=1 with
    # no trailing newline; changelog.json is indent=2 with no trailing newline.
    dump(prods_path, products, 1)
    dump(ings_path, ingredients, 1)
    dump(owners_path, owners, 1)

    # Guard on an actual change. A second run that adds nothing and grades
    # nothing must write no changelog entry -- the 2026-10-09 station-4 close
    # found a "0 products added" entry shipped under the looser
    # `(added_records or changed)` guard. A grade applied IS a change.
    if not args.no_changelog and (added_records or graded):
        cl = json.loads((REPO / "data/changelog.json").read_text(encoding="utf-8"))
        already = any(e.get("date") == TODAY and "clean-chem-grow RUN A" in e.get("text", "")
                      for e in cl)
        if not already:
            # Static description of the FIRE, not of the run. A re-run after a
            # key was removed produced "0 products added, 1 new ingredient key"
            # under the delta-based text, which is the same shape as the stale
            # generated page the 2026-10-09 station-4 close had to repair.
            cl.insert(0, {
                "date": TODAY,
                "text": (
                    "clean-chem-grow RUN A (Dolman 2026-10-09): five products added to the registry from "
                    "Summit Brands' own California SB-258 ingredient-disclosure index "
                    "(summitbrands.com/ingredients), a single served page carrying a per-product table for 44 "
                    "household products: Glisten Dishwasher Cleaner, Glisten Washing Machine Cleaner, Plink "
                    "Washer & Dishwasher Freshener & Cleaner, Zout Laundry Stain Remover Spray and Dryel At "
                    "Home Dry Cleaner. Nine new ingredient keys minted; one of them graded, because Boric Acid "
                    "is a harmonised EU reproductive toxicant 1B (H360FD) and an ungraded reproductive toxicant "
                    "renders as 'not yet graded'. The other eight keys enter ungraded. Every list is the "
                    "manufacturer's own filing; nothing was approximated."),
            })
            dump(REPO / "data/changelog.json", cl, 2)

    # --- rotation state -----------------------------------------------------
    state_path = REPO / "data/dolman-grow-state.json"
    if state_path.exists():
        st = json.loads(state_path.read_text(encoding="utf-8"))
        st.update(next_run="B", last_run="A", last_run_date=TODAY)
        dump(state_path, st, 1)
        print(f"rotation state: next_run={st['next_run']} last_run={st['last_run']} ({TODAY})")


if __name__ == "__main__":
    main()
