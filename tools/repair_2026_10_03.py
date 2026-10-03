#!/usr/bin/env python3
"""Repair 2026-10-03: Reckitt/Essential Home host split.

The Essential Home brands moved their US ingredient disclosure from
rbnainfo.com (Reckitt) to vestacyinfo.com (Vestacy, the Advent-backed
carve-out). Every Essential Home product id is live on vestacyinfo.com and
500s on rbnainfo.com; every Reckitt-retained id is the reverse. Measured
2026-10-03. This script repoints only the verified Essential Home records.

Idempotent: re-running is a no-op once the host is vestacyinfo.com.
"""
import json, sys, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry-run" in sys.argv
NO_CHANGELOG = "--no-changelog" in sys.argv

# name -> list of (field, old_url, new_url) verified live 2026-10-03
V = "https://www.vestacyinfo.com"
PLAN = {
    "Calgon Water Softener, Liquid": [
        ("source_url", "https://www.rbnainfo.com/smart-label/192", f"{V}/smart-label/192"),
        ("tier_src",   "https://www.rbnainfo.com/smart-label/192", f"{V}/smart-label/192"),
        ("exposure_src","https://www.rbnainfo.com/smart-label/192", f"{V}/smart-label/192"),
        ("source", "Reckitt SmartLabel ingredient disclosure", "Vestacy SmartLabel ingredient disclosure"),
        ("disclosure_note", "The Reckitt SmartLabel", "The Vestacy SmartLabel"),
    ],
    "Air Wick Scented Oil, Ocean Spray": [
        ("source_url", "https://www.rbnainfo.com/smart-label.php?productLineId=3404", f"{V}/smart-label.php?productLineId=3404"),
        ("tier_src",   "https://www.rbnainfo.com/smart-label.php?productLineId=3404", f"{V}/smart-label.php?productLineId=3404"),
        ("exposure_src","https://www.rbnainfo.com/smart-label.php?productLineId=3404", f"{V}/smart-label.php?productLineId=3404"),
        ("source", "Reckitt SmartLabel ingredient disclosure (California Cleaning Product Right to Know Act)",
                   "Vestacy SmartLabel ingredient disclosure (California Cleaning Product Right to Know Act)"),
        ("disclosure_note", "The Reckitt SmartLabel", "The Vestacy SmartLabel"),
    ],
    "Resolve Heavy Traffic Foam Carpet Cleaner": [
        ("source_url", "https://www.rbnainfo.com/product.php?productLineId=490", f"{V}/product.php?productLineId=490"),
        ("source", "Reckitt SmartLabel public ingredient disclosure", "Vestacy SmartLabel public ingredient disclosure"),
    ],
    "Woolite Delicates Laundry Detergent": [
        ("source_url", "https://rbnainfo.com/product.php?productLineId=592", f"{V}/product.php?productLineId=592"),
        ("source", "Reckitt SmartLabel public ingredient disclosure", "Vestacy SmartLabel public ingredient disclosure"),
    ],
    "Spray 'n Wash Laundry Stain Remover": [
        ("source_url", "https://rbnainfo.com/product.php?productLineId=1490", f"{V}/product.php?productLineId=1490"),
        ("source", "Reckitt (rbnainfo.com) SmartLabel public ingredient disclosure + SDS",
                   "Vestacy SmartLabel public ingredient disclosure + SDS"),
    ],
    "Old English Lemon Oil Furniture Polish": [
        ("source_url", "https://www.rbnainfo.com/productpro/getmsds/4000c754-a650-4bec-ac2c-e7449460b656",
                       f"{V}/productpro/getmsds/4000c754-a650-4bec-ac2c-e7449460b656"),
        ("source", "Manufacturer SDS (Reckitt, published via rbnainfo.com)",
                   "Manufacturer SDS (Vestacy, published via vestacyinfo.com)"),
    ],
    "Glass Plus Cleaner": [
        ("tier_src", "https://www.rbnainfo.com/product.php?productLineId=316", f"{V}/product.php?productLineId=316"),
        ("exposure_src", "https://www.rbnainfo.com/product.php?productLineId=316", f"{V}/product.php?productLineId=316"),
        ("tier_note", "Glass Plus is a Reckitt mass-market glass cleaner",
                      "Glass Plus is a Vestacy mass-market glass cleaner"),
    ],
    "Lime-A-Way Toilet Bowl Cleaner": [
        ("tier_src", "https://www.rbnainfo.com/product.php?productLineId=320", f"{V}/product.php?productLineId=320"),
        ("exposure_src", "https://www.rbnainfo.com/product.php?productLineId=320", f"{V}/product.php?productLineId=320"),
    ],
}

def main():
    p = json.loads((REPO/"data/products.json").read_text(encoding="utf-8"))
    products = p if isinstance(p, list) else p["products"]
    by_name = {x["name"]: x for x in products}
    edits = 0
    for name, ops in PLAN.items():
        rec = by_name.get(name)
        if rec is None:
            print(f"!! MISSING RECORD: {name}"); continue
        for field, old, new in ops:
            cur = rec.get(field)
            if cur is None:
                print(f"!! {name}: field {field} absent"); continue
            if cur == old:
                rec[field] = new; edits += 1
            elif cur == new or new in cur:
                pass  # already applied
            elif old in cur:
                rec[field] = cur.replace(old, new); edits += 1
            else:
                print(f"!! {name}.{field} unexpected value: {cur!r}"); continue
    # assert no rbnainfo citation survives on the eight
    left = [x["name"] for n, x in by_name.items()
            if n in PLAN and any(isinstance(v,str) and "rbnainfo" in v for v in x.values())]
    if left:
        print("!! rbnainfo citations still present:", left); sys.exit(2)
    # assert the three Reckitt-retained records are untouched
    for n in ["Lysol Disinfecting Wipes, Crisp Linen","Lysol Laundry Sanitizer, Free & Clear",
              "Vanish Oxi Action In-Wash Fabric Stain Remover"]:
        if any(isinstance(v,str) and "rbnainfo" not in v for k,v in by_name[n].items()
               if k in ("source_url",)):
            print(f"!! Reckitt-retained record {n} lost its rbnainfo citation"); sys.exit(2)

    # --- owners.json ---
    o = json.loads((REPO/"data/owners.json").read_text(encoding="utf-8"))
    eh = o["owners"]["Essential Home (Advent International)"]
    rk = o["owners"]["Reckitt"]
    eh["detail"] = (
        "Reckitt Benckiser divested its Essential Home business to Advent International, L.P. - "
        "agreement announced 2025-07-18, completed 2025-12-31 (both dates read from Reckitt's own "
        "press releases on 2026-10-03; an earlier note in this record said 2024-07-24 for the "
        "announcement, which no source supports). Essential Home spans roughly 80 brands sold across "
        "about 70 countries; Reckitt retains a 30% equity stake in Advent's acquisition vehicle. The "
        "business now trades as Vestacy, which describes itself as home to Air Wick, Calgon, Cillit "
        "Bang and Mortein, and publishes the US ingredient disclosures for the wider North American "
        "portfolio (Brasso, d-CON, Easy-Off, Glass Plus, Lime-A-Way, Mop & Glo, Old English, Resolve, "
        "Rid-X, Silvo, Spray 'n Wash, Woolite) at vestacyinfo.com. Air Wick and Calgon were moved here "
        "from Reckitt on 2026-10-02; Woolite was moved here on 2026-10-03 once Vestacy's own brand page "
        "listed it."
    )
    eh["src"] = "https://www.reckitt.com/news/reckitt-completes-divestment-of-essential-home/"
    for b in ["Woolite", "Brasso", "d-CON", "Easy-Off", "Glass Plus", "Lime-A-Way",
              "Mop & Glo", "Old English", "Resolve", "Rid-X", "Silvo", "Spray 'n Wash",
              "Botanical Origin", "Vestacy"]:
        if b not in eh["brands"]:
            eh["brands"].append(b)
    if "Woolite" in rk["brands"]:
        rk["brands"].remove("Woolite"); edits += 1
    rk["detail"] = rk["detail"].replace(
        "OPEN FLAG: Woolite is kept on this record but Reckitt's own brand page does not list it and "
        "no primary source for its current ownership was located this fire; unverified, not corrected.",
        "Woolite was REMOVED from this record on 2026-10-03: Vestacy's own brand page "
        "(vestacyinfo.com/brands.php, read 2026-10-03) lists WOOLITE among its brands, resolving the "
        "open flag raised 2026-10-02.")
    bs = rk.get("brand_sources", {})
    if "Woolite" in bs.get("unverified_kept_pending_primary", []):
        bs["unverified_kept_pending_primary"].remove("Woolite")
        if not bs["unverified_kept_pending_primary"]:
            del bs["unverified_kept_pending_primary"]

    if DRY:
        print(f"[dry-run] would apply {edits} edits"); return
    (REPO/"data/products.json").write_text(json.dumps(products, indent=1, ensure_ascii=False), encoding="utf-8")
    (REPO/"data/owners.json").write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"applied {edits} product-field edits; owners.json updated")

    if not NO_CHANGELOG:
        cpath = REPO/"data/changelog.json"
        c = json.loads(cpath.read_text(encoding="utf-8"))
        if not any(e.get("date") == "2026-10-03" and "vestacyinfo" in e.get("text","").lower() for e in c):
            c.insert(0, {"date": "2026-10-03",
                         "text": "Repointed eight product citations from rbnainfo.com to vestacyinfo.com. "
                                 "The Essential Home brands (Air Wick, Calgon, Glass Plus, Lime-A-Way, Old "
                                 "English, Resolve, Spray 'n Wash, Woolite) moved their US ingredient "
                                 "disclosures to Vestacy, the company carved out of Reckitt's Essential Home "
                                 "business. The old links returned errors; the same product pages are live at "
                                 "the new address. Woolite is also recorded under Vestacy now, which closes an "
                                 "open ownership question."})
            cpath.write_text(json.dumps(c, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            print("changelog entry added")

if __name__ == "__main__":
    main()
