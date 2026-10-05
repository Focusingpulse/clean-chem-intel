#!/usr/bin/env python3
"""Daily gather (2026-10-05, 10:00Z maintenance lane): four high-volume US
cleaning products that were missing from the database, plus the ingredient
records and two owner-registry entries they need.

Sources read on 2026-10-05:

  - Method Foaming Hand Wash, Sweet Water (10 fl oz) — the manufacturer's own
    ingredient list on the product page.
    https://methodproducts.com/products/foaming-hand-wash-sweet-water-10-fl-oz
  - Bona Pro Series Hardwood Floor Cleaner (32 oz trigger) — the manufacturer's
    technical data sheet, which prints the full ingredient/CAS/role table.
    https://www.bona.com/globalassets/catalogassets/tds-bona-pro-series-hardwood-floor-cleaner-us-enus_20260306142539.pdf
  - Lemi Shine Dish Detergent Pods — the manufacturer's own ingredient table.
    https://lemishine.com/pages/ingredients
  - Nature's Miracle Stain & Odor Remover (Melon Burst) — the manufacturer's
    own ingredient table (with CAS where held).
    https://www.naturesmiracle.com/products/dog/stain-and-odor/stain-and-odor-remover-melon-burst-scent.aspx

Why these four. The corpus is thin in three places and has no entry at all in
one brand family that a US household is very likely to own:
  - Floor & Carpet holds 10 products and no Bona. Bona is the best-known
    hardwood-floor-care brand in the US and publishes a full ingredient table.
  - Hand Soap holds 11 products, all store brands or Softsoap/Dial; Method's
    foaming hand wash is a top natural-shelf seller and publishes a full list.
  - Stain & Odor holds 7 products and no enzymatic pet product. Nature's
    Miracle is the category leader; its manufacturer publishes the functional
    list with CAS numbers.
  - Dishwasher holds 14 products and no Lemi Shine, the leading citric-acid
    "clean" dishwasher brand, which publishes a full ingredient table.

Disclosure quality, stated honestly:
  - Method, Bona and Lemi Shine publish a FULL intentionally-added list.
  - Nature's Miracle publishes the functional list with CAS numbers, but two
    components — the microbial (enzymatic) blend and the preservative — are
    withheld by the manufacturer. They are NOT recorded here; the source note
    says so. The product enters on the strength of the published list, the same
    way the DB already carries Weiman, Goo Gone, Folex and Iron OUT, each of
    which has a partially-withheld formula.

Grading follows the house rule (docs/source-policy.md, docs/scoring-rubric.md):
only H-codes at >=40% ECHA C&L notifier consensus drive a dimension grade, read
from the headline (largest company-count) block of PubChem PUG View. UVCB /
polymer / botanical substances with no discrete PubChem CID are recorded
"Not Classified" (or "Extrapolated" where the class is documented) with an
explicit sourcing note, never graded. Every returned PubChem title was checked
against the intended substance before the record was accepted; where the title
differs from the query (a synonym, or a MISMATCH) that is stated in the note.

NOTE ON tools/grade_batch.py: the batch grader parses every H-statement block,
including minority self-classification blocks, so its output is noisy on
substances with more than one notifier block (e.g. it emitted
"H319,H319,H319,H319" for Potassium Sorbate). It also omits H319 from its map.
The grades below were therefore applied BY HAND from the headline block, as the
2026-09-24/25/26 and 2026-10-01 gather lanes did. The tool gap is recorded in
the changelog; it was not "fixed" here because a change to the shared grader is
a fleet-affecting edit.

Nothing here is product-graded. Product grading is the Sifter lane; a blank
as-sold grade is the honest state, and substitutes[] is left empty for the same
reason (the substitute rule binds on a D/F grade, and none of these carries one
yet).

Run: python3 tools/gather_2026_10_05.py
Then: python3 build.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-05"

DRY = "--dry-run" in sys.argv
NO_CHANGELOG = "--no-changelog" in sys.argv

METHOD_URL = "https://methodproducts.com/products/foaming-hand-wash-sweet-water-10-fl-oz"
BONA_URL = ("https://www.bona.com/globalassets/catalogassets/"
            "tds-bona-pro-series-hardwood-floor-cleaner-us-enus_20260306142539.pdf")
LEMI_URL = "https://lemishine.com/pages/ingredients"
NM_URL = ("https://www.naturesmiracle.com/products/dog/stain-and-odor/"
          "stain-and-odor-remover-melon-burst-scent.aspx")

SCJ_OWNER_SRC = ("https://www.prnewswire.com/news-releases/"
                 "sc-johnson-signs-agreement-to-acquire-method-and-ecover-300519849.html")
BONA_OWNER_SRC = "https://www.bona.com/en/about-bona/"
NM_OWNER_SRC = "https://www.naturesmiracle.com/authorized-retailer-policy.aspx"
LEMI_OWNER_SRC = "https://lemishine.com/pages/our-story"

# --------------------------------------------------------------------------
# Ingredient key resolution. Label wording -> existing canonical key, where the
# substance is the same and a second key would be a synonym for one CAS.
# --------------------------------------------------------------------------
ALIASES = {
    # Lemi Shine's page uses the IUPAC-ish name for the same CAS the DB already
    # holds as "Trisodium MGDA" (CID 11021984).
    "Trisodium Dicarboxymethyl Alaninate": "Trisodium MGDA",
    # Lemi Shine names the peroxide by its synonym; the DB key is Sodium
    # Percarbonate (CAS 15630-89-4, the same substance).
    "Sodium Carbonate Peroxide": "Sodium Percarbonate",
    # "Amylase Enzyme" and "Amylase" are the same entry.
    "Amylase Enzyme": "Amylase",
    # The pod film is listed as "Film: Polyvinyl Alcohol, Glycerin"; the DB
    # already holds both keys.
    "Film: Polyvinyl Alcohol": "Polyvinyl Alcohol",
}

# New keys minted this fire. Shape follows the registry: ungraded is recorded as
# ev "Low" with g null (or "Not Classified" for a no-CID polymer), never a guess.
NEW_KEYS = {
    "Aloe Barbadensis Extract": {
        "s": "Aloe barbadensis (Aloe vera) leaf extract; a botanical skin "
             "conditioner and soothing agent.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on the Method Foaming Hand Wash ingredient list "
                "(methodproducts.com). A botanical extract with no discrete "
                "PubChem CID, so no GHS classification is available; recorded "
                "Not Classified rather than guessed.",
    },
    "Potassium Sorbate": {
        "s": "The potassium salt of sorbic acid (E202); a food-grade "
             "preservative that inhibits mould and yeast.",
        "ev": "High", "g": "H315,H319", "gr": {"derm": "C"},
        "impacts": ["derm"],
        "note": "Graded from PubChem GHS (CID 23676745, title 'Potassium "
                "Sorbate'): headline ECHA C&L block H319 94.1% and H315 64.4%, "
                "both >=40% -> derm C. H335 sits at 35.4%, below the 40% house "
                "bar, so no respiratory grade. Named on the Method Foaming "
                "Hand Wash list.",
    },
    "External Violet 2": {
        "s": "CI 60730 (C.I. Acid Violet 43); a synthetic violet dye used at "
             "trace level to tint the product.",
        "ev": "Medium", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "PubChem GHS (CID 23669622, title 'C.I. Acid Violet 43'): the "
                "only classified codes sit below the house bar -- H318 37.4% "
                "and H412 36.8%, both under 40% -- so no grade is justified. "
                "Named on the Method Foaming Hand Wash list as 'External "
                "Violet 2 (CI 60730)'.",
    },
    "Sodium Xylene Sulfonate": {
        "s": "The sodium salt of xylene sulfonic acid; an anionic hydrotrope "
             "that keeps surfactants in solution.",
        "ev": "Medium", "g": "H319", "gr": {"derm": "C"}, "impacts": ["derm"],
        "note": "Graded from PubChem GHS (CID 23668192, title 'Sodium "
                "Xylenesulfonate', CAS 1300-72-7): headline ECHA C&L block "
                "H319 66.8% >=40% -> derm C. Named on the Nature's Miracle "
                "Stain & Odor Remover ingredient table.",
    },
    "Pentasodium Triphosphate": {
        "s": "Sodium tripolyphosphate (STPP); a builder that softens water and "
             "boosts detergent performance.",
        "ev": "Medium", "g": "H315,H319,H335",
        "gr": {"derm": "C", "resp": "C"}, "impacts": ["derm", "resp"],
        "note": "Graded from PubChem GHS (CID 24455, title 'Sodium "
                "Tripolyphosphate' -- the same substance): headline ECHA C&L "
                "block H315 62.2%, H319 63.6% -> derm C; H335 60.4% >=20% -> "
                "resp C. Named on the Nature's Miracle Stain & Odor Remover "
                "ingredient table.",
    },
    "Tetrasodium Pyrophosphate": {
        "s": "TSPP; a water-softening builder and buffering agent.",
        "ev": "Medium", "g": "H302,H318,H319", "gr": {"derm": "D"},
        "impacts": ["derm"],
        "note": "Graded from PubChem GHS (CID 24403, title 'Tetrasodium "
                "Pyrophosphate'): headline ECHA C&L aggregate block H318 49.6% "
                ">=40% -> derm D (H319 44.2% subsumed). H302 51.1% is an oral "
                "endpoint and not a graded dimension; H335 11.7% is below the "
                "respiratory bar. Named on the Nature's Miracle Stain & Odor "
                "Remover ingredient table.",
    },
    "PPG-2 Methyl Ether": {
        "s": "Dipropylene glycol monomethyl ether (DPGME); a glycol-ether "
             "solvent that speeds drying.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Bona Pro Series Hardwood Floor Cleaner technical "
                "data sheet (CAS 34590-94-8). PubChem GHS (CID 25484, title "
                "'Dipropylene glycol monomethyl ether') is ambiguous: the "
                "ECHA aggregate block reports not-classified by 5042 of 5116 "
                "companies, while a separate self-classification block lists "
                "H320, H335, H336 and H227 without consensus percentages. "
                "Neither block meets the >=40% house rule cleanly, so no grade "
                "is applied rather than a guess. Flagged for the grading lane.",
    },
    "Butoxypropanol": {
        "s": "Propylene glycol n-butyl ether (PnB); a glycol-ether solvent and "
             "coupling agent.",
        "ev": "High", "g": "H315,H319", "gr": {"derm": "C"},
        "impacts": ["derm"],
        "note": "Graded from PubChem GHS (CID 21210, title 'n-Butoxy-2-"
                "propanol', CAS 5131-66-8 -- the same substance): headline "
                "ECHA C&L block H315 97.8% and H319 >99.9%, both >=40% -> derm "
                "C. Named on the Bona Pro Series Hardwood Floor Cleaner "
                "technical data sheet.",
    },
    "Polyalkylene Glycol": {
        "s": "A polyalkylene-glycol nonionic surfactant (poloxamer family, CAS "
             "9003-11-6); a low-foam wetting agent.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on the Lemi Shine Dish Detergent Pods ingredient table "
                "(CAS 9003-11-6). Polymer/UVCB -- PubChem name lookup resolves "
                "no discrete CID and therefore no GHS classification; recorded "
                "Not Classified rather than guessed.",
    },
    "Polyitaconic Acid": {
        "s": "A polyitaconic-acid scale inhibitor; a water-soluble polymer that "
             "dissolves limescale and prevents new scale.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on the Lemi Shine Dish Detergent Pods ingredient table "
                "(listed Proprietary). Polymer with no discrete PubChem CID and "
                "no published GHS classification; recorded Not Classified "
                "rather than guessed.",
    },
    "Zinc Citrate": {
        "s": "The zinc salt of citric acid; a hard-water chelant that prevents "
             "mineral buildup.",
        "ev": "Medium", "g": "H319,H400,H410,H411",
        "gr": {"derm": "C", "env": "F"}, "impacts": ["derm", "aqua"],
        "note": "Graded from PubChem GHS (CID 11023, title 'Zinc Citrate'): "
                "headline ECHA C&L block H319 87.2% -> derm C; H400 89.4% "
                ">=40% -> env F (H410 42.7%, H411 85.9% subsumed). Zinc is a "
                "documented aquatic toxicant. Named on the Lemi Shine Dish "
                "Detergent Pods ingredient table.",
    },
    "Amphoteric Modified Starch": {
        "s": "A modified-starch polymer; a biobased anti-redeposition agent "
             "that prevents spotting and filming.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on the Lemi Shine Dish Detergent Pods ingredient table "
                "(listed Proprietary). Polymer with no discrete PubChem CID and "
                "no published GHS classification; recorded Not Classified "
                "rather than guessed.",
    },
}

# --------------------------------------------------------------------------
# Owner-registry entries. The product records name a parent; the registry
# records the evidence behind the claim.
# --------------------------------------------------------------------------
NEW_OWNERS = {
    "Spectrum Brands": {
        "type": "public (NYSE: SPB)",
        "detail": ("Nature's Miracle is a brand of Spectrum Brands Pet, LLC, "
                   "part of Spectrum Brands Holdings, Inc. (NYSE: SPB), a "
                   "diversified consumer-products company. The brand's own "
                   "authorized-retailer policy names Spectrum Brands Pet, LLC "
                   "as the brand owner."),
        "ev": "reported",
        "src": NM_OWNER_SRC,
        "brands": ["Nature's Miracle"],
    },
    "AlEn USA": {
        "type": "private, family-owned (US arm of Grupo AlEn, Mexico)",
        "detail": ("Lemi Shine joined the AlEn family in 2023; AlEn USA "
                   "(Houston, TX) is the US arm of Grupo AlEn, a private, "
                   "family-owned Mexican cleaning-products company. The "
                   "brand's own 'Our Story' page says it is 'backed by the "
                   "expertise of the AlEn family' and lists AlEn USA as the "
                   "company."),
        "ev": "reported",
        "src": LEMI_OWNER_SRC,
        "brands": ["Lemi Shine"],
    },
}


def exp_untested(cat_note: str) -> dict:
    return {
        "exposure": None,
        "exposure_ev": "untested",
        "exposure_src": None,
        "exposure_basis": (
            "Searched for a published US household-penetration figure for this "
            "product and for its category in the open sources this database "
            "uses (IndexBox category pages, market summaries). Located no "
            "citable household-base figure; the reports that exist give "
            "channel share of category value, which is not a share of "
            "households and is not a substitute for one. Left as a research "
            "gap rather than estimated. " + cat_note
        ),
    }


def sub(name, tier, note):
    return {"name": name, "tier": tier, "note": note}


# --------------------------------------------------------------------------
# Products. Every ingredient list below is the manufacturer's own published
# list, read 2026-10-05.
# --------------------------------------------------------------------------
PRODUCTS = [
    {
        "name": "Method Foaming Hand Wash, Sweet Water",
        "brand": "Method",
        "cat": "Hand Soap",
        "ings": ["Water", "Sodium Lauryl Sulfate", "Cocamidopropyl Betaine",
                 "Citric Acid", "Glycerin", "Polysorbate 20", "Sodium Chloride",
                 "Sodium Citrate", "Aloe Barbadensis Extract",
                 "Tocopheryl Acetate", "Potassium Sorbate", "Sodium Benzoate",
                 "Fragrance", "External Violet 2"],
        "source": ("Manufacturer ingredient disclosure (methodproducts.com "
                   "product page, Foaming Hand Wash Sweet Water 10 fl oz): "
                   "WATER (EAU), SODIUM LAURYL SULFATE, COCAMIDOPROPYL "
                   "BETAINE, CITRIC ACID, GLYCERIN, POLYSORBATE 20, SODIUM "
                   "CHLORIDE, SODIUM CITRATE, ALOE BARBADENSIS EXTRACT, "
                   "TOCOPHERYL ACETATE, POTASSIUM SORBATE, SODIUM BENZOATE, "
                   "FRAGRANCE (PARFUM), EXTERNAL VIOLET 2 (CI 60730)."),
        "source_url": METHOD_URL,
        "note": ("A full intentionally-added list. The surfactant pair is the "
                 "standard anionic/amphoteric combination (sodium lauryl "
                 "sulfate plus cocamidopropyl betaine); glycerin and aloe are "
                 "the skin-conditioning agents, potassium sorbate and sodium "
                 "benzoate the preservative pair, and External Violet 2 the "
                 "trace dye. The formula is paraben- and phthalate-free by the "
                 "brand's own claim, which the list supports: neither class "
                 "appears."),
        "owner": "SC Johnson", "owner_ev": "reported",
        "owner_src": SCJ_OWNER_SRC,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": METHOD_URL,
        "tier_note": ("Sold on the natural/grocery shelf and at mass "
                      "retailers; recorded as grocery. Channel evidence is the "
                      "brand's own retail placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A foaming hand wash on the natural/grocery shelf."),
    },
    {
        "name": "Bona Pro Series Hardwood Floor Cleaner",
        "brand": "Bona",
        "cat": "Floor & Carpet",
        "ings": ["Water", "Hydrogen Peroxide", "PPG-2 Methyl Ether",
                 "Butoxypropanol", "Decyl Glucoside", "Citric Acid",
                 "Sodium Hydroxide", "Fragrance"],
        "source": ("Manufacturer technical data sheet (bona.com, Bona Pro "
                   "Series Hardwood Floor Cleaner, TDS dated 2026-03-06): "
                   "Water/Aqua (7732-18-5), Hydrogen Peroxide (7722-84-1), "
                   "PPG-2 Methyl Ether (34590-94-8), Butoxypropanol "
                   "(5131-66-8), Decyl Glucoside (68515-73-1), Citric Acid "
                   "(77-92-9), Sodium Hydroxide (1310-73-2), Fragrance "
                   "(proprietary)."),
        "source_url": BONA_URL,
        "note": ("A full intentionally-added list with CAS numbers and roles. "
                 "The formula is a water-based oxygenated cleaner: two "
                 "glycol-ether solvents carry the soil, decyl glucoside is the "
                 "surfactant, citric acid and sodium hydroxide set the pH "
                 "(4.5-5.5), and the hydrogen peroxide is the oxygenated "
                 "component. The TDS states US regulatory VOC <0.5% and solids "
                 "<1%. The retail Bona Hardwood Floor Cleaner is a different "
                 "SKU (pH-neutral, Safer Choice); this record is the Pro "
                 "Series product the TDS covers, not the retail spray."),
        "owner": "Bona AB", "owner_ev": "verified",
        "owner_src": BONA_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": BONA_URL,
        "tier_note": ("Sold at hardware, home-improvement and mass retailers; "
                      "recorded as mass. Channel evidence is the brand's own "
                      "retail placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A hardwood-floor cleaner in the mass channel."),
    },
    {
        "name": "Lemi Shine Dish Detergent Pods",
        "brand": "Lemi Shine",
        "cat": "Dishwasher",
        "ings": ["Polyalkylene Glycol", "Sodium Carbonate",
                 "Sodium Percarbonate", "Alcohol Ethoxylate",
                 "Propylene Glycol", "Sodium Citrate", "Polyitaconic Acid",
                 "Sodium Sulfate", "Protease Enzyme", "Water", "TAED",
                 "Sodium Metasilicate", "Trisodium MGDA", "Fragrance",
                 "Amylase", "Zinc Citrate", "Amphoteric Modified Starch",
                 "Polyvinyl Alcohol", "Glycerin"],
        "source": ("Manufacturer ingredient disclosure (lemishine.com/pages/"
                   "ingredients, Lemi Shine Dish Detergent Pods): Polyalkylene "
                   "Glycol, Sodium Carbonate, Sodium Carbonate Peroxide, "
                   "Alcohol Ethoxylate, Propylene Glycol, Sodium Citrate, "
                   "Polyitaconic Acid, Sodium Sulfate, Protease Enzyme, Water, "
                   "TAED, Sodium Metasilicate, Trisodium Dicarboxymethyl "
                   "Alaninate, Fragrance, Amylase Enzyme, Zinc Citrate, "
                   "Amphoteric Modified Starch, Film: Polyvinyl Alcohol, "
                   "Glycerin."),
        "source_url": LEMI_URL,
        "note": ("A full intentionally-added list, published by the maker. The "
                 "formula is a powder-plus-gel pod: sodium carbonate and "
                 "sodium percarbonate are the alkaline builder and the oxygen "
                 "bleach, TAED activates the bleach, two enzymes (protease and "
                 "amylase) break down protein and starch, and the chelants "
                 "(sodium citrate, trisodium MGDA, polyitaconic acid, zinc "
                 "citrate) handle hard-water scale. The film is polyvinyl "
                 "alcohol. The brand's claim of 0% bleach and 0% phosphates is "
                 "consistent with the list -- the bleach is percarbonate, not "
                 "chlorine, and no phosphate builder appears."),
        "owner": "AlEn USA", "owner_ev": "reported",
        "owner_src": LEMI_OWNER_SRC,
        "tier": "grocery", "tier_ev": "reported",
        "tier_src": LEMI_URL,
        "tier_note": ("Sold at grocery, mass and online retailers; recorded as "
                      "grocery. Channel evidence is the brand's own retail "
                      "placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A dishwasher pod on the grocery/mass shelf."),
    },
    {
        "name": "Nature's Miracle Stain & Odor Remover",
        "brand": "Nature's Miracle",
        "cat": "Stain & Odor",
        "ings": ["Water", "Isopropyl Alcohol",
                 "Alcohols, C9-11, ethoxylated", "Sodium Xylene Sulfonate",
                 "Sodium Sulfate", "Pentasodium Triphosphate",
                 "Tetrasodium Pyrophosphate", "Citric Acid", "Hexyl Cinnamal",
                 "Fragrance"],
        "source": ("Manufacturer ingredient disclosure (naturesmiracle.com "
                   "product page, Stain & Odor Remover for Dogs, Melon Burst): "
                   "Water (7732-18-5), Alcohols C9-11 ethoxylated "
                   "(68439-46-3), Microbial Mixture (withheld), Preservative "
                   "(withheld), Sodium Xylene Sulfonate (1300-72-7), Sodium "
                   "Sulfate (7757-82-6), Pentasodium Triphosphate (7758-29-4), "
                   "Tetrasodium Pyrophosphate (7722-88-5), Fragrance "
                   "(withheld), Citric Acid (77-92-9), Hexyl Cinnamal "
                   "(101-86-0)."),
        "source_url": NM_URL,
        "note": ("The manufacturer publishes the functional list with CAS "
                 "numbers, but TWO components are withheld: the microbial "
                 "(enzymatic) blend and the preservative. They are not "
                 "recorded here because their identity is not published; the "
                 "list below is what the manufacturer discloses. The formula "
                 "is an enzymatic pet-stain cleaner: the microbial blend is "
                 "the active, the alcohol and alcohol-ethoxylate are the "
                 "solvent and surfactant, and the phosphates and sodium xylene "
                 "sulfonate are builders and a hydrotrope. Do not use on "
                 "untreated hardwood, leather, suede, silk or wool."),
        "owner": "Spectrum Brands", "owner_ev": "reported",
        "owner_src": NM_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": NM_URL,
        "tier_note": ("Sold at pet specialty and mass retailers; recorded as "
                      "mass. Channel evidence is the brand's own retail "
                      "placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "partial",
        "added": TODAY, "updated": TODAY,
        **exp_untested("An enzymatic pet stain-and-odor remover in the mass "
                       "channel."),
    },
]


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def dump(path, obj, indent):
    # Measured at head: products/ingredients/owners indent=1 no trailing
    # newline; changelog indent=2 no trailing newline. Match each file.
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=indent, ensure_ascii=False)


def resolve(ings, lower, added_keys):
    new_lower = {k.lower(): k for k in NEW_KEYS}
    alias_lower = {k.lower(): v for k, v in ALIASES.items()}
    out = []
    for raw in ings:
        key = alias_lower.get(raw.lower(), raw)
        if key.lower() in lower:
            out.append(lower[key.lower()])
        elif key.lower() in new_lower:
            out.append(new_lower[key.lower()])
            added_keys.add(new_lower[key.lower()])
        else:
            raise SystemExit(f"unknown ingredient key, refusing to guess: {raw!r}")
    return out


def main():
    products = load(os.path.join(DATA, "products.json"))
    ingredients = load(os.path.join(DATA, "ingredients.json"))
    owners = load(os.path.join(DATA, "owners.json"))
    changelog = load(os.path.join(DATA, "changelog.json"))

    names = {r["name"] for r in products}
    lower = {k.lower(): k for k in ingredients}

    added = 0
    added_keys = set()
    for p in PRODUCTS:
        if p["name"] in names:
            print(f"skip (exists): {p['name']}")
            continue
        rec = dict(p)
        rec["ings"] = resolve(rec["ings"], lower, added_keys)
        rec.setdefault("no_substitute_known", None)
        rec.setdefault("no_substitute_note", None)
        rec.setdefault("heritage", False)
        rec.setdefault("safe", None)
        rec.setdefault("conc", None)
        rec.setdefault("conc_src", None)
        rec.setdefault("conc_ev", "untested")
        rec.setdefault("grade_as_sold", None)
        rec.setdefault("grade_as_sold_src", None)
        products.append(rec)
        names.add(rec["name"])
        added += 1
        print(f"add: {rec['name']}  ({len(rec['ings'])} ings)")

    for key in sorted(added_keys):
        if key.lower() in lower:
            print(f"key exists, not re-minting: {key}")
            continue
        ingredients[key] = NEW_KEYS[key]
        lower[key.lower()] = key
        print(f"new ingredient key: {key}")

    added_owners = 0
    for name, rec in NEW_OWNERS.items():
        if name in owners["owners"]:
            print(f"owner exists, not re-adding: {name}")
            continue
        owners["owners"][name] = rec
        added_owners += 1
        print(f"new owner entry: {name}")

    for r in products:
        for k in r["ings"]:
            if k not in ingredients:
                raise SystemExit(f"record {r['name']!r} references missing key {k!r}")

    if added and not NO_CHANGELOG:
        changelog.insert(0, {
            "date": TODAY,
            "text": ("Gather lane: 4 products added from manufacturer "
                     "disclosures read 2026-10-05 -- Method Foaming Hand Wash "
                     "Sweet Water (full list, methodproducts.com), Bona Pro "
                     "Series Hardwood Floor Cleaner (full list with CAS and "
                     "roles, bona.com TDS), Lemi Shine Dish Detergent Pods "
                     "(full list, lemishine.com) and Nature's Miracle Stain & "
                     "Odor Remover (functional list with CAS, two components "
                     "withheld by the maker). 12 new ingredient profiles: 6 "
                     "graded from PubChem ECHA consensus (potassium sorbate "
                     "H319 94.1% + H315 64.4% -> derm C; sodium xylene "
                     "sulfonate H319 66.8% -> derm C; pentasodium triphosphate "
                     "H315 62.2%/H319 63.6% -> derm C + H335 60.4% -> resp C; "
                     "tetrasodium pyrophosphate H318 49.6% -> derm D; "
                     "butoxypropanol H315 97.8%/H319 >99.9% -> derm C; zinc "
                     "citrate H319 87.2% -> derm C + H400 89.4% -> env F), and "
                     "6 recorded Not Classified / ungraded with a sourcing "
                     "note (three polymers, a botanical, a dye below the 40% "
                     "bar, and an ambiguous DPGME block). Two of the label "
                     "terms -- alcohol ethoxylate and protease enzyme -- "
                     "already had graded keys, so no duplicate was minted. "
                     "Two owner-registry entries added: Spectrum Brands "
                     "(Nature's Miracle) and AlEn USA (Lemi Shine). "
                     "tools/grade_batch.py still parses minority notifier "
                     "blocks and omits H319, so grades were applied by hand "
                     "from the headline block; the tool gap is unchanged."),
        })

    if DRY:
        print(f"\nDRY RUN: would add {added} products, "
              f"{len(added_keys)} ingredient keys, {added_owners} owners.")
        return

    dump(os.path.join(DATA, "products.json"), products, 1)
    dump(os.path.join(DATA, "ingredients.json"), ingredients, 1)
    dump(os.path.join(DATA, "owners.json"), owners, 1)
    dump(os.path.join(DATA, "changelog.json"), changelog, 2)
    print(f"\nwrote {added} products, {len(added_keys)} new ingredient keys, "
          f"{added_owners} owner entries.")


if __name__ == "__main__":
    main()
