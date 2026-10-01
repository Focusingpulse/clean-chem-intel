#!/usr/bin/env python3
"""Daily gather (2026-10-01, 10:00Z maintenance lane): four high-volume US
products that were missing from the database, plus the ingredient records they
need.

Sources read on 2026-10-01:

  - Dreft Stage 1: Newborn Baby Liquid Laundry Detergent (64 loads) — the P&G
    SmartLabel ingredient disclosure (UPC 00037000748113, updated 2024-06-12).
    https://smartlabel.pg.com/en-us/00037000748113.html
  - Scrub Free Total Bathroom Cleaner, Lemon Scent — the Church & Dwight
    ingredient-disclosure form (material number 42000220, dated 2024-05-14).
    https://churchdwight.com/ingredient-disclosure/cleaning-products/42000220-scrub-free-total-bathroom-cleaner-lemon-scent.aspx
  - Calgon Water Softener - Liquid — the Reckitt SmartLabel ingredient
    disclosure (UPC 0-51700-20900-2, updated 2022-01-01).
    https://www.rbnainfo.com/smart-label/192
  - Endust Multi-Surface Dusting & Cleaning Spray — the manufacturer's own
    product page, which prints the full intentionally-added list (Nakoma
    Products LLC).
    https://www.endust.com/multisurface-dusting-cleaning-spray

Why these four: the largest verifiable gaps left in the corpus are baby
laundry (no newborn-specific detergent on file), the value bathroom-cleaner
shelf, laundry water softeners (a whole product class absent), and dusting
aids. Each of the four publishes a full intentionally-added list, which is the
entry ticket; a product whose formula is withheld does not enter.

Canonical-key mappings (no new keys minted where a canonical key exists) are
recorded per product in `disclosure_note`:
  - "C10-16 Alketh" -> "C10-16 Pareth" (P&G's own 40-oz Dreft label uses the
    older INCI name for the same alcohol-alkoxylate; the DB key already exists)
  - "C10-16 Alkyldimethylamine Oxide" -> "Alkyldimethylamine Oxide" (the DB's
    generic amine-oxide key; the C10-16 cut is the same substance class)
  - "Hexamethylindanopyran" -> "Galaxolide" (CAS 1222-05-5; the C&D disclosure
    names the synonym, the DB key is the trade name)

Grading follows the house rule (docs/source-policy.md, docs/scoring-rubric.md):
only H-codes at >=40% ECHA C&L notifier consensus drive a dimension grade, read
from the headline (largest company-count) block of PubChem PUG View. UVCB /
polymer / botanical substances with no discrete PubChem CID are recorded
"Extrapolated" with an explicit sourcing note, never graded. Every returned
PubChem title was checked against the intended substance before the record was
accepted; where the title is a systematic name or a trade synonym for the
intended material, that is stated in the note.

NOTE ON tools/grade_batch.py: the batch grader's H-code map implements only
derm/resp/organ/env and omits H319 (and the repro/work/canc dimensions the DB
uses). H319 at >=40% is graded derm C by the house practice (see the DB's
Citric Acid, Sodium Benzoate, Lauramine Oxide and the 2026-09-24/25/26 gather
lanes), so the eye-irritant grades below were applied by hand from the headline
block rather than taken from grade_batch.py's output. The tool gap is recorded
in the changelog; it was not "fixed" here because a change to the shared grader
is a fleet-affecting edit.

Nothing here is product-graded. Product grading is the Sifter lane; a blank
as-sold grade is the honest state, and substitutes[] is left empty for the same
reason (the substitute rule binds on a D/F grade, and none of these carries one
yet).

Run: python3 tools/gather_2026_10_01.py
Then: python3 build.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
TODAY = "2026-10-01"

DREFT = "https://smartlabel.pg.com/en-us/00037000748113.html"
SCRUBFREE = ("https://churchdwight.com/ingredient-disclosure/cleaning-products/"
             "42000220-scrub-free-total-bathroom-cleaner-lemon-scent.aspx")
CALGON = "https://www.rbnainfo.com/smart-label/192"
ENDUST = "https://www.endust.com/multisurface-dusting-cleaning-spray"

BASE_BASIS = ("searched for a published per-product US household penetration figure; none "
              "exists in the open literature, so the estimate is derived from category "
              "penetration times the brand's share of its channel. Rounded to one "
              "significant figure. ")


# ---------------------------------------------------------------- ingredients
NEW_INGS = {
    # ---- Dreft
    "Sodium Salts of C12-18 Fatty Acids": {
        "ev": "Extrapolated",
        "g": "Extrapolated",
        "gr": {},
        "impacts": [],
        "s": "Sodium soap of C12-18 fatty acids (suds reducer). UVCB; no discrete PubChem CID.",
        "note": "PubChem PUG REST returns no CID for the name (404); it is a UVCB sodium "
                "soap cut, not a discrete substance. Recorded extrapolated rather than "
                "invented; the DB's sibling soap entries (MEA Salts of C12-18 Fatty Acids; "
                "Fatty Acids, C8-18 and C18-Unsaturated Sodium Salts) carry no dimension "
                "grade either. Suds reducer disclosed by the P&G SmartLabel for Dreft "
                "Stage 1 Newborn.",
    },
    "Sodium Cumenesulfonate": {
        "ev": "High",
        "g": "H319",
        "gr": {"derm": "C"},
        "impacts": ["derm"],
        "s": "Causes serious eye irritation",
        "note": "Graded from PubChem GHS (CID 23679813, returned title 'Sodium "
                "p-cumenesulfonate' - the para isomer the label term denotes; CAS "
                "28348-53-0). Headline ECHA C&L block: 258 reports from 2 notifications; "
                "H319 at 100% consensus -> derm C (serious eye irritation). No skin-hazard "
                "code reaches the house >=40% bar. Hydrotrope disclosed by the P&G "
                "SmartLabel for Dreft Stage 1 Newborn.",
    },
    "Calcium Formate": {
        "ev": "High",
        "g": "H318",
        "gr": {"derm": "D"},
        "impacts": ["derm"],
        "s": "Causes serious eye damage",
        "note": "Graded from PubChem GHS (CID 10997, returned title 'Calcium formate' - "
                "matches; CAS 544-17-2). Headline ECHA C&L block: 543 reports from 8 "
                "notifications; H318 at 90.4% consensus -> derm D (serious eye damage). "
                "Disclosed by the P&G SmartLabel for Dreft Stage 1 Newborn.",
    },
    # ---- Scrub Free
    "C6-12 Alcohol Ethoxylates": {
        "ev": "Extrapolated",
        "g": "Extrapolated",
        "gr": {},
        "impacts": [],
        "s": "C6-12 alcohol ethoxylate surfactant. UVCB; no discrete PubChem CID.",
        "note": "PubChem PUG REST returns no CID for the name or for CAS 68439-45-2 "
                "(404); it is a UVCB alcohol-ethoxylate cut, not a discrete substance. "
                "Recorded extrapolated rather than invented; the DB's sibling ethoxylate "
                "cuts (Alcohols, C9-11, ethoxylated; Alcohols, C10-16, Ethoxylated) carry "
                "no dimension grade. Surfactant disclosed by the Church & Dwight "
                "ingredient-disclosure form for Scrub Free Total Bathroom Cleaner - Lemon "
                "Scent (material 42000220).",
    },
    # ---- Calgon
    "Sodium Acrylic Acid/MA Copolymer": {
        "ev": "Extrapolated",
        "g": "Extrapolated",
        "gr": {},
        "impacts": [],
        "s": "Acrylic acid / maleic anhydride copolymer, sodium salt (antiredeposition polymer). Polymer; no discrete PubChem CID.",
        "note": "PubChem PUG REST returns no CID for the name or for CAS 52255-49-9 "
                "(404); it is a polymer (acrylic acid / maleic anhydride copolymer, sodium "
                "salt), not a discrete substance. Recorded extrapolated by polymer class "
                "rather than invented; the DB's sibling carboxylate polymers (Sodium "
                "Polyacrylate, Sodium Polycarboxylate) carry no dimension grade either. "
                "Antiredeposition agent disclosed by the Reckitt SmartLabel for Calgon "
                "Water Softener - Liquid.",
    },
    "Sodium Benzeneoxybispropylenesulfonate": {
        "ev": "Extrapolated",
        "g": "Extrapolated",
        "gr": {},
        "impacts": [],
        "s": "Diphenyl-oxide disulfonate surfactant (fragrance component). UVCB; no discrete PubChem CID.",
        "note": "PubChem PUG REST returns no CID for the name or for CAS 119345-04-9 "
                "(404); it is a UVCB surfactant (sodium dodecyl diphenyl oxide disulfonate "
                "class), not a discrete substance. Recorded extrapolated rather than "
                "invented; class-analogous to the DB's Sodium Dodecylbenzenesulfonate "
                "(derm D, env C), which is a class signal, not a grade for this substance. "
                "Fragrance component disclosed by the Reckitt SmartLabel for Calgon Water "
                "Softener - Liquid.",
    },
    "Magnesium Nitrate": {
        "ev": "Medium",
        "g": "H272,H319",
        "gr": {"derm": "C"},
        "impacts": ["derm"],
        "s": "May intensify fire; oxidizer",
        "note": "Graded from PubChem GHS (CID 25212, returned title 'Magnesium nitrate' - "
                "matches; CAS 10377-60-3). Headline ECHA C&L block: 2789 reports from 32 "
                "notifications; H319 at 64.2% -> derm C. H315 37.3% and H335 18.9% fall "
                "below the house bars; H272 78.4% is a physical oxidizer hazard and is not "
                "a graded dimension. Two secondary notifier blocks carry H370/H372/H371 "
                "without percentages and are noted, not graded. Non-functional constituent "
                "(nitrate salt) disclosed by the Reckitt SmartLabel for Calgon Water "
                "Softener - Liquid.",
    },
    # ---- Endust
    "Sorbitan Monooleate": {
        "ev": "Medium",
        "g": "Not Classified",
        "gr": {},
        "impacts": [],
        "s": "No GHS hazard criteria met (majority not-classified per ECHA C&L via PubChem)",
        "note": "PubChem GHS (CID 9920342, returned title 'Sorbitan "
                "mono-(9Z)-9-octadecenoate' - the monooleate ester the label calls "
                "'Sorbitan Monooleate'; CAS 1338-43-8). Headline ECHA C&L block: 1221 of "
                "1224 reports not meeting hazard criteria; no H-code reaches the house "
                ">=40% bar, so no dimension grade is justified. Emulsifier disclosed by "
                "Endust for Multi-Surface Dusting & Cleaning Spray.",
    },
}


# ------------------------------------------------------------------ products
def prod(name, brand, cat, ings, tier, tier_ev, tier_src, exposure, exposure_ev,
         exposure_src, exposure_basis, subs=None, no_sub=None, tier_note=None,
         heritage=None, owner=None, owner_ev="untested", owner_src=None,
         disclosure_note=None, source=None, source_url=None):
    p = {
        "name": name,
        "brand": brand,
        "cat": cat,
        "safe": None,
        "ings": ings,
        "added": TODAY,
        "updated": TODAY,
        "owner": owner,
        "owner_ev": owner_ev,
        "owner_src": owner_src,
        "tier": tier,
        "tier_ev": tier_ev,
        "tier_src": tier_src,
        "substitutes": subs or [],
        "exposure": exposure,
        "exposure_ev": exposure_ev,
        "exposure_src": exposure_src,
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "not_reviewed",
        "exposure_basis": exposure_basis,
    }
    if source:
        p["source"] = source
    if source_url:
        p["source_url"] = source_url
    if tier_note:
        p["tier_note"] = tier_note
    if no_sub:
        p["no_substitute_known"] = no_sub
    if heritage:
        p["heritage"] = True
        p["heritage_year"] = heritage[0]
        p["heritage_note"] = heritage[1]
    if disclosure_note:
        p["disclosure_note"] = disclosure_note
    return p


PRODUCTS = [
    prod("Dreft Stage 1: Newborn Baby Liquid Laundry Detergent", "Dreft", "Laundry",
         ["Water", "C10-16 Pareth", "Sodium C10-16 Alkylbenzenesulfonate",
          "Sodium Lauryl Sulfate", "Sodium Salts of C12-18 Fatty Acids", "Sodium Citrate",
          "Alkyldimethylamine Oxide", "Propylene Glycol", "Alcohol",
          "Polyethyleneimine Alkoxylated", "Sodium Cumenesulfonate", "Fragrance",
          "Tetrasodium Glutamate Diacetate", "Calcium Formate", "Subtilisin",
          "Benzisothiazolinone", "Amylase Enzyme", "Cellulase Enzyme"],
         "mass", "reported", DREFT,
         5, "extrapolated", DREFT,
         BASE_BASIS + "Dreft is the category-defining US baby-laundry brand; Stage 1 is "
                      "its newborn SKU. No per-product penetration figure exists, so the "
                      "estimate stops at the brand's share of the baby-laundry segment "
                      "rather than a measured product share.",
         owner="Procter & Gamble", owner_ev="reported", owner_src=DREFT,
         disclosure_note="Source spellings mapped to canonical keys: 'C10-16 Alketh' -> "
                         "'C10-16 Pareth' (P&G's own 40-oz Dreft label uses the older INCI "
                         "name for the same alcohol-alkoxylate; the DB key already exists); "
                         "'C10-16 Alkyldimethylamine Oxide' -> 'Alkyldimethylamine Oxide' "
                         "(the DB's generic amine-oxide key); 'Fragrances' -> 'Fragrance'. "
                         "The P&G SmartLabel (UPC 00037000748113, updated 2024-06-12) is "
                         "the manufacturer's own current disclosure and names every "
                         "intentionally-added component. The 40-oz SKU (UPC 00037000926986, "
                         "2022) carries a slightly different base - sodium borate and no "
                         "sodium lauryl sulfate - so the two sizes are not the same formula.",
         source="P&G SmartLabel ingredient disclosure",
         source_url=DREFT,
         tier_note="A mass-market newborn laundry detergent. The formula is an anionic/"
                   "nonionic surfactant base with a soap suds reducer, a sodium "
                   "cumenesulfonate hydrotrope, enzymes (subtilisin, amylase, cellulase), a "
                   "benzisothiazolinone preservative and a fragrance that is not broken out "
                   "by component. Entered ungraded: product grading is the Sifter lane."),

    prod("Scrub Free Total Bathroom Cleaner, Lemon Scent", "Scrub Free", "Bathroom",
         ["Water", "Sulfamic Acid", "Lauramine Oxide", "C6-12 Alcohol Ethoxylates",
          "Fragrance", "Butylphenyl Methylpropional", "Citrus Aurantium Peel Oil",
          "Galaxolide", "Limonene"],
         "mass", "reported", SCRUBFREE,
         5, "extrapolated", SCRUBFREE,
         BASE_BASIS + "Scrub Free is a value bathroom-cleaner line sold at mass retail; "
                      "the Total Bathroom Cleaner is its flagship SKU. No per-product "
                      "penetration figure exists, so the estimate stops at the brand's "
                      "share of the bathroom-cleaner category rather than a measured "
                      "product share.",
         owner="Church & Dwight", owner_ev="reported", owner_src=SCRUBFREE,
         disclosure_note="Source spellings mapped to canonical keys: 'Hexamethylindanopyran' "
                         "-> 'Galaxolide' (CAS 1222-05-5; the disclosure names the synonym, "
                         "the DB key is the trade name); 'Fragrances' -> 'Fragrance'. The "
                         "Church & Dwight ingredient-disclosure form (material 42000220, "
                         "dated 2024-05-14) is the manufacturer's own disclosure and lists "
                         "the fragrance components present at or above 100 ppm or on a "
                         "California designated list separately from the rest of the base.",
         source="Church & Dwight ingredient disclosure form",
         source_url=SCRUBFREE,
         tier_note="A mass-market bathroom cleaner. The active is sulfamic acid (an acid "
                   "descaler) with a lauramine-oxide surfactant and a C6-12 ethoxylate "
                   "surfactant; the fragrance is published at component level under the "
                   "California Cleaning Product Right to Know Act, which is why four "
                   "fragrance constituents appear by name instead of one 'fragrance' line. "
                   "Entered ungraded: product grading is the Sifter lane."),

    prod("Calgon Water Softener, Liquid", "Calgon", "Laundry",
         ["Water", "Sodium Acrylic Acid/MA Copolymer", "Sodium Citrate", "Fragrance",
          "Methylchloroisothiazolinone", "Methylisothiazolinone",
          "Sodium Benzeneoxybispropylenesulfonate", "Magnesium Nitrate"],
         "mass", "reported", CALGON,
         4, "extrapolated", CALGON,
         BASE_BASIS + "Calgon is the leading US laundry water-softener brand; the liquid "
                      "is its mass-retail format. No per-product penetration figure "
                      "exists, so the estimate stops at the brand's share of the laundry "
                      "additive category rather than a measured product share.",
         owner="Reckitt", owner_ev="reported", owner_src=CALGON,
         disclosure_note="'Fragrance/Parfum' mapped to 'Fragrance'. The Reckitt SmartLabel "
                         "(UPC 0-51700-20900-2, updated 2022-01-01) is the manufacturer's "
                         "own current disclosure and groups the list into intentionally "
                         "added, fragrance component and non-functional constituent, each "
                         "with a CAS number. The page carries the claim 'Contains no "
                         "phosphate' in the manufacturer's own words. A 2014 SDS served "
                         "from the same site names sodium hydroxide under Clean Water Act "
                         "311, which does not appear on the current list - either the "
                         "formula changed or one document is incomplete; the manufacturer "
                         "does not say which, so the current SmartLabel list is used here.",
         source="Reckitt SmartLabel ingredient disclosure",
         source_url=CALGON,
         tier_note="A liquid laundry water softener. The sequestering role is carried by "
                   "sodium citrate with an acrylic-acid/maleic-anhydride antiredeposition "
                   "copolymer; two isothiazolinone preservatives are present, and the "
                   "fragrance resolves into a diphenyl-oxide disulfonate component. This "
                   "is a whole product class the corpus did not previously hold. Entered "
                   "ungraded: product grading is the Sifter lane."),

    prod("Endust Multi-Surface Dusting & Cleaning Spray", "Endust", "Wood & Stone Care",
         ["Water", "Mineral Oil", "Isoparaffin", "Propane", "Fragrance", "Hexoxyethanol",
          "Sorbitan Monooleate", "Ethoxylated Alcohol"],
         "mass", "reported", ENDUST,
         5, "extrapolated", ENDUST,
         BASE_BASIS + "Endust is a long-standing US dusting-aid brand; the aerosol "
                      "multi-surface spray is its flagship SKU. No per-product penetration "
                      "figure exists, so the estimate stops at the brand's share of the "
                      "dusting-aid category rather than a measured product share.",
         owner="Nakoma Products LLC", owner_ev="reported", owner_src=ENDUST,
         disclosure_note="The manufacturer's own product page prints the full "
                         "intentionally-added list. The retail pack also names the maker as "
                         "Nakoma Products LLC, which the live ENDUST trademark (reg. "
                         "2309332) confirms. The formula is silicone-free: mineral oil and "
                         "isoparaffin carry the dust-trapping action, propane is the "
                         "propellant, and an ethoxylated alcohol plus sorbitan monooleate "
                         "are the emulsifiers. The fragrance is not broken out by component.",
         source="Endust manufacturer product page",
         source_url=ENDUST,
         tier_note="A mass-market aerosol dusting spray. Unlike a furniture polish it is "
                   "silicone-free and is meant to be sprayed on the cloth, not the surface; "
                   "the label warns against applying it directly to floors. Entered "
                   "ungraded: product grading is the Sifter lane."),
]


def main():
    prods = json.loads((DATA / "products.json").read_text(encoding="utf-8"))
    ings = json.loads((DATA / "ingredients.json").read_text(encoding="utf-8"))

    existing = {p.get("name") for p in prods}
    added_ings = []
    for name, rec in NEW_INGS.items():
        if name not in ings:
            ings[name] = rec
            added_ings.append(name)

    added_prods = []
    for p in PRODUCTS:
        if p["name"] in existing:
            continue
        prods.append(p)
        added_prods.append(p["name"])

    (DATA / "products.json").write_text(
        json.dumps(prods, indent=1, ensure_ascii=False), encoding="utf-8")
    (DATA / "ingredients.json").write_text(
        json.dumps(ings, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"products added: {len(added_prods)} -> {len(prods)} total")
    for n in added_prods:
        print("  +", n)
    print(f"ingredients added: {len(added_ings)} -> {len(ings)} total")
    for n in added_ings:
        print("  +", n)


if __name__ == "__main__":
    main()
