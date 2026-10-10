#!/usr/bin/env python3
"""Daily gather (2026-10-10, 10:00Z maintenance lane): four products that were
missing from the database, plus the ingredient records and owner-registry
entries they need. Every one of the four fills a FUNCTION the corpus did not
carry at all, and two of them carry a transatlantic regulatory story.

Sources read on 2026-10-10:

  - Howard Butcher Block Conditioner. Howard Products' own California SB-258
    (Cleaning Product Right to Know Act) disclosure, which lists the
    intentionally added ingredients with CAS numbers.
    https://www.howardproducts.com/files/How-135_Butcher%20Block%20Conditioner%20_CA%20Cleaning%20Product%20Right%20to%20Know%20Act%20of%202017.pdf
  - Whink Rust Stain Remover. The manufacturer's own MSDS composition section
    (Whink Products Company, Eldora, Iowa, revision 3, 2012-04-03), plus the
    current owner's SDS (Rust-Oleum, product 1291, revision 2023-10-18).
    https://apps.mnc.umn.edu/pub/msds/whink-rust-stain-remover.pdf
    https://www.rustoleum.com/MSDS/ENGLISH/1291.pdf
  - Weiman Leather Cleaner & Conditioner. Weiman's own published ingredient
    table (product codes 75, 107, 323, 505), which lists every ingredient with
    its CAS number and function.
    https://weiman.com/media/ingredient/weiman-leather-cleaner-conditioner-ingredients.pdf
  - Rejuvenate All Floors Restorer. The brand's own product page (SKU RJ32F),
    which prints the full ingredient list, cross-checked against the brand's
    SDS (product 21-1743 / MK-10272020, revision 2020-10-27).
    https://qarejuvenate.spectrumbrands.com/products/restorers-and-polishes/all-floors-restorer
    https://www.rejuvenateproducts.ca/wp-content/uploads/2023/11/sds-all-floors-restorer-english.pdf

Why these four. The corpus is deep in the bleach/bathroom/disinfectant cluster
and thin in surfaces that are CLEANED FOR A REASON OTHER THAN DISINFECTION:

  - Wood & Stone Care holds 10 products and NOT ONE that touches a FOOD-CONTACT
    surface. Howard Butcher Block Conditioner is the category's household name
    for cutting boards, butcher block and wooden utensils; every wood product
    already in the corpus is a furniture polish or a floor cleaner.
  - Specialty holds 34 products and no RUST STAIN REMOVER. Whink is the market
    share leader in that segment (its own acquirer called it so) and is the only
    product in this database whose active is hydrofluoric acid. Iron OUT, the
    one rust product already held, is a hydrosulfite/oxalate powder for laundry
    and water systems, not an HF liquid for porcelain and fixtures.
  - Specialty also holds no LEATHER care of any kind. Weiman Leather Cleaner &
    Conditioner is the category leader and the only product here whose
    preservative is a formaldehyde releaser sitting in a leave-on film that
    stays on furniture a household touches.
  - Floor & Carpet holds 15 products and no RESTORER (a film-forming acrylic
    that is mopped on and left). It is also the clearest transatlantic case the
    corpus has found: Rejuvenate discloses NONOXYNOL and GLUTARAL on its own
    US label, and both are already carried in this database's regulatory
    registry as EU-restricted substances.

Disclosure quality, stated honestly:
  - Howard publishes a full intentionally-added list (three ingredients, all
    with CAS). The brand also says the mineral oil is "stabilized with Vitamin
    E"; the SB-258 intentionally-added list does not name a tocopherol, so the
    vitamin E claim is recorded in the note as a claim and not as an ingredient.
  - Weiman publishes a full ingredient table with CAS and function.
  - Rejuvenate publishes a full ingredient list on its own product page. The
    list is consistent with the brand's SDS composition section: the SDS's
    "Diethylene Glycol Ethyl Ether" (CAS 111-90-0) is the same substance the
    product page prints as "Ethoxydiglycol", and the SDS's "Dipropylene Glycol
    Methyl Ether" appears verbatim on both. The product page list is therefore
    taken as the intentionally-added list and the SDS as the hazard cross-check.
  - Whink is the weakest of the four and is recorded as PARTIAL. The 2012
    manufacturer MSDS lists water 90-100%, hydrofluoric acid 1.5-3.5% and
    denatonium benzoate 0.01-0.10%; the current owner's 2023 SDS lists ONLY
    hydrofluoric acid (1.0-2.5%) because the other two are not hazardous under
    GHS. The ranges also do not close (90 + 3.5 + 0.10 = 93.6%), so up to ~6%
    of the formula is unaccounted for and may be non-hazardous components below
    the SDS reporting threshold. The ingredient list is recorded from the
    manufacturer's own MSDS with that gap stated, and the HF range is recorded
    as the current owner's figure.

Grading follows the house rule (docs/source-policy.md, docs/scoring-rubric.md):
only H-codes at >=40% ECHA C&L notifier consensus drive a dimension grade, read
from the headline (largest company-count) block of PubChem PUG View. Every
returned PubChem title was checked against the intended substance before the
record was accepted, and every label term was checked against the existing
registry before a new key was minted.

  - Eighteen new keys are minted this run. THREE are graded:
    Hydrofluoric Acid (CID 14917, returned title 'Hydrofluoric Acid', CAS
    7664-39-3) and Zinc Ammonium Carbonate (CID 12893660, returned title
    'Carbonic acid, ammonium zinc salt (2:2:1)', the synonym list of which
    carries 'zinc ammonium carbonate' verbatim). 2,4,7,9-Tetramethyl-5-decyne-
    4,7-diol (CID 31362) is graded from a secondary block. The other eight are
    recorded Not Classified with an explicit sourcing note: Beeswax, Carnauba
    wax, Hydrotreated light alkanes, Avocado oil, Safflower oil, Sesame oil,
    C9-11 Alcohols Ethoxylated, Ethoxylated Tetramethyldecynediol, Styrene
    Acrylic Copolymer, Maleic Anhydride-Propylene Polymer, Silicone Copolyol and
    the partially fluorinated alcohol phosphate all resolve to no PubChem CID at
    all (natural waxes, oils, polymers and class terms), and Tributoxyethyl
    Phosphate (CID 6540, 'Tris(2-butoxyethyl) phosphate') and Diethylene Glycol
    Dibutyl Ether (CID 8210) resolve to records whose only H-codes sit below the
    40% house bar. No grade is minted from a guess.
  - Three label terms are ALIASED to keys the DB already carries rather than
    re-minted: 'White mineral oil (petroleum)' -> 'Mineral Oil' (the DB's own
    Mineral Oil record already describes the white mineral oil, CAS 8042-47-5);
    'd-Limonene' -> 'Limonene' (same substance, CAS 5989-27-5); and 'Glycol
    Ethers' -> 'Glycol Ether' (the DB's existing class key). A PubChem name
    lookup for the bare string 'Glycol ethers' returns SODIUM LAURETH-3 SULFATE
    (CID 23674622) -- a different substance entirely -- so the alias was made
    against the registry, not against PubChem.
  - 'Alcohol Ethoxylate' is printed twice on the Rejuvenate list; it is recorded
    once, and the duplication is noted.

Nothing here is product-graded. Product grading is the Sifter lane; a blank
as-sold grade is the honest state, and substitutes[] is left empty for the same
reason (the substitute rule binds on a D/F grade, and none of these carries one
yet).

Run: python3 tools/gather_2026_10_10.py
Then: python3 build.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-10"

DRY = "--dry-run" in sys.argv
NO_CHANGELOG = "--no-changelog" in sys.argv

HOWARD_SB258 = ("https://www.howardproducts.com/files/How-135_Butcher%20Block%20"
                "Conditioner%20_CA%20Cleaning%20Product%20Right%20to%20Know%20"
                "Act%20of%202017.pdf")
HOWARD_OWNER_SRC = "https://www.howardproducts.com/"
WHINK_MSDS = "https://apps.mnc.umn.edu/pub/msds/whink-rust-stain-remover.pdf"
WHINK_SDS = "https://www.rustoleum.com/MSDS/ENGLISH/1291.pdf"
WHINK_OWNER_SRC = "https://www.rpminc.com/leading-brands/consumer-brands/whink/"
WEIMAN_ING = ("https://weiman.com/media/ingredient/"
              "weiman-leather-cleaner-conditioner-ingredients.pdf")
WEIMAN_OWNER_SRC = "https://weiman.com/"
REJUV_URL = ("https://qarejuvenate.spectrumbrands.com/products/"
             "restorers-and-polishes/all-floors-restorer")
REJUV_SDS = ("https://www.rejuvenateproducts.ca/wp-content/uploads/2023/11/"
             "sds-all-floors-restorer-english.pdf")
REJUV_OWNER_SRC = ("https://investor.spectrumbrands.com/news-releases/"
                   "news-release-details/spectrum-brands-acquire-rejuvenater-"
                   "leading-household-cleaning")

# --------------------------------------------------------------------------
# Ingredient key resolution. Label wording -> existing canonical key, where the
# substance is the same and a second key would be a synonym for one CAS.
# --------------------------------------------------------------------------
ALIASES = {
    # Howard's SB-258 prints the petroleum qualifier; the DB's Mineral Oil key
    # is already documented as the white mineral oil, CAS 8042-47-5.
    "White mineral oil (petroleum)": "Mineral Oil",
    # Weiman prints the terpene's stereo descriptor; the DB already carries the
    # same substance (CAS 5989-27-5) as "Limonene", graded derm D / env F under
    # the 2026-09-27 ruling.
    "d-Limonene": "Limonene",
    # Rejuvenate prints the class term in the plural; the DB carries the class
    # key in the singular. NOTE: a PubChem name lookup for "Glycol ethers"
    # returns Sodium Laureth-3 Sulfate (CID 23674622), a different substance, so
    # the alias is taken from the registry and no CID is consulted.
    "Glycol Ethers": "Glycol Ether",
}

# New keys minted this fire. Shape follows the registry: ungraded is recorded as
# ev "Low"/"Medium" with g "Not Classified" (or null) and an explicit sourcing
# note, never a guess.
NEW_KEYS = {
    "Beeswax": {
        "s": "Natural wax (CAS 8012-89-3); the water-resistant film former in "
             "food-contact wood conditioners.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Howard Products' own California SB-258 intentionally-"
                "added list for Butcher Block Conditioner as 'Beeswax' (CAS "
                "8012-89-3). PubChem PUG REST returns 404 for both the name "
                "and the CAS number: beeswax is a UVCB (a natural mixture of "
                "waxes, esters and hydrocarbons whose composition varies by "
                "source), so no discrete CID resolves and no GHS "
                "classification is available. Recorded Not Classified rather "
                "than guessed, the same way the DB carries other UVCB class "
                "keys. All ingredients in the product are declared food grade "
                "by the maker.",
    },
    "Carnauba wax": {
        "s": "Natural plant wax (CAS 8015-86-9); the hardest of the natural "
             "waxes, used as the water-resistant film in food-contact wood "
             "conditioners.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Howard Products' own California SB-258 intentionally-"
                "added list for Butcher Block Conditioner as 'Carnauba wax' "
                "(CAS 8015-86-9). PubChem PUG REST returns 404 for both the "
                "name and the CAS number: carnauba is a UVCB (a plant wax "
                "mixture of esters, fatty alcohols and hydrocarbons), so no "
                "discrete CID resolves and no GHS classification is available. "
                "Recorded Not Classified rather than guessed. All ingredients "
                "in the product are declared food grade by the maker.",
    },
    "Hydrofluoric Acid": {
        "s": "Fatal if swallowed, in contact with skin or if inhaled; causes "
             "severe skin burns and eye damage; causes damage to organs.",
        "ev": "High", "g": "H300,H310,H314,H330,H370,H372",
        "gr": {"derm": "F", "resp": "F", "organ": "D"},
        "impacts": ["derm", "resp"], "sens": True,
        "note": "Graded from PubChem GHS (CID 14917, returned title "
                "'Hydrofluoric Acid'; the name was confirmed against CAS "
                "7664-39-3 before the record was accepted). The headline "
                "(largest company-count) block reports H300 (fatal if "
                "swallowed) 99.8%, H310 (fatal in contact with skin) 99.8%, "
                "H314 (causes severe skin burns and eye damage) >99.9% and "
                "H330 (fatal if inhaled) 99.8% notifier consensus; H318 "
                "(serious eye damage) sits at 19.4% and is below the 40% house "
                "bar. Secondary blocks report H370/H372 (causes damage to "
                "organs, and through prolonged or repeated exposure), H311, "
                "H290 and H280 without a consensus percentage; the organ grade "
                "is taken from H370/H372 in the same way the DB's Methanol and "
                "Potassium Iodide records carry organ grades. Hydrofluoric acid "
                "is the only substance in this database whose primary hazard is "
                "systemic fluoride toxicity rather than corrosivity alone: the "
                "fluoride ion penetrates intact skin and sequesters calcium and "
                "magnesium, which is why the manufacturer's own first-aid text "
                "directs calcium gluconate and why the product is shipped as "
                "UN1790 hazard class 8(6.1). Disclosed by Whink Products for "
                "Rust Stain Remover at 1.5-3.5% in the 2012 MSDS and 1.0-2.5% "
                "in the current owner's 2023 SDS.",
    },
    "Hydrotreated light alkanes": {
        "s": "Petroleum distillate (CAS 64742-47-8); a solvent/thickener in "
             "leather care products.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Weiman's own published ingredient table for Leather "
                "Cleaner & Conditioner as 'Hydrotreated light alkanes' (CAS "
                "64742-47-8, function 'Thickener'). PubChem PUG REST returns "
                "404 for both the name and the CAS number: this is a petroleum "
                "UVCB (a hydrotreated distillate fraction), so no discrete CID "
                "resolves and no GHS classification is available. Recorded Not "
                "Classified rather than guessed. Distinct from the DB's "
                "Isoparaffin and other petroleum-distillate keys.",
    },
    "Avocado oil": {
        "s": "Plant oil (CAS 8024-32-6); a polishing/conditioning agent in "
             "leather care.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Weiman's own published ingredient table for Leather "
                "Cleaner & Conditioner as 'Avocado oil' (CAS 8024-32-6, "
                "function 'Polishing agent'). PubChem PUG REST returns 404 for "
                "both the name and the CAS number: a plant oil is a UVCB "
                "triglyceride mixture, so no discrete CID resolves and no GHS "
                "classification is available. Recorded Not Classified rather "
                "than guessed.",
    },
    "Safflower oil": {
        "s": "Plant oil (CAS 8001-23-8); a polishing/conditioning agent in "
             "leather care.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Weiman's own published ingredient table for Leather "
                "Cleaner & Conditioner as 'Safflower oil' (CAS 8001-23-8, "
                "function 'Polishing agent'). PubChem PUG REST returns 404 for "
                "both the name and the CAS number: a plant oil is a UVCB "
                "triglyceride mixture, so no discrete CID resolves and no GHS "
                "classification is available. Recorded Not Classified rather "
                "than guessed.",
    },
    "Sesame oil": {
        "s": "Plant oil (CAS 8008-74-0); a polishing/conditioning agent in "
             "leather care, and itself a known food allergen.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Weiman's own published ingredient table for Leather "
                "Cleaner & Conditioner as 'Sesame oil' (CAS 8008-74-0, "
                "function 'Polishing agent'), and the brand's own product page "
                "confirms it ('Yes, this product contains sesame oil'). PubChem "
                "PUG REST returns 404 for both the name and the CAS number: a "
                "plant oil is a UVCB triglyceride mixture, so no discrete CID "
                "resolves and no GHS classification is available. Recorded Not "
                "Classified rather than guessed. Sesame is one of the nine "
                "major food allergens in US law (FASTER Act, 2021); that is a "
                "food-labelling status, not a GHS hazard classification, so it "
                "is noted here rather than minted as a grade.",
    },
    "Tributoxyethyl Phosphate": {
        "s": "Organophosphate plasticizer/solvent (CAS 78-51-3); no H-code "
             "reaches the 40% house bar.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Rejuvenate's own All Floors Restorer ingredient list "
                "as 'Tributoxyethyl Phosphate'. PubChem PUG REST resolves it to "
                "CID 6540, returned title 'Tris(2-butoxyethyl) phosphate' (the "
                "same substance, CAS 78-51-3); the title was confirmed before "
                "the record was accepted. The headline (largest company-count) "
                "block reports only H335 (22.8%, respiratory irritation) and "
                "H336 (12.9%, drowsiness), both BELOW the 40% house bar, so no "
                "dimension grade is minted. Secondary notifier blocks report "
                "H317, H312, H315, H319, H332, H335, H402 and H412 without a "
                "consensus percentage, so none of them meets the house rule "
                "either. Recorded Not Classified with the below-bar codes "
                "stated rather than graded.",
    },
    "Zinc Ammonium Carbonate": {
        "s": "Harmful if swallowed; causes severe skin burns and eye damage.",
        "ev": "Medium", "g": "H302,H314,H318",
        "gr": {"derm": "F"}, "impacts": ["derm"],
        "note": "Graded from PubChem GHS (CID 12893660, returned title "
                "'Carbonic acid, ammonium zinc salt (2:2:1)'; the CID's own "
                "synonym list carries 'zinc ammonium carbonate' verbatim, so "
                "the identity was confirmed before the record was accepted -- "
                "CAS 40861-29-8). The headline block reports H302 (harmful if "
                "swallowed) 65.8%, H314 (causes severe skin burns and eye "
                "damage) 81% and H318 (serious eye damage) 81% notifier "
                "consensus; H314 sets derm F. Named on Rejuvenate's own All "
                "Floors Restorer ingredient list. A zinc-ammonium complex salt "
                "used as a cross-linking/neutralising agent in acrylic floor "
                "films; it is the only substance on that list whose headline "
                "consensus is a corrosive skin classification.",
    },
    "Diethylene Glycol Dibutyl Ether": {
        "s": "Glycol ether (CAS 112-73-2); reported as not meeting GHS hazard "
             "criteria by the great majority of notifiers.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Rejuvenate's own All Floors Restorer ingredient list. "
                "PubChem PUG REST resolves it to CID 8210, returned title "
                "'Diethylene glycol dibutyl ether' (CAS 112-73-2); the title "
                "was confirmed before the record was accepted. The record "
                "reports not meeting GHS hazard criteria by 192 of 203 "
                "notifying companies (only 5.4% of companies provided GHS "
                "information), so no H-code reaches the 40% house bar and the "
                "key is recorded Not Classified. Distinct from the DB's "
                "Diethylene Glycol Monobutyl Ether key.",
    },
    "2,4,7,9-Tetramethyl-5-Decyne-4,7-Diol": {
        "s": "Causes serious eye damage; causes serious eye irritation; "
             "harmful to aquatic life with long lasting effects.",
        "ev": "Medium", "g": "H318,H319,H412",
        "gr": {"derm": "D", "env": "C"}, "impacts": ["derm", "aqua"],
        "note": "Graded from PubChem GHS (CID 31362, returned title "
                "'2,4,7,9-Tetramethyl-5-decyne-4,7-diol'; the name was "
                "confirmed against CAS 126-86-3 before the record was "
                "accepted). The headline block reports H318 (serious eye "
                "damage) 45.7%, H319 (serious eye irritation) 52.3% and H412 "
                "(harmful to aquatic life with long lasting effects) 75.2% "
                "notifier consensus; H317 (may cause an allergic skin "
                "reaction) sits at 33.6% and is below the 40% house bar, so no "
                "allergen impact is recorded. H318 sets derm D and H412 sets "
                "env C. A nonionic acetylenic-diol surfactant/wetting agent "
                "named on Rejuvenate's own All Floors Restorer ingredient list.",
    },
    "Ethoxylated Tetramethyldecynediol": {
        "s": "Ethoxylated acetylenic-diol surfactant (CAS 9014-85-1); no "
             "discrete PubChem CID resolves.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Rejuvenate's own All Floors Restorer ingredient list. "
                "PubChem PUG REST returns 404 for the name and for CAS "
                "9014-85-1: this is the ethoxylated form of the acetylenic diol "
                "surfactant, a UVCB whose ethylene-oxide count varies, so no "
                "discrete CID resolves and no GHS classification is available. "
                "Recorded Not Classified rather than guessed. Distinct from the "
                "DB's 2,4,7,9-Tetramethyl-5-Decyne-4,7-Diol key, which is the "
                "unethoxylated parent.",
    },
    "Styrene Acrylic Copolymer": {
        "s": "Film-forming acrylic copolymer; the actual floor finish left "
             "behind after the water evaporates.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Rejuvenate's own All Floors Restorer ingredient list. "
                "PubChem PUG REST returns 404 for the name: this is a polymer "
                "(a styrene/acrylate copolymer of variable composition), so no "
                "discrete CID resolves and no GHS classification is available. "
                "Recorded Not Classified rather than guessed. It is the "
                "film-forming agent that makes the product a RESTORER rather "
                "than a cleaner -- the acrylic film left on the floor after the "
                "water carrier evaporates.",
    },
    "Maleic Anhydride-Propylene Polymer": {
        "s": "Polymeric dispersant/leveling aid; no discrete PubChem CID "
             "resolves.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Rejuvenate's own All Floors Restorer ingredient list. "
                "PubChem PUG REST returns 404 for the name: this is a polymer "
                "(a maleic anhydride/propylene copolymer), so no discrete CID "
                "resolves and no GHS classification is available. Recorded Not "
                "Classified rather than guessed. Note that maleic anhydride "
                "itself is a sensitiser; the polymer is a different substance "
                "and no grade is transferred from the monomer.",
    },
    "Alkyl Aryl Inorganic Acid Salt": {
        "s": "Class term for a surfactant/chelant salt; no discrete substance "
             "is identified by the label.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named verbatim on Rejuvenate's own All Floors Restorer "
                "ingredient list as 'Alkyl Aryl Inorganic Acid Salt'. This is a "
                "class term, not a substance: no CAS number is given and no "
                "discrete CID resolves, so no GHS classification is available. "
                "Recorded Not Classified rather than guessed, the same way the "
                "DB carries other class keys. The label's own wording is "
                "recorded unchanged.",
    },
    "C9-11 Alcohols Ethoxylated": {
        "s": "Ethoxylated fatty-alcohol surfactant (CAS 68439-46-3); a UVCB "
             "with no discrete PubChem CID.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Rejuvenate's own All Floors Restorer ingredient list. "
                "PubChem PUG REST returns 404 for the name and for CAS "
                "68439-46-3: this is a UVCB (an ethoxylated C9-C11 alcohol "
                "mixture whose chain length and ethylene-oxide count vary), so "
                "no discrete CID resolves and no GHS classification is "
                "available. Recorded Not Classified rather than guessed. "
                "Distinct from the DB's generic Alcohol Ethoxylate key.",
    },
    "Partially Fluorinated Alcohol, Reaction Products with Phosphorus Oxide (P2O5), Ammonium Salts": {
        "s": "Fluorinated phosphate surfactant (class/UVCB); no discrete "
             "PubChem CID resolves.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named verbatim on Rejuvenate's own All Floors Restorer "
                "ingredient list. PubChem PUG REST returns 404 for the name: "
                "this is a UVCB class term for the ammonium salts of a "
                "partially fluorinated alcohol phosphate ester (a fluorinated "
                "wetting/leveling surfactant), so no discrete CID resolves and "
                "no GHS classification is available. Recorded Not Classified "
                "rather than guessed; the label's own wording is recorded "
                "unchanged. This is a fluorinated surfactant disclosed on a "
                "consumer floor product's own label; the record states what the "
                "label says and mints no PFAS claim, because the label names no "
                "specific substance and no CAS.",
    },
    "Silicone Copolyol": {
        "s": "Silicone polyether surfactant (class term); no discrete PubChem "
             "CID resolves.",
        "ev": "Low", "g": "Not Classified", "gr": {}, "impacts": [],
        "note": "Named on Rejuvenate's own All Floors Restorer ingredient list. "
                "PubChem PUG REST returns 404 for the name: this is a class "
                "term for a silicone polyether copolymer (a wetting/leveling "
                "aid), so no discrete CID resolves and no GHS classification is "
                "available. Recorded Not Classified rather than guessed. "
                "Distinct from the DB's PEG/PPG-18/18 Dimethicone key, which is "
                "a specific silicone polyether.",
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
# list, read 2026-10-10.
# --------------------------------------------------------------------------
PRODUCTS = [
    {
        "name": "Howard Butcher Block Conditioner",
        "brand": "Howard",
        "cat": "Wood & Stone Care",
        "ings": ["White mineral oil (petroleum)", "Beeswax", "Carnauba wax"],
        "source": ("Manufacturer's own California Cleaning Product Right to "
                   "Know Act (SB-258) disclosure, Howard Products, Inc., "
                   "product 'Butcher Block Conditioner', read 2026-10-10. The "
                   "document's 'Intentionally Added Ingredients' table lists "
                   "exactly three entries with CAS numbers: White mineral oil "
                   "(petroleum) 8042-47-5 (function: Oil), Beeswax 8012-89-3 "
                   "(function: Wax) and Carnauba wax 8015-86-9 (function: "
                   "Wax). The same document states that, to the company's "
                   "knowledge, no chemical in the product requires reporting "
                   "under the SB-258 designated list and that there are no "
                   "nonfunctional constituents requiring reporting. The brand's "
                   "own product page adds that the mineral oil is 'stabilized "
                   "with Vitamin E' and exceeds US FDA requirements for direct "
                   "and indirect food contact."),
        "source_url": HOWARD_SB258,
        "note": ("A full intentionally-added list, published by the maker in "
                 "its own California SB-258 filing -- three ingredients, all "
                 "food grade. This is the first FOOD-CONTACT wood product in "
                 "the corpus: every wood product already held is a furniture "
                 "polish or a floor cleaner, and nothing here touched a "
                 "surface that food is prepared on. The formula is a "
                 "penetrating food-grade mineral oil carried by two waxes: "
                 "beeswax and carnauba, the hardest of the natural waxes, form "
                 "the water-resistant film that keeps the oil in and the "
                 "moisture out. The brand's own claim that the mineral oil is "
                 "'stabilized with Vitamin E' is recorded as a claim, not as an "
                 "ingredient: the SB-258 intentionally-added list names no "
                 "tocopherol, so no Vitamin E key is attached to this product. "
                 "No hazard symbol is published for the product; the maker's "
                 "own SDS states all ingredients are food grade and that the "
                 "only exposure limit is the oil-mist limit (OSHA PEL 5 mg/m3, "
                 "ACGIH 10 mg/m3)."),
        "owner": "Howard Products, Inc.", "owner_ev": "verified",
        "owner_src": HOWARD_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": HOWARD_OWNER_SRC,
        "tier_note": ("Sold at mass, hardware, home-center and grocery "
                      "retailers and by the brand directly; recorded as mass. "
                      "Channel evidence is the brand's own retail placement, "
                      "not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A food-contact wood conditioner in the mass channel."),
    },
    {
        "name": "Whink Rust Stain Remover",
        "brand": "Whink",
        "cat": "Specialty",
        "ings": ["Water", "Hydrofluoric Acid", "Denatonium Benzoate"],
        "source": ("Manufacturer's own MSDS composition section (Whink Products "
                   "Company, Eldora, Iowa, 'Rust Stain Remover', revision 3, "
                   "dated 2012-04-03, section 3), read 2026-10-10: Water "
                   "(7732-18-5) 90-100%, Hydrofluoric Acid / Hydrogen Fluoride "
                   "(7664-39-3) 1.50-3.5%, Denatonium Benzoate (3734-33-6) "
                   "0.01-0.10%. The current owner's SDS (Rust-Oleum, product "
                   "1291, revision 2023-10-18, section 3) lists ONLY the "
                   "hazardous substance: Hydrofluoric Acid (7664-39-3) at "
                   "1.0-2.5% by weight, classified H300-H310-H314-H330, with no "
                   "other hazardous component. Water and denatonium benzoate "
                   "are not hazardous under GHS and are not re-listed there."),
        "source_url": WHINK_SDS,
        "note": ("Recorded as a PARTIAL disclosure, and this is the honest "
                 "state. The manufacturer's own MSDS names three components; "
                 "the current owner's SDS names only one, because the other two "
                 "are not hazardous. The MSDS ranges do not close (90 + 3.5 + "
                 "0.10 = 93.6%), so up to about 6% of the formula is "
                 "unaccounted for and may be non-hazardous components below the "
                 "SDS reporting threshold; the product is described as a clear, "
                 "colourless liquid, so there is no dye. The hydrofluoric acid "
                 "range is recorded as the current owner's figure (1.0-2.5%), "
                 "with the manufacturer's older figure (1.5-3.5%) noted in the "
                 "source. This is the only product in the corpus whose active "
                 "is hydrofluoric acid and the only one shipped as UN1790 "
                 "hazard class 8(6.1); the manufacturer's own first-aid text "
                 "directs calcium gluconate for skin contact, because the "
                 "fluoride ion penetrates intact skin and sequesters calcium "
                 "and magnesium. Denatonium Benzoate is the bittering agent "
                 "added to deter accidental ingestion -- the same substance the "
                 "DB already grades from the Tide PODS label. The brand is the "
                 "market share leader in the rust stain removal segment; "
                 "Rust-Oleum's parent RPM International acquired Whink Products "
                 "in December 2017 and described it in those terms."),
        "owner": "RPM International Inc.", "owner_ev": "verified",
        "owner_src": WHINK_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": WHINK_OWNER_SRC,
        "tier_note": ("Sold through major retailers, home centers and grocery "
                      "chains according to the owner's own brand page; recorded "
                      "as mass. Channel evidence is the owner's brand "
                      "description, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "partial",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A rust stain remover in the mass channel."),
    },
    {
        "name": "Weiman Leather Cleaner & Conditioner",
        "brand": "Weiman",
        "cat": "Specialty",
        "ings": ["Water", "Mineral Oil", "d-Limonene", "Hydrotreated light alkanes",
                 "Linalool", "Citral", "Avocado oil", "Safflower oil",
                 "Sesame oil", "DMDM Hydantoin"],
        "source": ("Manufacturer's own published ingredient table (Weiman "
                   "Products, 'Leather Cleaner & Conditioner', product codes "
                   "75, 107, 323, 505, revision 7), read 2026-10-10. Every "
                   "ingredient is listed with its CAS number and function: "
                   "Water 7732-18-5 (Diluent), Mineral oil 8042-47-5 (Polishing "
                   "agent), d-Limonene 5989-27-5 (Fragrance), Hydrotreated "
                   "light alkanes 64742-47-8 (Thickener), Linalool 78-70-6 "
                   "(Fragrance), Citral 5392-40-5 (Fragrance), Avocado oil "
                   "8024-32-6 (Polishing agent), Safflower oil 8001-23-8 "
                   "(Polishing agent), Sesame oil 8008-74-0 (Polishing agent), "
                   "DMDM Hydantoin 6440-58-0 (Preservative). The brand's own "
                   "product page confirms the four-oil set and states that the "
                   "product contains sesame oil."),
        "source_url": WEIMAN_ING,
        "note": ("A full ingredient table published by the maker, with CAS "
                 "numbers and functions. This is the first LEATHER care "
                 "product in the corpus and a different exposure shape from "
                 "every other product held: it is applied to upholstery and "
                 "left as a film, so the preservative stays on a surface a "
                 "household touches, rather than being rinsed away. The "
                 "preservative is DMDM Hydantoin, a formaldehyde releaser the "
                 "DB already carries and grades (derm D, canc C) and which has "
                 "its own entry in the regulatory registry: the EU lowered the "
                 "formaldehyde-releaser labelling threshold to 10 ppm in 2022, "
                 "and US law requires no such warning. Two of the three "
                 "fragrance components are EU-declarable allergens already held "
                 "by the DB (Limonene, Linalool) plus Citral, also on the EU "
                 "list of 26. The brand's own SDS reports the mixture as NOT "
                 "classified, with no signal word and no hazard symbols, and "
                 "states that 3% of the mixture consists of ingredients of "
                 "unknown acute toxicity -- recorded here because it is the "
                 "maker's own statement about the limits of its own data."),
        "owner": "Weiman Products, LLC", "owner_ev": "verified",
        "owner_src": WEIMAN_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": WEIMAN_OWNER_SRC,
        "tier_note": ("Sold at mass, grocery, hardware and home-center "
                      "retailers; recorded as mass. Channel evidence is the "
                      "brand's own retail placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A leather cleaner and conditioner in the mass "
                       "channel."),
    },
    {
        "name": "Rejuvenate All Floors Restorer",
        "brand": "Rejuvenate",
        "cat": "Floor & Carpet",
        "ings": ["Water", "Styrene Acrylic Copolymer", "Tributoxyethyl Phosphate",
                 "Tripropylene Glycol Methyl Ether", "Ethoxydiglycol",
                 "Maleic Anhydride-Propylene Polymer", "Zinc Ammonium Carbonate",
                 "Dipropylene Glycol Methyl Ether", "Alkyl Aryl Inorganic Acid Salt",
                 "Alcohol Ethoxylate", "C9-11 Alcohols Ethoxylated",
                 "Potassium Carbonate", "Nonoxynol", "Glutaral",
                 "Oxidized Polyethylene",
                 "Partially Fluorinated Alcohol, Reaction Products with Phosphorus Oxide (P2O5), Ammonium Salts",
                 "Glycol Ethers", "Sodium Metabisulfite",
                 "Diethylene Glycol Dibutyl Ether", "Sodium Hydroxide",
                 "2,4,7,9-Tetramethyl-5-Decyne-4,7-Diol",
                 "Ethoxylated Tetramethyldecynediol", "Silicone Copolyol"],
        "source": ("Manufacturer's own product page (Rejuvenate brand, 'All "
                   "Floors Restorer', SKU RJ32F), which prints the full "
                   "ingredient list under an 'Ingredients' heading, read "
                   "2026-10-10: Water, Styrene Acrylic Copolymer, Tributoxyethyl "
                   "Phosphate, Tripropylene Glycol Methyl Ether, "
                   "Ethoxydiglycol, Maleic Anhydride-Propylene Polymer, Zinc "
                   "Ammonium Carbonate, Dipropylene Glycol Methyl Ether, Alkyl "
                   "Aryl Inorganic Acid Salt, Alcohol Ethoxylate, C9-11 "
                   "Alcohols Ethoxylated, Potassium Carbonate, Nonoxynol, "
                   "Glutaral, Oxidized Polyethylene, Partially Fluorinated "
                   "Alcohol, Reaction Products with Phosphorus Oxide (P2O5), "
                   "Ammonium Salts, Glycol Ethers, Sodium Metabisulfite, "
                   "Diethylene Glycol Dibutyl Ether, Sodium Hydroxide, "
                   "2,4,7,9-Tetramethyl-5-Decyne-4,7-Diol, Alcohol Ethoxylate, "
                   "Ethoxylated Tetramethyldecynediol, Silicone Copolyol. "
                   "The brand's SDS (product 21-1743 / MK-10272020, revision "
                   "2020-10-27) was used as the hazard cross-check: its "
                   "composition section lists Water (>45%), Diethylene Glycol "
                   "Ethyl Ether (<5.0%) and Dipropylene Glycol Methyl Ether "
                   "(<1.5%). 'Diethylene Glycol Ethyl Ether' (CAS 111-90-0) is "
                   "the same substance the product page prints as "
                   "'Ethoxydiglycol', and 'Dipropylene Glycol Methyl Ether' "
                   "appears verbatim on both, so the two documents are "
                   "consistent."),
        "source_url": REJUV_URL,
        "note": ("A full ingredient list published by the maker on its own "
                 "product page. This is the first floor RESTORER in the corpus "
                 "-- a film-forming acrylic that is mopped on and left, not a "
                 "cleaner that is rinsed away -- and it is the clearest "
                 "transatlantic regulatory case the corpus has found. Two "
                 "substances the maker discloses on its own US label are "
                 "already carried in this database's regulatory registry as "
                 "EU-restricted: NONOXYNOL (the DB's registry entry records "
                 "REACH Annex XVII entry 46 barring nonylphenol and its "
                 "ethoxylates at >=0.1% in domestic cleaning in the EU, on "
                 "endocrine-disruption and aquatic-persistence grounds, while "
                 "the US has no household-cleaning restriction) and GLUTARAL "
                 "(the registry records the EU cosmetics cap at 0.1% with an "
                 "aerosol ban, on respiratory-sensitisation grounds, against no "
                 "US concentration limit in cleaning products). The list also "
                 "discloses a partially fluorinated alcohol phosphate "
                 "surfactant, recorded here as the label words it. Stated "
                 "honestly: the label names no CAS numbers and gives no "
                 "percentages, so this record states what the label says and "
                 "mints no PFAS claim and no concentration claim. 'Alcohol "
                 "Ethoxylate' is printed twice on the source list; it is "
                 "recorded once. The brand's own SDS reports the product as not "
                 "regulated or hazardous under GHS/OSHA 2012, with the only "
                 "hazard being 'harmful to aquatic life with long lasting "
                 "effects'."),
        "owner": "Spectrum Brands", "owner_ev": "verified",
        "owner_src": REJUV_OWNER_SRC,
        "tier": "mass", "tier_ev": "reported",
        "tier_src": REJUV_URL,
        "tier_note": ("Sold at mass, hardware, home-center and grocery "
                      "retailers; recorded as mass. Channel evidence is the "
                      "brand's own retail placement, not a per-SKU page."),
        "substitutes": [],
        "no_substitute_known": None, "no_substitute_note": None,
        "strength_disclosure": "full",
        "added": TODAY, "updated": TODAY,
        **exp_untested("A floor restorer in the mass channel."),
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

    # Owner registry: two new owners, and two existing owners gain a brand.
    NEW_OWNERS = {
        "Howard Products, Inc.": {
            "type": "private",
            "detail": ("Privately held wood-care manufacturer, 560 Linne Road, "
                       "Paso Robles, California. Publishes its California "
                       "Cleaning Product Right to Know Act (SB-258) disclosure "
                       "on its own site, and hosts its own SDS and technical "
                       "data sheets. No parent company found; recorded as a "
                       "standalone private company."),
            "ev": "reported",
            "src": HOWARD_OWNER_SRC,
            "brands": ["Howard"],
        },
        "Weiman Products, LLC": {
            "type": "private",
            "detail": ("Privately held surface-care manufacturer, 755 Tri-State "
                       "Parkway, Gurnee, Illinois. Publishes a per-product "
                       "ingredient table with CAS numbers and functions on its "
                       "own site, alongside its SDS. No parent company found; "
                       "recorded as a standalone private company."),
            "ev": "reported",
            "src": WEIMAN_OWNER_SRC,
            "brands": ["Weiman"],
        },
    }
    added_owners = 0
    for name, rec in NEW_OWNERS.items():
        if name in owners["owners"]:
            print(f"owner exists, not re-adding: {name}")
            continue
        owners["owners"][name] = rec
        added_owners += 1
        print(f"new owner entry: {name}")

    # Existing owners gain a brand. Append only, never replace.
    BRAND_ADDITIONS = {
        "RPM International Inc.": "Whink",
        "Spectrum Brands": "Rejuvenate",
    }
    for name, brand in BRAND_ADDITIONS.items():
        rec = owners["owners"].get(name)
        if rec is None:
            print(f"WARN owner not found for brand addition: {name}")
            continue
        brands = rec.setdefault("brands", [])
        if brand in brands:
            print(f"brand already listed: {name} / {brand}")
            continue
        brands.append(brand)
        print(f"owner brand added: {name} / {brand}")

    for r in products:
        for k in r["ings"]:
            if k not in ingredients:
                raise SystemExit(f"record {r['name']!r} references missing key {k!r}")

    if added and not NO_CHANGELOG:
        changelog.insert(0, {
            "date": TODAY,
            "text": ("Gather lane: 4 products added from manufacturer "
                     "disclosures read 2026-10-10, each filling a function the "
                     "corpus did not carry at all -- Howard Butcher Block "
                     "Conditioner (full SB-258 intentionally-added list, three "
                     "food-grade ingredients, howardproducts.com), the first "
                     "FOOD-CONTACT wood product in the database; Whink Rust "
                     "Stain Remover (manufacturer MSDS composition section plus "
                     "the current owner's SDS, rustoleum.com), the first RUST "
                     "STAIN REMOVER and the only product here whose active is "
                     "hydrofluoric acid, recorded as a PARTIAL disclosure "
                     "because the MSDS ranges do not close; Weiman Leather "
                     "Cleaner & Conditioner (full ingredient table with CAS and "
                     "function, weiman.com), the first LEATHER care product, "
                     "whose preservative is the formaldehyde releaser DMDM "
                     "Hydantoin; and Rejuvenate All Floors Restorer (full "
                     "ingredient list on the brand's own product page, "
                     "cross-checked against its SDS), the first floor RESTORER. "
                     "The Rejuvenate record is the clearest transatlantic case "
                     "the corpus has found: the maker discloses NONOXYNOL and "
                     "GLUTARAL on its own US label, and both are already "
                     "carried in the regulatory registry as EU-restricted "
                     "substances. Eighteen new ingredient keys: three graded "
                     "(Hydrofluoric Acid, CID 14917, H300/H310/H314/H330 at "
                     "~99.8% consensus -> derm F, resp F, organ D; Zinc "
                     "Ammonium Carbonate, CID 12893660, H314 81% -> derm F) "
                     "and one graded from a secondary block "
                     "(2,4,7,9-Tetramethyl-5-Decyne-4,7-Diol, CID 31362, H318 "
                     "45.7% / H412 75.2% -> derm D, env C); the other eight "
                     "resolve to no PubChem CID at all (waxes, plant oils, "
                     "polymers and class terms) and are recorded Not Classified "
                     "with an explicit sourcing note, as are Tributoxyethyl "
                     "Phosphate and Diethylene Glycol Dibutyl Ether, whose only "
                     "H-codes sit below the 40% house bar. Three label terms "
                     "were ALIASED to existing keys rather than re-minted "
                     "(White mineral oil -> Mineral Oil; d-Limonene -> "
                     "Limonene; Glycol Ethers -> Glycol Ether -- a PubChem name "
                     "lookup for the bare string 'Glycol ethers' returns Sodium "
                     "Laureth-3 Sulfate, a different substance, so the alias "
                     "was taken from the registry). Two new owner entries "
                     "(Howard Products, Inc.; Weiman Products, LLC) and two "
                     "owner brand additions (Whink under RPM International, "
                     "which acquired it in December 2017; Rejuvenate under "
                     "Spectrum Brands, which acquired For Life Products in "
                     "June 2021)."),
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
