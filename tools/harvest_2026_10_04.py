#!/usr/bin/env python3
"""Night-shift station 2 harvest, 2026-10-04 (Dolman).

Ordered by EXPOSURE, not price tier (Trellis, Sep 22 2026). Every ingredient
list below is the intentionally-added list from a manufacturer California
SB-258 ingredient-disclosure filing, read TODAY, 2026-10-04, from KIK Consumer
Products' own disclosure index at https://www.kikcorp.com/ingredients/ .

Why this block. Previous station-2 fires took the Walmart house brand, the
branded value all-purpose cleaners, the value bleach shelf, and the bathroom /
glass / cleanser / ammonia shelf. What remained unread on the same index is the
**value bathroom, bleach and drain shelf** -- the products that sit at the
bottom of the price ladder in the rooms people clean most often. The dollar
channel is the thinnest and highest-need tier in the spectrum (SPX-001), and
this block is where its toilet, bathroom and bleach chemistry lives.

Three findings this block produces, each legible from the filings alone:

  1. **The value bleach formula is one formula.** Water / sodium hypochlorite /
     sodium hydroxide is the COMPLETE disclosed list on The Works Cleaning
     Bleach and Top Job Low-Strength Bleach -- two brands, two price points,
     three chemicals. The scented Comet Low-Splash Bleach adds only a
     surfactant and a fragrance. This is the fifth instance of the
     one-formula-many-brands pattern in this database.
  2. **A bleach TABLET is not bleach chemistry.** The Works Toilet Bowl Cleaner
     with Bleach (tablets) discloses three chlorinated hydantoins -- BCDMH,
     DCDMH and a third -- plus sodium chloride. No hypochlorite anywhere. The
     "with bleach" on the pack is a chlorinating agent, and it is a different
     substance class from the liquid bleach on the shelf beside it.
  3. **The value bathroom bleach cleaner is the same five lines across
     brands.** Top Job Bathroom Cleaner with Bleach and Top Job Basic All
     Purpose Cleaner with Bleach disclose an identical five-line list, and it
     is the same list as The Works Basic Bathroom Cleaner with Bleach and Comet
     Classic Foaming Bath Cleaner (both already in the corpus) -- four
     products, three brands, two price points, one formula.

Nothing here is graded. Product grading is the Sifter lane; a blank as-sold
grade is the honest state. No substitutes are owed by the grade rule, but
substitutes are supplied on the bleach and acid products because a reader can
act on those today.

Idempotent: a product whose `name` already exists is skipped, an ingredient key
already present is left untouched, and a second run reports 0 added.

Usage:  python3 tools/harvest_2026_10_04.py [--dry-run] [--no-changelog]
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-04"

DRY = "--dry-run" in sys.argv
NO_CHANGELOG = "--no-changelog" in sys.argv

KIK_INDEX = "https://www.kikcorp.com/ingredients/"
KIK_PRODUCTS = "https://www.kikcorp.com/our-products/"
SEC_APA = ("https://www.sec.gov/Archives/edgar/data/1295947/000129594718000020/"
           "exhibit101-assetpurchaseag.htm")

# Served, machine-readable retailer pages read 2026-10-04. Both return HTTP 200
# with the product name in og:title (checked by curl with a browser UA).
DG_WORKS = ("https://www.dollargeneral.com/p/"
            "the-works-disinfectant-toilet-bowl-cleaner-32-oz/74157033105")
DG_TOPJOB = ("https://www.dollargeneral.com/p/"
             "top-job-bathroom-cleaner-with-bleach-32-oz/836272010573")

IB_SURFACE = ("https://www.indexbox.io/store/"
              "united-states-household-surface-cleaners-market-analysis-"
              "forecast-size-trends-and-insights/")
IB_BLEACH = ("https://www.indexbox.io/store/"
             "united-states-bleach-market-analysis-forecast-size-trends-"
             "and-insights/")
IB_TOILET = ("https://www.indexbox.io/store/"
             "united-states-toilet-cleaning-products-market-analysis-"
             "forecast-size-trends-and-insights/")

U = "https://www.kikcorp.com/wp-content/uploads/"

# --------------------------------------------------------------------------
# Ingredient key resolution. Label wording -> existing canonical key, where the
# substance is the same and a second key would be a synonym for one CAS.
# --------------------------------------------------------------------------
ALIASES = {
    # The filings say "Fragrance Ingredients" / "Fragrance ingredients".
    "Fragrance Ingredients": "Fragrance",
    # Same CAS 112-34-5 as the existing key (Linnea R1, 2026-09-30).
    "Butoxydiglycol": "Diethylene Glycol Monobutyl Ether",
}

# New keys minted this fire. Shape follows the registry's existing entries:
# ungraded is recorded as ev "Low" with g null, never a guess.
NEW_KEYS = {
    # --- The chlorinated hydantoin trio on the bleach tablet ---------------
    "1-Bromo-3-chloro-5,5-dimethylimidazolidine-2,4-dione": {
        "s": "1-Bromo-3-chloro-5,5-dimethylhydantoin (BCDMH), a chlorinating "
             "and brominating agent used in toilet-bowl and spa tablets; "
             "CAS 16079-88-2.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on The Works Toilet Bowl Cleaner with Bleach (tablets) "
                "disclosure, 2019-12-27, with CAS 16079-88-2, as an "
                "antimicrobial active. Not yet graded. This is the substance "
                "behind a 'with bleach' claim on a tablet; it is not sodium "
                "hypochlorite, and it releases a bromine/chlorine species in "
                "water rather than hypochlorite.",
    },
    "1,3-Dichloro-5,5-dimethylhydantoin": {
        "s": "1,3-Dichloro-5,5-dimethylhydantoin (DCDMH), a chlorinating "
             "agent used in toilet-bowl and spa tablets; CAS 118-52-5.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on The Works Toilet Bowl Cleaner with Bleach (tablets) "
                "disclosure, 2019-12-27, with CAS 118-52-5, as an "
                "antimicrobial active. Not yet graded. A chlorinated "
                "hydantoin, not a hypochlorite.",
    },
    "1,3-Dichloro-5-ethyl-5-methylimidazolidine-2,4-dione": {
        "s": "1,3-Dichloro-5-ethyl-5-methylhydantoin, a chlorinating agent "
             "used in toilet-bowl and spa tablets; CAS 89415-87-2.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on The Works Toilet Bowl Cleaner with Bleach (tablets) "
                "disclosure, 2019-12-27, with CAS 89415-87-2, as an "
                "antimicrobial active. Not yet graded. Third of the three "
                "chlorinated hydantoins on the same tablet.",
    },
    # --- Named fatty acids from the Austin's drain opener ------------------
    "Myristic Acid": {
        "s": "Myristic acid (tetradecanoic acid), a saturated C14 fatty acid; "
             "CAS 544-63-8.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Austin's Wipe Away Professional Drain Opener "
                "disclosure, 2019-08-21, with CAS 544-63-8, as a surfactant. "
                "Not yet graded. Kept as its own key rather than folded into "
                "a mixed fatty-acid record: the filing names the individual "
                "acid and gives its own CAS.",
    },
    "Stearic Acid": {
        "s": "Stearic acid (octadecanoic acid), a saturated C18 fatty acid; "
             "CAS 57-11-4.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Austin's Wipe Away Professional Drain Opener "
                "disclosure, 2019-08-21, with CAS 57-11-4, as a surfactant. "
                "Not yet graded.",
    },
    "Palmitic Acid": {
        "s": "Palmitic acid (hexadecanoic acid), a saturated C16 fatty acid; "
             "CAS 57-10-3.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Austin's Wipe Away Professional Drain Opener "
                "disclosure, 2019-08-21, with CAS 57-10-3, as a surfactant. "
                "Not yet graded.",
    },
    "Caprylic Acid": {
        "s": "Caprylic acid (octanoic acid), a saturated C8 fatty acid; "
             "CAS 124-07-2.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Austin's Wipe Away Professional Drain Opener "
                "disclosure, 2019-08-21, with CAS 124-07-2, as a surfactant. "
                "Not yet graded. Kept separate from Sodium Caprylate, which "
                "is the salt, a different substance.",
    },
    "Capric Acid": {
        "s": "Capric acid (decanoic acid), a saturated C10 fatty acid; "
             "CAS 334-48-5.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Austin's Wipe Away Professional Drain Opener "
                "disclosure, 2019-08-21, with CAS 334-48-5, as a surfactant. "
                "Not yet graded.",
    },
    "Oleic Acid": {
        "s": "Oleic acid, a monounsaturated C18 fatty acid; CAS 112-80-1.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Austin's Wipe Away Professional Drain Opener "
                "disclosure, 2019-08-21, with CAS 112-80-1, as a surfactant. "
                "Not yet graded.",
    },
    # --- Fragrance allergen -------------------------------------------------
    "Benzyl Salicylate": {
        "s": "Benzyl salicylate, a fragrance material; CAS 118-58-1. Listed "
             "on Annex III of the EU Cosmetics Regulation as a fragrance "
             "allergen that must be declared above 0.01%.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Spic and Span Sun Fresh Extra Strength Powder "
                "disclosure, 2019-10-18, with CAS 118-58-1, flagged by the "
                "filing itself as an EU fragrance allergen. Not yet graded "
                "here; the grading lane should resolve it, because it is a "
                "declared allergen on a scented value powder cleanser.",
    },
    # --- Unidentified constituents (the disclosure names a class, not a
    #     substance). Recorded as such rather than folded into a guess. ------
    "Proprietary Chelating Agent": {
        "s": "A chelating agent named only by function on the disclosure; "
             "identity withheld as proprietary, CAS not available.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Comet Classic Shower Cleaner disclosure, "
                "2019-03-25, as 'Proprietary chelating agent' with CAS not "
                "available. The manufacturer disclosed the function and "
                "withheld the identity. Recorded as an unidentified "
                "constituent, not as a substance; this renders as not "
                "disclosed, which is the honest state.",
    },
    "Proprietary Surfactant": {
        "s": "A surfactant named only by function on the disclosure; identity "
             "withheld as proprietary, CAS not available.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Comet Classic Shower Cleaner disclosure, "
                "2019-03-25, as 'Proprietary surfactant' with CAS not "
                "available. Recorded as an unidentified constituent rather "
                "than folded into a guessed surfactant key.",
    },
    "Alkoxylated Amine Compound": {
        "s": "An alkoxylated amine, a class of ethoxylated/propoxylated amine "
             "used as a thickener and surfactant; exact identity proprietary, "
             "CAS not disclosed.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on The Works Professional Strength Drain Opener "
                "disclosure, 2019-12-27, as 'Alkoxylated Amine Compound' with "
                "CAS 'Proprietary', as a thickener. Recorded as an "
                "unidentified constituent rather than a specific amine.",
    },
}


# --------------------------------------------------------------------------
# Exposure helpers. One per category source, each quoting the figure verbatim
# and stating what was searched for a direct per-product figure.
# --------------------------------------------------------------------------
def exp_surface(cat_note: str) -> dict:
    return {
        "exposure_ev": "extrapolated",
        "exposure_src": IB_SURFACE,
        "exposure_basis": (
            "Derived, not measured. The source states that approximately 95 "
            "percent of U.S. households use at least one surface cleaner "
            "product per month, that specialised cleaners (bathroom, kitchen, "
            "glass, floor) collectively represent an estimated 30 to 35 percent "
            "of category value with bathroom cleaners the largest sub-segment, "
            "and that private-label store brands account for an estimated 20 to "
            "25 percent of unit sales in 2025-2026. Searched for a published "
            "per-product US household-penetration figure for this product and "
            "located none; brand shares are reported by company, not by value "
            "brand. The estimate therefore derives from category penetration "
            "and the product's position as one value brand inside a "
            "sub-segment, and stops there. Rounded to one significant figure, "
            "order-of-magnitude. " + cat_note
        ),
    }


def exp_bleach(cat_note: str) -> dict:
    return {
        "exposure_ev": "extrapolated",
        "exposure_src": IB_BLEACH,
        "exposure_basis": (
            "Derived, not measured. The source states that the US bleach "
            "market has 'near-universal household penetration (estimated at "
            "80-90% of United States households purchase bleach at least once "
            "per year)' and that private-label and store-brand products now "
            "account for an estimated 25-35% of retail volume, up from roughly "
            "15-20% a decade ago. Searched for a published per-product US "
            "household-penetration figure for this specific value-brand bleach "
            "and located none; brand shares are reported at company level and "
            "the value tier is fragmented across many small labels. The "
            "estimate therefore derives from category penetration and the "
            "product's position as one value-tier label inside a "
            "fragmented tier, and stops there. Rounded to one significant "
            "figure, order-of-magnitude. " + cat_note
        ),
    }


def exp_toilet(cat_note: str) -> dict:
    return {
        "exposure_ev": "extrapolated",
        "exposure_src": IB_TOILET,
        "exposure_basis": (
            "Derived, not measured. The source states that residential "
            "households account for roughly 55-60% of US toilet-cleaning "
            "product volume, that the residential segment is highly fragmented "
            "across about 130 million households, and that automatic in-tank "
            "tablets are among the fastest-growing formats at 5-7% annual "
            "rates off a small base. Searched for a published per-product US "
            "household-penetration figure for this specific tablet and located "
            "none; the format is a minority of the category. The estimate "
            "derives from category penetration and the product's position as "
            "one value-brand tablet in a small format, and stops there. "
            "Rounded to one significant figure, order-of-magnitude. "
            + cat_note
        ),
    }


def sub(name, tier, note):
    return {"name": name, "tier": tier, "note": note}


BLEACH_NaOH = ("The hazard on this bottle is the sodium hypochlorite and the "
               "sodium hydroxide, which is the same hazard on every liquid "
               "bleach. If bleach is the concern, no bleach cleaner is a "
               "substitute for it; the alternative is a non-bleach cleaner "
               "for the same room at the same price.")
DRAIN_MIX = ("Strong alkaline or acid drain openers must never be mixed with "
             "each other or with a bleach product; the hazard is the mixing "
             "as much as the bottle.")


# --------------------------------------------------------------------------
# Products. Every ings list below is the filing's intentionally-added list,
# read 2026-10-04.
# --------------------------------------------------------------------------
PRODUCTS = [
    # ---- The Works (HomeCare Labs / KIK). Dollar-channel value brand. -----
    {
        "name": "The Works Toilet Bowl Cleaner with Bleach",
        "brand": "The Works",
        "cat": "Bathroom",
        "ings": ["1-Bromo-3-chloro-5,5-dimethylimidazolidine-2,4-dione",
                 "1,3-Dichloro-5,5-dimethylhydantoin",
                 "1,3-Dichloro-5-ethyl-5-methylimidazolidine-2,4-dione",
                 "Sodium Chloride"],
        "source": ("HomeCare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "The Works Toilet Bowl Cleaner with Bleach, tablets, "
                   "2x6x3.5 oz. UPC 0-74157-03201-6, disclosure dated "
                   "2019-12-27. Four intentionally added ingredients with CAS "
                   "numbers."),
        "source_url": U + "2019/05/The-Works_Toilet-Bowl-Cleaner-with-Bleach-2x6x3.5oz_0-74157-03201-6.pdf",
        "note": ("Four lines, and none of them is bleach. The 'with bleach' "
                 "on the pack is three chlorinated hydantoins (BCDMH, DCDMH "
                 "and a third) plus salt. A hydantoin tablet releases a "
                 "chlorine/bromine species in water; it is a different "
                 "substance class from the liquid sodium hypochlorite on the "
                 "shelf beside it, and a reader comparing the two labels "
                 "would not guess that from the front of the pack. Never put "
                 "a tablet like this in a bowl that already has an acid or "
                 "ammonia cleaner in it."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "dollar-store", "tier_ev": "reported", "tier_src": DG_WORKS,
        "tier_note": ("The Works is a dollar-channel value brand. Dollar "
                      "General's own product page for the brand's liquid "
                      "toilet bowl cleaner is the served source; brand-level "
                      "channel evidence, not per-SKU."),
        "substitutes": [sub("The Works Toilet Bowl Cleaner", "dollar-store",
                            "Same brand and price band, a liquid instead of a "
                            "tablet. It is a hydrochloric-acid cleaner, so it "
                            "is a different hazard, not a smaller one; it "
                            "avoids the hydantoin actives and the "
                            "chlorine/bromine release. Do not use it in the "
                            "same session as any bleach or tablet product.")],
        "exposure": 2,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_toilet("A dollar-channel bleach tablet; in-tank tablets are a "
                     "small, fast-growing format."),
    },
    {
        "name": "The Works Cleaning Bleach",
        "brand": "The Works",
        "cat": "Disinfectant",
        "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide"],
        "source": ("HomeCare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "The Works Cleaning Bleach, liquid bleach, 128 oz. UPC "
                   "0-74157-64252-9, disclosure dated 2019-08-08. Three "
                   "intentionally added ingredients; sodium hydroxide flagged "
                   "on the California non-cancer hazards list."),
        "source_url": U + "2019/10/The-Works_Cleaning-Bleach-128oz_0-74157-64252-9.pdf",
        "note": ("Three lines: water, bleach, and the hydroxide that keeps it "
                 "stable. That is the complete disclosed formula on a gallon "
                 "of dollar-channel bleach, and it is the same three "
                 "chemicals Top Job Low-Strength Bleach discloses under "
                 "another label. The cheapest bleach and the mid-priced "
                 "bleach are the same bottle with a different name; what you "
                 "pay for is the label."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "dollar-store", "tier_ev": "reported", "tier_src": DG_WORKS,
        "tier_note": ("The Works is a dollar-channel value brand. Dollar "
                      "General's own product page for the brand's toilet bowl "
                      "cleaner is the served source; brand-level channel "
                      "evidence, not per-SKU."),
        "substitutes": [sub("Clorox Bleach", "mass",
                            "A mainstream liquid bleach in a comparable size "
                            "band. Same active at the same strength; the "
                            "difference is the price and the brand. " +
                            BLEACH_NaOH)],
        "exposure": 2,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_bleach("A dollar-channel liquid bleach, the cheapest label in a "
                     "fragmented value tier."),
    },
    {
        "name": "The Works Professional Strength Drain Opener",
        "brand": "The Works",
        "cat": "Specialty",
        "ings": ["Water", "Hydrochloric Acid", "Methenamine",
                 "Ethoxylated C8-18 and C18-unsatd. Alkylamines",
                 "Diethylene Glycol", "Isopropanol", "BHT", "Acetic Acid",
                 "Alkoxylated Amine Compound"],
        "source": ("HomeCare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "The Works Professional Strength Drain Opener, 64 oz. UPC "
                   "0-74157-03360-0, disclosure dated 2019-12-27. Nine "
                   "intentionally added ingredients with CAS numbers except "
                   "the thickener, which is listed as 'Alkoxylated Amine "
                   "Compound' with CAS 'Proprietary'; hydrochloric acid and "
                   "isopropanol are flagged on the California non-cancer "
                   "hazards list."),
        "source_url": U + "2019/05/The-Works_Professional-Strength-Drain-Opener-64oz_0-74157-03360-0.pdf",
        "note": ("An acid drain opener, not an alkaline one: hydrochloric and "
                 "acetic acid do the work, methenamine and a glycol keep the "
                 "metal safe, and an alkoxylated amine thickens it. Nine "
                 "lines, one of them a class rather than a substance. " +
                 DRAIN_MIX + " An acid opener is the one you must never "
                 "follow with a bleach-based gel."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "dollar-store", "tier_ev": "reported", "tier_src": DG_WORKS,
        "tier_note": ("The Works is a dollar-channel value brand. Dollar "
                      "General's own product page for the brand's toilet bowl "
                      "cleaner is the served source; brand-level channel "
                      "evidence, not per-SKU."),
        "substitutes": [sub("Drano Max Gel", "mass",
                            "A mainstream gel drain opener in the same price "
                            "band. It is alkaline rather than acid, so the "
                            "mixing rule is unchanged but reversed; it avoids "
                            "the hydrochloric acid. " + DRAIN_MIX)],
        "exposure": 2,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_surface("A dollar-channel drain opener; drain openers are a "
                      "small specialty segment."),
    },

    # ---- Top Job (KIK). Value bleach and bathroom staples. ----------------
    {
        "name": "Top Job Bathroom Cleaner with Bleach",
        "brand": "Top Job",
        "cat": "Bathroom",
        "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide",
                 "Lauramine Oxide", "Fragrance Ingredients"],
        "source": ("KIK International LLC / KIK Consumer Products California "
                   "Cleaning Product Right to Know (SB-258) ingredient "
                   "disclosure for Top Job Bathroom Cleaner with Bleach, 32 "
                   "oz. UPC 8-36272-01057-3, disclosure dated 2019-08-08. "
                   "Five intentionally added ingredients; sodium hydroxide "
                   "flagged on the California non-cancer hazards list."),
        "source_url": U + "2019/10/Top-Job_Bathroom-Cleaner-with-Bleach-32oz_8-36272-01057-3.pdf",
        "note": ("Five lines, and they are the same five lines as The Works "
                 "Basic Bathroom Cleaner with Bleach and Comet Classic "
                 "Foaming Bath Cleaner already in this database. Water, "
                 "bleach, the hydroxide that stabilises it, one surfactant "
                 "and a fragrance. Four products, three brands, two price "
                 "points, one formula. Dollar General sells this exact bottle "
                 "for about a dollar, and the bottle beside it costs several "
                 "times that for the same chemistry."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "dollar-store", "tier_ev": "reported", "tier_src": DG_TOPJOB,
        "tier_note": ("Dollar General's own product page for this exact "
                      "product (UPC 836272010573) is a served, machine-"
                      "readable page showing it in the dollar channel at $1. "
                      "Product-level channel evidence."),
        "substitutes": [sub("Comet Bath Cleaner, 32 oz", "mass",
                            "A non-bleach bathroom cleaner at a comparable "
                            "value price. Avoids the hypochlorite and the "
                            "hydroxide; it is a citric-acid formula, so it "
                            "does the same room without the bleach. " +
                            BLEACH_NaOH)],
        "exposure": 4,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_surface("A dollar-channel bleach bathroom cleaner; the bathroom "
                      "sub-segment is the largest of the specialised "
                      "cleaners."),
    },
    {
        "name": "Top Job Basic All Purpose Cleaner with Bleach",
        "brand": "Top Job",
        "cat": "All-Purpose",
        "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide",
                 "Lauramine Oxide", "Fragrance Ingredients"],
        "source": ("KIK International LLC / KIK Consumer Products California "
                   "Cleaning Product Right to Know (SB-258) ingredient "
                   "disclosure for Top Job Basic All Purpose Cleaner with "
                   "Bleach, 32 oz. UPC 8-36272-01040-5, disclosure dated "
                   "2019-08-08. Five intentionally added ingredients; sodium "
                   "hydroxide flagged on the California non-cancer hazards "
                   "list."),
        "source_url": U + "2019/10/Top-Job_Basic-All-purpose-cleaner-with-Bleach-32oz_8-36272-01040-5.pdf",
        "note": ("The identical five-line list to Top Job Bathroom Cleaner "
                 "with Bleach from the same manufacturer, on the same date, "
                 "under a different product name and a different pack. Two "
                 "labels for the same bottle of value bleach cleaner. If you "
                 "are choosing between the 'bathroom' and the 'all purpose' "
                 "version of this brand, you are choosing a word on the "
                 "label, not a formula."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Top Job is a KIK-branded value household cleaner; the "
                      "manufacturer's own product page names it as one of the "
                      "brands its U.S. household business markets. "
                      "Market-position vocabulary, not a single retail "
                      "channel."),
        "substitutes": [sub("Comet Classic All Purpose Cleaner with Bleach",
                            "mass",
                            "Same manufacturer, same value price band, same "
                            "job. Read its list before switching; it is also "
                            "a bleach all-purpose cleaner, so the bleach is "
                            "not avoided, only the label changes.")],
        "exposure": 3,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_surface("A value all-purpose bleach cleaner; all-purpose "
                      "cleaners are the largest single surface-cleaner "
                      "segment."),
    },
    {
        "name": "Top Job Low-Strength Bleach",
        "brand": "Top Job",
        "cat": "Disinfectant",
        "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide"],
        "source": ("KIK International LLC / KIK Consumer Products California "
                   "Cleaning Product Right to Know (SB-258) ingredient "
                   "disclosure for Top Job Low-Strength Bleach, liquid "
                   "bleach, 64 oz. UPC 8-36272-01069-6, disclosure dated "
                   "2019-12-06. Three intentionally added ingredients; sodium "
                   "hydroxide flagged on the California non-cancer hazards "
                   "list."),
        "source_url": U + "2019/12/Top-Job_-Low-Strength-Bleach-64oz_8-36272-01069-6.pdf",
        "note": ("Three lines: water, bleach, hydroxide. The same three "
                 "chemicals as The Works Cleaning Bleach under a different "
                 "label. 'Low-strength' names the concentration, not the "
                 "ingredients; the list is identical to the full-strength "
                 "value bleach, and the difference is how much hypochlorite "
                 "is in the water, which the label states and the ingredient "
                 "list does not."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Top Job is a KIK-branded value household cleaner. "
                      "Market-position vocabulary, not a single retail "
                      "channel."),
        "substitutes": [sub("Top Job Clear Ammonia", "mass",
                            "Same brand and price band, a non-bleach "
                            "ammonia cleaner for glass and general surfaces. "
                            "Different hazard, not a smaller one; it avoids "
                            "the hypochlorite. Never mix the two.")],
        "exposure": 2,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_bleach("A value low-strength liquid bleach."),
    },

    # ---- Comet (HomeCare Labs / KIK). -------------------------------------
    {
        "name": "Comet Low-Splash Bleach Spring Flower Scent",
        "brand": "Comet",
        "cat": "Disinfectant",
        "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide",
                 "Myristamine Oxide", "Coconut Fatty Acid",
                 "Fragrance Ingredients"],
        "source": ("Homecare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "Comet Low-Splash Bleach Spring Flower Scent, liquid "
                   "bleach, 32 oz. UPC 8-10003-44044-0, disclosure dated "
                   "2019-11-27. Six intentionally added ingredients; sodium "
                   "hydroxide flagged on the California non-cancer hazards "
                   "list."),
        "source_url": U + "2019/12/Comet_Low-Splash-Bleach-Spring-Flower-Scent-32oz_8-10003-44044-0.pdf",
        "note": ("The value bleach formula plus two lines: a surfactant and a "
                 "fragrance, which is what makes it low-splash and scented. "
                 "Six lines total. The unscented Comet and The Works bleaches "
                 "disclose three; this one adds a surfactant and a fragrance "
                 "and nothing else. If fragrance is the concern, the "
                 "unscented bleach on the same shelf is the shorter list."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Comet is a KIK-branded value household cleaner; the "
                      "manufacturer's own product page names it as one of the "
                      "brands its U.S. household business markets. "
                      "Market-position vocabulary, not a single retail "
                      "channel."),
        "substitutes": [sub("The Works Cleaning Bleach", "dollar-store",
                            "A dollar-channel unscented bleach with three "
                            "disclosed lines instead of six. Avoids the "
                            "fragrance and the surfactant; the bleach and the "
                            "hydroxide are the same. " + BLEACH_NaOH)],
        "exposure": 3,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_bleach("A value scented low-splash bleach."),
    },
    {
        "name": "Comet Classic Shower Cleaner",
        "brand": "Comet",
        "cat": "Bathroom",
        "ings": ["Water", "Proprietary Chelating Agent",
                 "Proprietary Surfactant", "Sodium Hydroxide",
                 "Benzisothiazolinone"],
        "source": ("Homecare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "Comet Classic Shower Cleaner, liquid trigger spray, 24 "
                   "oz. UPC 8-10003-44009-9, disclosure dated 2019-03-25. "
                   "Five intentionally added ingredients; two are named only "
                   "by function ('Proprietary chelating agent', 'Proprietary "
                   "surfactant') with CAS not available, and sodium hydroxide "
                   "is flagged on the California non-cancer hazards list."),
        "source_url": U + "2019/10/Comet-Classic-Shower-Cleaner-24oz_8-10003-44009-9.pdf",
        "note": ("Five lines, and two of them are classes rather than "
                 "substances: the manufacturer disclosed a chelating agent "
                 "and a surfactant and withheld what they are. This is the "
                 "honest edge of the tool. A reader can see the hydroxide and "
                 "the preservative by name, and can see plainly that two "
                 "other lines were withheld. That renders as not disclosed, "
                 "not as a blank, and not as a short clean list."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Comet is a KIK-branded value household cleaner. "
                      "Market-position vocabulary, not a single retail "
                      "channel."),
        "substitutes": [sub("Comet Bath Cleaner, 32 oz", "mass",
                            "Same brand and price band, and every one of its "
                            "eight lines is identified. It is a citric-acid "
                            "bathroom cleaner rather than a shower spray; it "
                            "avoids the withheld constituents and the "
                            "hydroxide.")],
        "exposure": 3,
        "strength_disclosure": "partial",
        "added": TODAY, "updated": TODAY,
        **exp_surface("A value shower cleaner; bathroom cleaners are the "
                      "largest sub-segment of the specialised cleaners."),
    },

    # ---- Spic and Span (Homecare Labs / KIK). -----------------------------
    {
        "name": "Spic and Span Sun Fresh Extra Strength Powder",
        "brand": "Spic and Span",
        "cat": "Abrasive Cleanser",
        "ings": ["Sodium Sulfate", "Sodium Carbonate",
                 "Sodium Dodecylbenzenesulfonate", "Sodium Silicate",
                 "Sodium Polyacrylate", "Hexyl Cinnamal", "Benzyl Salicylate",
                 "alpha-Isomethyl Ionone", "Limonene"],
        "source": ("Homecare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "Spic and Span Sun Fresh Extra Strength Powder, powder "
                   "cleanser, 27 oz. UPC 8-11435-00190-2, disclosure dated "
                   "2019-10-18. Nine intentionally added ingredients with CAS "
                   "numbers; sodium sulfate is flagged on the California "
                   "non-cancer hazards list and three fragrance ingredients "
                   "(hexyl cinnamal, benzyl salicylate, alpha-isomethyl "
                   "ionone) plus limonene are flagged as EU fragrance "
                   "allergens."),
        "source_url": U + "2019/10/SNS_Sun-Fresh-Extra-Strength-Powder-27oz_8-11435-00190-2.pdf",
        "note": ("A powder cleanser: sulfate and carbonate as the bulk and "
                 "builder, a sulfonate and a polyacrylate as the cleaning "
                 "and anti-redeposition agents, silicate for the scouring, "
                 "and four fragrance materials. The notable part is the "
                 "fragrance: four of the nine lines are fragrance, and the "
                 "filing names all four and flags each as an EU allergen. A "
                 "scented value powder is mostly filler and fragrance by "
                 "count."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Spic and Span is a KIK-branded value household "
                      "cleaner. Market-position vocabulary, not a single "
                      "retail channel."),
        "substitutes": [sub("Bon Ami cleansing powder", "mass",
                            "A powdered cleanser in the same aisle and a "
                            "comparable price band, with a shorter list and "
                            "no added fragrance. It is feldspar-based, so it "
                            "carries a respirable-silica question of its own; "
                            "read that entry before choosing it for a sealed "
                            "stone surface.")],
        "exposure": 3,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_surface("A value scented powder cleanser; the abrasive-cleanser "
                      "segment is a small share of surface care."),
    },

    # ---- Greased Lightning (HomeCare Labs / KIK). -------------------------
    {
        "name": "Greased Lightning Classic Cleaner & Degreaser",
        "brand": "Greased Lightning",
        "cat": "All-Purpose",
        "ings": ["Water", "Alkylbenzene Sulfonic Acid",
                 "Dipropylene Glycol Butyl Ether", "Undeceth-40",
                 "Sodium Hydroxide", "Butoxyethanol", "Tetrasodium EDTA",
                 "Fragrance Ingredients", "Limonene"],
        "source": ("HomeCare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "Greased Lightning Classic Cleaner & Degreaser, liquid "
                   "spray cleaner, 32 oz. UPC 0-81238-19853-0, disclosure "
                   "dated 2019-08-09. Nine intentionally added ingredients "
                   "with CAS numbers; sodium hydroxide and 2-butoxyethanol "
                   "are flagged on the California non-cancer hazards list and "
                   "limonene as an EU fragrance allergen."),
        "source_url": U + "2019/10/Greased-Lighting_-Classic-Cleaner-Degreaser-32oz-_0-81238-19853-0.pdf",
        "note": ("A value degreaser built on two solvents: a glycol ether and "
                 "2-butoxyethanol, the second of which California flags. A "
                 "sulfonic-acid surfactant and a hydroxide do the cutting, "
                 "and one named fragrance allergen finishes it. Nine lines, "
                 "two of them flagged by the state, all disclosed."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Greased Lightning is a KIK-branded value household "
                      "cleaner. Market-position vocabulary, not a single "
                      "retail channel."),
        "substitutes": [sub("Simple Green All-Purpose Cleaner", "mass",
                            "A mainstream value degreaser in a comparable "
                            "price band. Read its own list; it is a different "
                            "surfactant and solvent set, so it is a "
                            "substitute for the degreasing job, not a clean "
                            "swap.")],
        "exposure": 2,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_surface("A value all-purpose degreaser."),
    },

    # ---- Austin's (James Austin Company / KIK). ---------------------------
    {
        "name": "Austin's Wipe Away Glass & Window Cleaner with Ammonia",
        "brand": "Austin's",
        "cat": "Glass",
        "ings": ["Water", "Butoxydiglycol", "Ammonium Hydroxide",
                 "Propylene Glycol", "Caprylyl/Capryl Glucoside",
                 "Direct Blue 86", "Lauryl Glucoside",
                 "Trisodium Dicarboxymethyl Alaninate", "Sodium Hydroxide"],
        "source": ("James Austin Company / KIK Consumer Products California "
                   "Cleaning Product Right to Know (SB-258) ingredient "
                   "disclosure for Austin's Wipe Away Glass & Window Cleaner "
                   "with Ammonia, spray glass cleaner. UPC 0-54200-00066-7, "
                   "disclosure dated 2021-01-28. Nine intentionally added "
                   "ingredients with CAS numbers; butoxydiglycol is flagged "
                   "on the California TACs list and sodium hydroxide on the "
                   "non-cancer hazards list."),
        "source_url": U + "2021/03/Austins_Wipe-Away-Glass-Window-Cleaner-with-Ammonia-01.28.2021.pdf",
        "note": ("An ammonia glass cleaner, and a newer formula than the "
                 "classic blue sprays: two sugar-derived glucoside "
                 "surfactants instead of petroleum ones, a chelating agent, "
                 "and Direct Blue 86 for the colour. Still ammonia, still a "
                 "glycol ether solvent flagged by California. Nine disclosed "
                 "lines, all identified."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Austin's is a value household cleaning brand of the "
                      "James Austin Company, a KIK company since 2018. "
                      "Market-position vocabulary, not a single retail "
                      "channel."),
        "substitutes": [sub("Spic and Span Glass Cleaner, 32 oz", "mass",
                            "Same manufacturer and price band, a different "
                            "ammonia glass cleaner. Read its list; neither is "
                            "the fragrance-free option, and both carry a "
                            "glycol ether solvent.")],
        "exposure": 3,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_surface("A value ammonia glass cleaner; glass cleaners sit in "
                      "the specialised surface-cleaner sub-segment."),
    },
    {
        "name": "Austin's Wipe Away Professional Drain Opener",
        "brand": "Austin's",
        "cat": "Specialty",
        "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide",
                 "Myristamine Oxide", "Lauric Acid", "Sodium Silicate",
                 "Sodium Metaperiodate", "Myristic Acid", "Stearic Acid",
                 "Palmitic Acid", "Caprylic Acid", "Capric Acid",
                 "Oleic Acid"],
        "source": ("James Austin Company / KIK Consumer Products California "
                   "Cleaning Product Right to Know (SB-258) ingredient "
                   "disclosure for Austin's Wipe Away Professional Drain "
                   "Opener, 32 fl oz liquid drain opener. UPC 0-54200-01690-3, "
                   "disclosure dated 2019-08-21. Thirteen intentionally added "
                   "ingredients with CAS numbers; sodium hydroxide is flagged "
                   "on the California non-cancer hazards list."),
        "source_url": U + "2019/11/Austins_Wipe-Away-Professional-Drain-Opener-32oz_0-54200-01690-3.pdf",
        "note": ("A bleach-based drain opener, and the longest list in this "
                 "harvest: thirteen lines. It carries the same builder pair "
                 "-- sodium silicate and sodium metaperiodate -- that appears "
                 "on The Works Power Gel and the A-1 and Hi-lex bleach "
                 "labels from the same corporate family, plus seven named "
                 "fatty acids that act as surfactants. " + DRAIN_MIX + " A "
                 "bleach opener must never follow an acid one."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Austin's is a value household cleaning brand of the "
                      "James Austin Company, a KIK company since 2018. "
                      "Market-position vocabulary, not a single retail "
                      "channel."),
        "substitutes": [sub("The Works Professional Strength Drain Opener",
                            "dollar-store",
                            "An acid drain opener rather than a bleach one. "
                            "It avoids the hypochlorite, the silicate and the "
                            "periodate; it is a different hazard, not a "
                            "smaller one. " + DRAIN_MIX)],
        "exposure": 2,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_surface("A value drain opener; drain openers are a small "
                      "specialty segment."),
    },
]


# --------------------------------------------------------------------------
# Writer
# --------------------------------------------------------------------------
def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def dump(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)


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

    # Minting runs after the products so keys first seen there are written too;
    # a key referenced by any record but absent from the registry is the one
    # failure this harvest must not produce.
    for key in sorted(added_keys):
        if key.lower() in lower:
            print(f"key exists, not re-minting: {key}")
            continue
        ingredients[key] = NEW_KEYS[key]
        lower[key.lower()] = key
        print(f"new ingredient key: {key}")

    # Assert every ingredient referenced by every record resolves.
    for r in products:
        for k in r["ings"]:
            if k not in ingredients:
                raise SystemExit(f"record {r['name']!r} references missing key {k!r}")

    if added and not NO_CHANGELOG:
        changelog.insert(0, {
            "date": TODAY,
            "text": (f"Spectrum harvest: {added} products added to the value "
                     "bathroom, bleach and drain shelf from KIK manufacturer "
                     "SB-258 filings read 2026-10-04 (The Works, Top Job, "
                     "Comet, Spic and Span, Greased Lightning, Austin's). The "
                     "value liquid bleach is one three-line formula across two "
                     "brands; a bleach TABLET is chlorinated hydantoins, not "
                     "hypochlorite; the value bathroom bleach cleaner is the "
                     "same five lines across three brands."),
        })

    if DRY:
        print(f"\nDRY RUN: would add {added} products, "
              f"{len(added_keys)} ingredient keys.")
        return

    dump(os.path.join(DATA, "products.json"), products)
    dump(os.path.join(DATA, "ingredients.json"), ingredients)
    dump(os.path.join(DATA, "changelog.json"), changelog)
    print(f"\nwrote {added} products, {len(added_keys)} new ingredient keys.")


if __name__ == "__main__":
    main()
