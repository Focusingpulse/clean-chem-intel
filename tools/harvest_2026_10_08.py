#!/usr/bin/env python3
"""Spectrum harvest, night-shift station 2, 2026-10-08.

Tier worked: the two largest US retailers' house brands -- Walmart's Great Value
and Sam's Club's Member's Mark -- ordered by exposure. Every ingredient list is
read from the retailer's own California Cleaning Product Right to Know Act
(SB-258) ingredient disclosure, served from the retailer's own CDN, which is the
manufacturer's published specification and therefore `verified` under
docs/certainty.md.

Routes (both already in docs/source-policy.md):
  Walmart   https://i5.walmartimages.com/dfw/.../k2-_<uuid>.v1.pdf
  Sam's Club https://scene7.samsclub.com/is/content/samsclub/<upc>_pdf

Two filings located this fire are deliberately NOT entered:
  * Great Value Ultimate Fresh Blooming Lavender Fabric Softener Sheets 240 CT
    -- 45 of its 47 disclosed lines are fragrance constituents with only two
    non-fragrance lines behind them. That is the shape the open
    `fragrance-components-as-ingredient-keys` ruling governs, so it is held out
    rather than deepening an unruled decision at T-7 days from launch.
  * PINK LOTION DISH DETERGENT (MEMBERS MARK COMMERCIAL), Ecolab -- the filing
    declares Level 3 PARTIAL disclosure on both axes and withholds three
    ingredients by name. strength_disclosure has no render surface, so a partial
    list would render identically to a complete one.

Idempotent: a product already present by name is skipped, and an ingredient key
that already exists (case-insensitively, or through the alias map) is never
re-minted.

Usage:
  python3 tools/harvest_2026_10_08.py [--dry-run] [--no-changelog]
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TODAY = "2026-10-08"

OWNER = "Walmart Inc."
OWNER_SRC = "https://corporate.walmart.com/about"

# --- exposure sources (all read live 2026-10-08) ---------------------------
SRC_LAUNDRY = ("https://www.indexbox.io/store/united-states-laundry-home-products-"
               "market-analysis-forecast-size-trends-and-insights/")
SRC_SURFACE = ("https://www.indexbox.io/store/united-states-household-surface-cleaners-"
               "market-analysis-forecast-size-trends-and-insights/")
SRC_WIPES = ("https://www.indexbox.io/store/united-states-cleaning-wipes-"
             "market-analysis-forecast-size-trends-and-insights/")
SRC_DISH = ("https://www.indexbox.io/store/united-states-dishwashing-"
            "market-analysis-forecast-size-trends-and-insights/")
SRC_BLEACH = ("https://www.indexbox.io/store/united-states-bleach-"
              "market-analysis-forecast-size-trends-and-insights/")

WALMART_TIER_NOTE = ("Walmart house brand; the filing names Walmart, Inc. as distributor and "
                     "{maker} as manufacturer of record.")
SAMS_TIER_NOTE = ("Sam's Club house brand; the filing names Sam's West, Inc. as distributor and "
                  "{maker} as manufacturer of record.")

# --- products --------------------------------------------------------------
# name, brand, cat, source_url, source (prose), note, ings, exposure,
# exposure_src, exposure_basis, tier_note, substitutes, no_substitute_known,
# no_substitute_note, strength_disclosure, disclosure_note
PRODUCTS = [
    dict(
        name="Great Value Automatic Dishwasher Powder",
        brand="Great Value", cat="Dishwasher",
        source_url="https://i5.walmartimages.com/dfw/4ff9c6c9-f85c/k2-_3523b4ab-9d04-4599-b26d-df49b6e06dde.v1.pdf",
        source=("Walmart California Cleaning Product Right to Know (SB-258) ingredient disclosure for this "
                "product, published by Walmart on its own CDN (disclosure dated 9/30/2019, UPC 0-78742-27672-4, "
                "GS1 10000406 Dish Cleaning/Care - Automatic). Manufacturer of record Korex Corporation, "
                "distributor Walmart, Inc. Nineteen intentionally added ingredients with CAS numbers, including "
                "both enzymes and three fragrance/colour components. Read today from the served PDF."),
        note=("The largest US retailer's house-brand dishwasher powder, and the disclosure is unusually complete: "
              "the builder system (sodium sulfate, sodium carbonate, sodium percarbonate, sodium citrate, sodium "
              "silicate), two trade-secret copolymers, both enzymes and the three non-functional components are all "
              "named. Three things the filing itself flags are worth reading. Titanium dioxide is declared as the "
              "colourant and is marked present on the IARC carcinogens list. Myrcene, a fragrance component, is also "
              "marked IARC. Both enzymes are marked present on the EU respiratory sensitisers list, which is the "
              "standard detergent-enzyme caution rather than a formulation choice. Entered ungraded."),
        ings=["Sodium Sulfate", "Sodium Carbonate", "Sodium Percarbonate", "Sodium Citrate",
              "Sodium Silicate", "Acrylic Acid/Sulfonate Copolymer/Terpolymer",
              "Maleic/Olefin Copolymer", "2-Propenoic Acid, Telomer with Sodium Hydrogen Sulfite, Sodium Salt",
              "Alcohols, C10-12, Ethoxylated, Propoxylated", "Amylase", "Protease",
              "Phosphonic Acid, (1-Hydroxyethylidene)bis-, Tetrasodium Salt", "Myrcene", "Limonene",
              "Polyvinyl Alcohol", "Titanium Dioxide", "Polyoxyethylene Trimethyldecyl Alcohol",
              "Sucrose", "Starch"],
        exposure=4, exposure_src=SRC_DISH,
        exposure_basis=("Derived, not measured. The cited dishwashing page states private label and retailer "
                        "brands hold an estimated 16-19% of retail unit volume and that pod/tablet formats are "
                        "60-65% of the automatic segment, against dishwasher ownership in roughly seven of ten "
                        "US households. Walmart is the largest US retailer by household reach (its own corporate "
                        "page states approximately 280 million customers and members visit more than 10,900 "
                        "stores and clubs each week). Searched for a published US household-penetration or "
                        "unit-share figure for this specific Walmart house-brand dishwasher powder and located "
                        "none; SKU-level private-label share is not published. Rounded to one significant figure, "
                        "order-of-magnitude."),
        tier_note=WALMART_TIER_NOTE.format(maker="Korex Corporation"),
        substitutes=[
            dict(name="Seventh Generation Dishwasher Powder, Free & Clear", tier="grocery",
                 note=("Fragrance-free powder in the same aisle and price band. Avoids the myrcene and titanium "
                       "dioxide colourant this filing declares, and drops the percarbonate load.")),
            dict(name="AspenClean Zero Plastic Dishwasher Powder", tier="natural",
                 note=("Sodium citrate, carbonate and percarbonate only, with no fragrance or colourant at all. "
                       "Costs more than the Great Value tub, so it is a substitute for the chemistry, not for "
                       "the price.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Great Value Automatic Dishwasher Gel, Lemon Scent",
        brand="Great Value", cat="Dishwasher",
        source_url="https://i5.walmartimages.com/dfw/4ff9c6c9-4790/k2-_b07dff17-5a5f-440b-a5f3-9a4aba86d9d8.v1.pdf",
        source=("Walmart California Cleaning Product Right to Know (SB-258) ingredient disclosure for this "
                "product, published by Walmart on its own CDN (disclosure dated 9/30/2019, UPC 0-78742-27670-0, "
                "GS1 10000406 Dish Cleaning/Care - Automatic). Manufacturer of record Korex Corporation, "
                "distributor Walmart, Inc. Nineteen intentionally added ingredients with CAS numbers. Read today "
                "from the served PDF."),
        note=("Same brand, same maker and same disclosure date as the Great Value dishwasher powder, and a "
              "completely different formula: the powder is a percarbonate builder system with no preservative, "
              "the gel is water-based with xanthan gum for body and an isothiazolinone preservative pair. Two "
              "things the filing itself flags: propylene glycol is marked present on the US NTP reproductive or "
              "developmental toxicants list, and phenoxyethanol is marked on the California TACs list. Both "
              "enzymes are marked EU respiratory sensitisers. Entered ungraded."),
        ings=["Water", "Tetrasodium Glutamate Diacetate", "Sodium Citrate",
              "Alcohols, C10-12, Ethoxylated, Propoxylated", "Acrylic Acid/Sulfonate Copolymer/Terpolymer",
              "Maleic/Olefin Copolymer", "Xanthan Gum", "Protease", "Sodium Benzoate", "Amylase",
              "Myrcene", "Benzyl Benzoate", "Limonene", "Methylchloroisothiazolinone",
              "Methylisothiazolinone", "Propylene Glycol", "Glycerin", "Sodium Formate", "Phenoxyethanol"],
        exposure=4, exposure_src=SRC_DISH,
        exposure_basis=("Derived, not measured. The cited dishwashing page states private label and retailer "
                        "brands hold an estimated 16-19% of retail unit volume and that manual dish liquids and "
                        "gels carry a smaller share of the automatic segment than pods and tablets. Walmart is "
                        "the largest US retailer by household reach. Searched for a published US "
                        "household-penetration or unit-share figure for this specific Walmart house-brand "
                        "dishwasher gel and located none; SKU-level private-label share is not published. "
                        "Rounded to one significant figure, order-of-magnitude."),
        tier_note=WALMART_TIER_NOTE.format(maker="Korex Corporation"),
        substitutes=[
            dict(name="ECOS Dishwasher Gel, Free & Clear", tier="natural",
                 note=("The direct same-form swap. Fragrance-free, so it avoids the myrcene and benzyl benzoate "
                       "components this filing declares, and it does not carry the isothiazolinone preservative "
                       "pair that drives the sensitisation concern in the gel.")),
            dict(name="Great Value Automatic Dishwasher Powder", tier="grocery",
                 note=("Same brand, same price, different form. The powder carries no isothiazolinone "
                       "preservative and no phenoxyethanol, so it trades the gel's preservative load for the "
                       "powder's colourant and percarbonate.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Great Value Fresh Disinfectant Wipes, 75 ct",
        brand="Great Value", cat="Disinfectant",
        source_url="https://i5.walmartimages.com/dfw/4ff9c6c9-662d/k2-_3726d786-a7c3-4289-9988-9e037cb633a5.v1.pdf",
        source=("Walmart California Cleaning Product Right to Know (SB-258) ingredient disclosure for this "
                "product, published by Walmart on its own CDN (disclosure dated 9/4/2019, UPC 078742344454, "
                "GS1 10000405 Surface Cleaners). Manufacturer of record US Nonwovens, LLC, distributor Walmart, "
                "Inc. Six intentionally added ingredients with CAS numbers. Read today from the served PDF."),
        note=("The largest US retailer's house-brand disinfecting wipes, and the whole disclosed formula is "
              "water, four quaternary ammonium actives and a fragrance. That is a shorter list than the "
              "Member's Mark house-brand wipes already in this database, which add a secondary alcohol "
              "ethoxylate, tetrasodium EDTA and sodium silicate pentahydrate on top of the same four quats. "
              "Same category, same retailer tier, different formula, which is the point of the entry. The "
              "filing states every line is not present on any chemical list of concern; the actives are still "
              "quaternary ammonium compounds, which is the respiratory and skin-sensitisation concern in this "
              "category regardless of the filing's own hazard column. Entered ungraded."),
        ings=["Water", "Octyl Decyl Dimethyl Ammonium Chloride", "Dioctyldimethylammonium Chloride",
              "Didecyldimonium Chloride", "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride", "Fragrance"],
        exposure=8, exposure_src=SRC_WIPES,
        exposure_basis=("Derived, not measured. The cited cleaning wipes page states over 90% of US households "
                        "use at least one type of cleaning wipe regularly, and that the value-tier pricing "
                        "segment (private label and entry-level national brands) accounts for 30-35% of "
                        "category volume. Walmart is the largest US retailer by household reach, and its own "
                        "product page for the sibling wipes SKU carries thousands of ratings. Searched for a "
                        "published US household-penetration or unit-share figure for this specific Walmart "
                        "house-brand wipes SKU and located none. Rounded to one significant figure, "
                        "order-of-magnitude."),
        tier_note=WALMART_TIER_NOTE.format(maker="US Nonwovens, LLC"),
        substitutes=[
            dict(name="up&up Multi-Purpose Cleaner, Free & Clear", tier="grocery",
                 note=("For routine wiping, a fragrance-free spray and a cloth removes the four quat actives "
                       "and the fragrance entirely. It does not carry a disinfectant claim, which is the "
                       "trade: you give up the kill claim, not the cleaning.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Great Value Original Fresh Scent Glass Cleaner",
        brand="Great Value", cat="Glass",
        source_url="https://i5.walmartimages.com/dfw/4ff9c6c9-aeaf/k2-_80584dd7-3d55-4876-9bae-f445e79d9886.v1.pdf",
        source=("Walmart California Cleaning Product Right to Know (SB-258) ingredient disclosure for this "
                "product, published by Walmart on its own CDN (disclosure dated 7/23/2019, UPC 0 78742 04960 1, "
                "GS1 10000746 Cleaners Other). Manufacturer of record KIK Custom Products, distributor Walmart, "
                "Inc. Seven intentionally added ingredients with CAS numbers and no fragrance at all. Read "
                "today from the served PDF."),
        note=("A glass cleaner with no fragrance line, which is unusual and worth noting on its own: this "
              "filing declares no fragrance component, so there is nothing withheld behind a 'Fragrance' entry. "
              "What it does declare is the standard ammonia-and-glycol-ether glass formula: a butyl glycol "
              "ether acetate as the main solvent, propylene glycol, an alkyl polyglucoside surfactant, ammonium "
              "hydroxide for the streak-free finish, tetrasodium EDTA and a blue dye. A sibling Great Value "
              "glass cleaner filing adds sodium hydroxide as a non-functional ingredient. Entered ungraded."),
        ings=["Water", "Ethylene Glycol Monobutyl Ether Acetate", "Propylene Glycol",
              "C9-11 Alkyl Glucoside", "Ammonium Hydroxide", "Tetrasodium EDTA", "Direct Blue 86"],
        exposure=4, exposure_src=SRC_SURFACE,
        exposure_basis=("Derived, not measured. The cited household surface cleaners page states approximately "
                        "95% of US households use at least one surface cleaner product per month, and that "
                        "specialised cleaners (bathroom, kitchen, glass, floor) hold 30-35% of category value "
                        "with bathroom the largest sub-segment, so glass is the smaller part of that band. "
                        "Walmart is the largest US retailer by household reach and its own page names Great "
                        "Value among the value/entry tier brands. Searched for a published US "
                        "household-penetration or unit-share figure for this specific SKU and located none. "
                        "Rounded to one significant figure, order-of-magnitude."),
        tier_note=WALMART_TIER_NOTE.format(maker="KIK Custom Products"),
        substitutes=[],
        no_substitute_known=None, no_substitute_note=None,
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Great Value Automatic Toilet Bowl Cleaner with Bleaching Action",
        brand="Great Value", cat="Bathroom",
        source_url="https://i5.walmartimages.com/dfw/4ff9c6c9-5fd6/k2-_ca55bbfc-4f24-4439-b1f1-1de5331fc389.v1.pdf",
        source=("Walmart California Cleaning Product Right to Know (SB-258) ingredient disclosure for this "
                "product, published by Walmart on its own CDN (disclosure dated 8/19/2019, UPC 0 78742 08943 0). "
                "Manufacturer of record KIK Custom Products, distributor Walmart, Inc. Four intentionally added "
                "ingredients with CAS numbers and no fragrance. Read today from the served PDF; the product's own "
                "SDS on the same disclosure lists the same four components by weight (54.2 / 28.9 / 15.9 / 1 "
                "percent)."),
        note=("A drop-in toilet tank tablet, and the disclosed formula is four lines: three chlorinated "
              "hydantoins and sodium chloride. There is no hypochlorite in it, so a 'with bleaching action' "
              "tablet is a different substance class from liquid bleach, and it is the same substance class as "
              "the The Works toilet bowl tablets already in this database. Same chemistry, a dollar-store brand "
              "and the largest retailer's private label, two price points. These are strong oxidisers and the "
              "SDS on the same filing classifies the mixture as an oxidising solid, corrosive, so the handling "
              "caution is real. Entered ungraded."),
        ings=["1-Bromo-3-chloro-5,5-dimethylhydantoin", "1,3-Dichloro-5,5-dimethylhydantoin",
              "1,3-Dichloro-5-ethyl-5-methylhydantoin", "Sodium Chloride"],
        exposure=3, exposure_src=SRC_SURFACE,
        exposure_basis=("Derived, not measured. The cited household surface cleaners page states approximately "
                        "95% of US households use at least one surface cleaner product per month and that "
                        "bathroom cleaners are the largest specialised sub-segment at 30-35% of category value. "
                        "Drop-in tank tablets are one format inside toilet care rather than the whole segment. "
                        "Walmart is the largest US retailer by household reach. Searched for a published US "
                        "household-penetration or unit-share figure for this specific SKU and located none. "
                        "Rounded to one significant figure, order-of-magnitude."),
        tier_note=WALMART_TIER_NOTE.format(maker="KIK Custom Products"),
        substitutes=[
            dict(name="up&up Toilet Bowl Cleaner, Fresh Scent", tier="grocery",
                 note=("A manual gel in the same aisle at the same price band. It is not a chlorinated "
                       "hydantoin, so it avoids the oxidiser load and the corrosive classification the SDS on "
                       "this filing carries. It gives up the tank-drop convenience.")),
            dict(name="The Works Toilet Bowl Cleaner", tier="dollar-store",
                 note=("Cheaper than the Great Value tablets and the same job, without the oxidising tablet "
                       "chemistry. Read its own entry first: the formula differs by SKU in that brand.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Great Value Low-Splash Bleach, 43 oz",
        brand="Great Value", cat="Disinfectant",
        source_url="https://i5.walmartimages.com/dfw/4ff9c6c9-f8e0/k2-_ee6dfa7b-83e3-4324-a637-f9a28df9fb93.v1.pdf",
        source=("Walmart California Cleaning Product Right to Know (SB-258) ingredient disclosure for this "
                "product, published by Walmart on its own CDN (disclosure dated 10/4/2019, UPC 0 78742 33150 8, "
                "GS1 Bleach (Non-FIFRA Regulated)). Manufacturer of record KIK Custom Products, distributor "
                "Walmart, Inc. Five intentionally added ingredients with CAS numbers. Read today from the "
                "served PDF."),
        note=("The thickened bleach format, and the formula shows exactly what makes it low-splash: water, "
              "sodium hypochlorite, sodium hydroxide, then two surfactants, myristamine oxide and coconut "
              "fatty acid, that raise the viscosity so it does not spatter. Sodium hydroxide is marked on the "
              "California non-cancer hazards list in the filing itself. Compare the plain value bleach already "
              "in this database, which is water, hypochlorite and hydroxide only: the low-splash product is "
              "that formula plus two surfactants. Entered ungraded."),
        ings=["Water", "Sodium Hypochlorite", "Sodium Hydroxide", "Myristamine Oxide", "Coconut Fatty Acid"],
        exposure=6, exposure_src=SRC_BLEACH,
        exposure_basis=("Derived, not measured. The cited bleach page states near-universal household "
                        "penetration, estimated at 80-90% of United States households purchasing bleach at "
                        "least once per year, and that private-label and store-brand products now account for "
                        "an estimated 25-35% of retail volume. Splash-less thickened liquid is one of several "
                        "formats the same page names, alongside thin liquid and gel, so it is a share of that "
                        "base rather than the base. Searched for a published US household-penetration or "
                        "unit-share figure for this specific SKU and located none. Rounded to one significant "
                        "figure, order-of-magnitude."),
        tier_note=WALMART_TIER_NOTE.format(maker="KIK Custom Products"),
        substitutes=[
            dict(name="Seventh Generation Chlorine Free Bleach", tier="natural",
                 note=("Hydrogen peroxide rather than sodium hypochlorite, so it avoids chlorine and the "
                       "sodium hydroxide stabiliser this filing declares. It is a different product to use: "
                       "slower on whites and not a registered disinfectant.")),
            dict(name="OxiClean Versatile Stain Remover", tier="grocery",
                 note=("Sodium carbonate peroxide, an oxygen bleach in the same laundry aisle and a similar "
                       "price per load. Avoids chlorine and hydroxide entirely, and it is for laundry soaking "
                       "rather than surface disinfection.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Member's Mark Active Clean Laundry Detergent SPORT",
        brand="Member's Mark", cat="Laundry",
        source_url="https://scene7.samsclub.com/is/content/samsclub/078742266800_pdf",
        source=("Sam's Club California Cleaning Product Right to Know (SB-258) ingredient disclosure for this "
                "product, published by Sam's Club on its own CDN (disclosure dated 11/8/2019, UPC 078742266800, "
                "GS1 10000424 Laundry Detergents). Manufacturer of record Henkel Corporation, distributor "
                "Sam's West, Inc. Forty-one intentionally added ingredients with CAS numbers, including "
                "three enzymes and nineteen individually named fragrance components. Read today from the served PDF."),
        note=("The first Sam's Club laundry detergent in this database, and the disclosure is the fullest "
              "laundry list here alongside the Great Value Ultimate Fresh entry: three enzymes (protease, "
              "amylase and mannanase), the polymer and brightener system, both preservatives and "
              "nineteen named fragrance components. Three things the filing itself flags: ethanol is marked "
              "present on the California Prop 65, IARC carcinogens and US NTP carcinogens lists, both named "
              "enzymes are marked EU respiratory sensitisers and AOEC asthmagens, and 2-bromo-2-nitropropane-"
              "1,3-diol is a formaldehyde-releasing preservative. Manufacturer of record is Henkel, not Sam's "
              "Club. Entered ungraded."),
        ings=["Water", "Alcohols, C12-15, Ethoxylated", "Sodium Laureth Sulfate", "Sodium Citrate",
              "Sodium (C10-16) Alkylbenzenesulfonate", "Triethanolamine Alkyl C10-16-benzenesulfate",
              "Alcohol", "Polyethyleneimine Alkoxylated", "Sodium Cocoate", "Cocamidopropyl Betaine",
              "Tetrasodium Iminodisuccinate", "Modified Polycarboxylate", "Disodium Distyrylbiphenyl Disulfonate",
              "Calcium Chloride", "Benzene, C10-13 alkyl derivatives", "Protease", "Amylase",
              "2-Bromo-2-Nitropropane-1,3-Diol", "Colorant", "Mannanase Enzyme", "Potassium Chloride",
              "Methylchloroisothiazolinone", "Methylisothiazolinone", "Fragrance", "Galaxolide",
              "1-Butanone, 3-(dodecylthio)-1-(2,6,6-trimethyl-3-cyclohexen-1-yl)-", "Benzyl Salicylate",
              "Hexyl Salicylate", "Triethanolamine", "Tricyclodecenyl Propionate", "Mixed Ionones",
              "Tetramethyl Acetyloctahydronaphthalenes", "Butylphenyl Methylpropional", "alpha-Isomethyl Ionone",
              "Anisaldehyde", "2,6-Dimethyl-7-Octen-2-ol", "Dipropylene Glycol", "Methyldihydrojasmonate",
              "Methyl Decenol", "Phenethyl Alcohol", "Amyl Cinnamal"],
        exposure=3, exposure_src=SRC_LAUNDRY,
        exposure_basis=("Derived, not measured. The cited laundry & home products page states household "
                        "penetration above 98% for the category and that private label and retail-brand "
                        "products are now estimated at 18-22% of unit volume in laundry care. Member's Mark is "
                        "Sam's Club's house brand and Sam's Club is a membership warehouse club, so its "
                        "household reach is materially narrower than Walmart's even though the per-SKU volume "
                        "is high, which is why this estimate sits below the Great Value laundry entry already "
                        "in the database. Searched for a published US household-penetration or unit-share "
                        "figure for this specific SKU and located none. Rounded to one significant figure, "
                        "order-of-magnitude."),
        tier_note=SAMS_TIER_NOTE.format(maker="Henkel Corporation"),
        substitutes=[
            dict(name="Seventh Generation Free & Clear Laundry Detergent", tier="natural",
                 note=("Fragrance-free, so it removes the nineteen named fragrance components and the "
                       "formaldehyde-releasing preservative this filing declares, and it does not carry the "
                       "isothiazolinone pair. It costs more per load than the Member's Mark jug.")),
            dict(name="ATTITUDE Liquid Laundry Detergent, Unscented", tier="natural",
                 note=("Unscented and enzyme-light. Avoids the fragrance load and both isothiazolinone "
                       "preservatives; check its own entry for the surfactant base before swapping on a "
                       "sensitive-skin household.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Great Value Ultimate Fresh Original Clean Fabric Softener, 129 oz",
        brand="Great Value", cat="Laundry",
        source_url="https://i5.walmartimages.com/dfw/4ff9c6c9-b142/k2-_247245e9-896e-42e5-ad2d-015ad2b00ca5.v1.pdf",
        source=("Walmart California Cleaning Product Right to Know (SB-258) ingredient disclosure for this "
                "product, published by Walmart on its own CDN (disclosure dated 11/22/2019, UPC 0007874219997, "
                "GS1 10000747 Laundry Other). Manufacturer of record Henkel Corporation, distributor Walmart, "
                "Inc. Thirty-four intentionally added ingredients with CAS numbers. Read today from the served "
                "PDF."),
        note=("The first liquid fabric softener in this database, in a category that had almost no coverage "
              "against very high household use. The disclosure is complete, and what it shows is the shape of "
              "the product: a ten-line non-fragrance backbone (a cationic softener active, ethanol, lactic "
              "acid, glutaral preservative, two polymers, calcium chloride, a melamine resin dispersant, "
              "xanthan gum and a colourant) and twenty-four named fragrance components behind the fragrance "
              "entry. Three things the filing itself flags: ethanol is marked present on the California Prop "
              "65, IARC carcinogens and US NTP carcinogens lists, glutaral is marked EU respiratory sensitiser, "
              "California non-cancer hazards and AOEC asthmagen, and four of the fragrance components are EU "
              "fragrance allergens. Entered ungraded."),
        ings=["Water",
              "Ethanaminium, 2-hydroxy-N-(2-hydroxyethyl)-N,N-dimethyl-, esters with C16-18 and C18-unsatd. fatty acids, chlorides",
              "Alcohol", "Lactic Acid", "Glutaral", "Polyquaternium-37", "Calcium Chloride", "Melamine Resin",
              "Xanthan Gum", "Colorant", "Fragrance", "Isobutyl Methyl Tetrahydropyranol", "Dipropylene Glycol",
              "Linalool", "2,6-Dimethyl-7-Octen-2-ol", "Verdyl Acetate",
              "Tetramethyl Acetyloctahydronaphthalenes", "2,4-Dimethyl-3-Cyclohexene Carboxaldehyde",
              "4-tert-Butylcyclohexyl Acetate", "Benzyl Acetate", "Tricyclodecenyl Propionate", "Geraniol",
              "Citrus Aurantium Dulcis (Orange) Peel Oil", "Hexyl Acetate",
              "Hydroxyisohexyl 3-Cyclohexene Carboxaldehyde", "Nerol", "alpha-Isomethyl Ionone", "Coumarin",
              "Gamma-Undecalactone", "Phenethyl Alcohol", "Terpineol", "Methylbenzyl Acetate", "Prenyl Acetate",
              "Benzyl Benzoate"],
        exposure=8, exposure_src=SRC_LAUNDRY,
        exposure_basis=("Derived, not measured. The cited laundry & home products page states household "
                        "penetration above 98% for the category and that private label and retail-brand "
                        "products are now estimated at 18-22% of unit volume in laundry care. Fabric softener "
                        "is used by a smaller share of households than detergent, and this database holds only "
                        "a handful of softener records against a large detergent set, so the estimate sits "
                        "below the Great Value laundry detergent entry already in the database despite the "
                        "same retailer reach. Searched for a published US household-penetration or unit-share "
                        "figure for this specific SKU and located none. Rounded to one significant figure, "
                        "order-of-magnitude."),
        tier_note=WALMART_TIER_NOTE.format(maker="Henkel Corporation"),
        substitutes=[],
        no_substitute_known=True,
        no_substitute_note=("Accepted constraint, not a research gap. The hazard in a liquid fabric softener "
                            "is largely the product: the cationic softener active that makes it work, plus the "
                            "fragrance load and the glutaral preservative. There is no same-price product swap "
                            "that removes those and still softens clothes, and a fragrance-free softener was "
                            "not located in this database at any price. What the entry documents instead is the "
                            "actionable alternative, which is not another softener: skip the softener entirely, "
                            "or use dryer balls and a fragrance-free detergent."),
        strength_disclosure="full", disclosure_note=None,
    ),
]

# --- label term -> existing registry key ----------------------------------
# Only where the substance is the same and the registry already carries it.
ALIASES = {
    "Sodium citrate dihydrate": "Sodium Citrate",
    "Glycerol": "Glycerin",
    "Mannanase": "Mannanase Enzyme",
    "Polyethyleneimine Ethoxylate": "Polyethyleneimine Alkoxylated",
    "Hexamethylindanopyran": "Galaxolide",
    "Acetylcedrene": "Acetyl Cedrene",
    "Citrus Aurantium Dulcis (Orange) Oil": "Citrus Aurantium Dulcis (Orange) Peel Oil",
    "C9-C11 Alkyl Polyglucoside": "C9-11 Alkyl Glucoside",
    "Dioctyl Dimethyl Ammonium Chloride": "Dioctyldimethylammonium Chloride",
    "Didecyl Dimonium Chloride": "Didecyldimonium Chloride",
    "Dimethyl-3-Cyclohexene-1-Carboxaldehyde": "2,4-Dimethyl-3-Cyclohexene Carboxaldehyde",
    "Methyl Ionones": "Mixed Ionones",
    "Amylase alpha": "Amylase",
    "Protease enzyme": "Protease",
    "2-Bromo-2 Nitropropane-1,3-Diol": "2-Bromo-2-Nitropropane-1,3-Diol",
    "Benzene, C10-13, alkyl derivatives": "Benzene, C10-13 alkyl derivatives",
    "Sodium, C10-16 Alkylbenzenesulfonate": "Sodium (C10-16) Alkylbenzenesulfonate",
    "Fragrance ingredients, withheld as CBI": "Fragrance",
}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-changelog", action="store_true")
    args = ap.parse_args()

    prods_path = REPO / "data/products.json"
    ings_path = REPO / "data/ingredients.json"
    products = json.loads(prods_path.read_text(encoding="utf-8"))
    ingredients = json.loads(ings_path.read_text(encoding="utf-8"))

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
            if term in ALIASES:
                key = ALIASES[term]
                assert key in ingredients, f"alias target missing: {key}"
                aliased.append((term, key))
                resolved.append(key)
                continue
            if term.lower() in exact:
                key = exact[term.lower()]
                aliased.append((term, key))
                resolved.append(key)
                continue
            if norm(term) in folded:
                key = folded[norm(term)]
                aliased.append((term, key))
                resolved.append(key)
                continue
            # mint
            if term not in minted:
                minted.append(term)
            if not args.dry_run:
                ingredients[term] = {
                    "ev": "Low", "g": None, "gr": {}, "impacts": [],
                    "note": ("Minted 2026-10-08 from a retailer California SB-258 ingredient disclosure and "
                             "recorded ungraded. No PubChem or ECHA grade has been resolved for this entry "
                             "yet, so g is null rather than a guess."),
                    "s": f"{term}. Listed in the manufacturer disclosure; not yet graded against GHS.",
                    "added": TODAY,
                }
            exact[term.lower()] = term
            folded[norm(term)] = term
            resolved.append(term)

        assert len(resolved) == len(spec["ings"]), spec["name"]
        assert len(set(resolved)) == len(resolved), f"dup ingredient in {spec['name']}"

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
            "tier": "grocery",
            "tier_ev": "reported",
            "tier_src": spec["source_url"],
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
            "added": TODAY,
            "updated": TODAY,
            "owner_ev": "reported",
            "owner_src": OWNER_SRC,
        }
        if spec.get("disclosure_note"):
            rec["disclosure_note"] = spec["disclosure_note"]
        products.append(rec)
        added_records.append(rec)

    print(f"added {len(added_records)} products; skipped (already present) {len(skipped)}")
    for r in added_records:
        print(f"  + {r['name']}  ({len(r['ings'])} ingredients, exposure {r['exposure']})")
    if skipped:
        print("  skipped:", skipped)
    print(f"aliased {len(aliased)} label terms onto existing keys:")
    for a, b in sorted(set(aliased)):
        print(f"    {a!r} -> {b!r}")
    print(f"minted {len(minted)} new ingredient keys:")
    for m in minted:
        print(f"    {m}")

    # case-variant guard. Two checks, kept apart on purpose:
    #   1. collisions that PRE-EXIST this harvest are reported, not fatal -- this
    #      lane is the harvest lane, and a merged key changes which grade a
    #      product reads, which is a grade-surface change that belongs with a
    #      ruling. Recorded to gaps/ instead of repaired here.
    #   2. collisions this harvest would CREATE are fatal.
    by_norm = {}
    for k in ingredients:
        by_norm.setdefault(norm(k), []).append(k)
    pre_existing = {n: ks for n, ks in by_norm.items() if len(ks) > 1}
    mine = {norm(k) for k in ingredients if k in set(minted)}
    own_collisions = {n: ks for n, ks in pre_existing.items() if n in mine}
    if pre_existing:
        print(f"PRE-EXISTING case/space-variant collisions ({len(pre_existing)}), NOT repaired by this fire:")
        for n, ks in sorted(pre_existing.items()):
            print(f"    {ks}")
    if own_collisions:
        print("COLLISIONS CREATED BY THIS HARVEST -- refusing to write:", own_collisions)
        sys.exit(1)

    if args.dry_run:
        print("dry run: no files written")
        return

    def dump(path, obj, indent, trailing_newline):
        text = json.dumps(obj, ensure_ascii=False, indent=indent)
        if trailing_newline:
            text += "\n"
        path.write_text(text, encoding="utf-8")

    dump(prods_path, products, 1, False)
    dump(ings_path, ingredients, 1, False)

    if not args.no_changelog and added_records:
        cl = json.loads((REPO / "data/changelog.json").read_text(encoding="utf-8"))
        if not cl or cl[0].get("date") != TODAY or "station 2" not in cl[0].get("text", ""):
            cl.insert(0, {
                "date": TODAY,
                "text": (f"Spectrum harvest station 2 (Dolman {TODAY}): {len(added_records)} products added to the "
                         "Walmart / Sam's Club house-brand block, ordered by exposure. Every ingredient list read "
                         "from the retailer's own California SB-258 disclosure on its own CDN. "
                         f"{len(minted)} new ingredient keys minted, all ungraded. Substitutes set on every "
                         "record whose ingredients carry a hazard flag; one accepted-constraint no_substitute_known."),
            })
            dump(REPO / "data/changelog.json", cl, 2, True)


if __name__ == "__main__":
    main()
