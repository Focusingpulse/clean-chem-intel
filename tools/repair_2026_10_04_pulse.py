#!/usr/bin/env python3
"""Repair 2026-10-04 research pulse (Dolman).

Two products added by the Sifter lane carry a COMPANY NAME in their `brand`
string, so `apply_owners()` finds no owner record and silently leaves them at
`owner: null, owner_ev: untested`. The validator reports "292 of 294 products
carry an ownership record".

  Affresh Washer Cleaner Tablets   brand "Whirlpool"      -> owner record absent
  Iron OUT Powder Rust & Stain     brand "Summit Brands"  -> owner record absent

Fix: (1) add the two missing owner records, both `verified` on the company's own
published brand material; (2) set the brand string to the LABEL brand, which is
the convention the rest of the corpus uses (brand = what is on the package,
owner = the company that owns it).

Sources read directly 2026-10-04:
  Whirlpool Corporation  https://www.whirlpoolcorp.com/   -- the corporate site
      carries the asset path "Our Brands_Affresh_logo.png", i.e. Affresh is
      listed among Whirlpool's own brands.
  Summit Brands          https://summitbrands.com/about/  -- the company's own
      brand menu lists Glisten, Iron OUT, Pumie, Dryel, Zout, OUT, Plink,
      EarthStone, Septobac, and the Iron OUT SDS is hosted on the same domain.

Idempotent: a second run changes nothing and says so.

Run: python3 tools/repair_2026_10_04_pulse.py [--dry-run]
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"

WHIRLPOOL = (
    "Whirlpool Corporation",
    {
        "type": "public company",
        "detail": (
            "Affresh is one of Whirlpool Corporation's own brands: the corporate "
            "site whirlpoolcorp.com serves the brand asset 'Our Brands_Affresh_logo.png' "
            "on its brands block, and affresh.com carries the Whirlpool logo and links "
            "to whirlpoolcorp.com legal notices. Whirlpool Corporation (NYSE: WHR) is the "
            "parent. The 'Whirlpool' string is also kept here so a product labelled with "
            "the corporate name still resolves."
        ),
        "ev": "verified",
        "src": "https://www.whirlpoolcorp.com/",
        "brands": ["Affresh", "Whirlpool"],
    },
)

SUMMIT = (
    "Summit Brands",
    {
        "type": "private, family-owned",
        "detail": (
            "Summit Brands' own site lists Iron OUT among its brand family (Glisten, "
            "Iron OUT, Pumie, Dryel, Zout, OUT, Plink, EarthStone, Septobac) and hosts the "
            "Iron OUT SDS on summitbrands.com. Family-owned and privately held since 1958, "
            "Fort Wayne, Indiana. The company publishes no legal suffix, so the record name "
            "is the name it uses. NOTE: Pumie is listed on this site too; the Pumie ownership "
            "flag on the U.S. Pumice Company record stays OPEN -- do not reassign it here."
        ),
        "ev": "verified",
        "src": "https://summitbrands.com/about/",
        "brands": ["Iron OUT"],
    },
)

# product name -> (company-name brand string currently held, label brand to set)
BRAND_FIXES = {
    "Affresh Washer Cleaner Tablets": ("Whirlpool", "Affresh"),
    "Iron OUT Powder Rust & Stain Remover": ("Summit Brands", "Iron OUT"),
}


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def dump(obj, name):
    raw = (DATA / name).read_text(encoding="utf-8")
    out = json.dumps(obj, indent=1, ensure_ascii=False)
    if raw.endswith("\n"):
        out += "\n"
    (DATA / name).write_text(out, encoding="utf-8")


def main():
    dry = "--dry-run" in sys.argv
    owners = load("owners.json")
    products = load("products.json")
    changes = []

    for name, rec in (WHIRLPOOL, SUMMIT):
        cur = owners["owners"].get(name)
        if cur == rec:
            continue
        if cur is not None:
            changes.append(f"owner record {name!r} present but differs; left as-is")
            continue
        owners["owners"][name] = rec
        changes.append(f"added owner record {name!r} (ev=verified)")

    for p in products:
        fix = BRAND_FIXES.get(p.get("name"))
        if not fix:
            continue
        old, new = fix
        if p.get("brand") == new:
            continue
        if p.get("brand") != old:
            changes.append(
                f"{p.get('name')!r}: brand is {p.get('brand')!r}, expected {old!r}; left as-is")
            continue
        p["brand"] = new
        changes.append(f"{p['name']!r}: brand {old!r} -> {new!r}")

    if not changes:
        print("idempotent: nothing to change")
        return 0

    for c in changes:
        print(" -", c)
    if dry:
        print("dry-run: no files written")
        return 0

    dump(owners, "owners.json")
    dump(products, "products.json")
    print("written: data/owners.json, data/products.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
