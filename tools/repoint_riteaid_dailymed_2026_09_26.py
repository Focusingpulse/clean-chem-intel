#!/usr/bin/env python3
"""Repoint the Rite Aid hand-soap source to the primary FDA label (DailyMed).

Source-policy rule: when a product's source_url points at a third-party NDC
mirror, resolve the NDC against DailyMed and use the primary SPL. This record
(today's station-2 harvest) cited https://ndclist.com/ndc/11822-2003 -- a mirror,
and one that answers a machine request with a Cloudflare interstitial. The
primary route is the DailyMed API:

    https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?ndc=11822-2003
      -> setid 20d8b8a8-9d15-ad76-e063-6294a90a0521
      -> "SIMPLIFY CLEAN AND PROTECT COOL SPLASH LHS (BENZALKONIUM CHLORIDE)
          LIQUID [RITE AID CORPORATION]"

Reader page read live 2026-09-26 (HTTP 200): NDC Code(s) 11822-2003-1, Packager
RITE AID CORPORATION, Category HUMAN OTC DRUG LABEL, active benzalkonium
chloride.

Idempotent: asserts the expected prior state; a second run is a no-op.
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
NAME = "Rite Aid Simplify Clean And Protect Medicated Liquid Hand Soap"
OLD = "https://ndclist.com/ndc/11822-2003"
NEW = (
    "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm"
    "?setid=20d8b8a8-9d15-ad76-e063-6294a90a0521"
)


def main():
    prods = json.loads((DATA / "products.json").read_text(encoding="utf-8"))
    p = next(x for x in prods if x["name"] == NAME)
    applied = []
    for field in ("source_url", "tier_src"):
        if p.get(field) == OLD:
            p[field] = NEW
            applied.append(field)
        elif p.get(field) == NEW:
            applied.append(f"{field} (already)")
        else:
            raise SystemExit(f"{field} unexpected: {p.get(field)!r}")
    (DATA / "products.json").write_text(
        json.dumps(prods, indent=1, ensure_ascii=False), encoding="utf-8")
    print("edits applied: %d -> %s" % (len(applied), ", ".join(applied)))


if __name__ == "__main__":
    main()
