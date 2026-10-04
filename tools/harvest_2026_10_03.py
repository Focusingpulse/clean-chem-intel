#!/usr/bin/env python3
"""Night-shift station 2 harvest, 2026-10-03 (Dolman).

Ordered by EXPOSURE, not price tier (Trellis, Sep 22 2026). Every ingredient
list below was read from a manufacturer California SB-258 ingredient-disclosure
filing read TODAY, 2026-10-03, from KIK Consumer Products' own disclosure index
at https://www.kikcorp.com/ingredients/ .

Why this block. The previous station-2 fires took the Walmart house brand, the
branded value cleaners (Comet, Spic and Span, The Works all-purpose), and the
value bleach shelf. The remaining unread part of the same index is the rest of
the **household bathroom, glass, cleanser and ammonia shelf** -- the products
that sit beside the national brands at a lower price in the highest-traffic
rooms in the house. Bathroom cleaners are the largest sub-segment of the
specialised surface-cleaner segment (IndexBox), so this is the largest
high-exposure block still missing from the corpus.

What the block shows, in three lines:

  1. **The bleach bathroom shelf is one formula under many labels.** Water,
     sodium hypochlorite, sodium hydroxide, lauramine oxide (plus fragrance on
     the scented ones) is the complete disclosed list on Comet Classic Foaming
     Bath Cleaner and on The Works Basic Bathroom Cleaner with Bleach -- two
     different brands, two price points, same four chemicals. This is the
     fourth instance of the one-formula-many-brands pattern in this database.
  2. **The quat sprays are the ones carrying the extra load.** Comet Classic
     Antibacterial Spray Cleaner, Comet Ultra Bathroom Spray and Comet Foaming
     Bath Spray all disclose four different quaternary ammonium actives each.
     A plain bleach bathroom cleaner is the shorter list.
  3. **Comet Multi-Surface Spray Cleaner discloses tris(N-hydroxyethyl)
     hexahydrotriazine**, a formaldehyde-releasing preservative, at a value
     price point, in a "Country Apple" scent sold for kitchen surfaces. That is
     the single most notable line in this harvest and it is disclosed, not
     hidden -- which is the point of the tool.

Nothing here is graded. Product grading is the Sifter lane; a blank as-sold
grade is the honest state.

Two repairs carried in the same commit (both discovered while harvesting, both
data-quality, neither a new record):
  * `Comet Bathroom` carried a four-line list with no source. The manufacturer
    filing for Comet Bath Cleaner (both sizes) discloses eight. Completed and
    sourced.
  * `The Works Toilet Bowl Cleaner` carried no tier. Dollar General's own
    product page for the exact UPC is a served, machine-readable page and gives
    the brand a real dollar-channel tier source.

Idempotent: a product whose `name` already exists is skipped, an ingredient key
already present is left untouched, and both repairs are no-ops on a second run.
Run it twice; the second run reports 0 added.

Usage:  python3 tools/harvest_2026_10_03.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-03"

DRY = "--dry-run" in sys.argv
NO_CHANGELOG = "--no-changelog" in sys.argv

KIK_INDEX = "https://www.kikcorp.com/ingredients/"
KIK_PRODUCTS = "https://www.kikcorp.com/our-products/"
SEC_APA = ("https://www.sec.gov/Archives/edgar/data/1295947/000129594718000020/"
           "exhibit101-assetpurchaseag.htm")
DG_WORKS = ("https://www.dollargeneral.com/p/"
            "the-works-disinfectant-toilet-bowl-cleaner-32-oz/74157033105")

IB_SURFACE = ("https://www.indexbox.io/store/"
              "united-states-household-surface-cleaners-market-analysis-"
              "forecast-size-trends-and-insights/")

U = "https://www.kikcorp.com/wp-content/uploads/"

# --------------------------------------------------------------------------
# Ingredient key resolution. Label wording -> existing canonical key, where the
# substance is the same and a second key would be a synonym for one CAS. Each
# target was checked case-insensitively against the live registry before use;
# the writer halts if a target key is absent.
# --------------------------------------------------------------------------
ALIASES = {
    # Same CAS 67701-05-7 as the existing key; the Comet filing names it by
    # its trade description.
    "Whole Cut Fatty Acid": "Fatty Acids, C8-C18 and C18 Unsaturated",
    # The filings name the dye only as "Green dye" / "Blue Dye" with CAS
    # "Not Available". The registry collapses unspecified dyes to Colorant.
    "Green dye": "Colorant",
    "Blue Dye": "Colorant",
    # Same substance, different word order / CAS registration line.
    "Alcohols, C12-C15 ethoxylated": "C12-15 Alcohols Ethoxylated",
    "Ethoxylated C10-16 Alcohols": "Alcohols, C10-16, Ethoxylated",
    "C9-11 Alcohols Ethoxylated": "Alcohols, C9-11, ethoxylated",
    # Same CAS 29911-28-2 as the existing key.
    "Dipropylene Glycol n-Butyl Ether": "Dipropylene Glycol Butyl Ether",
    # Same CAS 112-34-5. Linnea's R1 merged Butoxydiglycol into this key on
    # 2026-09-30; the Spic and Span Glass Cleaner filing uses the short form.
    "Butoxydiglycol": "Diethylene Glycol Monobutyl Ether",
    # Same CAS 1300-72-7; the Top Job filing uses the British spelling.
    "Sodium Xylene Sulphonate": "Sodium Xylenesulfonate",
    # The filings say "Fragrance Ingredients" / "Fragrance ingredients".
    "Fragrance Ingredients": "Fragrance",
    # Monoethanolamine is ethanolamine, CAS 141-43-5.
    "Monoethanolamine": "Ethanolamine",
    # Same CAS 68424-85-1 as the existing key; the Comet Ultra filing spells
    # out the alkyl chain distribution, the Comet Foaming Bath filing does not.
    "Alkyl (40% C12, 50% C14, 10% C16) Dimethyl Benzyl Ammonium Chloride":
        "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride",
}

# New keys minted this fire. Shape follows the registry's existing entries:
# ungraded is recorded as ev "Low" with g null, never a guess.
NEW_KEYS = {
    "Polyacrylic Acid": {
        "s": "Polyacrylic acid. Water-soluble polymer used as a dispersant and "
             "thickener in cream cleansers; CAS 9003-01-4.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Comet Soft Cleanser with Bleach disclosure "
                "(2023-04-19) with CAS 9003-01-4, listed as a surfactant. "
                "Not yet graded against GHS; recorded rather than guessed.",
    },
    "Sodium Cumene Sulfonate": {
        "s": "Sodium cumene sulfonate, a hydrotrope used to keep surfactants "
             "in solution; CAS 28348-53-0.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Comet Bath Cleaner disclosure (both sizes) with "
                "CAS 28348-53-0, listed in the chelant role. Not yet graded.",
    },
    "Morpholine": {
        "s": "Morpholine. Secondary amine used as a corrosion inhibitor; "
             "CAS 110-91-8.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Comet Foaming Bath Spray disclosure with CAS "
                "110-91-8, as a corrosion inhibitor. Not yet graded. Worth the "
                "grading lane's attention: it is a secondary amine co-listed "
                "here with sodium nitrite, and secondary amines plus nitrite "
                "are the classic nitrosamine precursor pair.",
    },
    "Sodium Nitrite": {
        "s": "Sodium nitrite. Inorganic salt used here as a corrosion "
             "inhibitor; CAS 7632-00-0.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Comet Foaming Bath Spray disclosure with CAS "
                "7632-00-0, as a corrosion inhibitor. Not yet graded. Listed "
                "on the same filing as morpholine; see that entry.",
    },
    "Tris(N-Hydroxyethyl) Hexahydrotriazine": {
        "s": "1,3,5-Tris(2-hydroxyethyl)-hexahydro-s-triazine. A preservative "
             "that releases formaldehyde; CAS 4719-04-4.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Comet Multi-Surface Spray Cleaner (Country Apple) "
                "disclosure with CAS 4719-04-4, listed as a preservative. Not "
                "yet graded here; the grading lane should resolve it, because "
                "this is a formaldehyde-releasing preservative disclosed on a "
                "value-price kitchen surface spray.",
    },
    "Acid Blue 204": {
        "s": "Acid Blue 204, a blue anthraquinone dye (Colour Index 61554).",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Comet Multi-Surface Spray Cleaner (Country Apple) "
                "disclosure with CAS 61724-00-3, as a dye. Not yet graded.",
    },
    "Solvent Green 7": {
        "s": "Solvent Green 7, a green fluorescent dye (Colour Index 59040).",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Comet Multi-Surface Spray Cleaner (Country Apple) "
                "disclosure with CAS 6358-69-6, as a dye. Not yet graded.",
    },
    "Ammonium Laureth Sulfate": {
        "s": "Ammonium lauryl ether sulfate, an anionic surfactant; "
             "CAS 67762-19-0.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Comet Classic Window Cleaner disclosure with CAS "
                "67762-19-0, as a surfactant. Not yet graded.",
    },
    "Dipropylene Glycol Methyl Ether": {
        "s": "Dipropylene glycol methyl ether (DPM). Glycol ether solvent; "
             "CAS 34590-94-8.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on The Works Tub & Shower Cleaner disclosure with CAS "
                "34590-94-8, as a solvent. Not yet graded. Kept as its own key "
                "rather than folded into the butyl glycol ether key: this is "
                "the methyl ether, a different substance and a different CAS.",
    },
    "Silicone Emulsion": {
        "s": "Silicone emulsion, an antifoam. Composition not specified on the "
             "disclosure.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on The Works Limeosol Cleaner disclosure as a foam "
                "suppressant with no CAS ('not available'). Recorded as an "
                "unidentified constituent rather than a substance; the "
                "disclosure does not say which silicone.",
    },
    "Coconut Fatty Acid": {
        "s": "Coconut fatty acid, a mixture of C8-C18 saturated fatty acids "
             "from coconut oil; CAS 61788-47-4.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on The Works Power Gel disclosure with CAS 61788-47-4, "
                "as a surfactant. Not yet graded. Kept separate from the "
                "existing C8-C18 fatty acid key: the CAS differs and the "
                "filings name them separately.",
    },
    "PEG-40 Castor Oil": {
        "s": "PEG-40 castor oil, an ethoxylated castor oil used as an "
             "emulsifier/solubiliser; CAS 61791-12-6.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Spic and Span Cinch Glass Cleaner disclosure with "
                "CAS 61791-12-6, as an emulsifier. Not yet graded.",
    },
    "Yellow 8": {
        "s": "Yellow 8 (Fluorescein sodium), a yellow dye; CAS 518-47-8.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Top Job Lemon Ammonia disclosure with CAS "
                "518-47-8, as a dye. Not yet graded.",
    },
    "Alcohols, C6-C12, Ethoxylated": {
        "s": "Ethoxylated C6-C12 alcohols, a non-ionic surfactant; "
             "CAS 68439-45-2.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Comet Bath Cleaner disclosure (both sizes) with "
                "CAS 68439-45-2, as a surfactant. Not yet graded. Kept as its "
                "own key rather than folded into the C10-16 alcohol "
                "ethoxylate: the chain length and the CAS differ.",
    },
    "Alkyl (67% C12, 25% C14, 7% C16, 1% C8+C10+C18) Dimethyl Benzyl Ammonium Chloride": {
        "s": "A dialkyl dimethyl benzyl ammonium chloride disinfectant active "
             "(benzalkonium chloride type), CAS 63449-41-2.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Comet Ultra Bathroom Spray disclosure with CAS "
                "63449-41-2, as an active ingredient. Not yet graded. Kept as "
                "its own record rather than folded into Benzalkonium Chloride, "
                "matching the registry's existing practice of keeping each "
                "UVCB quat blend under its own filing wording for "
                "traceability (see Alkyl C12-16 Dimethylbenzyl Ammonium "
                "Chloride).",
    },
    "Non-ionic Surfactant": {
        "s": "An ethoxylated non-ionic surfactant, named only by class on the "
             "disclosure.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Named on the Comet Ultra Bathroom Spray disclosure as "
                "'Non-ionic Surfactant' with CAS 'Not available'. The "
                "disclosure gives the class and withholds the identity; "
                "recorded as such rather than folded into a guessed key.",
    },
}


def exp(cat_note: str, src: str = IB_SURFACE) -> dict:
    return {
        "exposure_ev": "extrapolated",
        "exposure_src": src,
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


def sub(name, tier, note):
    return {"name": name, "tier": tier, "note": note}


BLEACH_NaOH = ("The hazard on this bottle is the sodium hypochlorite and the "
               "sodium hydroxide, which is the same hazard on every bleach "
               "cleaner. If bleach is the concern, no bleach cleaner is a "
               "substitute for it; the alternative is a non-bleach cleaner "
               "for the same room at the same price.")
QUAT_NOTE = ("Avoids the four quaternary ammonium actives in this formula. "
             "Trades a disinfectant claim for a plain cleaning job at the "
             "same price; if a disinfectant claim is what you need, read the "
             "substitute's own list before switching.")


# --------------------------------------------------------------------------
# Products. Every ings list below is the filing's intentionally-added list,
# read 2026-10-03.
# --------------------------------------------------------------------------
PRODUCTS = [
    # ---- Comet (KIK / HomeCare Labs). Disclosures from the KIK index. -----
    {
        "name": "Comet Soft Cleanser with Bleach",
        "brand": "Comet",
        "cat": "Abrasive Cleanser",
        "ings": ["Water", "Calcium Carbonate", "Sodium Hypochlorite",
                 "Myristamine Oxide", "Whole Cut Fatty Acid",
                 "Sodium Hydroxide", "Sodium Carbonate", "Green dye",
                 "Polyacrylic Acid", "Fragrance Ingredients"],
        "source": ("HomeCare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "Comet Soft Cleanser with Bleach, cream cleanser, 24 oz. "
                   "UPC 8-10003-44016-7, disclosure dated 2023-04-19. Ten "
                   "intentionally added ingredients with CAS numbers; sodium "
                   "hydroxide flagged on the California non-cancer hazards "
                   "list. NOTE: the 2019 filing for the same UPC, then named "
                   "Comet Cream Cleanser, disclosed sixteen lines including "
                   "titanium dioxide (IARC carcinogens), sodium silicate, "
                   "sodium metaperiodate and bentonite. The 2023 filing for "
                   "the same UPC lists ten and omits those. The record carries "
                   "the current filing; the difference is filed as a gap."),
        "source_url": U + "2023/04/Comet_Soft-Cleanser-with-Bleach-24oz_8-10003-44016-7.pdf",
        "note": ("An abrasive cream cleanser: calcium carbonate is the grit, "
                 "hypochlorite is the bleach, the oxides and fatty acid are "
                 "the surfactants, and polyacrylic acid keeps it from "
                 "separating. Ten disclosed lines. The same UPC's 2019 "
                 "disclosure carried sixteen, including titanium dioxide "
                 "listed as an IARC carcinogen. That is either a "
                 "reformulation or a disclosure that got shorter, and the "
                 "filings do not say which."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Comet is a KIK-branded value household cleaner; the "
                      "manufacturer's own product page names it as one of the "
                      "brands its U.S. household business markets. "
                      "Market-position vocabulary, not a single retail channel."),
        "substitutes": [sub("Bon Ami", "mass",
                            "A powdered cleanser with no bleach and no "
                            "hypochlorite, in the same aisle and a comparable "
                            "price band. Avoids the hypochlorite; it is an "
                            "abrasive, so it does the same scouring job.")],
        "exposure": 4,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("A long-standing value abrasive cleanser; the abrasive-cream "
              "segment is a small share of surface care."),
    },
    {
        "name": "Comet Foaming Bath Spray, Fresh Lemon Scent",
        "brand": "Comet",
        "cat": "Bathroom",
        "ings": ["Water", "Diethylene Glycol Monobutyl Ether", "Isobutane",
                 "Sodium Lauroyl Sarcosinate", "Tetrasodium EDTA",
                 "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride", "Ethanol",
                 "Quaternium-24", "Dimethyldioctylammonium Chloride",
                 "Didecyldimonium Chloride", "Sodium Laurate",
                 "C12-15 Alcohols Ethoxylated", "Morpholine", "Sodium Nitrite",
                 "Fragrance Ingredients"],
        "source": ("HomeCare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "Comet Foaming Bath Spray, Fresh Lemon Scent, 17 oz. UPC "
                   "8-10003-44027-3, disclosure dated 2019-11. Fifteen "
                   "intentionally added ingredients with CAS numbers; the "
                   "glycol ether is flagged on the California TACs list and "
                   "isobutane on the EU CMRs list."),
        "source_url": U + "2019/11/Comet_Foaming-Bath-Spray-Fresh-Lemon-Scent-17oz_8-10003-44027-3.pdf",
        "note": ("A foaming aerosol bathroom spray, and the longest list in "
                 "this harvest. Four separate quaternary ammonium actives "
                 "carry the disinfectant claim, isobutane is the propellant, "
                 "and a glycol ether is the solvent. The two lines worth "
                 "reading are morpholine and sodium nitrite: a secondary "
                 "amine and a nitrite salt, which are the classic nitrosamine "
                 "precursor pair, both disclosed here as corrosion inhibitors "
                 "in a product sprayed into the air of a bathroom."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Comet is a KIK-branded value household cleaner. "
                      "Market-position vocabulary, not a single retail channel."),
        "substitutes": [sub("Comet Bath Cleaner, 32 oz", "mass",
                            "Same brand, same aisle, comparable price, and "
                            "eight disclosed lines instead of fifteen. No "
                            "quaternary ammonium actives, no propellant, no "
                            "morpholine and no nitrite. It is a pump spray, "
                            "not an aerosol, and it does not carry a "
                            "disinfectant claim.")],
        "exposure": 3,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("A value aerosol bathroom cleaner; the aerosol form is a small "
              "share of the bathroom sub-segment."),
    },
    {
        "name": "Comet Multi-Surface Spray Cleaner, Country Apple",
        "brand": "Comet",
        "cat": "All-Purpose",
        "ings": ["Water", "Sodium Metasilicate Pentahydrate", "Tetrasodium EDTA",
                 "Tris(N-Hydroxyethyl) Hexahydrotriazine",
                 "Alcohols, C12-C15 ethoxylated", "Fragrance",
                 "Sodium Lauryl Sulfate", "Acid Blue 204", "Solvent Green 7"],
        "source": ("HomeCare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "Comet Multi-Surface Spray Cleaner, Country Apple, 22 oz. "
                   "UPC 8-10003-44004-4, disclosure dated 2019-11. Nine "
                   "intentionally added ingredients with CAS numbers."),
        "source_url": U + "2019/11/Comet_Multi-Surface-Spray-Cleaner-Country-Apple-22oz_8-10003-44004-4.pdf",
        "note": ("Nine lines, and the one that matters is "
                 "tris(N-hydroxyethyl) hexahydrotriazine, a "
                 "formaldehyde-releasing preservative, listed as a "
                 "preservative. This is a value-price spray sold for kitchen "
                 "surfaces in a fruit scent. It is disclosed, which is the "
                 "difference between this and a product whose preservative is "
                 "hidden behind 'fragrance'; disclosed is not the same as "
                 "harmless, and it is the line to look at."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Comet is a KIK-branded value household cleaner. "
                      "Market-position vocabulary, not a single retail channel."),
        "substitutes": [sub("Spic and Span Multi-Surface Cleaner, Sun Fresh",
                            "mass",
                            "Same manufacturer, same value price band, same "
                            "job. Thirteen disclosed lines, no formaldehyde "
                            "releaser and no quaternary ammonium. It does "
                            "carry DMDM hydantoin, which is also a "
                            "formaldehyde-releasing preservative, so read its "
                            "list before switching.")],
        "exposure": 4,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("A value all-purpose spray; all-purpose sprays and liquids are "
              "the largest single segment of surface cleaners."),
    },
    {
        "name": "Comet Classic Window Cleaner",
        "brand": "Comet",
        "cat": "Glass",
        "ings": ["Water", "Tetrasodium EDTA", "Ammonium Hydroxide",
                 "Butyloxyethanol", "Ammonium Laureth Sulfate",
                 "Ethoxylated C10-16 Alcohols", "Isopropanol", "Blue Dye"],
        "source": ("HomeCare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "Comet Classic Window Cleaner, 24 oz. UPC 8-10003-44010-5, "
                   "disclosure dated 2019-12. Eight intentionally added "
                   "ingredients; 2-butoxyethanol is flagged on the California "
                   "non-cancer hazards list."),
        "source_url": U + "2019/12/15-Comet-Classic_Window-Cleaner-24oz_8-10003-44010-5.pdf",
        "note": ("A classic ammonia glass cleaner. Two solvents (a glycol "
                 "ether and isopropanol), two surfactants, ammonia for the "
                 "streak-free finish and a blue dye. The 2-butoxyethanol is "
                 "the line flagged by California, and it is the one that "
                 "makes an ammonia glass cleaner harsher than a plain vinegar "
                 "or alcohol one at the same price."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Comet is a KIK-branded value household cleaner. "
                      "Market-position vocabulary, not a single retail channel."),
        "substitutes": [sub("Spic and Span Glass Cleaner, 32 oz", "mass",
                            "Same manufacturer, same value price band, no "
                            "2-butoxyethanol and no dye. It still contains "
                            "ammonium hydroxide, so the ammonia is not "
                            "avoided; the glycol ether and the dye are.")],
        "exposure": 4,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("A value glass cleaner; glass cleaners sit in the specialised "
              "surface-cleaner sub-segment."),
    },
    {
        "name": "Comet Ultra Bathroom Spray, Lemon Scent",
        "brand": "Comet",
        "cat": "Bathroom",
        "ings": ["Water", "Lauramine Oxide", "Tetrasodium EDTA",
                 "Alkyl (40% C12, 50% C14, 10% C16) Dimethyl Benzyl Ammonium Chloride",
                 "Alkyl (67% C12, 25% C14, 7% C16, 1% C8+C10+C18) Dimethyl Benzyl Ammonium Chloride",
                 "Sodium Metasilicate", "C9-11 Alcohols Ethoxylated",
                 "Non-ionic Surfactant", "Fragrance Ingredients"],
        "source": ("KIK Consumer Products California Cleaning Product Right to "
                   "Know (SB-258) ingredient disclosure for Comet Ultra "
                   "Bathroom Spray, Lemon Scent, 32 oz. UPC 8-10003-44097-6, "
                   "disclosure dated 2022-09. Nine intentionally added "
                   "ingredients with CAS numbers; one surfactant is named only "
                   "by class ('Non-ionic Surfactant', CAS not available)."),
        "source_url": U + "2022/09/Comet-Ultra_Bathroom-Spray-Lemon-Scent-32oz_8-10003-44097-6.pdf",
        "note": ("A ready-to-use bathroom spray with two dialkyl benzyl "
                 "ammonium chloride actives. Nine disclosed lines, and one of "
                 "them is a surfactant named only as 'Non-ionic Surfactant' "
                 "with no CAS. That is the honest edge of this tool: eight "
                 "lines are identified and one is a class. It renders as not "
                 "disclosed, not as a blank."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Comet is a KIK-branded value household cleaner. "
                      "Market-position vocabulary, not a single retail channel."),
        "substitutes": [sub("Comet Bath Cleaner, 32 oz", "mass",
                            "Same brand and price band, eight disclosed lines "
                            "with every one identified. " + QUAT_NOTE)],
        "exposure": 3,
        "strength_disclosure": "partial",
        "added": TODAY, "updated": TODAY,
        **exp("A value ready-to-use bathroom cleaner."),
    },
    {
        "name": "Comet Classic Foaming Bath Cleaner",
        "brand": "Comet",
        "cat": "Bathroom",
        "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide",
                 "Lauramine Oxide"],
        "source": ("HomeCare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "Comet Classic Foaming Bath Cleaner, 24 oz. UPC "
                   "8-10003-44012-9, disclosure dated 2019-12. Four "
                   "intentionally added ingredients; sodium hydroxide flagged "
                   "on the California non-cancer hazards list."),
        "source_url": U + "2019/12/19-Comet-Classic_Foaming-Bath-Cleaner-24oz_8-10003-44012-9.pdf",
        "note": ("Four lines. Water, bleach, the hydroxide that stabilises it, "
                 "and one surfactant to make it foam. That is the whole "
                 "disclosed formula on a bathroom bleach cleaner, and it is "
                 "the same four chemicals The Works Basic Bathroom Cleaner "
                 "with Bleach discloses under a different label at a "
                 "different price. This is the fourth time in this database "
                 "that a value cleaner's complete formula has turned out to "
                 "be a handful of commodity chemicals."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Comet is a KIK-branded value household cleaner. "
                      "Market-position vocabulary, not a single retail channel."),
        "substitutes": [sub("Comet Bath Cleaner, 32 oz", "mass",
                            "Same brand, same aisle, comparable price, and no "
                            "bleach at all. It is a citric-acid bathroom "
                            "cleaner, so it does the same room without the "
                            "hypochlorite. " + BLEACH_NaOH)],
        "exposure": 4,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("A value foaming bleach bathroom cleaner."),
    },
    {
        "name": "Comet Classic Antibacterial Spray Cleaner",
        "brand": "Comet",
        "cat": "Disinfectant",
        "ings": ["Water", "Octyl decyl dimethyl ammonium chloride",
                 "Dioctyl dimethyl ammonium chloride",
                 "Didecyl dimethyl ammonium chloride",
                 "Alkyl (50% C14, 40% C12, 10% C16) Dimethyl Benzyl Ammonium Chloride",
                 "Tetrasodium EDTA", "Sodium Metasilicate Pentahydrate",
                 "C12-15 Alcohols Ethoxylated", "Fragrance Ingredients",
                 "Green Dye"],
        "source": ("HomeCare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "Comet Classic Antibacterial Spray Cleaner, 16 oz. UPC "
                   "8-10003-44056-3, disclosure dated 2020-09. Ten "
                   "intentionally added ingredients with CAS numbers."),
        "source_url": U + "2020/09/Comet-Classic_Antibacterial-Spray-Cleaner-16oz_8-10003-44056-3.pdf",
        "note": ("Four quaternary ammonium actives, four different alkyl "
                 "chains, all disclosed by name and CAS. This is what an "
                 "'antibacterial' claim is made of, and the label will not "
                 "tell you that; the SB-258 filing does. A plain bleach "
                 "bathroom cleaner from the same brand discloses four lines "
                 "in total."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Comet is a KIK-branded value household cleaner. "
                      "Market-position vocabulary, not a single retail channel."),
        "substitutes": [sub("Spic and Span Multi-Surface Cleaner, Sun Fresh",
                            "mass",
                            "Same manufacturer, same value price band. " +
                            QUAT_NOTE)],
        "exposure": 3,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("A value antibacterial spray cleaner."),
    },

    # ---- The Works (HomeCare Labs / KIK). Dollar-channel value brand. -----
    {
        "name": "The Works Tub & Shower Cleaner",
        "brand": "The Works",
        "cat": "Bathroom",
        "ings": ["Water", "Undeceth-3", "Oxalic Acid", "Sulfamic Acid",
                 "Dipropylene Glycol Methyl Ether",
                 "Propylene Glycol Butyl Ether", "Fragrance",
                 "C9-11 Alcohols Ethoxylated", "Hexyl Acetate",
                 "Allyl Heptanoate"],
        "source": ("Homecare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "The Works Tub & Shower Cleaner, 16 oz. UPC 0-74157-03370-9, "
                   "disclosure dated 2019-05. Ten intentionally added "
                   "ingredients with CAS numbers; two fragrance ingredients "
                   "(hexyl acetate, allyl heptanoate) are disclosed by name "
                   "rather than as a class."),
        "source_url": U + "2019/05/The-Works_Tub-Shower-Cleaner-6x16oz_0-74157-03370-9.pdf",
        "note": ("An acid descaler for tubs and showers: oxalic and sulfamic "
                 "acid do the work, two glycol ethers carry it, and one "
                 "surfactant wets the surface. Two of the ten lines are "
                 "fragrance ingredients named individually, which is unusual "
                 "-- most filings stop at the word 'fragrance'. Acids mean "
                 "gloves and ventilation, and never a bleach product in the "
                 "same bucket."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "dollar-store", "tier_ev": "reported", "tier_src": DG_WORKS,
        "tier_note": ("The Works is a dollar-channel value brand. Dollar "
                      "General's own product page for the brand's toilet bowl "
                      "cleaner is the served source; the brand-level channel "
                      "is evidenced, the individual SKU's channel is not."),
        "substitutes": [sub("Comet Bath Cleaner, 32 oz", "mass",
                            "A non-acid bathroom cleaner at a comparable "
                            "value price. Avoids oxalic and sulfamic acid and "
                            "both glycol ethers; it will not dissolve hard "
                            "water scale the way an acid does, so it is a "
                            "substitute for the cleaning job, not for the "
                            "descaling job.")],
        "exposure": 4,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("A dollar-channel tub and shower cleaner; the bathroom "
              "sub-segment is the largest of the specialised cleaners."),
    },
    {
        "name": "The Works Basic Bathroom Cleaner with Bleach",
        "brand": "The Works",
        "cat": "Bathroom",
        "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide",
                 "Lauramine Oxide", "Fragrance Ingredients"],
        "source": ("Homecare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "The Works Basic Bathroom Cleaner with Bleach, 32 oz. UPC "
                   "0-74157-64280-2, disclosure dated 2019-10. Five "
                   "intentionally added ingredients; sodium hydroxide flagged "
                   "on the California non-cancer hazards list."),
        "source_url": U + "2019/10/The-Works_Basic-Bathroom-Cleaner-with-Bleach-32oz_0-74157-64280-2.pdf",
        "note": ("Five lines, and four of them are the same four as Comet "
                 "Classic Foaming Bath Cleaner. Two brands, two price points, "
                 "one formula: water, bleach, hydroxide, one surfactant, plus "
                 "a fragrance on this one. The bleach is the bleach either "
                 "way. Paying more for a brand name does not change what is "
                 "in the bottle."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "dollar-store", "tier_ev": "reported", "tier_src": DG_WORKS,
        "tier_note": ("The Works is a dollar-channel value brand. Dollar "
                      "General's own product page for the brand's toilet bowl "
                      "cleaner is the served source; brand-level channel "
                      "evidence, not per-SKU."),
        "substitutes": [sub("The Works Tub & Shower Cleaner", "dollar-store",
                            "Same brand and price band. Non-bleach, so it "
                            "avoids the hypochlorite and the hydroxide; it is "
                            "an acid, so do not use it in the same session as "
                            "any bleach product.")],
        "exposure": 4,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("A dollar-channel bleach bathroom cleaner."),
    },
    {
        "name": "The Works Limeosol Cleaner",
        "brand": "The Works",
        "cat": "Specialty",
        "ings": ["Water", "Oxalic Acid", "Glycolic Acid",
                 "Cocamidopropyl Betaine", "Silicone Emulsion"],
        "source": ("Homecare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "The Works Limeosol Cleaner, 32 oz. UPC 0-74157-03330-3, "
                   "disclosure dated 2019-05. Five intentionally added "
                   "ingredients; the antifoam is listed as 'Silicone Emulsion' "
                   "with no CAS."),
        "source_url": U + "2019/05/The-Works_Limeosol-Cleaner-32oz_0-74157-03330-3.pdf",
        "note": ("A five-line acid descaler: two acids, one surfactant, one "
                 "antifoam and water. The antifoam is named only as a "
                 "silicone emulsion, so one of five lines is a class rather "
                 "than a substance. Short, legible and corrosive; the acids "
                 "are the reason for gloves."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "dollar-store", "tier_ev": "reported", "tier_src": DG_WORKS,
        "tier_note": ("The Works is a dollar-channel value brand. Dollar "
                      "General's own product page for the brand's toilet bowl "
                      "cleaner is the served source; brand-level channel "
                      "evidence, not per-SKU."),
        "substitutes": [sub("CLR", "Specialty",
                            "A calcium-lime-rust descaler in the same job and "
                            "a comparable price band. Read its own list; it "
                            "is a different acid blend, so it is a substitute "
                            "for the descaling job, not a clean swap.")],
        "exposure": 1,
        "strength_disclosure": "partial",
        "added": TODAY, "updated": TODAY,
        **exp("A dollar-channel descaler; descalers are a small specialty "
              "segment."),
    },
    {
        "name": "The Works Power Gel Drain Opener",
        "brand": "The Works",
        "cat": "Specialty",
        "ings": ["Water", "Sodium Hypochlorite", "Sodium Hydroxide",
                 "Myristamine Oxide", "Coconut Fatty Acid", "Sodium Silicate",
                 "Sodium Metaperiodate"],
        "source": ("Homecare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "The Works Power Gel, liquid drain opener, 32 oz. UPC "
                   "0-59647-11001-6. Seven intentionally added ingredients; "
                   "sodium hydroxide flagged on the California non-cancer "
                   "hazards list."),
        "source_url": U + "2019/12/The-Works_Power-Gel-32oz_0-59647-11001-6.pdf",
        "note": ("A bleach-based gel drain opener. Seven lines, and it carries "
                 "the same builder pair -- sodium silicate and sodium "
                 "metaperiodate -- that appears on the A-1 and Hi-lex bleach "
                 "labels from the same corporate family. Bleach drain openers "
                 "are a genuine hazard: never with an acid or ammonia "
                 "cleaner, and never on a drain you have already treated with "
                 "one."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "dollar-store", "tier_ev": "reported", "tier_src": DG_WORKS,
        "tier_note": ("The Works is a dollar-channel value brand. Dollar "
                      "General's own product page for the brand's toilet bowl "
                      "cleaner is the served source; brand-level channel "
                      "evidence, not per-SKU."),
        "substitutes": [sub("Drano Max Gel", "mass",
                            "A mainstream gel drain opener in the same price "
                            "band. It is still a strong alkaline product, so "
                            "the mixing rule is unchanged; it avoids the "
                            "hypochlorite and the periodate builder pair.")],
        "exposure": 2,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("A dollar-channel drain opener; drain openers are a small "
              "specialty segment."),
    },

    # ---- Spic and Span / Cinch (Homecare Labs / KIK). ---------------------
    {
        "name": "Spic and Span Cinch Glass Cleaner, 17 oz",
        "brand": "Spic and Span",
        "cat": "Glass",
        "ings": ["Water", "Isopropanol", "Propylene Glycol Butyl Ether",
                 "Sodium Lauryl Sulfate", "Ethanolamine", "PEG-40 Castor Oil",
                 "Tartaric Acid", "Fragrance Ingredients"],
        "source": ("Homecare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "Spic and Span Cinch Glass Cleaner, 17 oz. UPC "
                   "8-11435-00201-5, disclosure dated 2019-08-05. Eight "
                   "intentionally added ingredients with CAS numbers; "
                   "isopropanol flagged on the California non-cancer hazards "
                   "list."),
        "source_url": U + "2019/12/22_SNS_Cinch_Window_Cleaner_17oz_8_11435_00201_51.pdf",
        "note": ("Cinch is the glass-cleaner brand KIK bought from Prestige "
                 "Brands in 2018, sold here under the Spic and Span name. No "
                 "ammonia: it uses isopropanol and a glycol ether as the "
                 "solvents instead, which is why it smells different from a "
                 "classic blue window spray. Eight disclosed lines."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("A KIK-branded value glass cleaner. Market-position "
                      "vocabulary, not a single retail channel."),
        "substitutes": [sub("Spic and Span Glass Cleaner, 32 oz", "mass",
                            "Same manufacturer and price band. Trades the "
                            "isopropanol for ammonium hydroxide and a "
                            "different surfactant set; read its list, because "
                            "neither is the 'plain' option.")],
        "exposure": 2,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("A value glass cleaner under the Cinch name."),
    },
    {
        "name": "Spic and Span Glass Cleaner, 32 oz",
        "brand": "Spic and Span",
        "cat": "Glass",
        "ings": ["Water", "Butoxydiglycol", "Ammonium Hydroxide",
                 "Propylene Glycol", "Caprylyl/Capryl Glucoside",
                 "Direct Blue 86", "Lauryl Glucoside",
                 "Trisodium Dicarboxymethyl Alaninate", "Sodium Hydroxide"],
        "source": ("KIK Consumer Products California Cleaning Product Right "
                   "to Know (SB-258) ingredient disclosure for Spic and Span "
                   "Glass Cleaner, 32 oz. UPC 8-11435-00765-2, disclosure "
                   "dated 2022-04. Nine intentionally added ingredients with "
                   "CAS numbers; butoxydiglycol flagged on the California TACs "
                   "list and sodium hydroxide on the non-cancer hazards list."),
        "source_url": U + "2022/04/Spic-and-Span-Glass-Cleaner-32oz_8-11435-00765-2.pdf",
        "note": ("An ammonia glass cleaner, and a newer formula than the "
                 "Cinch: two sugar-derived glucoside surfactants instead of "
                 "petroleum ones, a chelating agent, and Direct Blue 86 for "
                 "the colour. Still ammonia, still a glycol ether solvent. "
                 "Nine disclosed lines, all identified."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("A KIK-branded value glass cleaner. Market-position "
                      "vocabulary, not a single retail channel."),
        "substitutes": [sub("Spic and Span Cinch Glass Cleaner, 17 oz", "mass",
                            "Same manufacturer and price band. No ammonia, no "
                            "dye; it trades the ammonia for isopropanol and a "
                            "glycol ether. Pick by which solvent you would "
                            "rather have in the room.")],
        "exposure": 2,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("A value ammonia glass cleaner."),
    },

    # ---- Top Job (KIK). Ammonia staples. ----------------------------------
    {
        "name": "Top Job Clear Ammonia",
        "brand": "Top Job",
        "cat": "Glass",
        "ings": ["Water", "Ammonium Hydroxide", "Tetrasodium EDTA",
                 "Sodium C10-16 Alkylbenzenesulfonate",
                 "Sodium Xylene Sulphonate"],
        "source": ("KIK Consumer Products California Cleaning Product Right "
                   "to Know (SB-258) ingredient disclosure for Top Job Clear "
                   "Ammonia, 64 oz. UPC 8-36272-00073-4, disclosure dated "
                   "2019-10. Five intentionally added ingredients with CAS "
                   "numbers."),
        "source_url": U + "2019/10/Top-Job-Clear-Ammonia-64oz_8-36272-00073-4.pdf",
        "note": ("Five lines: water, ammonia, a chelant and two surfactants. "
                 "This is the unscented member of the Top Job ammonia pair, "
                 "and the difference between it and the lemon version is a "
                 "dye, a fragrance and one named allergen. Ammonia is the "
                 "hazard on both, and it is the same hazard on every clear "
                 "ammonia on the shelf."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Top Job is a KIK-branded value household cleaner; the "
                      "manufacturer's own product page names it as one of the "
                      "brands its U.S. household business markets. "
                      "Market-position vocabulary, not a single retail channel."),
        "substitutes": [sub("Austins Clear Ammonia", "mass",
                            "The same two disclosed ingredients -- water and "
                            "ammonium hydroxide -- under another label from "
                            "the same corporate family, at a comparable price. "
                            "A shorter list, not a different hazard.")],
        "exposure": 3,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("A value clear ammonia, a glass and general-purpose staple."),
    },
    {
        "name": "Top Job Lemon Ammonia",
        "brand": "Top Job",
        "cat": "Glass",
        "ings": ["Water", "Ammonium Hydroxide", "Tetrasodium EDTA",
                 "Sodium C10-16 Alkylbenzenesulfonate",
                 "Sodium Xylene Sulphonate", "Yellow 5", "Yellow 8",
                 "Fragrance Ingredients", "Limonene"],
        "source": ("KIK Consumer Products California Cleaning Product Right "
                   "to Know (SB-258) ingredient disclosure for Top Job Lemon "
                   "Ammonia, 64 oz. UPC 8-36272-00075-8, disclosure dated "
                   "2019-10. Nine intentionally added ingredients with CAS "
                   "numbers; limonene flagged as an EU fragrance allergen."),
        "source_url": U + "2019/10/Top-Job-Lemon-Ammonia-64oz_8-36272-00075-8.pdf",
        "note": ("The unscented ammonia plus four lines: two yellow dyes, a "
                 "fragrance, and limonene flagged as an EU fragrance "
                 "allergen. Same bottle, same ammonia, four more ingredients. "
                 "If fragrance or dyes are the concern, the clear version is "
                 "on the same shelf at the same price."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Top Job is a KIK-branded value household cleaner. "
                      "Market-position vocabulary, not a single retail channel."),
        "substitutes": [sub("Top Job Clear Ammonia", "mass",
                            "Same brand, same size, same price, same ammonia. "
                            "Drops the two dyes, the fragrance and the named "
                            "allergen and changes nothing else.")],
        "exposure": 2,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("A value scented ammonia."),
    },

    # ---- Austin's (James Austin Company / KIK). ---------------------------
    {
        "name": "Austin's Clear Ammonia",
        "brand": "Austin's",
        "cat": "Glass",
        "ings": ["Water", "Ammonium Hydroxide"],
        "source": ("James Austin Company / KIK Consumer Products California "
                   "Cleaning Product Right to Know (SB-258) ingredient "
                   "disclosure for Austin's Clear Ammonia, 64 oz. UPC "
                   "0-54200-00051-3, disclosure dated 2019-11. Two "
                   "intentionally added ingredients with CAS numbers."),
        "source_url": U + "2019/11/Austins_Clear-Ammonia-64oz_0-54200-00051-3.pdf",
        "note": ("Two ingredients. Water and ammonium hydroxide. That is the "
                 "complete disclosed formula on a bottle of clear ammonia, "
                 "and it is the shortest list in this harvest. Every other "
                 "clear ammonia in this database adds a chelant and two "
                 "surfactants; this one adds nothing."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Austin's is a value household cleaning brand of the "
                      "James Austin Company, a KIK company since 2018. "
                      "Market-position vocabulary, not a single retail channel."),
        "substitutes": [sub("Top Job Clear Ammonia", "mass",
                            "Same active, same price band, three more lines "
                            "(a chelant and two surfactants). Listed as the "
                            "nearest shelf neighbour, not as an improvement: "
                            "the ammonia is identical.")],
        "exposure": 1,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("A value clear ammonia under the Austin's label."),
    },
    {
        "name": "Austin's Cleaning Vinegar",
        "brand": "Austin's",
        "cat": "Specialty",
        "ings": ["Water", "Acetic Acid"],
        "source": ("James Austin Company / KIK Consumer Products California "
                   "Cleaning Product Right to Know (SB-258) ingredient "
                   "disclosure for Austin's Cleaning Vinegar, 64 oz. UPC "
                   "0-54200-10005-3, disclosure dated 2019-11. Two "
                   "intentionally added ingredients with CAS numbers."),
        "source_url": U + "2019/11/Austins_Cleaning-Vinegar-64oz_0-54200-10005-3.pdf",
        "note": ("Two ingredients: water and acetic acid. Cleaning vinegar is "
                 "a higher-concentration acetic acid solution than the "
                 "kitchen bottle, and this filing makes that the whole "
                 "formula. Vinegar appears in this database as a graded "
                 "ingredient, which is Sandra's explicit ruling: the "
                 "marketing rule against vinegar does not apply to the "
                 "chemistry record. Never mix it with bleach."),
        "owner": "KIK Consumer Products", "owner_ev": "verified",
        "owner_src": SEC_APA,
        "tier": "mass", "tier_ev": "reported", "tier_src": KIK_PRODUCTS,
        "tier_note": ("Austin's is a value household cleaning brand of the "
                      "James Austin Company, a KIK company since 2018. "
                      "Market-position vocabulary, not a single retail channel."),
        "substitutes": [sub("Distilled White Vinegar (5%)", "apothecary-bulk",
                            "The same two ingredients at a lower acetic-acid "
                            "concentration, sold as a food-grade bulk "
                            "staple. Same chemistry, weaker solution; it "
                            "avoids nothing, it just dilutes what is already "
                            "a two-line formula.")],
        "exposure": 3,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp("Cleaning vinegar, a bulk staple; sold in the specialty/cleaning "
              "vinegar segment rather than as a surface spray."),
    },
]


# --------------------------------------------------------------------------
# Repairs. Both discovered while harvesting; neither is a new record.
# --------------------------------------------------------------------------
REPAIR_COMET_BATH = {
    "name": "Comet Bathroom",
    "set": {
        "ings": ["Water", "Citric Acid", "Sodium Hydroxide",
                 "Alcohols, C6-C12, Ethoxylated", "Cocamidopropyl Betaine",
                 "Sodium Cumene Sulfonate",
                 "Dipropylene Glycol n-Butyl Ether", "Fragrance"],
        "source": ("Homecare Labs / KIK Consumer Products California Cleaning "
                   "Product Right to Know (SB-258) ingredient disclosure for "
                   "Comet Bath Cleaner, 32 oz. UPC 8-10003-44031-0, disclosure "
                   "dated 2019-12; the 17 oz filing (UPC 8-10003-44030-3) "
                   "discloses the identical eight-line list. Eight "
                   "intentionally added ingredients with CAS numbers; sodium "
                   "hydroxide flagged on the California non-cancer hazards "
                   "list."),
        "source_url": U + "2019/12/5-Comet_Bath-Cleaner-32oz_8-10003-44031-0.pdf",
        "strength_disclosure": "full",
        "disclosure_note": ("List completed 2026-10-03. This record carried "
                            "four lines (water, citric acid, sodium hydroxide, "
                            "fragrance) and no source; the manufacturer filing "
                            "for Comet Bath Cleaner discloses eight, and the "
                            "four missing lines sat between the third and the "
                            "last. The manufacturer's list is now the source. "
                            "The record name is retained as found."),
        "updated": TODAY,
    },
}

REPAIR_WORKS_TB = {
    "name": "The Works Toilet Bowl Cleaner",
    "set": {
        "tier": "dollar-store",
        "tier_ev": "reported",
        "tier_src": DG_WORKS,
        "tier_note": ("The Works is a dollar-channel value brand. Dollar "
                      "General's own product page for this exact product "
                      "(UPC 074157033105) is a served, machine-readable page "
                      "and is the channel source."),
        "updated": TODAY,
    },
}


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

    repaired = 0
    by_name = {r["name"]: r for r in products}
    for rep in (REPAIR_COMET_BATH, REPAIR_WORKS_TB):
        rec = by_name.get(rep["name"])
        if rec is None:
            raise SystemExit(f"repair target missing: {rep['name']}")
        changed = False
        for k, v in rep["set"].items():
            if k == "ings":
                v = resolve(v, lower, added_keys)
            if rec.get(k) != v:
                rec[k] = v
                changed = True
        if changed:
            repaired += 1
            print(f"repair: {rep['name']}")

    # Minting runs after the repairs so keys first seen in a repair list are
    # written too; a key referenced by any record but absent from the registry
    # is the one failure this harvest must not produce.
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
            "text": (f"Spectrum harvest: {added} products added to the "
                     "bathroom, glass, cleanser and ammonia shelf from KIK "
                     "manufacturer SB-258 filings read 2026-10-03 "
                     "(Comet, The Works, Spic and Span, Top Job, Austin's). "
                     "Comet Bathroom list completed and sourced; The Works "
                     "Toilet Bowl Cleaner given a dollar-channel tier source."),
        })

    if DRY:
        print(f"\nDRY RUN: would add {added} products, "
              f"{len(added_keys)} ingredient keys, repair {repaired}.")
        return

    dump(os.path.join(DATA, "products.json"), products)
    dump(os.path.join(DATA, "ingredients.json"), ingredients)
    dump(os.path.join(DATA, "changelog.json"), changelog)
    print(f"\nadded {added} products, {len(added_keys)} ingredient keys, "
          f"repaired {repaired} records.")


if __name__ == "__main__":
    main()
