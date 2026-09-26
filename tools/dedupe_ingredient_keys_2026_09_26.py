#!/usr/bin/env python3
"""Close the `case_duplicate_grades` Class B lane (deadline 2026-09-30).

Lane: the same chemical sits under two keys differing only by case, with
different `gr` blocks. The lane's own words: "products reference whichever the
ingest lane wrote, so the answer changes by spelling."

What this does: removes the UNREFERENCED member of each case-insensitive
duplicate group. It changes no grade, because the removed record is referenced by
no product (verified before removal, and asserted here). The referenced member --
the curated, sourced record -- is untouched.

Origin of the duplicates: `bulk_ingest.py` keys new ingredient records by
`name.lower()` while the curated records are stored capitalised, so a chemical
already present as "Isopropanol" was re-added as "isopropanol". That is an
ingest-side cause, filed separately; this script closes the lane in the data.

Run: python3 tools/dedupe_ingredient_keys_2026_09_26.py
Then: python3 tools/validate_certainty.py --apply && python3 build.py
"""
import json
import collections
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"


def main():
    products = json.loads((DATA / "products.json").read_text())
    ings = json.loads((DATA / "ingredients.json").read_text())

    ref = collections.Counter()
    for p in products:
        for i in (p.get("ings") or []):
            ref[i] += 1

    ref_names = set(ref)
    missing = ref_names - set(ings)
    assert not missing, f"products reference ingredients not in DB: {sorted(missing)[:5]}"

    by_lower = {}
    for n in ings:
        by_lower.setdefault(n.strip().lower(), []).append(n)

    removed, kept = [], []
    for k, names in sorted(by_lower.items()):
        if len(names) < 2:
            continue
        referenced = [n for n in names if ref.get(n, 0) > 0]
        orphan = [n for n in names if ref.get(n, 0) == 0]
        assert len(referenced) == 1, (
            f"group {k!r}: expected exactly one referenced key, got {referenced} "
            f"(refs {[(n, ref.get(n,0)) for n in names]})")
        assert orphan, f"group {k!r}: no unreferenced duplicate to remove"
        for n in orphan:
            del ings[n]
            removed.append((k, n, ings and len(ings)))
        kept.append(referenced[0])

    (DATA / "ingredients.json").write_text(
        json.dumps(ings, indent=1, ensure_ascii=False))
    print(f"case_duplicate_grades: removed {len(removed)} unreferenced duplicate key(s)")
    for k, n, _ in removed:
        print(f"  - {n!r} ({k})")
    print(f"kept: {len(kept)} referenced key(s); ingredients now {len(ings)}")


if __name__ == "__main__":
    main()
