#!/usr/bin/env python3
"""Apply Linnea's 2026-10-06 verdict R1-R3 to the Target up&up block.

Verdict: verdicts/SPX-spectrum-station2-verdict-2026-10-06.md (FAIL; R1-R3 required, R4 recommended).

R1 (required, data): the up&up Fresh Scent Disinfecting Wipes note said
    "four quaternary ammonium compounds and nothing else declared". The served filing
    (CLOUD_2ccd7122..., 2,145 bytes, 11 data rows) declares SEVEN withheld ingredients
    (name "Undisclosed Ingredient", CAS "Withheld", purpose "Pesticide Active") in
    addition to the four named quats. Correct the note; no ingredient-list change.

R2 (required, data): the up&up Multi-Purpose Cleaner, Free & Clear filing
    (CLOUD_18f92a5e..., reversed orientation) declares ONE withheld ingredient
    (purpose: Solvent). Its note said nothing about it. Record the withheld state.
    Consequence of the same revision: the Pine record's substitute note claimed the
    Free & Clear formula has "no declared withheld ingredient", which is now false —
    that clause is removed.

R3 (required, finding text only): handled in the finding file, not here.

Idempotent: re-running is a no-op after the first application.
"""
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
PRODUCTS = REPO / "data" / "products.json"
CHANGELOG = REPO / "data" / "changelog.json"

CHANGELOG_MARKER = "Station-4 close: recorded the withheld-ingredient state"
CHANGELOG_TEXT = (
    "Station-4 close: recorded the withheld-ingredient state in the Target up&up block "
    "(Linnea R1/R2 2026-10-06). The Fresh Scent Disinfecting Wipes filing declares seven "
    "withheld ingredients the first pass said were absent; six of the block's documents "
    "declare withheld rows (23 in all), and the Free & Clear note now records its one. The "
    "Pine substitute note's \"no declared withheld ingredient\" clause was removed because "
    "R2 made it false. No ingredient, grade, evidence level or ownership value changed."
)

WIPES = "up&up Fresh Scent Disinfecting Wipes"
FREE_CLEAR = "up&up Multi-Purpose Cleaner, Free & Clear"
PINE = "up&up Multi-Surface Cleaner, Pine"

WIPES_MARKER = "seven withheld ingredients"
FREE_CLEAR_MARKER = "declares one withheld ingredient (purpose: solvent)"
PINE_MARKER = "and no declared withheld ingredient"

WIPES_NOTE = (
    "The shortest and the sharpest list in this block: four named quaternary ammonium "
    "compounds, plus seven withheld ingredients the filing declares without naming, so the "
    "list is complete as filed but not complete as chemistry. No water, no surfactant, no "
    "fragrance component is listed as intentionally added, so what the filing describes is "
    "the active system on the wipe rather than the whole wet formula. Four different quats "
    "in one wipe is the reason this class shows up as a contact irritant and, in the "
    "environment, as a persistent aquatic toxicant. Keep them off food-contact surfaces you "
    "will not rinse."
)

FREE_CLEAR_NOTE = (
    "The one formula in this block with no quaternary ammonium active and no declared "
    "fragrance: two glucoside surfactants, a citric acid / sodium carbonate buffer, sodium "
    "gluconate as a chelator, and benzisothiazolinone as the preservative. It is the mildest "
    "list here and the one to reach for when the job is cleaning rather than disinfecting. "
    "Benzisothiazolinone is still a contact allergen, so it is not allergen-free, only "
    "fragrance-free. The filing declares one withheld ingredient (purpose: solvent), so the "
    "list is complete as filed but not complete as chemistry."
)

PINE_SUB_NOTE = (
    "Same store, same price band, and the only up&up multi-surface formula in this set "
    "with no quaternary ammonium active."
)


def main() -> int:
    products = json.loads(PRODUCTS.read_text(encoding="utf-8"))
    by_name = {p.get("name"): p for p in products}

    changed = 0

    p = by_name.get(WIPES)
    if p is None:
        print(f"ERROR: record not found: {WIPES}")
        return 1
    if WIPES_MARKER in (p.get("note") or ""):
        print(f"already applied: {WIPES}")
    else:
        p["note"] = WIPES_NOTE
        changed += 1
        print(f"R1 applied: {WIPES}")

    p = by_name.get(FREE_CLEAR)
    if p is None:
        print(f"ERROR: record not found: {FREE_CLEAR}")
        return 1
    if FREE_CLEAR_MARKER in (p.get("note") or ""):
        print(f"already applied: {FREE_CLEAR}")
    else:
        p["note"] = FREE_CLEAR_NOTE
        changed += 1
        print(f"R2 applied: {FREE_CLEAR}")

    # Consequence of R2: the Pine substitute note's "no declared withheld ingredient"
    # clause is false now. Remove the clause, keep the true part.
    p = by_name.get(PINE)
    if p is None:
        print(f"ERROR: record not found: {PINE}")
        return 1
    subs = p.get("substitutes") or []
    touched_pine = False
    for s in subs:
        if s.get("name") == FREE_CLEAR and PINE_MARKER in (s.get("note") or ""):
            s["note"] = PINE_SUB_NOTE
            touched_pine = True
            changed += 1
            print(f"R2 consequence applied: {PINE} substitute note")
    if not touched_pine:
        print(f"already applied: {PINE} substitute note")

    if changed:
        PRODUCTS.write_text(
            json.dumps(products, indent=1, ensure_ascii=False), encoding="utf-8"
        )
        print(f"wrote {PRODUCTS} ({changed} change(s))")
    else:
        print(f"no changes needed: {PRODUCTS}")

    # Changelog entry (indent=2, no trailing newline; newest first).
    log = json.loads(CHANGELOG.read_text(encoding="utf-8"))
    if any(CHANGELOG_MARKER in (e.get("text") or "") for e in log):
        print(f"already applied: {CHANGELOG}")
    else:
        log.insert(0, {"date": "2026-10-06", "text": CHANGELOG_TEXT})
        CHANGELOG.write_text(
            json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"wrote {CHANGELOG}")

    # Idempotence assertion
    check = {p.get("name"): p for p in json.loads(PRODUCTS.read_text(encoding="utf-8"))}
    assert WIPES_MARKER in (check[WIPES].get("note") or ""), "R1 not present after write"
    assert FREE_CLEAR_MARKER in (check[FREE_CLEAR].get("note") or ""), "R2 not present after write"
    for s in check[PINE].get("substitutes") or []:
        if s.get("name") == FREE_CLEAR:
            assert PINE_MARKER not in (s.get("note") or ""), "stale Pine clause remains"
    print("verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
