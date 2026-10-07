#!/usr/bin/env python3
"""Daily gather (2026-10-07, 10:00Z maintenance lane): four high-volume US
cleaning products that were missing from the database, plus the ingredient
records and owner-registry entries they need.

Sources read on 2026-10-07:

  - Finish Jet-Dry Rinse Aid - Original. Reckitt's own SmartLabel ingredient
    disclosure, in descending weight percent, with CAS numbers.
    https://www.rbnainfo.com/smart-label.php?productLineId=654
  - Mrs. Meyer's Clean Day Liquid Hand Soap, Lavender. The manufacturer's own
    per-SKU ingredient list on its product page, plus the same company's
    product-information PDF for the refill (which carries one extra line).
    https://mrsmeyers.com/products/liquid-hand-soap-lavender
    https://pi.scjp.com/us/mrs-meyers-clean-day-liquid-hand-soap-refill-lavender-scent-us.pdf
  - Downy Unstopables In-Wash Scent Booster Beads, Fresh. P&G's own SmartLabel
    disclosure (information last updated 2024-12-28 by Downy).
    https://smartlabel.pg.com/en-us/00030772087268.html
  - Spot Shot Instant Carpet Stain Remover (Aerosol). WD-40 Company's own
    GHS safety data sheet, section 3.
    https://files.wd40.com/pdf/sds/spotshot/spot-shot-instant-carpet-stain-remover-aerosol-us-ghs.pdf

Why these four. The corpus is thin in three places and has no entry at all in
two brand families a US household is likely to own:

  - Dishwasher holds 16 products and NOT ONE rinse aid. Jet-Dry is the category
    leader and a different function from every detergent already recorded: it
    is dispensed in the rinse cycle, not the wash, so its ingredient set
    (surfactant + hydrotrope + chelant + preservative, no builder, no bleach)
    is not represented anywhere in the corpus.
  - Hand Soap holds 12 products and no Mrs. Meyer's. Mrs. Meyer's Clean Day is
    the leading garden-scented hand soap in the US natural channel and the
    brand is already in the corpus for multi-surface and dish, but not for the
    hand soap that is its largest line.
  - Laundry holds 45 products and no scent BOOSTER. The in-wash bead is now a
    real US category (Downy Unstopables is the largest seller) and it is a
    different delivery form from anything the DB carries: a solid PEG bead
    added alongside the detergent, not a detergent, softener or sheet.
  - Floor & Carpet holds 14 products -- the thinnest non-specialty category --
    and no WD-40 Company brand at all. Spot Shot is, in the acquirer's own
    10-K wording, "a leading brand in the carpet stain remover category", and
    WD-40 Company owns a whole household-cleaning family (2000 Flushes, X-14,
    Carpet Fresh) that the corpus does not carry.

Disclosure quality, stated honestly:
  - Jet-Dry, Mrs. Meyer's and Downy Unstopables publish a FULL
    intentionally-added list.
  - Spot Shot's aerosol SDS names only the components that cross the hazard
    disclosure threshold and states the exact percentages are a trade secret.
    This is a PARTIAL disclosure and is recorded as such, the same way the DB
    already carries Sprayway Glass Cleaner.

Grading follows the house rule (docs/source-policy.md, docs/scoring-rubric.md):
only H-codes at >=40% ECHA C&L notifier consensus drive a dimension grade, read
from the headline (largest company-count) block of PubChem PUG View. Every
returned PubChem title was checked against the intended substance before the
record was accepted, and every label term was checked against the existing
registry before a new key was minted.

  - Eight new keys are minted this run and ALL EIGHT are recorded Not Classified
    with an explicit sourcing note: Trideceth-3, Polyquaternium-2,
    Cocamidopropyl Hydroxysultaine, Sodium Methyl 2-Sulfolaurate, Lavandula
    Angustifolia (Lavender) Oil, Olea Europaea (Olive) Fruit Oil and
    Polyoxyalkylene Substituted Chromophore (Cyan) resolve to no PubChem CID or
    no GHS section at all; Disodium 2-Sulfolaurate resolves to a CID whose only
    H-codes (H302, H315, H319, H412) sit at 11.1% consensus, below the house
    bar. No grade is minted from a guess.
  - Four label terms are ALIASED to keys the DB already carries rather than
    re-minted: "C10-16 Alcohols Ethoxylated Propoxylated" -> "Alcohols, C10-16,
    Ethoxylated"; "CI Acid Blue 9" -> "Acid Blue 9"; "Sodium Cumene Sulfonate"
    -> "Sodium Cumenesulfonate" (the Sifter sort lane merged that spelling pair
    on 2026-10-04); and "2-(2-Butoxyethoxy)ethanol" -> "Diethylene Glycol
    Monobutyl Ether" (same substance, CAS 112-34-5). Two of those aliases land
    on keys that are already graded, so the verified grade reaches these
    products instead of a fresh ungraded duplicate.

Nothing here is product-graded. Product grading is the Sifter lane; a blank
as-sold grade is the honest state, and substitutes[] is left empty for the same
reason (the substitute rule binds on a D/F grade, and none of these carries one
yet).

Run: python3 tools/gather_2026_10_07.py
Then: python3 build.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-07"

DRY = "--dry-run" in sys.argv
NO_CHANGELOG = "--no-changelog" in sys.argv

JETDRY_URL = "https://www.rbnainfo.com/smart-label.php?productLineId=654"
RECKITT_OWNER_SRC = "https://www.reckitt.com/our-brands/"
MRSMEYERS_URL = "https://mrsmeyers.com/products/liquid-hand-soap-lavender"
MRSMEYERS_PI_URL = ("https://pi.scjp.com/us/mrs-meyers-clean-day-liquid-hand-"
                    "soap-refill-lavender-scent-us.pdf")
SCJ_OWNER_SRC = ("https://www.prnewswire.com/news-releases/sc-johnson-signs-"
                 "agreement-to-acquire-method-and-ecover-300519849.html")
DOWNY_URL = "https://smartlabel.pg.com/en-us/00030772087268.html"
PG_OWNER_SRC = "https://us.pg.com/brands/"
SPOTSHOT_URL = ("https://files.wd40.com/pdf/sds/spotshot/spot-shot-instant-"
                "carpet-stain-remover-aerosol-us-ghs.pdf")
WD40_OWNER_SRC = ("https://www.sec.gov/Archives/edgar/data/105132/"
                  "000119312504179631/d10k.htm")

# --------------------------------------------------------------------------
# Ingredient key resolution. Label wording -> existing canonical key, where the
# substance is the same and a second key would be a synonym for one CAS.
# --------------------------------------------------------------------------
ALIASES = {
    # Reckitt prints the C10-16/C12-14 alcohol ethoxylate-propoxylate under its
    # INCI-style label name; the DB key is the same substance class.
    "C10-16 Alcohols Ethoxylated Propoxylated": "Alcohols, C10-16, Ethoxylated",
    # Reckitt prints the colour-index form; the DB key is the same dye
    # (CI 42045, FD&C Blue 1, CAS 3844-45-9).
    "CI Acid Blue 9": "Acid Blue 9",
    # Reckitt prints "Sodium Cumene Sulfonate"; the DB already carries the same
    # substance (CAS 28348-53-0) as "Sodium Cumenesulfonate", graded derm C from
    # CID 23679813. The Sifter sort lane merged that spelling pair on 2026-10-04
    # and recorded the reason on the surviving key, so this run must NOT mint a
    # second key for it.
    "Sodium Cumene Sulfonate": "Sodium Cumenesulfonate",
    # Spot Shot's SDS prints the IUPAC-style name for the same substance the DB
    # already carries as Butyloxyethanol (CAS 111-76-2).
    "2-Butoxyethanol": "Butyloxyethanol",
    # Spot Shot's SDS prints "2-(2-Butoxyethoxy)ethanol"; the DB already carries
    # the same substance (CAS 112-34-5) as "Diethylene Glycol Monobutyl Ether",
    # graded derm C / repro C. Same substance, one CAS, so no second key.
    "2-(2-Butoxyethoxy)ethanol": "Diethylene Glycol Monobutyl Ether",
}

# New keys minted this fire. Shape follows the registry: ungraded is recorded as
# ev "Low"/"Medium" with g "Not Classified" (or null) and an explicit sourcing
# note, never a guess.
NEW_KEYS = {
    "Trideceth-3": {
        "s": "A tridecyl alcohol ethoxylate with an average of 3 ethylene oxide "
             "units (CAS 78330-21-9); a nonionic surfactant/solvent.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Reckitt's own SmartLabel for Finish Jet-Dry Rinse Aid "
                "with CAS 78330-21-9. PubChem PUG REST resolves the name to CID "
                "78116 (title 'Trideceth-3') but that record carries no Safety "
                "and Hazards / GHS section, so no classification is available "
                "from the approved source. Recorded Not Classified rather than "
                "guessed. Distinct from the DB's 'Isotridecanol Ethoxylated' "
                "(a branched C13 alcohol ethoxylate) and from 'Alcohols, C13, "
                "branched, ethoxylated'.",
    },
    "Polyquaternium-2": {
        "s": "A cationic polymeric conditioner (CAS 68555-36-2); a film-forming "
             "polymer used for sheeting and anti-spotting.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Reckitt's own SmartLabel for Finish Jet-Dry Rinse Aid "
                "with CAS 68555-36-2. PubChem PUG REST returns 404 for the name "
                "— no discrete CID resolves for this polymer — so no GHS "
                "classification is available. Recorded Not Classified rather "
                "than guessed, the same way the DB already carries other "
                "polymer class keys.",
    },
    "Cocamidopropyl Hydroxysultaine": {
        "s": "An amphoteric surfactant of the hydroxysultaine class (CAS "
             "68139-30-0); a mild foam booster and viscosity builder.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Mrs. Meyer's own ingredient list for the Lavender "
                "Liquid Hand Soap, first in the surfactant pair. PubChem PUG "
                "REST returns 404 for the name and for the CAS number "
                "68139-30-0 — no discrete CID resolves — so no GHS "
                "classification is available. Recorded Not Classified rather "
                "than guessed. Distinct from the DB's 'Cocamidopropyl Betaine' "
                "(a different amphoteric) and from 'Cocamidopropylamine Oxide'.",
    },
    "Sodium Methyl 2-Sulfolaurate": {
        "s": "The sodium salt of the methyl ester of 2-sulfolauric acid (CAS "
             "149458-07-1); an anionic surfactant of the alpha-sulfo methyl "
             "ester class.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Mrs. Meyer's own ingredient list for the Lavender "
                "Liquid Hand Soap, second in the surfactant pair. PubChem PUG "
                "REST resolves a CID for the name but its PUG View record "
                "carries no GHS section (the fetch returns PUGVIEW.NotFound), "
                "and the CAS number 149458-07-1 returns 404 — so no "
                "classification is available from the approved source. "
                "Recorded Not Classified rather than guessed.",
    },
    "Lavandula Angustifolia (Lavender) Oil": {
        "s": "Lavender essential oil (Lavandula angustifolia); the scent "
             "component named on the label.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Mrs. Meyer's own ingredient list for the Lavender "
                "Liquid Hand Soap. This is a UVCB botanical oil: PubChem PUG "
                "REST returns 404 for the name and for the CAS number "
                "8000-28-0, so no discrete CID resolves and no GHS "
                "classification is available. Recorded Not Classified rather "
                "than guessed. The DB carries essential oils under class keys "
                "('Essential Oils') and under named single-constituent keys "
                "(Linalool, Limonene); this is the label's own oil name and is "
                "kept separate for the same reason the DB keeps 'Basil Oil'.",
    },
    "Disodium 2-Sulfolaurate": {
        "s": "The disodium salt of 2-sulfolauric acid (CAS 68015-67-8); an "
             "anionic surfactant of the alpha-sulfo methyl ester class.",
        "ev": "Medium", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Graded from PubChem GHS (CID 23139701, returned title "
                "'Disodium 2-sulfolaurate'). The record carries H302, H315, "
                "H319 and H412 but every one sits at 11.1% notifier consensus, "
                "below the 40% house bar, so no dimension grade is minted and "
                "the key is recorded Not Classified. Named on Mrs. Meyer's own "
                "ingredient list for the Lavender Liquid Hand Soap.",
    },
    "Olea Europaea (Olive) Fruit Oil": {
        "s": "Olive fruit oil (CAS 8001-25-0); the emollient named on the "
             "label.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Mrs. Meyer's own ingredient list for the Lavender "
                "Liquid Hand Soap. This is a UVCB triglyceride oil: PubChem PUG "
                "REST returns 404 for the name and for the CAS number "
                "8001-25-0, so no discrete CID resolves and no GHS "
                "classification is available. Recorded Not Classified rather "
                "than guessed, the same way the DB already carries Brassica "
                "Campestris Seed Oil.",
    },
    "Polyoxyalkylene Substituted Chromophore (Cyan)": {
        "s": "A polymeric colourant (a polyoxyalkylene-substituted chromophore) "
             "used to tint the scent-booster beads; the label's own class term.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on P&G's own SmartLabel for Downy Unstopables In-Wash "
                "Scent Booster Beads, Fresh. This is a label class term for a "
                "proprietary polymeric dye, not a discrete substance: PubChem "
                "PUG REST returns 404 for the name, so no CID resolves and no "
                "GHS classification is available. Recorded Not Classified "
                "rather than guessed. Distinct from the DB's discrete dye keys "
                "(Acid Blue 9, Acid Blue 182, Acid Red 52 and so on); the DB "
                "already carries the sibling class term 'Polyoxyalkylene "
                "Substituted Chromophore' from the Tide PODS disclosure.",
    },
}

# --------------------------------------------------------------------------
# Owners. WD-40 Company is new to the registry; Reckitt, SC Johnson and
# Procter & Gamble are already recorded.
# --------------------------------------------------------------------------
NEW_OWNERS = {
    "WD-40 Company": {
        "type": "public (WDFC)",
        "detail": ("WD-40 Company, founded 1953, headquartered in San Diego, "
                   "California; trades on Nasdaq as WDFC. The company's own "
                   "10-K describes the household-cleaning family it assembled "
                   "by acquisition: 3-IN-ONE Oil (December 1995, from "
                   "affiliates of Reckitt & Colman), Lava heavy-duty hand "
                   "cleaner (April 1999, from Block Drug), Solvol (October "
                   "2000, from Unilever Australia), the Global Household "
                   "Brands -- 2000 Flushes and X-14 automatic toilet bowl "
                   "cleaners, X-14 hard surface cleaners and Carpet Fresh rug "
                   "and room deodorizers (April 2001) -- the Spot Shot brand "
                   "(May 2002, from Heartland Corporation) and the UK 1001 "
                   "line of carpet and household cleaners (April 2004, from PZ "
                   "Cussons). The filing describes Spot Shot as 'an aerosol "
                   "stain remover and a leading brand in the carpet stain "
                   "remover category'."),
        "ev": "verified",
        "src": WD40_OWNER_SRC,
        "brands": ["Spot Shot", "2000 Flushes", "X-14", "Carpet Fresh",
                   "WD-40", "3-IN-ONE", "Lava", "Solvol"],
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


# --------------------------------------------------------------------------
# Products. Every ingredient list below is the manufacturer's own published
# list, read 2026-10-07.
# --------------------------------------------------------------------------
PRODUCTS = [
    {
        "name": "Finish Jet-Dry Rinse Aid, Original",
        "brand": "Reckitt",
        "cat": "Dishwasher",
        "ings": ["Water", "Alcohols, C10-16, Ethoxylated", "Trideceth-3",
                 "Sodium Cumene Sulfonate", "Citric Acid", "Potassium Sorbate",
                 "Polyquaternium-2", "Acid Blue 9",
                 "Methylchloroisothiazolinone", "Methylisothiazolinone",
                 "Sodium Sulfate"],
        "source": ("Manufacturer ingredient disclosure (Reckitt, Finish "
                   "Jet-Dry Rinse Aid - Original, SmartLabel, in descending "
                   "weight percent within each category): Water (7732-18-5), "
                   "C10-16 Alcohols Ethoxylated Propoxylated (68551-13-3 or "
                   "120313-48-6 or 68439-51-0), Trideceth-3 (78330-21-9), "
                   "Sodium Cumene Sulfonate (28348-53-0), Citric Acid "
                   "(77-92-9), Potassium Sorbate (24634-61-5), "
                   "Polyquaternium-2 (68555-36-2), CI Acid Blue 9 (3844-45-9), "
                   "Methylchloroisothiazolinone (26172-55-4), "
                   "Methylisothiazolinone (2682-20-4), Sodium Sulfate "
                   "(7757-82-6)."),
        "source_url": JETDRY_URL,
        "note": ("A full intentionally-added list, published by the maker on "
                 "its own SmartLabel page. This is the first RINSE AID in the "
                 "corpus and a different function from every dishwasher "
                 "detergent already recorded: it is dispensed in the rinse "
                 "cycle, so the formula is a surfactant/hydrotrope/chelant "
                 "package with no builder, no bleach and no enzyme. The "
                 "surfactant pair (the C10-16 alcohol ethoxylate-propoxylate "
                 "and Trideceth-3) is what makes water sheet off the glass; "
                 "sodium cumene sulfonate is the hydrotrope, citric acid the "
                 "chelant, and the isothiazolinone pair (CMIT/MIT) the "
                 "preservative. The label's own precaution is 'CAUTION: MAY "
                 "IRRITATE EYES', which is consistent with the CMIT/MIT pair "
                 "the DB already grades F on the dermal dimension. The maker "
                 "sells the same product as a solid clip-on for machines "
                 "without a dispenser; that SKU is not the one recorded here."),
        "owner": "Reckitt", "owner_ev": "reported",
        "owner_src": RECKITT_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": JETDRY_URL,
        "tier_note": ("Sold at mass, grocery and club retailers; recorded as "
                      "mass. Channel evidence is the brand's own retail "
                      "placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A dishwasher rinse aid in the mass channel."),
    },
    {
        "name": "Mrs. Meyer's Clean Day Liquid Hand Soap, Lavender",
        "brand": "SC Johnson",
        "cat": "Hand Soap",
        "ings": ["Water", "Cocamidopropyl Hydroxysultaine",
                 "Sodium Methyl 2-Sulfolaurate", "Glycerin",
                 "Lavandula Angustifolia (Lavender) Oil",
                 "Citrus Aurantium Dulcis (Orange) Peel Oil", "Fragrance",
                 "Disodium 2-Sulfolaurate", "Olea Europaea (Olive) Fruit Oil",
                 "Aloe Barbadensis Leaf Juice", "Citric Acid",
                 "Sodium Chloride", "Polysorbate 20", "Potassium Sorbate",
                 "Sodium Benzoate"],
        "source": ("Manufacturer ingredient list (Mrs. Meyer's Clean Day, "
                   "Lavender Liquid Hand Soap, mrsmeyers.com product page, "
                   "read 2026-10-07): Water, Cocamidopropyl Hydroxysultaine, "
                   "Sodium Methyl 2-Sulfolaurate, Glycerin, Lavandula "
                   "Angustifolia (Lavender) Oil, Citrus Aurantium Dulcis "
                   "(Orange) Peel Oil, Fragrance, Disodium 2-Sulfolaurate, "
                   "Olea Europaea (Olive) Fruit Oil, Aloe Barbadensis Leaf "
                   "Juice, Citric Acid, Sodium Chloride, Potassium Sorbate, "
                   "Sodium Benzoate. The same company's product-information "
                   "PDF for the Lavender refill (pi.scjp.com, dated 01/2026) "
                   "prints the identical list and additionally names "
                   "Polysorbate 20 between Sodium Chloride and Potassium "
                   "Sorbate; the union is recorded and the difference is "
                   "stated rather than silently merged."),
        "source_url": MRSMEYERS_URL,
        "note": ("A full intentionally-added list, published by the maker on "
                 "its own product page. The surfactant pair is the "
                 "hydroxysultaine (a mild amphoteric) plus the alpha-sulfo "
                 "methyl ester pair (sodium methyl 2-sulfolaurate and its "
                 "disodium salt), which is the plant-derived system the brand "
                 "positions on; glycerin, olive oil and aloe are the "
                 "emollients, and potassium sorbate plus sodium benzoate the "
                 "preservative pair. The scent is carried by the lavender oil, "
                 "the orange peel oil and a fragrance blend. The brand's own "
                 "claims -- no parabens, no phthalates, no MEA or DEA, no "
                 "artificial colours, no SLS -- are consistent with the list: "
                 "none of those appears. The manufacturer's separate product-"
                 "information PDF for the refill adds Polysorbate 20, an "
                 "emulsifier; both documents are the manufacturer's own, and "
                 "the two lists are recorded as they are rather than "
                 "reconciled by guess."),
        "owner": "SC Johnson", "owner_ev": "verified",
        "owner_src": SCJ_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": MRSMEYERS_URL,
        "tier_note": ("Sold at mass, grocery and natural retailers and direct "
                      "from the brand; recorded as mass. Channel evidence is "
                      "the brand's own retail placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A liquid hand soap in the mass and natural channels."),
    },
    {
        "name": "Downy Unstopables In-Wash Scent Booster Beads, Fresh",
        "brand": "P&G",
        "cat": "Laundry",
        "ings": ["Polyethylene Glycol",
                 "Methyl Di-t-butyl Hydroxyhydrocinnamate", "Fragrance",
                 "Polyoxyalkylene Substituted Chromophore (Cyan)"],
        "source": ("Manufacturer ingredient disclosure (Procter & Gamble, "
                   "Downy Unstopables In-Wash Scent Booster Beads, Fresh "
                   "Scent, 24 oz, SmartLabel, information last updated "
                   "2024-12-28 by Downy): Polyethylene Glycol, Methyl "
                   "Di-t-butyl Hydroxyhydrocinnamate, Fragrance, "
                   "Polyoxyalkylene Substituted Chromophore (Cyan)."),
        "source_url": DOWNY_URL,
        "note": ("A full intentionally-added list for the current US core "
                 "product, published by the maker on its own SmartLabel page. "
                 "This is the first in-wash SCENT BOOSTER in the corpus and a "
                 "different delivery form from every laundry product already "
                 "recorded: a solid polyethylene-glycol bead added alongside "
                 "the detergent, carrying fragrance rather than cleaning "
                 "actives. The list is short by design -- the bead is PEG "
                 "carrier plus fragrance, with methyl di-t-butyl "
                 "hydroxyhydrocinnamate as the antioxidant that stabilises the "
                 "scent and a polymeric cyan chromophore as the tint. The "
                 "fragrance is disclosed as a single 'Fragrance' entry, which "
                 "is P&G's SmartLabel convention for this product; the DB "
                 "carries that under its existing 'Fragrance' key. The DB "
                 "already grades methyl di-t-butyl hydroxyhydrocinnamate env D "
                 "(H411 at 99.7% consensus) from the Tide PODS disclosure."),
        "owner": "Procter & Gamble", "owner_ev": "verified",
        "owner_src": PG_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": DOWNY_URL,
        "tier_note": ("Sold at mass, grocery and club retailers; recorded as "
                      "mass. Channel evidence is the brand's own retail "
                      "placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("An in-wash laundry scent booster in the mass channel."),
    },
    {
        "name": "Spot Shot Instant Carpet Stain Remover (Aerosol)",
        "brand": "WD-40 Company",
        "cat": "Floor & Carpet",
        "ings": ["2-(2-Butoxyethoxy)ethanol", "Butyloxyethanol",
                 "Liquefied Petroleum Gas"],
        "source": ("Manufacturer safety data sheet (WD-40 Company, Spot Shot "
                   "Instant Carpet Stain Remover Aerosol, US GHS SDS, section "
                   "3): 2-(2-Butoxyethoxy)ethanol (112-34-5, <10%, Eye "
                   "Irritation Category 2A), 2-Butoxyethanol (111-76-2, <5%, "
                   "Acute Oral Toxicity Category 4 and further), Liquefied "
                   "Petroleum Gas (68476-85-7, <10%, Flammable Gas Category 1, "
                   "Gas Under Pressure, Compressed). The sheet states the "
                   "exact percentages are a trade secret."),
        "source_url": SPOTSHOT_URL,
        "note": ("A PARTIAL disclosure, and the honest edge of the tool: the "
                 "SDS names only the components that cross the hazard "
                 "disclosure threshold and states the exact percentages are a "
                 "trade secret. The formula is a water-based aerosol carpet "
                 "stain remover -- the two glycol ethers are the solvent pair "
                 "and liquefied petroleum gas is the propellant -- and water "
                 "plus the unnamed surfactant/polymer package is the balance. "
                 "The manufacturer's separate SDS for the trigger format of "
                 "the same product family is thinner still: it declares a "
                 "'Detergent Polymer' at 1-10% and states the balance is water "
                 "and non-hazardous ingredients, naming no other substance. "
                 "Because the non-hazardous fraction is unnamed, the list "
                 "below is what the manufacturer discloses, not a full "
                 "intentionally-added list. WD-40 Company acquired the brand "
                 "in May 2002 from Heartland Corporation and describes it in "
                 "its own 10-K as a leading brand in the carpet stain remover "
                 "category."),
        "owner": "WD-40 Company", "owner_ev": "verified",
        "owner_src": WD40_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": SPOTSHOT_URL,
        "tier_note": ("Sold at mass, grocery, club, hardware and home-center "
                      "retailers; recorded as mass. Channel evidence is the "
                      "acquirer's own 10-K description of the brand's retail "
                      "placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "partial",
        "added": TODAY, "updated": TODAY,
        **exp_untested("An aerosol carpet stain remover in the mass channel."),
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
                     "disclosures read 2026-10-07 -- Finish Jet-Dry Rinse Aid "
                     "Original (full SmartLabel list with CAS, rbnainfo.com), "
                     "Mrs. Meyer's Clean Day Liquid Hand Soap Lavender (full "
                     "per-SKU list, mrsmeyers.com, with the company's own "
                     "refill PDF adding Polysorbate 20), Downy Unstopables "
                     "In-Wash Scent Booster Beads Fresh (full SmartLabel "
                     "list, smartlabel.pg.com) and Spot Shot Instant Carpet "
                     "Stain Remover Aerosol (SDS section 3, hazardous "
                     "components only, files.wd40.com). Two brand families new "
                     "to the corpus: Mrs. Meyer's hand soap (the brand was "
                     "already carried for multi-surface and dish) and WD-40 "
                     "Company (owner-registry entry added, verified against "
                     "its own SEC 10-K). Eight new ingredient keys, ALL "
                     "recorded Not Classified with an explicit sourcing note "
                     "-- seven resolve to no PubChem CID or no GHS section "
                     "(Trideceth-3, Polyquaternium-2, Cocamidopropyl "
                     "Hydroxysultaine, Sodium Methyl 2-Sulfolaurate, Lavandula "
                     "Angustifolia (Lavender) Oil, Olea Europaea (Olive) Fruit "
                     "Oil, Polyoxyalkylene Substituted Chromophore (Cyan)) and "
                     "one (Disodium 2-Sulfolaurate) has H-codes only at 11.1% "
                     "consensus, below the 40% house bar. Four label terms were "
                     "ALIASED to keys the DB already carries instead of being "
                     "re-minted: C10-16 Alcohols Ethoxylated Propoxylated -> "
                     "Alcohols, C10-16, Ethoxylated; CI Acid Blue 9 -> Acid "
                     "Blue 9; Sodium Cumene Sulfonate -> Sodium "
                     "Cumenesulfonate (the pair the Sifter sort lane merged "
                     "2026-10-04); and 2-(2-Butoxyethoxy)ethanol -> Diethylene "
                     "Glycol Monobutyl Ether (same CAS 112-34-5). Two of those "
                     "aliases land on already-graded keys, so the verified "
                     "grade reaches these products rather than a fresh "
                     "ungraded duplicate. Fills three gaps: the first "
                     "dishwasher RINSE AID (Dishwasher had 16 products and no "
                     "rinse aid), the first in-wash laundry SCENT BOOSTER "
                     "(Laundry had 45 products and no scent booster) and the "
                     "first WD-40 Company product in the thinnest "
                     "non-specialty category (Floor & Carpet, 14 products)."),
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
