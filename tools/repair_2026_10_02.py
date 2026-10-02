#!/usr/bin/env python3
"""RUN C data-quality repair, 2026-10-02: merge a case-variant ingredient key.

Defect: the same chemical sat under two keys differing only by case, both
referenced by products, with identical substance identity (PubChem CID 7714,
CAS 104-67-6) and identical grade ("Not Classified"):

    Gamma-Undecalactone   <- 3 products (Arm & Hammer liquid laundry detergent,
                             Glade PlugIns Hawaiian Breeze, Great Value Ultimate
                             Fresh laundry detergent)
    gamma-Undecalactone   <- 1 product  (Air Wick Scented Oil, Ocean Spray)

Origin: `tools/gather_2026_09_30.py` minted the lowercase key while the curated
record already existed capitalised -- the same ingest-side cause the
2026-09-26 `case_duplicate_grades` lane closed. That lane's tool
(`dedupe_ingredient_keys_2026_09_26.py`) only removes the UNREFERENCED member of
a group and asserts exactly one referenced key, so it could not see this pair:
both members were referenced. This script handles that shape by repointing the
minority readers onto the canonical key, and the assertion in `chem_maintain.py`
added the same day means it cannot recur unnoticed.

What it changes: ONE ingredient record removed, ONE product's `ings` repointed.
No grade, no evidence level, and no product grade is touched. Both records'
facts are preserved on the surviving record.

Idempotent: re-running after the merge is a no-op.

Run: python3 tools/repair_2026_10_02.py
Then: python3 chem_maintain.py && python3 build.py && python3 update_counts.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"

CANON = "Gamma-Undecalactone"
VARIANT = "gamma-Undecalactone"

MERGED_S = (
    "Lactone fragrance (peach). No GHS hazard criteria met "
    "(majority not-classified per ECHA C&L via PubChem)."
)
MERGED_NOTE = (
    "PubChem CID 7714 (returned title 'Gamma-undecalactone', matches; CAS 104-67-6). "
    "H411 (10.3%) and H412 (19.3%) are both below the 40% house bar and H401 appears "
    "without a notifier percentage, so no grade is justified. Disclosed as a fragrance "
    "component by Church & Dwight (Arm & Hammer liquid laundry detergent) and by the "
    "Reckitt SmartLabel for Air Wick Scented Oil, Ocean Spray."
)


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def dump(name, obj):
    (DATA / name).write_text(
        json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")


def main():
    products = load("products.json")
    ings = load("ingredients.json")

    if VARIANT not in ings:
        print(f"no-op: {VARIANT!r} already absent")
    else:
        assert CANON in ings, f"canonical key {CANON!r} missing -- refusing to merge"

        readers = [p["name"] for p in products if VARIANT in (p.get("ings") or [])]
        assert readers, f"{VARIANT!r} is present but referenced by no product"

        kept = ings[CANON]
        dropped = ings[VARIANT]

        # Same substance, same grade -- asserted, not assumed.
        assert kept.get("g") == dropped.get("g"), (
            f"grade differs: {kept.get('g')!r} vs {dropped.get('g')!r} -- "
            "this is not a spelling variant of one record, get a ruling")
        assert kept.get("ev") == dropped.get("ev"), (
            f"evidence level differs: {kept.get('ev')!r} vs {dropped.get('ev')!r}")

        # Preserve both records' facts on the survivor.
        merged = {
            "ev": kept["ev"],
            "g": kept["g"],
            "gr": kept.get("gr") or {},
            "impacts": kept.get("impacts") or [],
            "note": MERGED_NOTE,
            "s": MERGED_S,
        }
        ings[CANON] = merged
        del ings[VARIANT]

        for p in products:
            if VARIANT in (p.get("ings") or []):
                p["ings"] = [CANON if i == VARIANT else i for i in p["ings"]]

        print(f"merged {VARIANT!r} -> {CANON!r}; repointed {len(readers)} product(s):")
        for r in readers:
            print(f"  - {r}")

    # Invariant: no case-variant duplicate group may survive this script.
    by_lower = {}
    for name in ings:
        by_lower.setdefault(name.strip().lower(), []).append(name)
    groups = {k: v for k, v in by_lower.items() if len(v) > 1}
    assert not groups, f"case-variant duplicate keys remain: {groups}"

    # Invariant: every product ingredient must resolve.
    missing = sorted({i for p in products for i in (p.get("ings") or []) if i not in ings})
    assert not missing, f"products reference ingredients not in DB: {missing[:5]}"

    dump("ingredients.json", ings)
    dump("products.json", products)
    print(f"ok: {len(products)} products, {len(ings)} ingredients, no case-variant keys")


if __name__ == "__main__":
    main()
