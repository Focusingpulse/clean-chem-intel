#!/usr/bin/env python3
"""Spectrum harvest, night-shift station 2, 2026-10-07.

Tier worked: the mass-market Essential Home (Vestacy) household shelf, ordered by
exposure. Every ingredient list is read from the manufacturer's own California
Cleaning Product Right to Know Act disclosure served at vestacyinfo.com, which is
the manufacturer's published specification and therefore `verified` under
docs/certainty.md.

Route: https://www.vestacyinfo.com/product.php?productLineId=<id>
       (product pages enumerated from https://www.vestacyinfo.com/brand.php?brandId=<n>)

Idempotent: a product already present by name is skipped, and an ingredient key
that already exists (case-insensitively) is never re-minted.

Usage:
  python3 tools/harvest_2026_10_07.py [--dry-run] [--no-changelog]
"""
import argparse
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
TODAY = "2026-10-07"
OWNER = "Essential Home (Advent International)"
OWNER_SRC = "https://www.reckitt.com/news/reckitt-completes-divestment-of-essential-home/"

# --- exposure sources ------------------------------------------------------
SRC_LAUNDRY = ("https://www.indexbox.io/store/united-states-laundry-home-products-"
               "market-analysis-forecast-size-trends-and-insights/")
SRC_FLOOR = ("https://www.indexbox.io/store/united-states-kw-floor-cleaning-solution-840-"
             "market-analysis-forecast-size-trends-and-insights/")
SRC_CARPET = ("https://www.indexbox.io/store/united-states-carpet-cleaning-products-"
              "market-analysis-forecast-size-trends-and-insights/")
SRC_KITCHEN = ("https://www.indexbox.io/store/united-states-kitchen-cleaners-"
               "market-analysis-forecast-size-trends-and-insights/")
SRC_SURFACE = ("https://www.indexbox.io/store/united-states-household-surface-cleaners-"
               "market-analysis-forecast-size-trends-and-insights/")

# --- products --------------------------------------------------------------
# name, brand, cat, productLineId, exposure, exposure_src, exposure_basis, note,
# substitutes, no_substitute_known, no_substitute_note
PRODUCTS = [
    dict(
        pid="3065", name="Woolite Damage Defense Laundry Detergent", brand="Woolite",
        cat="Laundry", exposure=2, exposure_src=SRC_LAUNDRY,
        exposure_basis=(
            "The cited laundry & home products page states household penetration above 98 percent "
            "for the category. Woolite is a delicates and washable-wool specialist inside that "
            "category, not a mainstream volume brand. Searched for a published US household-"
            "penetration figure for Woolite by name and located none; brand-level shares are sold "
            "in syndicated data rather than published. The estimate therefore derives from the "
            "category figure and Woolite's position as a small specialist brand inside it, and "
            "stops there rather than naming a share that was not read. Rounded to one significant "
            "figure, order of magnitude."),
        note=(
            "A liquid detergent built for the delicates wash, and the ingredient list is a "
            "mainstream surfactant base plus a fragrance. Two fragrance allergens are declared "
            "(butylphenyl methylpropional, eugenol) plus isoeugenol and hexyl salicylate. "
            "Butylphenyl methylpropional is the notable one: it is restricted in the EU cosmetics "
            "regulation on reproductive-toxicity grounds, and it is declared here on the label "
            "rather than hidden behind the word 'fragrance'. The 'Damage Defense' name refers to "
            "the wash, not to the chemistry."),
        substitutes=[
            dict(name="Woolite Darks Defense Laundry Detergent", tier="mass",
                 note="Same brand, same price band, same surfactant base. It adds a dye-transfer "
                      "inhibitor and does not remove the fragrance allergens, so it is a "
                      "same-shelf alternative rather than a lower-hazard one."),
        ],
    ),
    dict(
        pid="3064", name="Woolite Darks Defense Laundry Detergent", brand="Woolite",
        cat="Laundry", exposure=2, exposure_src=SRC_LAUNDRY,
        exposure_basis=(
            "Same derivation as the Woolite Damage Defense record: category penetration above "
            "98 percent from the cited laundry & home page, no published Woolite-specific US "
            "household figure located, estimate stops at the brand's small-specialist position. "
            "Rounded to one significant figure."),
        note=(
            "The darks variant. Same surfactant base as the other Woolite liquids, plus polyvinyl "
            "pyridine-N-oxide as the dye-transfer inhibitor and a CI 61585 colourant. Four "
            "fragrance allergens are declared. The dye-transfer chemistry is the difference; the "
            "hazard profile is not meaningfully different from the plain Delicates product."),
        substitutes=[
            dict(name="Woolite Delicates Laundry Detergent", tier="mass",
                 note="Same brand and price band. It gives up the dye-transfer inhibitor, which is "
                      "the reason to buy this one, so it is only a substitute for a load that is "
                      "not colour-fragile."),
        ],
    ),
    dict(
        pid="2251", name="Woolite Clean & Care Pacs", brand="Woolite",
        cat="Laundry", exposure=2, exposure_src=SRC_LAUNDRY,
        exposure_basis=(
            "Same derivation as the other Woolite records: category penetration above 98 percent "
            "from the cited laundry & home page, no published Woolite-specific US household "
            "figure located. Unit-dose pacs are the fastest-growing detergent form, but that is a "
            "format statement rather than a penetration figure, so the estimate stays at the "
            "brand position and is rounded to one significant figure."),
        note=(
            "A unit-dose pac, and the reason to read it is the film and the fragrance, not the "
            "surfactants. The PVA film is the same class as every other pod on the shelf; the "
            "fragrance declares sixteen named components rather than the word 'fragrance' alone, "
            "including three EU-declarable allergens. Dosing is fixed by the pac, which is a real "
            "advantage over a liquid, and it is also why an over-dose is not possible to notice."),
        substitutes=[
            dict(name="Woolite Delicates Laundry Detergent", tier="mass",
                 note="Same brand, same shelf, similar price per wash. It is a liquid rather than a "
                      "pac, so the dose is chosen rather than fixed, and it carries a shorter "
                      "declared fragrance list."),
        ],
    ),
    dict(
        pid="2718", name="Botanical Origin Plant-Based Laundry Detergent, Fresh Jasmine and Wild Lavender",
        brand="Botanical Origin", cat="Laundry", exposure=1, exposure_src=SRC_LAUNDRY,
        exposure_basis=(
            "The cited laundry & home page states category household penetration above 98 percent. "
            "Botanical Origin is a plant-based line launched under the Essential Home portfolio; "
            "no published US household-penetration or brand-share figure for it was located in the "
            "sources searched. The estimate is therefore a floor for a newly launched niche line "
            "inside a near-universal category, rounded to one significant figure."),
        note=(
            "'Plant-based' describes the surfactant feedstock and is true; it is not a statement "
            "about hazard. The list is an alcohol-ethoxylate and sodium-laureth-sulfate base with "
            "four enzymes and a declared fragrance of nine components. The enzymes are the "
            "respiratory-sensitisation class that matters in a laundry product, and they are "
            "declared here by name. Compare with the conventional Woolite liquids on the same "
            "shelf: fewer fragrance allergens, more enzymes."),
        substitutes=[
            dict(name="Woolite Delicates Laundry Detergent", tier="mass",
                 note="Same shelf, similar price. It is the conventional alternative, and reading "
                      "both lists side by side is the point: neither is hazard-free, they differ "
                      "in which class of ingredient is present."),
        ],
    ),
    dict(
        pid="2719", name="Botanical Origin Plant-Based Fabric Conditioner, Fresh Jasmine and Wild Lavender",
        brand="Botanical Origin", cat="Laundry", exposure=1, exposure_src=SRC_LAUNDRY,
        exposure_basis=(
            "Same derivation as the Botanical Origin detergent record: category penetration above "
            "98 percent from the cited laundry & home page; the brand is a new niche line with no "
            "published US household-penetration figure located. Rounded to one significant figure."),
        note=(
            "A fabric conditioner, which is the category where the chemistry is most often left "
            "off the label. This one declares a fourteen-component fragrance by name plus a "
            "quaternary conditioner active and a silicone. Fabric conditioners work by depositing "
            "a cationic layer on the fibre, which is also why they leave a residue in the machine; "
            "that is a maintenance fact, not a hazard finding, and it belongs in the same entry as "
            "the ingredient list."),
        substitutes=[
            dict(name="Woolite Delicates Laundry Detergent", tier="mass",
                 note="Not a like-for-like: this removes the conditioner step rather than replacing "
                      "the product. Listed because the honest same-price alternative for someone "
                      "who wants softer fabric without a conditioner is to skip the step."),
        ],
    ),
    dict(
        pid="2998", name="Mop & Glo Multi-Surface Floor Cleaner", brand="Mop & Glo",
        cat="Floor & Carpet", exposure=6, exposure_src=SRC_FLOOR,
        exposure_basis=(
            "The cited floor cleaning solution page states residential households consume roughly "
            "70 to 75 percent of category volume, and that all-purpose floor cleaners are the "
            "largest volume segment at 42 to 50 percent of the category. Mop & Glo is a "
            "long-established national brand inside that segment. Searched for a published "
            "Mop & Glo-specific US household-penetration figure and located none. The estimate "
            "derives from the category volume figure and the brand's position as one national "
            "brand among several, and stops there. Rounded to one significant figure."),
        note=(
            "A clean-and-shine floor cleaner: a surfactant and solvent base plus an acrylic "
            "polymer and a rosin resin that dry to the shine. The shine is a coating, so the "
            "product leaves a film by design, and the film is the thing that builds up over "
            "repeated use. No fragrance allergen is declared individually, but a fragrance is "
            "present. The professional 64 oz SKU (productLineId 3225) discloses an identical "
            "ingredient list."),
        substitutes=[
            dict(name="Bona Pro Series Hardwood Floor Cleaner", tier="mass",
                 note="Same shelf and comparable price band. It is a cleaner without the "
                      "film-forming acrylic and rosin, so it cleans without leaving a shine "
                      "coating to build up. It gives up the shine."),
        ],
    ),
    dict(
        pid="2704", name="Easy-Off Fume Free Oven Cleaner Aerosol, Lemon Scent", brand="Easy-Off",
        cat="Specialty", exposure=5, exposure_src=SRC_KITCHEN,
        exposure_basis=(
            "The cited kitchen cleaners page states specialty cleaners (oven, grill and heavy-duty "
            "grease removers) are 12 to 15 percent of the category, and that end use is roughly 70 "
            "to 75 percent household. Easy-Off is the leading oven-cleaner brand inside that "
            "specialty segment. Searched for a published Easy-Off-specific US household-penetration "
            "figure and located none. The estimate derives from the segment share inside the "
            "kitchen cleaners category and the brand's leading position in it, and stops there. "
            "Rounded to one significant figure."),
        note=(
            "This is the cold, low-odour oven cleaner, and the mechanism is worth stating plainly: "
            "it is a caustic foam. Potassium carbonate and ethanolamine do the work, with sodium "
            "lauroyl sarcosinate as the surfactant that holds the foam on a vertical oven wall. "
            "The word 'fume free' means the amine odour has been reduced, not that the chemistry "
            "is milder. Gloves and ventilation are the label's own instructions. The distinct "
            "product from the same brand, the Heavy Duty Oven Cleaner, is the sodium-hydroxide "
            "aerosol already in this database."),
        substitutes=[
            dict(name="Easy-Off Heavy Duty Oven Cleaner", tier="mass",
                 note="Same brand, same price band, and the honest comparison: the Heavy Duty "
                      "version is a sodium hydroxide aerosol. There is no low-hazard oven cleaner "
                      "at this price; the work is caustic or it is scrubbing."),
        ],
    ),
    dict(
        pid="513", name="Resolve Carpet & Rug Spot & Stain Remover", brand="Resolve",
        cat="Floor & Carpet", exposure=6, exposure_src=SRC_CARPET,
        exposure_basis=(
            "The cited carpet cleaning products page states residential cleaning, including DIY "
            "spot and stain removers, accounts for an estimated 35 to 40 percent of total product "
            "volume, with consumers favouring spot and stain removers. Resolve is the leading "
            "retail carpet-care brand inside that segment. Searched for a published "
            "Resolve-specific US household-penetration figure and located none. The estimate "
            "derives from the residential share of the category and the brand's position in it, "
            "and stops there. Rounded to one significant figure."),
        note=(
            "The oxidising spot remover: hydrogen peroxide is the active, and it is declared at "
            "the top of the list rather than buried. Peroxide is the reason this product works on "
            "a stain that a surfactant alone will not lift, and it is also why the label says to "
            "test on a hidden area: it can bleach a colour. The surfactant is sodium lauryl "
            "sulfate. Declared fragrance is short, four components."),
        substitutes=[
            dict(name="Folex Instant Carpet Spot Remover", tier="mass",
                 note="Same shelf, comparable price. Folex is a surfactant-and-solvent spot "
                      "remover without the peroxide, so it does not carry the bleaching risk. "
                      "It gives up the oxidising action that lifts a set stain."),
        ],
    ),
    dict(
        pid="832", name="Resolve Pet Expert Stain & Odor Remover Trigger", brand="Resolve",
        cat="Stain & Odor", exposure=4, exposure_src=SRC_CARPET,
        exposure_basis=(
            "Same category derivation as the other Resolve record: the cited carpet cleaning "
            "products page puts residential spot and stain removers at 35 to 40 percent of total "
            "product volume. The pet sub-segment is a fraction of that and no published "
            "pet-specific penetration figure was located. The estimate is set lower than the "
            "general spot remover on that basis and rounded to one significant figure."),
        note=(
            "The pet-stain version, and the list is close to the general spot remover: the same "
            "peroxide active and the same surfactant, with a longer declared fragrance that "
            "includes limonene and isoeugenol. Nothing on the label establishes the odour "
            "mechanism beyond the fragrance, and an odour remover is a product where the label "
            "wording and the chemistry should be read side by side."),
        substitutes=[
            dict(name="Folex Instant Carpet Spot Remover", tier="mass",
                 note="Same shelf, comparable price, no peroxide and a shorter fragrance list. "
                      "It gives up the oxidising action on a set pet stain."),
        ],
    ),
    dict(
        pid="1644", name="Spray 'n Wash Max Laundry Stain Remover", brand="Spray 'n Wash",
        cat="Stain & Odor", exposure=4, exposure_src=SRC_LAUNDRY,
        exposure_basis=(
            "The cited laundry & home page states category household penetration above 98 percent. "
            "Spray 'n Wash is a laundry pre-treatment brand inside that category; pre-treatment is "
            "a step most but not all households take, and no published Spray 'n Wash-specific US "
            "household figure was located. The estimate derives from the category penetration and "
            "the brand's position as one of several pre-treatment brands, and stops there. Rounded "
            "to one significant figure."),
        note=(
            "A peroxide laundry pre-treatment. The list is short and legible: two alcohol "
            "ethoxylates, an alkylbenzenesulfonic acid, peroxide, and a declared fragrance. It is "
            "a genuinely different product from the Spray 'n Wash Laundry Stain Remover already in "
            "this database, which is an enzyme-based formula; the Max is the oxidising one. Read "
            "the two side by side and the choice between them is legible."),
        substitutes=[
            dict(name="Spray 'n Wash Laundry Stain Remover", tier="mass",
                 note="Same brand, same price band. It is the enzyme-based formula rather than the "
                      "peroxide one, so it works on protein and food soils where the oxidiser "
                      "works on colour and tannin. Which is better depends on the stain."),
        ],
    ),
    dict(
        pid="439", name="Old English Furniture Polish Aerosol, Fresh Lemon", brand="Old English",
        cat="Wood & Stone Care", exposure=4, exposure_src=SRC_SURFACE,
        exposure_basis=(
            "The cited household surface cleaners page states approximately 95 percent of US "
            "households use at least one surface cleaner per month and puts specialty niche "
            "products (stone, stainless, grout) in the small remaining share. Furniture polish is "
            "an aerosol niche inside that, not a surface cleaner in the page's own segmentation, "
            "and no published household-penetration figure for furniture polish was located. The "
            "estimate is set below the category figure on that basis and rounded to one "
            "significant figure."),
        note=(
            "An aerosol furniture polish, and the list is dominated by the aerosol and the "
            "silicone: isobutane and propane as propellants, dimethicone and cyclopentasiloxane as "
            "the shine, mineral oil as the carrier, and a lemon fragrance that declares four "
            "components by name. It is a spray-on, so the exposure route is inhalation of a fine "
            "mist in a closed room, which is why the label says to use it ventilated. The Lemon "
            "Oil Polish (non-aerosol) is a separate product already in this database."),
        substitutes=[
            dict(name="Old English Lemon Oil Furniture Polish", tier="mass",
                 note="Same brand, same shelf, non-aerosol. It removes the propellant and the "
                      "mist route, which is the main exposure difference between the two."),
        ],
    ),
    dict(
        pid="189", name="Brasso Metal Polish", brand="Brasso", cat="Specialty",
        exposure=2, exposure_src=SRC_SURFACE,
        exposure_basis=(
            "Metal polish is a specialty niche; the cited household surface cleaners page puts "
            "specialty products in the small remaining share of a category used by approximately "
            "95 percent of households. No published household-penetration figure for metal polish "
            "was located. The estimate is a floor for a long-established niche brand and is "
            "rounded to one significant figure."),
        note=(
            "An abrasive metal polish: calcium carbonate and pumice are the abrasives, oxalic acid "
            "does the chemical work on tarnish, and an isoparaffin solvent carries it. Oxalic acid "
            "is the ingredient to read about; it is a systemic toxicant if swallowed and the "
            "record for it carries the mechanism. It is also a product used by hand with a cloth, "
            "which is a direct dermal route, so gloves are the label's own instruction."),
        substitutes=[
            dict(name="Bar Keepers Friend", tier="mass",
                 note="Same shelf and comparable price. It is an oxalic-acid powder rather than a "
                      "solvent paste, so it keeps the active that does the work and removes the "
                      "isoparaffin solvent. It is a powder, so it is a different way to apply it."),
        ],
    ),
]

# label wording -> existing registry key, where the label's own words differ
ALIAS = {
    "fragrance/parfum": "Fragrance",
    "fragrance": "Fragrance",
    "d-limonene": "Limonene",
    "limonene": "Limonene",
    "dl-citronellol": "Citronellol",
    "oxalic acid dihydrate": "Oxalic Acid",
    "sodium (c10-16) alkyl benzenesulfonate": "Sodium (C10-16) Alkylbenzenesulfonate",
    "c13-14 isoparaffin": "Isoparaffin",
    "ethanolamine (ethanol, 2-amino-)": "Ethanolamine",
    "c10-16 pareth": "C10-16 Pareth",
    "tetrasodium iminodisuccinate": "Tetrasodium Iminodisuccinate",
    "methylchloroisothiazolinone": "Methylchloroisothiazolinone",
    # polydimethylsiloxane is the chemistry; Dimethicone is the same substance under its
    # INCI name, which this registry already carries. Same substance, one key.
    "polydimethylsiloxane": "Dimethicone",
}


def norm(s):
    s = re.sub(r"\.dl-.*$", "", s)
    s = re.sub(r"\s*\(.*?\)\s*", " ", s)
    s = s.lower()
    return re.sub(r"[^a-z0-9]", "", s)


def clean(s):
    s = re.sub(r"<(style|svg|defs)\b.*?</\1>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\.dl-[a-z-]*\{[^}]*\}", "", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def parse_page(path):
    t = Path(path).read_text(encoding="utf-8", errors="ignore")
    heads = re.findall(
        r'<div id="seaIngHead\d+" class="seapodIngredient collapsed"[^>]*>\s*(.*?)\s*'
        r'<span class="toggle-arrow', t, re.S)
    names = [clean(h) for h in heads]
    cas = [c.strip() for c in re.findall(r"<b>CAS:</b>\s*([^<]*)</p>", t)]
    upcs = re.findall(
        r"(\d-\d{5}-\d{5}-\d)\s*</td>\s*<td[^>]*>\s*([^<]*?)\s*</td>\s*<td[^>]*>\s*([^<]*?)\s*</td>",
        t)
    return names, cas, upcs


def strip_trailing_paren(n):
    return re.sub(r"\s*\(.*?\)\s*$", "", n).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-changelog", action="store_true")
    ap.add_argument("--cache", default="/tmp/vest")
    args = ap.parse_args()

    products = json.loads((REPO / "data/products.json").read_text(encoding="utf-8"))
    ingredients = json.loads((REPO / "data/ingredients.json").read_text(encoding="utf-8"))
    existing_names = {p["name"] for p in products}
    key_by_norm = {norm(k): k for k in ingredients}

    added, skipped, new_keys = [], [], {}
    for meta in PRODUCTS:
        if meta["name"] in existing_names:
            skipped.append(meta["name"])
            continue
        names, cas, upcs = parse_page(Path(args.cache) / (meta["pid"] + ".html"))
        ings = []
        for raw in names:
            n = strip_trailing_paren(raw)
            low = n.lower()
            if low in ALIAS:
                key = ALIAS[low]
            elif norm(n) in key_by_norm:
                key = key_by_norm[norm(n)]
            else:
                key = n
                if norm(n) not in key_by_norm:
                    key_by_norm[norm(n)] = key
                    new_keys[key] = True
            if key not in ings:
                ings.append(key)
        rec = {
            "name": meta["name"],
            "brand": meta["brand"],
            "cat": meta["cat"],
            "ings": ings,
            "source": (
                "Vestacy (Essential Home, Advent International) California Cleaning Product Right "
                "to Know Act ingredient disclosure, read 2026-10-07 from the manufacturer's own "
                "product page (productLineId %s, %s)."
                % (meta["pid"], upcs[0][0] if upcs else "UPC not read")),
            "source_url": "https://www.vestacyinfo.com/product.php?productLineId=%s" % meta["pid"],
            "note": meta["note"],
            "owner": OWNER,
            "owner_ev": "verified",
            "owner_src": OWNER_SRC,
            "tier": "mass",
            "tier_ev": "reported",
            "tier_src": "https://www.vestacyinfo.com/product.php?productLineId=%s" % meta["pid"],
            "tier_note": (
                "National mass-market household brand sold through grocery, mass and drug "
                "channels; tier assigned from the brand's retail distribution rather than from a "
                "published channel share."),
            "substitutes": meta["substitutes"],
            "no_substitute_known": None,
            "no_substitute_note": None,
            "strength_disclosure": "full",
            "added": TODAY,
            "updated": TODAY,
            "exposure": meta["exposure"],
            "exposure_ev": "extrapolated",
            "exposure_src": meta["exposure_src"],
            "exposure_basis": meta["exposure_basis"],
            "heritage": False,
            "safe": None,
            "conc": None,
            "conc_src": None,
            "conc_ev": "untested",
            "grade_as_sold": None,
            "grade_as_sold_src": None,
        }
        products.append(rec)
        added.append(rec["name"])

    for k in new_keys:
        ingredients[k] = {
            "s": "%s. Named on a Vestacy (Essential Home) California SB-258 ingredient "
                 "disclosure, read 2026-10-07." % k,
            "ev": "Low",
            "g": None,
            "gr": {},
            "impacts": [],
            "note": ("Added by the 2026-10-07 night-shift harvest from a manufacturer's California "
                     "Cleaning Product Right to Know Act disclosure. No PubChem or ECHA grade has "
                     "been resolved for this entry yet, so g is null rather than a guess. It enters "
                     "ungraded, which is the honest state until the grading lane reaches it."),
        }

    print("products added: %d" % len(added))
    for n in added:
        print("   +", n)
    print("skipped (already present): %d" % len(skipped))
    print("new ingredient keys: %d" % len(new_keys))
    for k in sorted(new_keys):
        print("   *", k)

    if args.dry_run:
        print("[dry-run] no files written")
        return

    def dump(path, obj, indent, trailing_newline):
        text = json.dumps(obj, ensure_ascii=False, indent=indent)
        if trailing_newline:
            text += "\n"
        path.write_text(text, encoding="utf-8")

    dump(REPO / "data/products.json", products, 1, False)
    dump(REPO / "data/ingredients.json", ingredients, 1, False)

    if not args.no_changelog:
        cl = json.loads((REPO / "data/changelog.json").read_text(encoding="utf-8"))
        cl.insert(0, {
            "date": TODAY,
            "text": ("Spectrum harvest station 2 (Dolman 2026-10-07): %d products added to the "
                     "mass-market Essential Home shelf, ordered by exposure. Every ingredient list "
                     "read from the manufacturer's own California SB-258 disclosure at "
                     "vestacyinfo.com. %d new ingredient keys minted, all ungraded. Substitutes "
                     "set on every record." % (len(added), len(new_keys))),
        })
        dump(REPO / "data/changelog.json", cl, 2, True)


if __name__ == "__main__":
    main()
