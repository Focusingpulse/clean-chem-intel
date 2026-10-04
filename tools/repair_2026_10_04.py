#!/usr/bin/env python3
"""Repair 2026-10-04: station-4 close, acting on Linnea's 2026-10-04 verdicts.

PART 1 -- dedupe merge (flag F1 of clean-chem-delta-runC-sifter-verdict).

Same substance -- 2-butoxyethanol, CAS 111-76-2 (PubChem CID 8133) -- under two
ingredient keys:

  Butyloxyethanol  ev High, graded (corrected 2026-10-03 by the Sifter lane
                   against PubChem CID 8133) -- read by ONE product
                   (Windex Original).
  Butoxyethanol    ev Low, g null (minted 2026-09-29 from a KIK SB-258
                   manufacturer filing) -- read by FOUR value-brand products
                   (Greased Lightning All Purpose Cleaner, Top Job Basic
                   Multi-Purpose Cleaner & Degreaser, Comet Classic Window
                   Cleaner, Greased Lightning Classic Cleaner & Degreaser).

The corrected grade sat on the key only one product reads, so the four products
that actually disclose the chemical rendered "not yet graded" -- a false-safety
surface. Linnea's suggested canonical key is Butyloxyethanol (the graded one,
with the verified note and the PubChem citation). This script repoints the four
readers onto it and drops the ungraded twin. Both records' facts are preserved
on the survivor. No grade, no evidence level, and no product grade is changed.

PART 2 -- finding-text correction, applied to the data (R1 of
SPX-spectrum-station2-verdict-2026-10-04).

The note on Top Job Bathroom Cleaner with Bleach said its five lines are "the
same five lines as ... Comet Classic Foaming Bath Cleaner ... Four products,
three brands, two price points, one formula." Comet Classic Foaming Bath
Cleaner discloses FOUR lines (Water, Sodium Hypochlorite, Sodium Hydroxide,
Lauramine Oxide) with no fragrance. The four chemistry lines are shared; three
of the four products add a fragrance line. Text-only; no ingredient list
changes.

Also corrects three harvest scripts at source (09-29, 10-03, 10-04) so a re-run
cannot re-mint the removed key.

Idempotent: re-running after the repairs is a no-op.

Run: python3 tools/repair_2026_10_04.py
Then: python3 build.py && python3 tools/validate_certainty.py
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
DRY = "--dry-run" in sys.argv

CANON = "Butyloxyethanol"
VARIANT = "Butoxyethanol"

MERGE_NOTE = (
    " Merged 2026-10-04 (dedupe lane, flag F1 of Linnea's 2026-10-04 delta "
    "verdict): the same substance (2-butoxyethanol, CAS 111-76-2) sat under a "
    "second key, Butoxyethanol, minted ungraded 2026-09-29 from a KIK SB-258 "
    "manufacturer filing. Four value-brand products disclosed it under that "
    "spelling -- Greased Lightning All Purpose Cleaner, Top Job Basic "
    "Multi-Purpose Cleaner & Degreaser, Comet Classic Window Cleaner and "
    "Greased Lightning Classic Cleaner & Degreaser -- and now read this key, "
    "so the verified grade reaches them."
)

# R1: exact old/new note on the Top Job Bathroom record.
TOJOB_NAME = "Top Job Bathroom Cleaner with Bleach"
TOJOB_OLD_NOTE = (
    "Five lines, and they are the same five lines as The Works Basic Bathroom "
    "Cleaner with Bleach and Comet Classic Foaming Bath Cleaner already in this "
    "database. Water, bleach, the hydroxide that stabilises it, one surfactant "
    "and a fragrance. Four products, three brands, two price points, one "
    "formula. Dollar General sells this exact bottle for about a dollar, and "
    "the bottle beside it costs several times that for the same chemistry."
)
TOJOB_NEW_NOTE = (
    "Five lines: water, bleach, the hydroxide that stabilises it, one "
    "surfactant, and a fragrance. The four chemistry lines are the same four "
    "The Works Basic Bathroom Cleaner with Bleach and Comet Classic Foaming "
    "Bath Cleaner disclose -- four products, three brands, two price points, "
    "one four-line formula. The three Top Job / The Works bottles add a "
    "fragrance line; Comet Classic Foaming Bath Cleaner does not. Dollar "
    "General sells this exact bottle for about a dollar, and the bottle beside "
    "it costs several times that for the same chemistry."
)

# Harvest scripts that name the removed key; fixed at source so a re-run cannot
# re-mint it.
SCRIPT_FIXES = [
    REPO / "tools" / "harvest_2026_09_29.py",
    REPO / "tools" / "harvest_2026_10_03.py",
    REPO / "tools" / "harvest_2026_10_04.py",
]

CHANGELOG_TEXT = (
    "Station-4 close: merged the Butoxyethanol / Butyloxyethanol duplicate pair "
    "(same substance, CAS 111-76-2, two keys; Linnea flag F1 2026-10-04) onto "
    "the graded key so the corrected Sifter grade reaches the four value-brand "
    "products that disclose it; corrected the Top Job Bathroom Cleaner with "
    "Bleach note (Linnea R1: Comet Classic Foaming Bath Cleaner discloses four "
    "lines, no fragrance). No grade, evidence level or product grade changed."
)


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def dump(name, obj):
    (DATA / name).write_text(
        json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")


def main():
    products = load("products.json")
    ingredients = load("ingredients.json")
    changelog = load("changelog.json")

    changed = []

    # ---- PART 1: merge the duplicate pair ---------------------------------
    if VARIANT in ingredients:
        canon = ingredients[CANON]
        variant = ingredients[VARIANT]
        if MERGE_NOTE.strip() not in canon.get("note", ""):
            canon["note"] = canon.get("note", "").rstrip() + MERGE_NOTE
        del ingredients[VARIANT]
        changed.append(f"ingredients: removed '{VARIANT}', merged into '{CANON}' "
                       f"(was ev={variant.get('ev')}, g={variant.get('g')})")
    else:
        changed.append(f"ingredients: '{VARIANT}' already absent (no-op)")

    repointed = 0
    for p in products:
        ings = p.get("ings") or []
        if VARIANT in ings:
            p["ings"] = [CANON if i == VARIANT else i for i in ings]
            repointed += 1
    changed.append(f"products: repointed {repointed} record(s) "
                   f"{VARIANT} -> {CANON}")

    # ---- PART 2: R1 note correction ---------------------------------------
    tojob = [p for p in products if p.get("name") == TOJOB_NAME]
    if len(tojob) != 1:
        raise SystemExit(f"expected exactly 1 '{TOJOB_NAME}', found {len(tojob)}")
    if tojob[0].get("note") == TOJOB_OLD_NOTE:
        tojob[0]["note"] = TOJOB_NEW_NOTE
        changed.append(f"products: corrected the note on '{TOJOB_NAME}' (R1)")
    elif tojob[0].get("note") == TOJOB_NEW_NOTE:
        changed.append(f"products: '{TOJOB_NAME}' note already corrected (no-op)")
    else:
        raise SystemExit(
            f"'{TOJOB_NAME}' note does not match the expected pre- or "
            f"post-repair text; refusing to overwrite. Actual:\n"
            f"{tojob[0].get('note')!r}")

    # ---- source-script fixes ---------------------------------------------
    script_edits = 0
    for path in SCRIPT_FIXES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if f'"{VARIANT}"' in text:
            if not DRY:
                path.write_text(text.replace(f'"{VARIANT}"', f'"{CANON}"'),
                                encoding="utf-8")
            script_edits += 1
    changed.append(f"tools: corrected {script_edits} harvest script(s) at source")

    # ---- changelog --------------------------------------------------------
    if not changelog or changelog[0].get("text") != CHANGELOG_TEXT:
        if not any(c.get("text") == CHANGELOG_TEXT for c in changelog):
            changelog.insert(0, {"date": "2026-10-04", "text": CHANGELOG_TEXT})
            changed.append("changelog: entry added")
    else:
        changed.append("changelog: entry already present (no-op)")

    for line in changed:
        print(("DRY " if DRY else "") + line)

    if DRY:
        return

    dump("products.json", products)
    dump("ingredients.json", ingredients)
    (DATA / "changelog.json").write_text(
        json.dumps(changelog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
