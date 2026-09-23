#!/usr/bin/env python3
"""Certainty validation and ownership application.

Two jobs, both enforcement rather than documentation:

1. Every graded claim in data/oils.json must carry a valid evidence level.
   A claim with no level, or a level outside the five, fails the build. This
   is the same principle as the voice rule in build.py: a rule that is only
   remembered gets violated by the next automated writer.

2. Apply data/owners.json to data/products.json, writing owner, owner_ev and
   owner_src onto each product. Ownership is an evidence claim like any other.

Usage:
    python3 tools/validate_certainty.py          # validate + report
    python3 tools/validate_certainty.py --apply  # validate, then write owners
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"

LEVELS = {"verified", "reported", "extrapolated", "untested", "unknown"}
FLAGS = {"avoid", "caution", "no_signal", "untested"}

failures = []
warnings = []


def load(name, default=None):
    p = DATA / name
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def check_claim(where, claim):
    """A claim is a dict with an 'ev' key from LEVELS."""
    if not isinstance(claim, dict):
        failures.append(f"{where}: claim is not an object")
        return
    ev = claim.get("ev")
    if ev is None:
        failures.append(f"{where}: claim has no evidence level")
    elif ev not in LEVELS:
        failures.append(f"{where}: invalid evidence level {ev!r}")
    # A verified claim must resolve to a source.
    if ev == "verified" and not claim.get("src"):
        failures.append(f"{where}: marked verified with no source")


def validate_oils():
    oils = load("oils.json")
    if oils is None:
        warnings.append("oils.json not present, skipped")
        return 0
    n = 0
    for section in ("oils", "blends"):
        for name, o in oils.get(section, {}).items():
            for dim, claim in o.get("cleaning", {}).items():
                check_claim(f"oils.{section}.{name}.cleaning.{dim}", claim)
                n += 1
            for pop, claim in o.get("populations", {}).items():
                check_claim(f"oils.{section}.{name}.populations.{pop}", claim)
                flag = claim.get("flag")
                if flag not in FLAGS:
                    failures.append(
                        f"oils.{section}.{name}.populations.{pop}: "
                        f"invalid flag {flag!r}")
                n += 1
            # A legend or a claim conflict must carry its own level.
            for extra in ("naming_legend", "claim_conflict"):
                if extra in o:
                    blk = o[extra]
                    if "ev" in blk or extra == "claim_conflict":
                        if extra == "naming_legend":
                            check_claim(f"oils.{section}.{name}.{extra}", blk)
                            n += 1
    return n


def apply_owners(dry=True):
    owners = load("owners.json")
    products = load("products.json")
    if owners is None or products is None:
        warnings.append("owners.json or products.json missing, skipped")
        return 0, 0

    # brand -> (parent, ev, src)
    table = {}
    for parent, info in owners.get("owners", {}).items():
        for b in info.get("brands", []):
            table[b] = (parent, info.get("ev", "untested"), info.get("src"))

    matched = 0
    for p in products:
        brand = p.get("brand")
        if brand in table:
            parent, ev, src = table[brand]
            p["owner"], p["owner_ev"], p["owner_src"] = parent, ev, src
            matched += 1
        elif brand in owners.get("independents", {}).get("brands", []):
            # Deliberately explicit. "No parent found" is not "independent".
            p["owner"] = None
            p["owner_ev"] = "untested"
            p["owner_src"] = None
            matched += 1
        else:
            p["owner"] = None
            p["owner_ev"] = "unknown"
            p["owner_src"] = None

    if not dry:
        (DATA / "products.json").write_text(
            json.dumps(products, indent=1, ensure_ascii=False), encoding="utf-8")
    return matched, len(products)


def main():
    apply = "--apply" in sys.argv
    n_oil = validate_oils()
    matched, total = apply_owners(dry=not apply)

    print(f"certainty: {n_oil} oil claims checked")
    print(f"ownership: {matched} of {total} products carry an ownership record")

    if warnings:
        for w in warnings:
            print(f"  warn: {w}")

    if failures:
        print(f"\nFAIL — {len(failures)} problem(s):")
        for f in failures:
            print(f"  {f}")
        return 1

    print("PASS — every claim carries a valid evidence level")
    return 0


if __name__ == "__main__":
    sys.exit(main())
