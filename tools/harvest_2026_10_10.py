#!/usr/bin/env python3
"""Spectrum harvest, night-shift station 2, 2026-10-10.

HARVEST -- five missing high-exposure products, each read from the
manufacturer's own ingredient declaration.

Route: the Spanish-locale CVS host (`es.cvs.com`) serves the manufacturer's
California Cleaning Product Right to Know Act (SB-258) declaration (or, for an
EPA-registered product, the label's active + inactive composition) in a JSON
field named `vendorIngredientsParagraph`. `www.cvs.com` 403s the same path; the
prodid alone resolves, so a junk slug plus a valid prodid 301s to the canonical
page. This fire uses the same route the 2026-10-09 station-2 fire opened, but
against NAME-BRAND products rather than the CVS house brand -- the route carries
the manufacturer's paragraph for any product CVS lists, not only its own label.

Why these five: the spectrum data build is complete across all four channel
tiers, and the CVS shelf's remaining house-brand cleaners publish only coarse
active-only lines (held out, see the finding). What is genuinely missing is a
handful of NAME-BRAND products that carry a full declaration: an in-tank toilet
tablet, a foaming glass cleaner, a granite cleaner, a viral bathroom foam and a
bleach mold remover. Each is a product a household actually buys, every list is
the manufacturer's own, and no list is a class-name or active-only stub.

Idempotent: a product already present by name is skipped, an ingredient key that
already exists (case-insensitively, or through the alias map) is never re-minted,
and the owner record is only extended if the brand string is absent.

Usage:
  python3 tools/harvest_2026_10_10.py [--dry-run] [--no-changelog]
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TODAY = "2026-10-10"

SRC_SURFACE = ("https://www.indexbox.io/store/united-states-household-surface-cleaners-"
               "market-analysis-forecast-size-trends-and-insights/")
SRC_TOILET = ("https://www.indexbox.io/store/united-states-toilet-cleaning-products-"
              "market-analysis-forecast-size-trends-and-insights/")
SRC_KITCHEN = ("https://www.indexbox.io/store/united-states-kitchen-cleaners-"
               "market-analysis-forecast-size-trends-and-insights/")

CVS = "https://es.cvs.com/shop/ingredients/"

# --- the new owner record ------------------------------------------------
# Ty-D-Bol is owned by Willert Home Products (St. Louis, MO), which acquired the
# brand in 2010 and states the family of brands on its own site. Company's own
# published corporate page read directly -> `verified` per the ownership rule.
NEW_OWNER_NAME = "Willert Home Products"
NEW_OWNER = {
    "type": "private company",
    "detail": "Family-owned household-products manufacturer, St. Louis, MO, founded 1946. Its own "
              "site names the brand family Ty-D-Bol, Bowl Fresh, Enoz and airBOSS.",
    "ev": "verified",
    "src": "https://tydbol.com/about/",
    "brands": ["Ty-D-Bol"],
}

PRODUCTS = [
    dict(
        name="Ty-D-Bol Toilet Bowl Cleaner Tablets, Lavender",
        brand="Ty-D-Bol", cat="Bathroom",
        source_url=CVS + "ty-d-bol-toilet-bowl-cleaner-tablets-lavender-3-ct-prodid-823262",
        tier="mass", tier_src="https://tydbol.com/about/",
        tier_note=("National brand; the manufacturer's own site states it is sold at home improvement stores, "
                   "discount stores, drug stores, hardware stores and grocery stores, so the tier is the broad "
                   "mass channel rather than any one shelf."),
        source=("Manufacturer ingredient declaration for Ty-D-Bol Toilet Bowl Cleaner Tablets (Lavender), read "
                "from the served page on the CVS Spanish-locale host es.cvs.com in the "
                "`vendorIngredientsParagraph` field. This is the manufacturer's California Cleaning Product "
                "Right to Know Act (SB-258) declaration published by the retailer that lists the product. "
                "Sixteen intentionally added lines, all named; the violet dye is declared only by its colour "
                "name and the surfactant is declared by its CAS chemical name. Read today from the served page."),
        note=("The in-tank toilet tablet, and the useful part is the borate. The formula is an effervescent "
              "tablet: sodium sulfate and sodium borate as the bulk, a linear alkylbenzene sulfonate surfactant, "
              "cellulose gum and hydroxyethylcellulose as binders, sodium chloride and sodium ferrocyanide, a "
              "trideceth-3 wetter, aluminum sulfate and a tetrasodium EDTA chelator, with citric acid and PEG. "
              "Sodium borate is the line to read twice, and it is why this record carries a substitute: borate "
              "is the reason some households avoid this whole product class, and the declaration puts it second "
              "on the list rather than hiding it. The label names the surfactant by its CAS name rather than a "
              "brand word, so it maps to the registry's alkylbenzenesulfonate key instead of a trade name."),
        ings=["Sodium Sulfate", "Sodium Borate", "Sodium (C10-16) Alkylbenzenesulfonate", "Cellulose Gum",
              "Hydroxyethylcellulose", "Sodium Chloride", "Sodium Ferrocyanide", "Water", "Colorant",
              "Trideceth-3", "Aluminum Sulfate", "Tetrasodium EDTA", "Citric Acid", "PEG"],
        substitutes=[
            dict(name="Seventh Generation Toilet Bowl Cleaner, Emerald Cypress & Fir", tier="mass",
                 note=("Same aisle, comparable price, and no borate at all, which is the line this record is "
                       "substituted for. It carries EWG top-rated and EPA Safer Choice.")),
            dict(name="Ecover Toilet Bowl Cleaner Pine Fresh", tier="mass",
                 note=("Borax-free toilet cleaner at a grocery price; EPA Safer Choice and EWG top-rated, so it "
                       "is the same-price answer for a household avoiding the tablet's sodium borate.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=3, exposure_src=SRC_TOILET,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household figure "
                        "for Ty-D-Bol tablets (the brand site, the CVS listing, and a general web search) and "
                        "found none. IndexBox's US toilet-cleaning page states residential households are "
                        "roughly 55-60% of category volume across about 130 million households, so toilet "
                        "cleaners are near-universal, but in-tank tablets are one format inside that category "
                        "and a fraction of households use them. The estimate stops at category penetration times "
                        "the tablet format's small share, because nothing more specific is published."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Windex Fast Shine Foaming Glass Cleaner Spray, Rain Shower",
        brand="Windex", cat="Glass",
        source_url=CVS + "windex-fast-shine-foaming-glass-cleaner-spray-rainshower-19-oz-prodid-648414",
        tier="mass", tier_src="https://windex.com/en-us",
        tier_note=("National brand; SC Johnson's own Windex site positions it as America's top-selling glass "
                   "cleaner, so the tier is the broad mass channel."),
        source=("Manufacturer ingredient declaration for Windex Fast Shine Foaming Glass Cleaner Spray (Rain "
                "Shower), read from the served page on the CVS Spanish-locale host es.cvs.com in the "
                "`vendorIngredientsParagraph` field. The paragraph carries the label's active ingredient and the "
                "inactive composition, which is the manufacturer's California SB-258 publication as served by "
                "the retailer. Read today from the served page."),
        note=("An aerosol foaming glass cleaner, and it is a different animal from the plain Windex spray. The "
              "label's active ingredient is given only as the supplier trade name 'Ammonia-D', which is a "
              "solution of ammonium hydroxide, so this record maps it to the registry's ammonium hydroxide key "
              "and does not pretend the trade name is a separate substance. Behind the propellant (isobutane and "
              "propane) the working ingredients are propylene glycol butyl ether and hexoxyethanol as solvents, "
              "an alkyl sec sulfonate and two glucoside surfactants, a tetrasodium iminodisuccinate chelator, and "
              "a fragrance line with no named allergens. The one allergen-free note worth making: the "
              "manufacturer declares the fragrance only as 'Fragrances' here, so a reader sensitive to fragrance "
              "gets a class word rather than a list."),
        ings=["Water", "Isobutane", "Propylene Glycol Butyl Ether", "Propane", "Hexoxyethanol",
              "Ammonium Hydroxide", "Sodium C14-17 Alkyl Sec Sulfonate", "Tetrasodium Iminodisuccinate",
              "Decyl Glucoside", "Lauryl Glucoside", "Fragrance"],
        substitutes=[
            dict(name="up&up Glass Cleaner Spray, Unscented", tier="grocery",
                 note=("Same aisle, store-brand price, and it declares itself unscented, so it drops the "
                       "fragrance line this record carries.")),
            dict(name="Whole Foods Glass Cleaner, Unscented", tier="grocery",
                 note=("Fragrance-free glass cleaner that carries EWG top-rated; the substitute is for the "
                       "fragrance and the aerosol propellants here, not for the cleaning job.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=2, exposure_src=SRC_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household figure "
                        "for Windex Fast Shine (the brand site, the CVS listing, and a general web search) and "
                        "found none. The corpus carries Windex Original at 15 on the strength of the brand being "
                        "category-defining; this is one foaming SKU inside that brand, so the estimate is the "
                        "brand figure times the single-SKU fraction. The estimate stops there because no "
                        "per-SKU penetration figure is published."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Method Daily Granite Cleaner, Apple Orchard",
        brand="Method", cat="Wood & Stone Care",
        source_url=CVS + "method-daily-granite-cleaner-spray-apple-orchard-28-fl-oz-prodid-2450135",
        tier="mass", tier_src=CVS + "method-daily-granite-cleaner-spray-apple-orchard-28-fl-oz-prodid-2450135",
        tier_note=("Method is a national brand sold through grocery, drugstore and mass channels; the corpus "
                   "files Method under the mass tier, and this record follows that convention. The tile is "
                   "declared by the retailer that lists it, not by a single-shelf claim."),
        source=("Manufacturer ingredient declaration for Method Daily Granite Cleaner (Apple Orchard), read from "
                "the served page on the CVS Spanish-locale host es.cvs.com in the `vendorIngredientsParagraph` "
                "field. This is the manufacturer's California SB-258 publication as served by the retailer. "
                "Seven substances, each named. Read today from the served page."),
        note=("A stone-counter cleaner, and it fills a real hole: the corpus had only a handful of "
              "surfaces-for-stone products and no Method one. The formula is short and mostly benign: water and "
              "denatured alcohol as the base, a capryleth-4 surfactant, sodium citrate as the builder and "
              "fragrance. The two lines that matter are the preservatives, methylisothiazolinone and "
              "octylisothiazolinone. That pair is the allergen pair people react to in water-based cleaners, and "
              "it is declared here rather than hidden, which is why this record carries a substitute. The label "
              "gives no colourant and no dye, so stone stays stone."),
        ings=["Water", "Alcohol Denat.", "Capryleth-4", "Sodium Citrate", "Fragrance",
              "Methylisothiazolinone", "Octylisothiazolinone"],
        substitutes=[
            dict(name="Granite Gold Daily Cleaner", tier="mass",
                 note=("Purpose-built stone cleaner at a comparable price that does not carry the "
                       "isothiazolinone preservative pair; the substitute is for that pair and the fragrance "
                       "line, not for the stone safety.")),
            dict(name="Ever Spring Granite & Stone Cleaner (BMVC)", tier="grocery",
                 note=("The stone cleaner already in the corpus, kept for comparison: it is the same job "
                       "without the declared fragrance or the isothiazolinones.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=2, exposure_src=SRC_KITCHEN,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household figure "
                        "for Method Daily Granite (the brand site, the CVS listing, the IndexBox kitchen-cleaners "
                        "page, and a general web search) and found none. The estimate is the share of US homes "
                        "with sealed stone countertops times the small share of those who buy a dedicated stone "
                        "cleaner rather than using an all-purpose spray, times Method's share of that niche. "
                        "Rounded to one significant figure because nothing more specific is published."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="The Pink Stuff Miracle Bathroom Foam Cleaner",
        brand="The Pink Stuff", cat="Bathroom",
        source_url=CVS + "the-pink-stuff-miracle-bathroom-foam-cleaner-25-4-oz-prodid-477392",
        tier="mass",
        tier_src=CVS + "the-pink-stuff-miracle-bathroom-foam-cleaner-25-4-oz-prodid-477392",
        tier_note=("National brand sold through mass and drugstore channels; the corpus files The Pink Stuff "
                   "under the mass tier, and this record follows that convention. The tile records where the "
                   "declaration was read, not a single-shelf claim."),
        source=("Manufacturer ingredient declaration for The Pink Stuff Miracle Bathroom Foam Cleaner, read from "
                "the served page on the CVS Spanish-locale host es.cvs.com in the `vendorIngredientsParagraph` "
                "field. The paragraph carries the active ingredients and the inactive composition, which is the "
                "manufacturer's California SB-258 publication as served by the retailer. Read today from the "
                "served page."),
        note=("The bathroom foam from the brand that went viral, and it is a genuine bathroom cleaner rather "
              "than a paste in a spray bottle. Behind water and citric acid it is a surfactant-and-quat spray: "
              "two C9-11 pareth surfactants, a cocamine oxide booster, propylene glycol butyl ether as solvent, "
              "a tetrasodium GLDA chelator, benzalkonium chloride as the antimicrobial, a fragrance and Acid Red "
              "52 for the colour. The benzalkonium chloride is the line to read, and it is why this record "
              "carries a substitute: a quaternary ammonium is a respiratory and skin irritant at use strength, "
              "and it is declared here rather than left as 'disinfectant'."),
        ings=["Water", "Citric Acid", "C9-11 Pareth-8", "C9-11 Pareth-6", "Cocamine Oxide",
              "Propylene Glycol Butyl Ether", "Tetrasodium Glutamate Diacetate", "Benzalkonium Chloride",
              "Fragrance", "Acid Red 52"],
        substitutes=[
            dict(name="ATTITUDE Bathroom Cleaner Spray, Unscented", tier="natural",
                 note=("Quat-free and fragrance-free bathroom spray that carries EWG Verified; the substitute "
                       "drops the benzalkonium chloride, the fragrance and the dye this record declares.")),
            dict(name="Green Shield Organic Bathroom Cleaner, Fresh", tier="natural",
                 note=("Plant-based bathroom cleaner at a comparable price without the quaternary ammonium "
                       "active, which is the specific line being substituted.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=2, exposure_src=SRC_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household figure "
                        "for The Pink Stuff (the brand site, the CVS listing, and a general web search) and found "
                        "none. The brand is a viral import with a growing but still minority US share, and this "
                        "is one SKU inside it, so the estimate is category penetration for bathroom cleaners "
                        "times the brand's small share times the single-SKU fraction. The corpus carries the "
                        "companion paste at 2; this foam is carried at the same figure."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Lysol Mold & Mildew Remover Spray with Bleach",
        brand="Lysol", cat="Disinfectant",
        source_url=CVS + "lysol-mold-mildew-remover-spray-with-bleach-32-fl-oz-prodid-525309",
        tier="mass", tier_src="https://www.rbnainfo.com/brands.php",
        tier_note=("Lysol is a Reckitt brand; Reckitt's own ingredient site lists Lysol among its retained "
                   "brands, and the product is sold through grocery, drugstore and mass channels, so the tier is "
                   "the broad mass channel."),
        source=("Manufacturer ingredient declaration for Lysol Mold & Mildew Remover Spray with Bleach, read "
                "from the served page on the CVS Spanish-locale host es.cvs.com in the "
                "`vendorIngredientsParagraph` field. The paragraph carries the label's active ingredient and the "
                "inactive composition, which is the manufacturer's California SB-258 publication as served by "
                "the retailer. Read today from the served page."),
        note=("A bleach mold-and-mildew spray, and the list is short and honest. Sodium hypochlorite is the "
              "active, and the inactive side is only water, sodium chloride, a lauramine oxide surfactant and "
              "sodium hydroxide. Five lines total, no fragrance line and no dye, which is unusual for a "
              "bathroom spray and worth saying plainly. The hazard is the bleach itself: a hypochlorite at this "
              "strength is corrosive to skin and eyes and dangerous to mix with ammonia or acid cleaners, and "
              "that is the whole reason this record carries a non-bleach substitute rather than a different "
              "brand of bleach."),
        ings=["Sodium Hypochlorite", "Water", "Sodium Chloride", "Lauramine Oxide", "Sodium Hydroxide"],
        substitutes=[
            dict(name="Seventh Generation Tub & Tile Cleaner, Emerald Cypress & Fir", tier="mass",
                 note=("Non-bleach tub and tile cleaner at a comparable price that carries EWG top-rated; the "
                       "substitute avoids the sodium hypochlorite this record is built on.")),
            dict(name="ATTITUDE Daily Shower & Tile Cleaner, Citrus Zest", tier="natural",
                 note=("Fragrance-declared, bleach-free shower and tile cleaner, EWG Verified, for a household "
                       "that wants the mildew job without hypochlorite.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=4, exposure_src=SRC_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household figure "
                        "for Lysol Mold & Mildew with Bleach (the Reckitt ingredient site, the CVS listing, and a "
                        "general web search) and found none. Bleach-based bathroom sprays are a common household "
                        "staple and Lysol is a lead brand in the category; the estimate is category penetration "
                        "for bathroom cleaners times the share using a bleach mold product times the brand's "
                        "share. Rounded to one significant figure because nothing more specific is published."),
        strength_disclosure="full", disclosure_note=None,
    ),
]

ALIASES = {
    "violet dye": "Colorant",
    "ammonia-d": "Ammonium Hydroxide",
}

MINT_NOTE = ("Minted {today} from a retailer-served manufacturer California SB-258 ingredient declaration and "
             "recorded ungraded. No PubChem or ECHA grade has been resolved for this entry yet, so g is null "
             "rather than a guess.")


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


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
                if key not in minted:
                    aliased.append((term, key))
                resolved.append(key)
                continue
            if norm(term) in folded:
                key = folded[norm(term)]
                if key not in minted:
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
            "owner": None,  # stamped by apply_owners() from the owner record
            "tier": spec["tier"],
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

    # new owner record
    owner_added = False
    if NEW_OWNER_NAME not in owners["owners"]:
        owner_added = True
        if not args.dry_run:
            owners["owners"][NEW_OWNER_NAME] = NEW_OWNER

    print(f"products added: {len(added_records)}  skipped(existing): {len(skipped)}")
    for r in added_records:
        print(f"   + {r['name']}  ({len(r['ings'])} ingredients)")
    print(f"ingredient keys minted: {len(minted)} -> {minted}")
    print(f"ingredient keys aliased: {len(aliased)}")
    for a, b in aliased:
        print(f"   {a!r} -> {b!r}")
    print(f"owner record added: {owner_added} ({NEW_OWNER_NAME!r})")

    if args.dry_run:
        print("dry run: no files written")
        return

    def dump(path, obj, indent, trailing_newline):
        text = json.dumps(obj, ensure_ascii=False, indent=indent)
        if trailing_newline:
            text += "\n"
        path.write_text(text, encoding="utf-8")

    # measured 2026-10-10 at upstream HEAD: products.json ends `]` with no
    # trailing newline; owners.json ends `}` with no trailing newline;
    # changelog.json is indent=2 and ends `]` with no trailing newline;
    # ingredients.json ends `}` WITH a trailing newline (changed upstream in the
    # 2026-10-10 ingest commit, which is why this run matches the newline rather
    # than assuming the earlier no-newline reading still held).
    dump(prods_path, products, 1, False)
    dump(ings_path, ingredients, 1, True)
    dump(owners_path, owners, 1, False)

    if not args.no_changelog and (added_records or owner_added):
        cl = json.loads((REPO / "data/changelog.json").read_text(encoding="utf-8"))
        if not cl or cl[0].get("date") != TODAY:
            cl.insert(0, {
                "date": TODAY,
                "text": (f"Spectrum harvest station 2 (Dolman {TODAY}): {len(added_records)} missing high-exposure "
                         "name-brand products added, every list read from the manufacturer's own California SB-258 "
                         "declaration served on es.cvs.com -- an in-tank toilet tablet, a foaming glass cleaner, a "
                         "granite cleaner, a viral bathroom foam and a bleach mold remover. "
                         f"{len(minted)} new ingredient keys minted, all ungraded. New owner record: "
                         f"{NEW_OWNER_NAME} (Ty-D-Bol)."),
            })
            dump(REPO / "data/changelog.json", cl, 2, False)


if __name__ == "__main__":
    main()
