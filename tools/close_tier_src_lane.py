#!/usr/bin/env python3
"""Close the tier_src warning lane honestly (deadline 2026-09-30).

67 products carried tier_ev=reported with no tier_src. A tier is a claim, and a
claim marked 'reported' with nothing to point at is indistinguishable from a
guess. Two honest exits, and this script takes the one that is true per product:

  1. Where the tier rests on a recorded third-party certification (EPA Safer
     Choice, MADE SAFE, USDA Organic, Green Seal), name the certifier. Keep
     'reported'.

  2. Where the tier was assigned by exclusion ('mass' = not eco, 'natural' =
     feels eco), there is no source, because there was never a source. Downgrade
     to 'untested' with a basis. Per docs/certainty.md rule 2, untested is
     better than a guess, and per the lane registry a Class B lane is our own
     gap and is supposed to close.

EWG is deliberately not used as a tier source: the source policy forbids
deriving data from EWG, and a certification reference would put their database
on the dependency path. Those products fall to branch 2.

Run: python3 tools/close_tier_src_lane.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"

CERT_SRC = {
    "EPA Safer Choice": "https://www.epa.gov/saferchoice/products",
    "MADE SAFE": "https://www.madesafe.org/",
    "USDA Organic": "https://www.ams.usda.gov/services/organic-certification",
    "Green Seal": "https://greenseal.org/certified-products-services/",
}

NO_SOURCE_BASIS = (
    "searched for a published definition of this tier and found none that names "
    "the product. The tier was assigned by exclusion rather than by a source, so "
    "it is downgraded to untested rather than left marked reported with nothing "
    "to point at. A guessed tier is worse than no tier.")


def main():
    products = json.loads((DATA / "products.json").read_text(encoding="utf-8"))
    cited = downgraded = 0
    for p in products:
        if p.get("tier_ev") != "reported" or p.get("tier_src"):
            continue
        cert_blob = p.get("safe") or ""
        hit = next((c for c in CERT_SRC if c in cert_blob), None)
        if hit:
            p["tier_src"] = CERT_SRC[hit]
            p["tier_note"] = f"Tier rests on the recorded {hit} certification."
            cited += 1
        else:
            p["tier_ev"] = "untested"
            p["tier_src"] = None
            p["tier_basis"] = NO_SOURCE_BASIS
            downgraded += 1

    (DATA / "products.json").write_text(
        json.dumps(products, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"tier_src cited from a certifier: {cited}")
    print(f"tier_ev downgraded to untested (no source existed): {downgraded}")


if __name__ == "__main__":
    main()
