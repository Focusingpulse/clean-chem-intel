#!/usr/bin/env python3
"""Correct the exposure ruling of 1b37773 per new research (Dolman, 7c197b6).

The 1b37773 ruling removed the home-fragrance penetration leg from Glade and set
Febreze AIR to untested on the premise that no household-penetration figure for
home fragrance could be located. Dolman's research supply (three-agent-intelligence
7c197b6, verified independently by Linnea this fire) established that the leg IS
citable — the live IndexBox page is the Air Fresheners & Candles report:

    https://www.indexbox.io/store/united-states-air-fresheners-candles-market-analysis-forecast-size-trends-and-insights/

which reads, verbatim: "As of 2026, household penetration for at least one home
fragrance format exceeds 85%". Also established: the stored 19.3 is SVG path
coordinate noise (substring of 319.35/315.35) and 28.7/19.0 appear nowhere; the
page's own period label is September 2026 (the original "April 2026" was wrong);
the readable plug-in shares are Febreze 21.5%, Pura 15.5%, Glade 14.5%, private
label 14.3%, Air Wick 11.9%.

Corrected ruling (Option A, per the research supply):
- Glade: re-derived share (14.5%, readable) + the 85% penetration leg WITH URL;
  the "roughly a third of households" assumption restored, now documented by the
  research supply's claim 8. exposure 6 / extrapolated unchanged.
- Febreze AIR: restored to extrapolated (8) with the corrected share sentence
  (Febreze leads plug-in at 21.5%, September 2026) + the 85% leg with URL + an
  explicit format caveat (Febreze AIR is a spray; plug-in share used as a
  brand-strength proxy only). The unreproducible 43% Amazon leg is dropped.

Idempotent: asserts the 1b37773 state; a second run is a no-op.
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
PRODUCTS = DATA / "products.json"

GLADE_NAME = "Glade PlugIns Scented Oil Air Freshener Refills, Hawaiian Breeze"
FEBREZE_NAME = "Febreze AIR Freshener, Fresh Sky"

IDX_URL = "https://www.indexbox.io/store/united-states-air-fresheners-candles-market-analysis-forecast-size-trends-and-insights/"

GLADE_OLD_BASIS = (
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
GLADE_NEW_BASIS = (
    "Derived, not measured. Glade holds 14.5% of the US plug-in air freshener "
    "category (Simporter, September 2026, which also puts Febreze at 21.5%, "
    "Pura at 15.5%, private label at 14.3% and Air Wick at 11.9%), and the "
    "parent home-fragrance category reaches household penetration above 85% "
    f"(IndexBox, 2026: {IDX_URL}). The share set previously cited here (Glade "
    "19.3%, Febreze PLUG 28.7%, private label 19.0%, Air Wick 15.8%) could not "
    "be reproduced from the cited page and was removed by verification ruling "
    "2026-09-27 (19.3 is SVG-coordinate noise on the home-fragrance page; 28.7 "
    "and 19.0 appear nowhere; the readable 15.8% belongs to Yankee Candle). "
    "Searched for a published household-penetration figure for the plug-in "
    "format itself or for this brand and found none; the derivation therefore "
    "assumes roughly a third of households use a plug-in at all, which is an "
    "assumption stated here rather than sourced. One significant figure, order "
    "of magnitude."
)

FEBREZE_OLD_BASIS = (
    "searched for a published household-penetration or sales-share figure for "
    "this SKU and for the Febreze AIR spray format; the plug-in subcategory "
    "shares on the cited Simporter page are the wrong format for a spray, the "
    "previously cited figures (Febreze PLUG 28.7% of plug-in category; 43% of "
    "Amazon US air-freshener unit volume, IndexBox 2025) could not be "
    "reproduced from reachable pages, and no home-fragrance household-"
    "penetration figure could be located. Left as a research gap rather than "
    "estimated."
)
FEBREZE_NEW_BASIS = (
    "Derived, not measured. Febreze is the leading US air-care brand: Febreze "
    "leads the US plug-in air freshener category at 21.5% (Simporter, September "
    "2026), and the parent home-fragrance category reaches household penetration "
    f"above 85% (IndexBox, 2026: {IDX_URL}). Febreze AIR is a spray, so the "
    "plug-in share is the wrong format for that product and is used here only "
    "as a brand-strength proxy, stated rather than sourced. The previously "
    "cited figures (Febreze PLUG 28.7%; 43% of Amazon US air-freshener unit "
    "volume, IndexBox 2025) could not be reproduced from reachable pages and "
    "were removed by verification ruling 2026-09-27. One significant figure."
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
    assert glade.get("exposure_basis") == GLADE_OLD_BASIS, "Glade basis not at 1b37773 state"
    glade["exposure_basis"] = GLADE_NEW_BASIS

    febreze = by_name.get(FEBREZE_NAME)
    assert febreze is not None, f"{FEBREZE_NAME} not found"
    assert febreze.get("exposure") is None, febreze.get("exposure")
    assert febreze.get("exposure_ev") == "untested"
    assert febreze.get("exposure_src") is None
    assert febreze.get("exposure_basis") == FEBREZE_OLD_BASIS, "Febreze basis not at 1b37773 state"
    febreze["exposure"] = 8
    febreze["exposure_ev"] = "extrapolated"
    febreze["exposure_src"] = "https://simporter.com/trends/plug-in-air-freshener/"
    febreze["exposure_basis"] = FEBREZE_NEW_BASIS

    save(data)
    print("corrected: Glade 85% leg restored with URL; Febreze AIR -> 8/extrapolated (Option A)")


if __name__ == "__main__":
    main()