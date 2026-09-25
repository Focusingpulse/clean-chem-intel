#!/usr/bin/env python3
"""Apply Linnea's revision notes on the station-2 spectrum build.

Verdict: verdicts/SPX-spectrum-station2-verdict-2026-09-25.md (three-agent-intelligence)

R1 (required)  La Corona export share: the 15% figure was cited to expansion.mx, which
               never states it. Re-cited to the source that does state it:
               Mexico Desconocido, "Historia y usos del Jabon Zote..." (Tania Aleman
               Saavedra, 2020-01-16): "un 15% de esta llega a distintos mercados,
               principalmente el sudamericano y estadounidense."
               Live page returns 403 to curl; text confirmed in three Wayback snapshots
               (20200117150407, 20200221121903, 20241201), all statuscode 200.
R2 (required)  Dish-soap household penetration: the ">95%" figure was cited to
               asinsight.com (an Amazon top-10 sales analysis, which carries no
               penetration figure at all). Replaced with the category figure indexbox
               actually publishes -- "household penetration above 98%" for US Laundry &
               Home Products, a category whose stated scope includes dishwashing --
               and stated as a derivation from it rather than as a dish-soap figure.
               Same defect existed on two sibling records (Better Life, Seventh
               Generation) and on the Borax record's "exceeds 95%"; repaired together.
R4 (informational)  The 11 station-2 products carried no source_url. Backfilled from
               tier_src and paired with a source label, matching the 61 records that
               already carry both fields.
R6 (found while applying)  Zote Laundry Soap, White carried tier_src pointing at
               directionsforme 7383, which is the PINK page. White is 7384. Repointed.
               The finding cited 7384 correctly; only the data record was wrong.

Idempotent: each replacement asserts it matched. Re-running is a no-op or re-asserts.
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

MEXICO_DESCONOCIDO = (
    "https://www.mexicodesconocido.com.mx/"
    "historia-y-usos-del-jabon-zote-el-favorito-de-las-familias-mexicanas.html"
)
INDEXBOX = (
    "https://www.indexbox.io/store/"
    "united-states-laundry-home-products-market-analysis-forecast-size-trends-and-insights/"
)
ZOTE_PINK = "https://directionsforme.org/product/7383"
ZOTE_WHITE = "https://directionsforme.org/product/7384"

MAX_NEARLY_UNIVERSAL = (
    "The category-penetration figure published for US laundry and home products is "
    "household penetration above 98% (indexbox), and dishwashing is named in that "
    "category's scope; no dish-soap-specific penetration figure is published."
)

# --------------------------------------------------------------- replacements
OLD_LC_DETAIL = (
    "Mexican soap and detergent manufacturer; owns the Zote laundry-soap brand. The pink "
    "bar is its highest-volume line and about 15% of the brand's sales leave Mexico, "
    "primarily to the United States."
)
NEW_LC_DETAIL = (
    "Mexican soap and detergent manufacturer; owns the Zote laundry-soap brand. About 15% "
    "of its production reaches markets outside Mexico, mainly South America and the "
    "United States."
)

OLD_PINK = (
    "The pink bar is the brand's highest-volume line and about 15% of the brand's sales "
    "leave Mexico, primarily to the United States, so the product is genuinely common in "
    "US households even though no US penetration figure is published."
)
NEW_PINK = (
    "The pink bar is the brand's highest-volume line (expansion.mx, 2022), and about 15% "
    "of La Corona's production reaches markets outside Mexico, mainly South America and "
    "the United States (Mexico Desconocido, 2020), so the product is genuinely common in "
    "US households even though no US penetration figure is published."
)

OLD_WHITE = (
    "The white bar is a smaller line than the pink bar, and about 15% of the brand's "
    "sales leave Mexico primarily to the United States."
)
NEW_WHITE = (
    "The white bar is a smaller line than the pink bar, and about 15% of La Corona's "
    "production reaches markets outside Mexico, mainly South America and the United "
    "States (Mexico Desconocido, 2020)."
)

OLD_SPROUTS = (
    "Liquid dish soap is owned by over 95% of US households; that category figure is the "
    "one published number here, and Sprouts' own share of it is small. Channel share, not "
    "a measured product share."
)
NEW_SPROUTS = (
    MAX_NEARLY_UNIVERSAL
    + " Sprouts' own share of the category is small. Channel share, not a measured "
    "product share."
)

OLD_ECO = (
    "Eco hand-dish brands are a small fraction of the >95% of households that own liquid "
    "dish soap."
)
NEW_ECO = (
    "Eco hand-dish brands are a small fraction of that category, which indexbox reports "
    "at above 98% household penetration."
)

OLD_BORAX = (
    "Borax is a legacy laundry booster; laundry care exceeds 95% of US households but "
    "boosters are a small share of that."
)
NEW_BORAX = (
    "Borax is a legacy laundry booster; the laundry and home products category is "
    "reported at above 98% household penetration (indexbox), but boosters are a small "
    "share of that."
)

BASIS_EDITS = [
    ("Zote Laundry Soap, Pink", OLD_PINK, NEW_PINK),
    ("Zote Laundry Soap, White", OLD_WHITE, NEW_WHITE),
    ("Sprouts Free & Clear Dish Soap", OLD_SPROUTS, NEW_SPROUTS),
    ("Dish Liquid, Unscented", OLD_ECO, NEW_ECO),
    ("Dish Liquid, Free & Clear", OLD_ECO, NEW_ECO),
    ("20 Mule Team Borax (BMVC)", OLD_BORAX, NEW_BORAX),
]

# name -> (source label, source_url override or None to inherit tier_src)
SRC_LABEL = {
    "CVS Health Moisturizing Antibacterial Hand Soap": "FDA OTC drug label (DailyMed), labeler CVS Pharmacy",
    "Walgreens Antibacterial Hand Soap, Amber": "FDA OTC drug label (DailyMed), labeler Walgreen Co.",
    "Power Force Antibacterial Hand Soap, Green Apple": "FDA OTC drug label (DailyMed), labeler Korex Chicago LLC",
    "365 Everyday Value All-Purpose Cleaner, Wild Orange": "Whole Foods Market household-cleaner ingredient disclosure (CA SB-258)",
    "365 by Whole Foods Market All Purpose Cleaner, Citrus": "Whole Foods Market household-cleaner ingredient disclosure (CA SB-258)",
    "Whole Foods Market Organic Multisurface Cleaner, Lavender Lemon": "Whole Foods Market household-cleaner ingredient disclosure (CA SB-258)",
    "Sprouts Citrus Scent All Purpose Cleaner": "Sprouts California Cleaning Product Right to Know Act declaration",
    "Sprouts Free & Clear Dish Soap": "Sprouts California Cleaning Product Right to Know Act declaration",
    "Zote Laundry Soap, Pink": "Retailer ingredient panel (directionsforme) + La Corona SDS",
    "Zote Laundry Soap, White": "Retailer ingredient panel (directionsforme) + La Corona SDS",
    "Kirk's Original Coco Castile Soap": "Kirk's manufacturer ingredient page",
}
SRC_URL_OVERRIDE = {"Zote Laundry Soap, White": ZOTE_WHITE}


def main():
    prods = json.loads((DATA / "products.json").read_text(encoding="utf-8"))
    owners = json.loads((DATA / "owners.json").read_text(encoding="utf-8"))
    by_name = {p["name"]: p for p in prods}
    applied = []

    # ---- R1: owner record ------------------------------------------------
    lc = owners["owners"]["Fabrica de Jabon La Corona, S.A. de C.V."]
    if lc["detail"] == OLD_LC_DETAIL:
        lc["detail"] = NEW_LC_DETAIL
        lc["src"] = MEXICO_DESCONOCIDO
        applied.append("owners: La Corona detail + src re-cited to Mexico Desconocido")
    elif lc["detail"] == NEW_LC_DETAIL and lc["src"] == MEXICO_DESCONOCIDO:
        applied.append("owners: La Corona already revised")
    else:
        raise SystemExit(f"R1 owner record did not match either state:\n{lc['detail']!r}")

    # ---- R1/R2: exposure bases -------------------------------------------
    for name, old, new in BASIS_EDITS:
        p = by_name.get(name)
        if p is None:
            raise SystemExit(f"R1/R2: product not found: {name}")
        basis = p["exposure_basis"]
        if old in basis:
            p["exposure_basis"] = basis.replace(old, new)
            applied.append(f"basis: {name}")
        elif new in basis:
            applied.append(f"basis: {name} (already revised)")
        else:
            raise SystemExit(f"R1/R2: no match on {name}\n  tail: ...{basis[-160:]!r}")

    # Zote exposure source: the export share is the discriminating figure there,
    # so the record's source is the one that states it.
    for name in ("Zote Laundry Soap, Pink", "Zote Laundry Soap, White"):
        p = by_name[name]
        if p["exposure_src"] != MEXICO_DESCONOCIDO:
            p["exposure_src"] = MEXICO_DESCONOCIDO
            applied.append(f"exposure_src: {name} -> Mexico Desconocido")

    # Sprouts dish soap: the penetration number now comes from indexbox, so the
    # source follows the number.
    sp = by_name["Sprouts Free & Clear Dish Soap"]
    if sp["exposure_src"] != INDEXBOX:
        sp["exposure_src"] = INDEXBOX
        applied.append("exposure_src: Sprouts Free & Clear Dish Soap -> indexbox")

    # ---- R6: white Zote panel -------------------------------------------
    zw = by_name["Zote Laundry Soap, White"]
    if zw.get("tier_src") == ZOTE_PINK:
        zw["tier_src"] = ZOTE_WHITE
        applied.append("tier_src: Zote White 7383 (pink) -> 7384 (white)")

    # ---- R4: source + source_url on the 11 -------------------------------
    for name, label in SRC_LABEL.items():
        p = by_name.get(name)
        if p is None:
            raise SystemExit(f"R4: product not found: {name}")
        url = SRC_URL_OVERRIDE.get(name) or p.get("tier_src")
        if not url:
            raise SystemExit(f"R4: no tier_src to derive source_url from on {name}")
        if p.get("source_url") == url and p.get("source") == label:
            continue
        p["source"] = label
        p["source_url"] = url
        applied.append(f"source_url: {name}")

    (DATA / "products.json").write_text(
        json.dumps(prods, indent=1, ensure_ascii=False), encoding="utf-8")
    (DATA / "owners.json").write_text(
        json.dumps(owners, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"edits applied: {len(applied)}")
    for a in applied:
        print("  -", a)


if __name__ == "__main__":
    main()
