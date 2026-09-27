#!/usr/bin/env python3
"""Apply Linnea's 2026-09-27 exposure ruling to the two Simporter-cited records.

Ruling source: three-agent-intelligence
`gaps/exposure-brand-shares-not-in-cited-page-prose-2026-09-27.md` (ruled
2026-09-27 20:00Z) and `verdicts/SPX-spectrum-station2-verdict-rev1-2026-09-27.md`.

What was wrong: the two derived exposure bases quoted Simporter brand shares
(Glade 19.3%, Febreze PLUG 28.7%, private label 19.0%, Air Wick 15.8%) that are
not in the readable text of the cited page, plus a home-fragrance
household-penetration figure (above 85%, IndexBox 2026) that could not be
located on any reachable IndexBox page, plus a Febreze "43% of Amazon US
air-freshener unit volume (IndexBox 2025)" figure that could not be reproduced.

Re-derived this ruling (independent fetches, browser UA, 2026-09-27):
- simporter.com/trends/plug-in-air-freshener/ readable text: Febreze 21.5%,
  Pura 15.5%, private label 14.3%, Glade 14.5%, Air Wick 11.9%. No 19.3, 28.7,
  19.0 anywhere (raw HTML included); 15.8 appears only in chart JSON.
- simporter.com/trends/home-fragrance/ readable text: Bath & Body Works 22.5%,
  Yankee Candle 15.8%, Private Label 12.3%. 19.3 appears only in chart JSON;
  28.7 and 19.0 appear nowhere.
- The IndexBox "household penetration above 85%" sentence that does exist is
  the fabric-softener-pack report (a different category), not home fragrance.

Ruling:
- Glade PlugIns (a plug-in refill -- right format): re-derive to the readable
  figure, Glade 14.5% of the US plug-in air freshener category (Simporter,
  2026, readable text). exposure stays 6, exposure_ev stays extrapolated,
  exposure_src unchanged. The unsupported companion figures and the 85% leg
  are dropped; the missing household base is stated as a limitation.
- Febreze AIR (a spray -- the plug-in subcategory share is the wrong format):
  set to untested with a null exposure and a basis naming the searches.

Idempotent: asserts the expected prior state; a second run is a no-op.
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
PRODUCTS = DATA / "products.json"

GLADE_NAME = "Glade PlugIns Scented Oil Air Freshener Refills, Hawaiian Breeze"
FEBREZE_NAME = "Febreze AIR Freshener, Fresh Sky"

GLADE_OLD_BASIS = (
    "Derived, not measured. Glade PlugIns holds 19.3% of the US plug-in air "
    "freshener category (Simporter, April 2026, which also puts Febreze PLUG at "
    "28.7%, private label at 19.0% and Air Wick at 15.8%), and the home-fragrance "
    "category reaches household penetration above 85% (IndexBox, 2026). Searched "
    "for a published household-penetration figure for the plug-in format itself "
    "or for this brand and found none; the derivation therefore assumes roughly "
    "a third of households use a plug-in at all, which is an assumption stated "
    "here rather than sourced. One significant figure, order of magnitude."
)
GLADE_NEW_BASIS = (
    "Derived, not measured. Glade holds 14.5% of the US plug-in air freshener "
    "category (Simporter, 2026, readable text of the plug-in trends page). The "
    "share set previously cited here (Glade 19.3%, Febreze PLUG 28.7%, private "
    "label 19.0%, Air Wick 15.8%) could not be reproduced from the cited page "
    "and was removed by verification ruling 2026-09-27: 19.3 appears only as "
    "chart data on the home-fragrance page, 28.7 and 19.0 appear nowhere, and "
    "the readable 15.8% belongs to Yankee Candle. No household-penetration "
    "figure for home fragrance or the plug-in format could be located at this "
    "layer's standard, so the derivation is a category share without a "
    "household base, stated here rather than sourced. One significant figure, "
    "order of magnitude."
)

FEBREZE_OLD_BASIS = (
    "Derived, not measured. Febreze is the leading US air-care brand: Febreze "
    "PLUG holds 28.7% of the plug-in air freshener category (Simporter, April "
    "2026) and Febreze holds roughly 43% of Amazon US air-freshener unit volume "
    "(IndexBox, 2025). Searched for a per-SKU or per-brand household-penetration "
    "figure for Febreze AIR specifically and found none, so the estimate is a "
    "category-share read applied to home-fragrance penetration above 85% "
    "(IndexBox, 2026) with a format-share assumption stated rather than sourced. "
    "One significant figure."
)
FEBREZE_NEW_BASIS = (
    "searched for a published household-penetration or sales-share figure for "
    "this SKU and for the Febreze AIR spray format; the plug-in subcategory "
    "shares on the cited Simporter page are the wrong format for a spray, the "
    "previously cited figures (Febreze PLUG 28.7% of plug-in category; 43% of "
    "Amazon US air-freshener unit volume, IndexBox 2025) could not be "
    "reproduced from reachable pages, and no home-fragrance household-"
    "penetration figure could be located. Left as a research gap rather than "
    "estimated."
)


def load():
    with open(PRODUCTS) as fh:
        return json.load(fh)


def save(data):
    with open(PRODUCTS, "w") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main():
    data = load()
    items = list(data.values()) if isinstance(data, dict) else data
    by_name = {p.get("name"): p for p in items}

    glade = by_name.get(GLADE_NAME)
    assert glade is not None, f"{GLADE_NAME} not found"
    assert glade.get("exposure") == 6, glade.get("exposure")
    assert glade.get("exposure_ev") == "extrapolated"
    assert glade.get("exposure_basis") == GLADE_OLD_BASIS, "Glade basis drifted"
    glade["exposure_basis"] = GLADE_NEW_BASIS

    febreze = by_name.get(FEBREZE_NAME)
    assert febreze is not None, f"{FEBREZE_NAME} not found"
    assert febreze.get("exposure") == 8, febreze.get("exposure")
    assert febreze.get("exposure_ev") == "extrapolated"
    assert febreze.get("exposure_basis") == FEBREZE_OLD_BASIS, "Febreze basis drifted"
    febreze["exposure"] = None
    febreze["exposure_ev"] = "untested"
    febreze["exposure_src"] = None
    febreze["exposure_basis"] = FEBREZE_NEW_BASIS

    save(data)
    print("applied: Glade re-derived (14.5%, readable); Febreze AIR -> untested/null")


if __name__ == "__main__":
    main()