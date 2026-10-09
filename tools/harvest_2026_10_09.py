#!/usr/bin/env python3
"""Spectrum harvest, night-shift station 2, 2026-10-09.

Two jobs, both in the harvest lane:

1. HARVEST -- the drugstore house-brand CLEANER block, which the 2026-10-05
   gap recorded as unbuilt. The route is the Spanish-locale CVS host
   (`es.cvs.com`), which serves the manufacturer's California Cleaning Product
   Right to Know Act (SB-258) ingredient paragraph in a JSON field named
   `vendorIngredientsParagraph`. `www.cvs.com` 403s the same path. The prodid
   alone resolves, so a junk slug plus a valid prodid 301s to the canonical
   page. Four Total Home records enter; the ones whose served disclosure is a
   coarse active-only line, a class-name list, or a trade-named blend are held
   out and filed instead (see the finding).

2. CITATION REPAIR -- 12 product records cite `https://smartlabel.pg.com/...`,
   a catch-all shell host that returns a byte-identical 2,317-byte body for
   every path and is therefore never a valid citation. The manufacturer's real
   disclosure is served by the keyless P&G SmartLabel API, and the GTIN is
   already in the cited URL's path, so the repair is mechanical. Repointed only
   where the API's ingredient list matches the record's own list; the two
   records that do not match are left alone and named in the finding.

Idempotent: a product already present by name is skipped, an ingredient key
that already exists (case-insensitively, or through the alias map) is never
re-minted, and the citation repair is a no-op once applied.

Usage:
  python3 tools/harvest_2026_10_09.py [--dry-run] [--no-changelog]
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TODAY = "2026-10-09"

OWNER = "CVS Health Corporation"
# The served CVS brand page names Total Home as a CVS house brand. It is not the
# record's `src` (one src per owner record -- the known apply_owners precision
# defect); it is cited in the tier_note and the finding instead.
OWNER_BRAND_TO_ADD = "Total Home"

# --- exposure sources -----------------------------------------------------
SRC_DISH = ("https://www.indexbox.io/store/united-states-dishwashing-"
            "market-analysis-forecast-size-trends-and-insights/")
SRC_LAUNDRY = ("https://www.indexbox.io/store/united-states-laundry-home-products-"
               "market-analysis-forecast-size-trends-and-insights/")

# --- products -------------------------------------------------------------
PRODUCTS = [
    dict(
        name="Total Home Ultra Liquid Dish Soap, Clean Scent, 14.7 fl oz",
        brand="Total Home", cat="Dish Soap",
        source_url="https://es.cvs.com/shop/ingredients/total-home-ultra-liquid-dish-soap-clean-14-7-fl-oz-prodid-258358",
        tier_src="https://es.cvs.com/shop/total-home-ultra-liquid-dish-soap-clean-14-7-fl-oz-prodid-258358",
        source=("CVS house-brand (Total Home) ingredient disclosure, served by CVS on its Spanish-locale host "
                "es.cvs.com in the page's `vendorIngredientsParagraph` field. This is the manufacturer's "
                "California Cleaning Product Right to Know Act (SB-258) declaration published by the retailer "
                "that sells the product. Fourteen intentionally added ingredients, thirteen of them named with a "
                "CAS number; fragrance and the colourant are declared as classes. Read today from the served page."),
        note=("The house-brand dish soap in the largest US drugstore chain, and it is the same formula the "
              "retailer lists under two sizes. The surfactant system is ordinary and fully named: a C14-16 "
              "olefin sulfonate, an amine oxide, sodium laureth sulfate and sodium lauryl sulfate, with sodium "
              "chloride and sodium xylenesulfonate for viscosity and a citric acid pH adjuster. Two things are "
              "worth a reader's attention. The preservative pair methylisothiazolinone and "
              "methylchloroisothiazolinone is the allergen pair that made some people switch dish soaps, and it "
              "is declared here rather than hidden. Limonene and hexyl cinnamal are declared fragrance "
              "constituents, which most dish soaps bury inside the word fragrance. The label names the amine "
              "oxide only by class and gives three CAS numbers for it (61792-31-2, 67806-10-4 and/or 1643-20-5), "
              "so this record maps it to the registry's generic alkyldimethylamine oxide key rather than "
              "asserting one of the three."),
        ings=["Water", "Sodium C14-16 Olefin Sulfonate", "Alkyldimethylamine Oxide",
              "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate", "Sodium Chloride",
              "Sodium Xylenesulfonate", "Fragrance", "Limonene", "Hexyl Cinnamal",
              "Methylisothiazolinone", "Methylchloroisothiazolinone", "Citric Acid", "Colorant"],
        substitutes=[
            dict(name="ATTITUDE Dishwashing Liquid, Unscented", tier="natural",
                 note=("Same aisle, natural-set price band. Avoids the methylisothiazolinone and "
                       "methylchloroisothiazolinone preservative pair and the declared fragrance constituents, "
                       "which is the whole point of choosing it over this record.")),
            dict(name="Seventh Generation Dish Liquid, Free & Clear", tier="grocery",
                 note=("Grocery-aisle price, widely stocked. Fragrance-free and isothiazolinone-free, so it "
                       "drops the allergen pair and the limonene and hexyl cinnamal this record declares.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=2,
        exposure_src=SRC_DISH,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household figure "
                        "for CVS Total Home cleaners (the CVS corporate site, the IndexBox US dishwashing page, "
                        "and a general web search for 'Total Home by CVS household penetration') and found none. "
                        "The estimate is category penetration times drugstore-channel share times house-brand "
                        "share inside that channel: liquid dish soap is used in more than nine of ten US "
                        "households, drugstores are a minority channel for it, and the chain's own house brand is "
                        "a fraction of the drugstore shelf. The estimate stops at the channel-and-house-brand "
                        "level because nothing more specific is published."),
        tier_note=("CVS house brand. The served CVS brand page names Total Home as a CVS-exclusive home care "
                   "line, so the tier is the drugstore channel rather than a grocery or mass shelf."),
        strength_disclosure="full",
        disclosure_note=None,
    ),
    dict(
        name="Total Home Power Foam Dish Soap Spray, Clean Scent, 16 fl oz",
        brand="Total Home", cat="Dish Soap",
        source_url="https://es.cvs.com/shop/ingredients/total-home-power-foam-dish-soap-spray-clean-16-fl-oz-prodid-258371",
        tier_src="https://es.cvs.com/shop/total-home-power-foam-dish-soap-spray-clean-16-fl-oz-prodid-258371",
        source=("CVS house-brand (Total Home) ingredient disclosure, served by CVS on es.cvs.com in the page's "
                "`vendorIngredientsParagraph` field, the retailer's publication of the manufacturer's California "
                "SB-258 declaration. Sixteen intentionally added ingredients, all named, with fragrance declared "
                "as a class and limonene and linalool named separately. Read today from the served page."),
        note=("The spray form of the same house brand, and a different formula from the liquid: this one is built "
              "on denatured alcohol and lauramine oxide with a laureth-7 wetting agent, and it carries sodium "
              "hydroxide, which the liquid does not. The two preservatives are the isothiazolinone pair again. "
              "Denatured alcohol is what makes it flash off without streaking, and it is also why the label "
              "carries a flammability caution. Read it against the liquid record if you are choosing between "
              "them: the spray trades a lower surfactant load for alcohol and a caustic pH adjuster."),
        ings=["Alcohol Denat.", "Citric Acid", "Fragrance", "Lauramine Oxide", "Laureth-7", "Limonene",
              "Linalool", "Methylchloroisothiazolinone", "Methylisothiazolinone", "PPG-2 Butyl Ether",
              "Propylene Glycol", "Sodium Hydroxide", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
              "Tetrasodium Glutamate Diacetate", "Water"],
        substitutes=[
            dict(name="AspenClean Dish Soap, Unscented", tier="natural",
                 note=("Fragrance-free and isothiazolinone-free, so it drops the declared limonene and linalool "
                       "and the preservative pair, and it has no denatured alcohol or added hydroxide.")),
            dict(name="Puracy Dish Soap, Green Tea & Lime", tier="natural",
                 note=("Plant-based surfactant base in the same price band. Avoids the alcohol and the caustic "
                       "pH adjuster, and it declares its fragrance constituents rather than burying them.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=2,
        exposure_src=SRC_DISH,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household figure "
                        "for CVS Total Home cleaners (CVS corporate site, IndexBox US dishwashing page, and a "
                        "general web search for 'Total Home by CVS household penetration') and found none. The "
                        "estimate is category penetration times drugstore-channel share times house-brand share "
                        "inside that channel; the spray is a smaller slice of the dish-soap shelf than the "
                        "liquid, so the figure is carried at the same order of magnitude rather than raised."),
        tier_note=("CVS house brand; sold in the drugstore channel, same as the rest of the Total Home line."),
        strength_disclosure="full",
        disclosure_note=None,
    ),
    dict(
        name="Total Home Free & Clear Liquid Laundry Detergent, Unscented, 100 fl oz",
        brand="Total Home", cat="Laundry",
        source_url="https://es.cvs.com/shop/ingredients/total-home-free-clear-liquid-laundry-detergent-unscented-100-fl-oz-prodid-142909",
        tier_src="https://es.cvs.com/shop/total-home-free-clear-liquid-laundry-detergent-unscented-100-fl-oz-prodid-142909",
        source=("CVS house-brand (Total Home) ingredient disclosure, served by CVS on es.cvs.com in the page's "
                "`vendorIngredientsParagraph` field, the retailer's publication of the manufacturer's California "
                "SB-258 declaration. Eleven intentionally added ingredients, all named, and no fragrance line at "
                "all, which is the point of the Free & Clear label. Read today from the served page."),
        note=("The fragrance-free house-brand laundry detergent, and the absence of a fragrance line is the "
              "useful part: the 2026-10-08 Walmart/Sam's harvest held out a dryer-sheet filing because 45 of its "
              "47 disclosed lines were fragrance constituents, and this record is the opposite shape. It is a "
              "plain anionic/nonionic builder: ethoxylated alcohol and sodium laureth sulfate with "
              "dodecylbenzene sulfonic acid neutralised by caustic soda, an amine oxide booster, sodium borate "
              "for buffering and pH control, a silicone antifoam and a triazine preservative. Sodium borate is "
              "the one worth a second look on a household with small children, and it is why this record carries "
              "a substitute."),
        ings=["Water", "Ethoxylated Alcohol", "Dodecylbenzene Sulfonic Acid", "Sodium Laureth Sulfate",
              "Sodium Chloride", "Sodium Hydroxide", "Alkyldimethylamine Oxide", "Sodium Borate",
              "Dimethicone", "Triazine", "Citric Acid"],
        substitutes=[
            dict(name="ATTITUDE Laundry Detergent, Unscented", tier="natural",
                 note=("Fragrance-free like this record, without the sodium borate, so it is the same-price "
                       "answer for a household avoiding borate around small children.")),
            dict(name="ECOS Laundry Detergent, Free & Clear", tier="grocery",
                 note=("Grocery price, no borate and no triazine preservative, and it declares its own "
                       "ingredients the same way.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=1,
        exposure_src=SRC_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household figure "
                        "for CVS Total Home laundry products (CVS corporate site, IndexBox US laundry and home "
                        "products page, and a general web search) and found none. The estimate is category "
                        "penetration (laundry care is used in more than nine of ten US households) times the "
                        "drugstore channel's small share of laundry sales times the house brand's share inside "
                        "that channel. Laundry is a big-box category, so the drugstore slice is smaller than the "
                        "dish-soap slice and the figure is carried one point lower."),
        tier_note=("CVS house brand; drugstore channel."),
        strength_disclosure="full",
        disclosure_note=None,
    ),
    dict(
        name="Total Home Liquid Laundry Detergent, Fresh Scent, 100 fl oz",
        brand="Total Home", cat="Laundry",
        source_url="https://es.cvs.com/shop/ingredients/total-home-liquid-laundry-detergent-fresh-100-fl-oz-prodid-126417",
        tier_src="https://es.cvs.com/shop/total-home-liquid-laundry-detergent-fresh-100-fl-oz-prodid-126417",
        source=("CVS house-brand (Total Home) ingredient disclosure, served by CVS on es.cvs.com in the page's "
                "`vendorIngredientsParagraph` field, the retailer's publication of the manufacturer's California "
                "SB-258 declaration. Thirteen intentionally added ingredients, all named, with fragrance declared "
                "as a class and the colourant named only as the supplier's dye trade name. Read today from the "
                "served page."),
        note=("The scented twin of the Free & Clear record above, and the two differ by exactly two lines: a "
              "fragrance and a dye. Everything else is the same list, so the pair is a clean read on what the "
              "scent costs you. If someone in the house reacts to detergent, this record is the one to compare "
              "against the Free & Clear entry rather than the other way round. The dye is declared only as "
              "'liquitint blue Hp', a supplier trade name, so this record maps it to the registry's generic "
              "colourant key and does not pretend to know its chemistry."),
        ings=["Water", "Ethoxylated Alcohol", "Dodecylbenzene Sulfonic Acid", "Sodium Laureth Sulfate",
              "Sodium Chloride", "Sodium Hydroxide", "Alkyldimethylamine Oxide", "Sodium Borate",
              "Dimethicone", "Fragrance", "Triazine", "Citric Acid", "Colorant"],
        substitutes=[
            dict(name="Total Home Free & Clear Liquid Laundry Detergent, Unscented, 100 fl oz", tier="drugstore",
                 note=("The same brand, the same shelf, the same price, and the same formula minus the fragrance "
                       "and the dye. It is the substitute because the disclosure shows the two differ by exactly "
                       "those two lines.")),
            dict(name="AspenClean Laundry Detergent, Unscented", tier="natural",
                 note=("Fragrance-free and dye-free with no borate, for a household that wants out of all three "
                       "rather than just the scent.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=1,
        exposure_src=SRC_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household figure "
                        "for CVS Total Home laundry products (CVS corporate site, IndexBox US laundry and home "
                        "products page, and a general web search) and found none. Category penetration times the "
                        "drugstore channel's small share of laundry sales times house-brand share inside that "
                        "channel; carried at the same figure as the Free & Clear record because the two are the "
                        "same product with two label variants."),
        tier_note=("CVS house brand; drugstore channel."),
        strength_disclosure="full",
        disclosure_note=None,
    ),
]

# --- citation repair: shell host -> the manufacturer's real API ------------
# GTIN -> (record name, locale). Repoint only where the API list matches the
# record's own list (checked in the finding). Cascade and Ivory are excluded:
# the first carries a five-line stub against a nineteen-line filing, the second
# is a Canadian SKU and needs locale=en-CA.
PG_API = ("https://az-na-smartlabel-prod-functionapp-api.pgcloud.com/"
          "api/getproductdetails?gtin={gtin}&locale={locale}")
REPOINT = [
    ("00037000248613", "en-US", "Downy Ultra Free & Gentle Liquid Fabric Conditioner"),
    ("00037000073123", "en-US", "Bounce Fabric Softener Sheets, Outdoor Fresh"),
    ("00037000930358", "en-US", "Tide PODS Laundry Detergent Pacs, Original Scent"),
    ("00037000523642", "en-US", "Dawn Powerwash Dish Spray, Fresh"),
    ("00037000485896", "en-US", "Microban 24 Hour Multi-Purpose Cleaner and Disinfectant Spray, Fresh Scent"),
    ("00037000969990", "en-US", "Febreze AIR Freshener, Fresh Sky"),
    ("00037000791294", "en-US", "Mr. Clean Clean Freak Deep Cleaning Mist, Lemon Zest"),
    ("00030772064726", "en-US", "Cascade Platinum Plus ActionPacs, Fresh"),
    ("00037000748113", "en-US", "Dreft Stage 1: Newborn Baby Liquid Laundry Detergent"),
    ("00030772087268", "en-US", "Downy Unstopables In-Wash Scent Booster Beads, Fresh"),
    ("00037000524083", "en-US", "Downy WrinkleGuard Wrinkle Releaser Fabric Spray, Fresh"),
    ("00037000751007", "en-CA", "Ivory Concentrated Dishwashing Liquid, Classic Scent"),
    # The GTIN 0982081 is shared by two records. This one carries the full
    # eighteen-line list and matches the filing; "Cascade" carries a five-line
    # stub and is deliberately left alone (see the finding).
    ("00037000982081", "en-US", "Cascade Complete ActionPacs"),
]

ALIASES = {
    "caustic soda": "Sodium Hydroxide",
    "polydimethylsiloxane": "Dimethicone",
    "amine oxide": "Alkyldimethylamine Oxide",
    "polyethyleneimine ethoxylate": "Polyethyleneimine Alkoxylated",
    "coconut acid": "Coconut Fatty Acid",
    "polyvinyl alcohol": "Polyvinyl Alcohol",
    "proprietary colorant": "Colorant",
    "liquitint blue hp": "Colorant",
}

MINT_NOTE = ("Minted {today} from a CVS-hosted California SB-258 ingredient disclosure and recorded ungraded. "
             "No PubChem or ECHA grade has been resolved for this entry yet, so g is null rather than a guess.")


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def repoint_citations(products):
    """Swap the smartlabel.pg.com shell-host citation for the P&G SmartLabel API URL."""
    changed = []
    for gtin, locale, name in REPOINT:
        url = PG_API.format(gtin=gtin, locale=locale)
        for p in products:
            if p.get("name") != name:
                continue
            for f in ("source_url", "tier_src", "exposure_src"):
                v = p.get(f)
                if isinstance(v, str) and "smartlabel.pg.com" in v:
                    p[f] = url
                    changed.append((name, f))
            cf = p.get("claim_conflict")
            if isinstance(cf, dict) and isinstance(cf.get("toxicology_src"), str) \
                    and "smartlabel.pg.com" in cf["toxicology_src"]:
                cf["toxicology_src"] = url
                changed.append((name, "claim_conflict.toxicology_src"))
            if isinstance(p.get("source"), str) and "smartlabel.pg.com" in p["source"]:
                p["source"] = re.sub(r"(https?://)?smartlabel\.pg\.com(/[^\s,;)]*)?", url, p["source"])
                changed.append((name, "source(prose)"))
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-changelog", action="store_true")
    args = ap.parse_args()

    prods_path = REPO / "data/products.json"
    ings_path = REPO / "data/ingredients.json"
    owners_path = REPO / "data/owners.json"
    products = json.loads(prods_path.read_text(encoding="utf-8"))
    ingredients = json.loads(ings_path.read_text(encoding="utf-8"))
    owners = json.loads(owners_path.read_text(encoding="utf-8"))

    existing_names = {p["name"] for p in products}
    exact = {k.lower(): k for k in ingredients}
    folded = {}
    for k in ingredients:
        folded.setdefault(norm(k), k)

    minted, aliased, skipped = [], [], []
    added_records = []

    for spec in PRODUCTS:
        if spec["name"] in existing_names:
            skipped.append(spec["name"])
            continue

        resolved = []
        for term in spec["ings"]:
            if term in ingredients:
                resolved.append(term)
                continue
            if term.lower() in ALIASES and ALIASES[term.lower()] in ingredients:
                key = ALIASES[term.lower()]
                aliased.append((term, key))
                resolved.append(key)
                continue
            if term.lower() in exact:
                key = exact[term.lower()]
                if key not in minted:  # minted earlier in this run, not an alias
                    aliased.append((term, key))
                resolved.append(key)
                continue
            if norm(term) in folded:
                key = folded[norm(term)]
                if key not in minted:  # minted earlier in this run, not an alias
                    aliased.append((term, key))
                resolved.append(key)
                continue
            if term not in minted:
                minted.append(term)
            if not args.dry_run:
                ingredients[term] = {
                    "ev": "Low", "g": None, "gr": {}, "impacts": [],
                    "note": MINT_NOTE.format(today=TODAY),
                    "s": f"{term}. Listed in the manufacturer disclosure; not yet graded against GHS.",
                    "added": TODAY,
                }
            exact[term.lower()] = term
            folded[norm(term)] = term
            resolved.append(term)

        assert len(resolved) == len(spec["ings"]), spec["name"]
        assert len(set(resolved)) == len(resolved), f"dup ingredient in {spec['name']}"
        for k in resolved:
            assert k in ingredients or args.dry_run, f"unresolved key {k}"

        rec = {
            "name": spec["name"],
            "brand": spec["brand"],
            "cat": spec["cat"],
            "safe": None,
            "ings": resolved,
            "heritage": False,
            "source": spec["source"],
            "source_url": spec["source_url"],
            "note": spec["note"],
            "owner": OWNER,
            "tier": "drugstore",
            "tier_ev": "reported",
            "tier_src": spec["tier_src"],
            "tier_note": spec["tier_note"],
            "substitutes": spec["substitutes"],
            "no_substitute_known": spec["no_substitute_known"],
            "no_substitute_note": spec["no_substitute_note"],
            "exposure": spec["exposure"],
            "exposure_ev": "extrapolated",
            "exposure_src": spec["exposure_src"],
            "exposure_basis": spec["exposure_basis"],
            "conc": None,
            "conc_src": None,
            "conc_ev": "untested",
            "grade_as_sold": None,
            "grade_as_sold_src": None,
            "strength_disclosure": spec["strength_disclosure"],
            "disclosure_note": spec["disclosure_note"],
            "added": TODAY,
        }
        added_records.append(rec)
        if not args.dry_run:
            products.append(rec)
            existing_names.add(rec["name"])

    # owner record: add the house-brand string so apply_owners() stamps it
    brand_added = False
    rec = owners["owners"].get(OWNER)
    assert rec, f"owner record missing: {OWNER}"
    if OWNER_BRAND_TO_ADD not in rec["brands"]:
        brand_added = True
        if not args.dry_run:
            rec["brands"].append(OWNER_BRAND_TO_ADD)

    changed = repoint_citations(products) if not args.dry_run else []

    print(f"products added: {len(added_records)}  skipped(existing): {len(skipped)}")
    for r in added_records:
        print(f"   + {r['name']}  ({len(r['ings'])} ingredients)")
    print(f"ingredient keys minted: {len(minted)} -> {minted}")
    print(f"ingredient keys aliased: {len(aliased)}")
    for a, b in aliased:
        print(f"   {a!r} -> {b!r}")
    print(f"owner brand string added: {brand_added} ({OWNER_BRAND_TO_ADD!r})")
    print(f"citations repointed: {len(changed)}")
    for n, f in changed:
        print(f"   {f}: {n}")

    if args.dry_run:
        print("dry run: no files written")
        return

    def dump(path, obj, indent, trailing_newline):
        text = json.dumps(obj, ensure_ascii=False, indent=indent)
        if trailing_newline:
            text += "\n"
        path.write_text(text, encoding="utf-8")

    # measured 2026-10-09: products/ingredients/owners are indent=1 with no
    # trailing newline; changelog.json is indent=2 with no trailing newline.
    dump(prods_path, products, 1, False)
    dump(ings_path, ingredients, 1, False)
    dump(owners_path, owners, 1, False)

    if not args.no_changelog and (added_records or changed):
        cl = json.loads((REPO / "data/changelog.json").read_text(encoding="utf-8"))
        if not cl or cl[0].get("date") != TODAY:
            cl.insert(0, {
                "date": TODAY,
                "text": (f"Spectrum harvest station 2 (Dolman {TODAY}): {len(added_records)} Total Home (CVS) "
                         "house-brand cleaners added to the drugstore tier, every list read from the "
                         "manufacturer's California SB-258 declaration served on es.cvs.com. "
                         f"{len(minted)} new ingredient keys minted, all ungraded. Also repointed the records that "
                         "cited the smartlabel.pg.com shell host onto the keyless P&G SmartLabel API URL, which "
                         "serves the same manufacturer's real disclosure; the two records whose own lists do not "
                         "match the filing were left alone."),
            })
            dump(REPO / "data/changelog.json", cl, 2, False)


if __name__ == "__main__":
    main()
