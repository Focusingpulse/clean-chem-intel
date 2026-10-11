#!/usr/bin/env python3
"""Station 4 close, 2026-10-11.

Applies Linnea's two REQUIRED text-only revisions from
verdicts/SPX-spectrum-station2-verdict-2026-10-11.md.

R1 (required): the Arm & Hammer Plus OxiClean 4-in-1 Power Paks record states
    "18 fragrance components" in its `source` text (and "18 fragrance keys" in its
    `note`). The served Church & Dwight disclosure form lists 16 (verified by
    table-row parse). Correct 18 -> 16 in both fields.

R2 (required) is text-only on the FINDING in three-agent-intelligence
(findings/SPX-spectrum-station2-2026-10-11.md, claim 23) and is handled there,
not here.

R4 (recommended, applied): align two substitute names with the corpus record
    names -- "Gel Hand Soap" -> "Branch Basics Gel Hand Soap" (Dove record) and
    "Simple Green All-Purpose Cleaner" -> "Simple Green" (Spray Nine record).
    No grade, evidence level, mapping, ownership or exposure value changes.

No product grade, ingredient grade, evidence level, mapping, ownership or
exposure value is touched. Idempotent: re-running after a successful run is a
no-op. `--dry-run` guards EVERY write.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PRODUCTS = REPO / "data" / "products.json"

DRY = "--dry-run" in sys.argv

# R1: the wrong count, in the two fields of the one record that carries it.
R1_RECORD = "Arm & Hammer Plus OxiClean 4-in-1 Power Paks"
R1_PAIRS = [
    ("additionally discloses 18 fragrance components", "additionally discloses 16 fragrance components"),
    ("rather than minting 18 fragrance keys", "rather than minting 16 fragrance keys"),
]

# R4: substitute-name alignment. Substitute entries are dicts {name, tier, note}.
R4 = {
    "Dove Foaming Hand Wash, Aloe & Eucalyptus": [("Gel Hand Soap", "Branch Basics Gel Hand Soap")],
    "Spray Nine Heavy-Duty Cleaner, Degreaser & Disinfectant": [("Simple Green All-Purpose Cleaner", "Simple Green")],
}


def main() -> int:
    raw = PRODUCTS.read_text(encoding="utf-8")
    trailing_nl = raw.endswith("\n")
    products = json.loads(raw)

    changed = 0

    for p in products:
        if p.get("name") == R1_RECORD:
            for field in ("source", "note"):
                text = p.get(field)
                if not isinstance(text, str):
                    continue
                for old, new in R1_PAIRS:
                    if old in text and old != new:
                        text = text.replace(old, new)
                        changed += 1
                p[field] = text

        subs = p.get("substitutes")
        if isinstance(subs, list):
            for s in subs:
                if not isinstance(s, dict):
                    continue
                nm = s.get("name")
                if not isinstance(nm, str):
                    continue
                for old, new in R4.get(p.get("name"), []):
                    if nm == old:  # exact match: the new name contains the old one
                        s["name"] = new
                        changed += 1
                        break

    if changed == 0:
        print("repair_2026_10_11: nothing to do (already applied)")
        return 0

    out = json.dumps(products, ensure_ascii=False, indent=1)
    if trailing_nl:
        out += "\n"

    if DRY:
        print(f"repair_2026_10_11: DRY RUN — would apply {changed} text change(s); no file written")
        return 0

    PRODUCTS.write_text(out, encoding="utf-8")
    print(f"repair_2026_10_11: applied {changed} text change(s) to {PRODUCTS.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
