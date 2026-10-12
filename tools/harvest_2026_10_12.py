#!/usr/bin/env python3
"""Spectrum harvest, night-shift station 2, 2026-10-12.

HARVEST: eight missing high-exposure household cleaning products, every
ingredient list read from the manufacturer's own published California
Cleaning Product Right to Know Act (SB-258) disclosure form.

Why these eight. The spectrum data build is complete across all four channel
tiers. The KIK value-brand index is exhausted for household products, and the
largest remaining category gap (air care) is blocked on the open
fragrance-components-as-ingredient-keys ruling, not on a route. What is
genuinely missing is high-exposure household products from Church & Dwight's
cleaning family, whose own per-product disclosure index is a working route
(verified HTTP 200 today, 716 filings). The set takes the two thinnest
mid-size categories in the corpus (Floor & Carpet, 17 records; Wood & Stone
Care, 11 records), plus bathroom, disinfectant, and laundry, which are the
highest-penetration surfaces there are (IndexBox: approximately 95% of US
households use at least one surface cleaner per month; laundry and home
products above 98%):

  1. OxiClean Foam-Tastic Bathroom Cleaner, Fresh Scent        (Bathroom, aerosol)
  2. OxiClean Bathroom Cleaner, Fresh Scent                    (Bathroom)
  3. OxiClean Mold & Mildew Stain Remover with Bleach          (Disinfectant)
  4. Kaboom Plus Disinfex 3-in-1 Bathroom Spray                (Disinfectant)
  5. Orange Glo Multi-Surface Cleaner                          (Floor & Carpet)
  6. Orange Glo Wood Furniture 2-in-1 Clean & Polish           (Wood & Stone Care)
  7. Arm & Hammer Clean Scentsations Scent Booster, Fresh Burst (Laundry, in-wash)
  8. Xtra Plus OxiClean Powder Laundry Detergent, Summer Breeze (Laundry, powder)

Mapping discipline. A label term is mapped to the closest EXISTING key wherever
the substance is the same, so a graded key is never bypassed by an equivalent
twin. The mappings made this fire and why:

  - "Butoxydiglycol" (CAS 112-34-5) -> "Diethylene Glycol Monobutyl Ether":
    same CAS, and the pairing Linnea's 2026-10-08 R1 already routed.
  - "Sodium lauryl sulfate" (the filing prints CAS 68585-47-7, which is the
    C10-16 alkyl sulfate, not the CAS 151-21-3 substance of that name)
    -> "SODIUM C10-16 ALKYL SULFATE", the CAS match.
  - "Sodium laureth sulfate" (filing prints CAS 68585-34-2)
    -> "SODIUM C10-16 ALKETH-2 SULFATE", the CAS match.
  - "Sodium xylene sulfonate" -> the merged key "Sodium Xylenesulfonate".
  - "Hydrated silica" -> "Silica".
  - "Sorbitan oleate" -> the existing "Sorbitan Monooleate" (same substance).
  - "Dearomatized alkanes" (CAS 64742-47-8) -> the existing
    "Hydrotreated light alkanes", which is the same CAS and was itself named
    from a manufacturer table. NOTE: this registry carries CAS 64742-47-8 on
    three keys with divergent evidence ("C11-15 Alkane/Cycloalkane" records
    H304, the other two record Not Classified). That is the duplicate-substance
    class already filed to Trellis; this fire maps by served name and discloses
    the collision rather than resolving it.
  - The Arm & Hammer filing's long dye-blend string -> the existing "Colorant",
    with the served text quoted in the record's source prose.
  - Fragrance components disclosed at or above 100 ppm are quoted in the record's
    source prose and NOT minted as keys, because the
    fragrance-components-as-ingredient-keys question is an open ruling.

Owner. Church & Dwight's consumer brand page (churchdwight.com/our-brands/
consumer-brands/, read 2026-10-12, HTTP 200) names every brand in this set,
so the existing "Church & Dwight" owner record gains Kaboom, Xtra and Orange
Glo, and its record-level src is upgraded from /our-brands/ (which names only
Arm & Hammer) to /our-brands/consumer-brands/ (which names them all). That
upgrade is a precision improvement against the already-filed apply_owners
src-precision gap, not a new claim; it is disclosed in the finding.

Idempotent: a product already present by name is skipped, an ingredient key
that already exists (case-insensitively, or through the alias map) is never
re-minted, and the owner record is only extended with brands it does not hold.
The duplicate guard reports pre-existing collisions and refuses only to create
new ones.

Usage:
  python3 tools/harvest_2026_10_12.py [--dry-run] [--no-changelog]
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TODAY = "2026-10-12"

SRC_SURFACE = ("https://www.indexbox.io/store/united-states-household-surface-cleaners-"
               "market-analysis-forecast-size-trends-and-insights/")
SRC_LAUNDRY = ("https://www.indexbox.io/store/united-states-laundry-home-products-"
               "market-analysis-forecast-size-trends-and-insights/")
SRC_FLOOR = ("https://www.indexbox.io/store/united-states-kw-floor-cleaning-solution-840-"
             "market-analysis-forecast-size-trends-and-insights/")
CD = "https://www.churchdwight.com/ingredient-disclosure/"
CD_BRANDS = "https://churchdwight.com/our-brands/consumer-brands/"

# --- owner record extension ------------------------------------------------
# Church & Dwight's consumer brand page names all of these brands in its own
# served text (read 2026-10-12). The record's existing src, /our-brands/, names
# only Arm & Hammer, which is the already-filed apply_owners src-precision
# defect; the upgrade to /our-brands/consumer-brands/ is a precision
# improvement for every Church & Dwight product in the corpus.
OWNER_NAME = "Church & Dwight"
OWNER_NEW_SRC = CD_BRANDS
OWNER_ADD_BRANDS = ["Kaboom", "Xtra", "Orange Glo"]

PRODUCTS = [
    dict(
        name="OxiClean Foam-Tastic Bathroom Cleaner, Fresh Scent",
        brand="OxiClean", cat="Bathroom",
        source_url=CD + "cleaning-products/42000010-OxiClean-foamtastic-fresh-scent.aspx",
        tier="mass", tier_src=CD_BRANDS,
        tier_note=("National brand sold through grocery, mass, club and dollar channels; the corpus files "
                   "Church & Dwight's national brands under the mass tier. The cited page evidences brand "
                   "ownership rather than the shelf, which is the known tier_src governance gap in this "
                   "repo; disclosed here rather than smoothed."),
        source=("Church & Dwight Product Ingredient Communication Form for 'OxiClean Foam-Tastic - Fresh "
                "Scent' (material 42000010, category cleaning products, date of disclosure 2024-03-07), read "
                "2026-10-12 from the served page, HTTP 200. Intentionally added ingredients with CAS and "
                "function: Water 7732-18-5 (Solvent); Isobutane 75-28-5 (Propellant, EU CMRs); Dipropylene "
                "glycol propyl ether 29911-27-1 (Solvent); Tripropylene glycol methyl ether 25498-49-1 "
                "(Solvent, CA TACs); Tetrasodium EDTA 64-02-8 (Chelating agent); Lauramine oxide 1643-20-5 "
                "(Surfactant); Sodium lauroyl sarcosinate 137-16-6 (Surfactant); Sodium hydroxide 1310-73-2 "
                "(pH adjuster, CA Non-Cancer Hazards); Triethanolamine 102-71-6 (pH adjuster); Fragrances "
                "(see below); Thymolphthalein 125-20-2 (Colorant); Sodium benzoate 532-32-1 (Corrosion "
                "inhibitor); Dimethylamino methylpropanol 7005-47-2 (Corrosion inhibitor); Butane 106-97-8 "
                "(Propellant, EU CMRs). Fragrance components the filing discloses at or above 100 ppm or on "
                "a designated list, recorded here rather than minted as keys because the "
                "fragrance-components question is an open ruling in this repo: 2-t-Butylcyclohexyl acetate "
                "(20298-69-5, 88-41-5); 2,6-Dimethyl-7-octen-2-ol (18479-58-8); Dipropylene glycol "
                "(25265-71-8); Hexamethylindanopyran (1222-05-5, EU Fragrance Allergens and US EPA PBTs); "
                "Tetramethyl acetyloctahydronaphthalenes (54464-57-2, EU Fragrance Allergens); Orange "
                "terpenes (68647-72-3, 8028-48-6, EU Fragrance Allergens); 4-tert-Butylcyclohexyl acetate "
                "(32210-23-4); Limonene (5989-27-5, EU Fragrance Allergens); Acetophenone (98-86-2, CA "
                "TACs)."),
        note=("The aerosol bathroom foam from the OxiClean line, and a straightforward example of why the "
              "maker's own designated-list column matters: the propellant pair (isobutane, butane) carries "
              "the EU CMR flag on the form itself. The cleaning system is a lauramine oxide and a sodium "
              "lauroyl sarcosinate on two glycol ether solvents, with tetrasodium EDTA as the chelator, "
              "thymolphthalein as the pH indicator that makes the foam change colour, and sodium benzoate "
              "with dimethylamino methylpropanol as corrosion inhibitors for the can. The line that drives "
              "the grade is sodium lauroyl sarcosinate, which this database grades on the severe end for "
              "skin and respiratory reasons. Recorded honestly: this is a full intentionally-added list "
              "with CAS numbers, and the fragrance is declared as a class plus a separate component table, "
              "so the record carries Fragrance as one key and the components live in the source text."),
        ings=["Water", "Isobutane", "Dipropylene Glycol Propyl Ether", "Tripropylene Glycol Methyl Ether",
              "Tetrasodium EDTA", "Lauramine Oxide", "Sodium Lauroyl Sarcosinate", "Sodium Hydroxide",
              "Triethanolamine", "Fragrance", "Thymolphthalein", "Sodium Benzoate",
              "Dimethylamino Methylpropanol", "Butane"],
        substitutes=[
            dict(name="Seventh Generation Tub & Tile Cleaner, Emerald Cypress & Fir", tier="mass",
                 note=("Same aisle and price band. A plant-based surfactant system with no sarcosinate and no "
                       "flammable propellant pair, so it avoids both the surface-active line and the EU CMR "
                       "propellants this aerosol carries.")),
            dict(name="ECOS Shower Kleener", tier="natural",
                 note=("Spray rather than aerosol, so no isobutane or butane; avoids the propellant pair and "
                       "the sodium lauroyl sarcosinate.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=2, exposure_src=SRC_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household "
                        "figure for the OxiClean Foam-Tastic bathroom line (the Church & Dwight brand site, "
                        "the disclosure form, and a general web search) and found none. IndexBox's US "
                        "Household Surface Cleaners page states approximately 95% of US households use at "
                        "least one surface cleaner per month, and that specialised cleaners (bathroom, "
                        "kitchen, glass, floor) are 30 to 35% of category value with bathroom cleaners the "
                        "largest sub-segment. The estimate is category penetration times the specialised "
                        "share times the bathroom share of that, times one SKU's share inside a national "
                        "brand, rounded to one significant figure."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="OxiClean Bathroom Cleaner, Fresh Scent",
        brand="OxiClean", cat="Bathroom",
        source_url=CD + "cleaning-products/42011957-OxiClean-bathroom-cleaner-fresh-scent.aspx",
        tier="mass", tier_src=CD_BRANDS,
        tier_note=("National brand sold through grocery, mass, club and dollar channels; the corpus files "
                   "Church & Dwight's national brands under the mass tier. The cited page evidences brand "
                   "ownership rather than the shelf; disclosed, not smoothed."),
        source=("Church & Dwight Product Ingredient Communication Form for 'OxiClean Bathroom Cleaner "
                "Fresh Scent' (material 42011957, category cleaning products, date of disclosure "
                "2026-05-11), read 2026-10-12 from the served page, HTTP 200. Intentionally added "
                "ingredients with CAS and function: Water 7732-18-5 (Solvent); Hydrogen peroxide 7722-84-1 "
                "(Cleaning agent); C10-12 Alcohol ethoxylates 66455-15-0 (Surfactant); Alkylbenzene sulfonic "
                "acid 68584-22-5 (Surfactant); Trisodium dicarboxymethyl alaninate 164462-16-2 (Chelating "
                "agent); Citric acid 77-92-9 (pH balance); Dipropylene glycol butyl ether 29911-28-2 "
                "(Solvent); Fragrances (see below). Fragrance components disclosed at or above 100 ppm: "
                "2,6-Dimethyl-7-octen-2-ol (18479-58-8); Dipropylene Glycol (25265-71-8). This is the most "
                "recently disclosed filing of the eight (2026-05-11) and the shortest ingredient list."),
        note=("The peroxide bathroom spray from OxiClean, and the shortest ingredient list in this fire: "
              "seven intentionally added ingredients plus a fragrance, with hydrogen peroxide doing the "
              "cleaning work rather than a quaternary ammonium biocide or hypochlorite. The two surfactants "
              "are a C10-12 alcohol ethoxylate and an alkylbenzene sulfonic acid, chelation is a trisodium "
              "dicarboxymethyl alaninate (the same MGDA chemistry this database already carries), and the "
              "solvent is a dipropylene glycol butyl ether. The fragrance is declared as a class plus two "
              "named components, so this record carries Fragrance as one key. Recorded honestly, and this "
              "is the part that matters: the short list is not a mild list. Hydrogen peroxide is graded "
              "severe on skin and eyes in this database because it is corrosive in concentrate and the "
              "label's irritant language understates it, so this product's own active is what drives its "
              "grade. What it avoids is the other routes, no quaternary ammonium biocide, no hypochlorite, "
              "no added fragrance beyond the class, and no aerosol propellant. Worth comparing against the "
              "other OxiClean bathroom record in this same fire: the two share a brand and a room and "
              "share almost no chemistry."),
        ings=["Water", "Hydrogen Peroxide", "C10-12 Alcohol Ethoxylates", "Alkylbenzene Sulfonic Acid",
              "Trisodium Dicarboxymethyl Alaninate", "Citric Acid", "Dipropylene Glycol Butyl Ether",
              "Fragrance"],
        substitutes=[
            dict(name="Seventh Generation Tub & Tile Cleaner, Emerald Cypress & Fir", tier="mass",
                 note=("Fragrance-free plant-based bathroom cleaner at a comparable price; the substitute is "
                       "for the fragrance class this record declares.")),
            dict(name="ATTITUDE Bathroom Cleaner Spray, Unscented", tier="natural",
                 note=("Unscented bathroom spray at a natural-segment price for a household avoiding the "
                       "fragrance class.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=2, exposure_src=SRC_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household "
                        "figure for the OxiClean bathroom spray (the brand site, the disclosure form, and a "
                        "general web search) and found none. IndexBox's US Household Surface Cleaners page "
                        "states approximately 95% of US households use at least one surface cleaner per "
                        "month and puts specialised cleaners at 30 to 35% of category value with bathroom "
                        "the largest sub-segment. The estimate is that penetration times the specialised "
                        "share times the bathroom share times one SKU's share inside the brand, rounded to "
                        "one significant figure."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="OxiClean Mold & Mildew Stain Remover with Bleach",
        brand="OxiClean", cat="Disinfectant",
        source_url=CD + "cleaning-products/40500092-OxiClean-mold-and-mildew-stain-remover-with-bleach.aspx",
        tier="mass", tier_src=CD_BRANDS,
        tier_note=("National brand sold through grocery, mass, club and dollar channels; filed under the "
                   "mass tier with the rest of Church & Dwight's national brands. The cited page evidences "
                   "brand ownership rather than the shelf; disclosed."),
        source=("Church & Dwight Product Ingredient Communication Form for 'OxiClean Mold & Mildew Stain "
                "Remover with Bleach' (material 40500092, category cleaning products, date of disclosure "
                "2024-03-26), read 2026-10-12 from the served page, HTTP 200. Intentionally added "
                "ingredients with CAS and function: Water 7732-18-5 (Solvent); Sodium hypochlorite 7681-52-9 "
                "(Bleach); Lauramine oxide 1643-20-5 (Surfactant); Sodium hydroxide 1310-73-2 (pH adjuster, "
                "CA Non-Cancer Hazards); Sodium lauryl sulfate 68585-47-7 (Surfactant); Sodium xylene "
                "sulfonate 1300-72-7 (Surfactant); Octyl dimethyl amine oxide 2605-78-9 (Surfactant); "
                "Fragrance (see below). Two mapping notes, both deliberate: the filing prints the name "
                "'Sodium lauryl sulfate' against CAS 68585-47-7, which is the C10-16 alkyl sulfate rather "
                "than the CAS 151-21-3 substance of that name, so the record carries Sodium C10-16 Alkyl "
                "Sulfate, the CAS match rather than the wording. And 'Sodium xylene sulfonate' maps to the "
                "existing merged key Sodium Xylenesulfonate. Fragrance components disclosed at or above 100 "
                "ppm: 2-t-Butylcyclohexyl acetate (88-41-5); Dipropylene glycol (25265-71-8); "
                "Hexamethylindanopyran (1222-05-5, US EPA PBTs)."),
        note=("The chlorinated mould and mildew spray from OxiClean. The working chemistry is a hypochlorite "
              "bleach at alkaline pH, held by sodium hydroxide, with three surfactants (lauramine oxide, a "
              "linear alkylbenzene sulfonate, and an octyl dimethyl amine oxide) and a hydrotrope to keep "
              "them in solution. The filing flags sodium hydroxide against California's non-cancer hazard "
              "list on its own form. Recorded honestly: a hypochlorite product carries the dermal and "
              "respiratory profile of bleach itself, and no surfactant choice removes that, so the "
              "substitute named here changes the active rather than the additives."),
        ings=["Water", "Sodium Hypochlorite", "Lauramine Oxide", "Sodium Hydroxide", "Sodium C10-16 Alkyl Sulfate",
              "Sodium Xylenesulfonate", "Octyl Dimethyl Amine Oxide", "Fragrance"],
        substitutes=[
            dict(name="Seventh Generation Disinfecting Multi-Surface Cleaner, Lemongrass Citrus", tier="mass",
                 note=("Thymol-based rather than hypochlorite-based, at a comparable price in the same "
                       "aisle. Avoids the bleach this record's active is, and avoids the sodium hydroxide "
                       "load that carries the CA non-cancer flag.")),
            dict(name="ECOS Shower Kleener", tier="natural",
                 note=("For the shower and tile job specifically, a non-chlorinated spray for a household "
                       "that wants the mildew handled without hypochlorite.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=1, exposure_src=SRC_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household "
                        "figure for the OxiClean mould and mildew line (the brand site, the disclosure form, "
                        "and a general web search) and found none. Mildew-specific stain removers are a "
                        "narrow slice of the specialised surface-cleaner segment that IndexBox measures at "
                        "30 to 35% of category value, and this is one SKU inside a national brand, so the "
                        "estimate is category penetration times that narrow share, rounded down to one "
                        "significant figure."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Kaboom Plus Disinfex 3-in-1 Bathroom Spray",
        brand="Kaboom", cat="Disinfectant",
        source_url=CD + "cleaning-products/40501022-kaboom-Plus-Disinfex-3-in1-Bathroom-Spray.aspx",
        tier="mass", tier_src=CD_BRANDS,
        tier_note=("Kaboom is a national Church & Dwight brand sold through grocery, mass, club and dollar "
                   "channels; filed under the mass tier with the rest of the company's national brands. The "
                   "cited page evidences brand ownership rather than the shelf; disclosed."),
        source=("Church & Dwight Product Ingredient Communication Form for 'Kaboom Plus Disinfex 3-in1 "
                "Bathroom Spray' (material 40501022, category cleaning products, date of disclosure "
                "2024-03-01), read 2026-10-12 from the served page, HTTP 200. Intentionally added "
                "ingredients with CAS and function: Water 7732-18-5 (Solvent); Butoxydiglycol 112-34-5 "
                "(Solvent, CA TACs and IARC Carcinogens); Tetrasodium EDTA 64-02-8 (Chelating agent); "
                "Undeceth-7 34398-01-1 (Surfactant); Alkyl C12-18 dimethylbenzyl ammonium chloride 68391-01-5 "
                "(Biocide, CA Priority Chemicals); Alkyl C12-18 dimethyl ethylbenzyl ammonium chloride "
                "68956-79-6 (Biocide); Sodium metasilicate 6834-92-0 (Cleaning agent); Fragrances (see "
                "below). Mapping note: the filing's 'Butoxydiglycol' is CAS 112-34-5, the same substance the "
                "registry already carries as Diethylene Glycol Monobutyl Ether, so the record uses that key "
                "rather than minting a twin. Fragrance components disclosed at or above 100 ppm: d-Limonene "
                "(5989-27-5, EU Fragrance Allergens); Terpinolene (586-62-9, EU Fragrance Allergens); "
                "Hexamethylindanopyran (1222-05-5, US EPA PBTs); Myrcene (123-35-3, IARC Carcinogens)."),
        note=("The disinfecting bathroom spray from Kaboom, and the second chlorinated-free biocide record "
              "in this fire, so the reader can compare a quaternary ammonium system against the hypochlorite "
              "one directly. The disinfecting pair is an alkyl dimethylbenzyl ammonium chloride and an alkyl "
              "dimethyl ethylbenzyl ammonium chloride, the standard dual-quat blend; the rest is cleaning "
              "power, a sodium metasilicate builder, an undeceth-7 surfactant and tetrasodium EDTA. "
              "Recorded honestly: the form flags four of its own fragrance components against designated "
              "lists, including one IARC carcinogen and one US EPA PBT, and flags the solvent against both "
              "California toxic air contaminants and the IARC list. That is the manufacturer's own "
              "designation, not ours."),
        ings=["Water", "Diethylene Glycol Monobutyl Ether", "Tetrasodium EDTA", "Undeceth-7",
              "Alkyl C12-18 Dimethylbenzyl Ammonium Chloride",
              "Alkyl C12-18 Dimethyl Ethylbenzyl Ammonium Chloride", "Sodium Metasilicate", "Fragrance"],
        substitutes=[
            dict(name="up&up Bathroom Disinfecting Cleaner, Unscented", tier="grocery",
                 note=("Unscented bathroom disinfectant at a lower price in the same aisle. Avoids the "
                       "fragrance class and its flagged components, which is the substitute for a household "
                       "that wants the disinfecting job done without the scent load.")),
            dict(name="Method All-Purpose Surface Cleaner, Ginger Yuzu", tier="mass",
                 note=("Same price band, and the substitute is specifically for the fragrance components the "
                       "Kaboom form flags against designated lists; the Method formula names its fragrance "
                       "components too, so the comparison is like for like.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=1, exposure_src=SRC_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household "
                        "figure for the Kaboom bathroom line (the brand site, the disclosure form, and a "
                        "general web search) and found none. IndexBox's US Household Surface Cleaners page "
                        "puts disinfectants and sanitizers at 25 to 30% of category value and specialised "
                        "cleaners at 30 to 35% with bathroom the largest sub-segment; Kaboom is a smaller "
                        "brand than the category leaders, so the estimate is category penetration times "
                        "those shares times a small brand share, rounded to one significant figure."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Orange Glo Multi-Surface Cleaner",
        brand="Orange Glo", cat="Floor & Carpet",
        source_url=CD + "cleaning-products/42000164-orange-glo-everyday-hardwood-floor-cleaner.aspx",
        tier="mass", tier_src=CD_BRANDS,
        tier_note=("National Church & Dwight brand sold through grocery, mass and dollar channels; filed "
                   "under the mass tier with the company's other national brands. The cited page evidences "
                   "brand ownership rather than the shelf; disclosed."),
        source=("Church & Dwight Product Ingredient Communication Form for the product whose index link "
                "text reads 'Orange Glo Multi-Surface Cleaner' and whose filing URL slug reads "
                "'orange-glo-everyday-hardwood-floor-cleaner' (material 42000164, category cleaning "
                "products, date of disclosure 2024-04-26), read 2026-10-12 from the served page, HTTP 200. "
                "The served anchor text and the served URL slug disagree about what this SKU is called; "
                "both are recorded here rather than one being chosen silently. Intentionally added "
                "ingredients with CAS and function: Water 7732-18-5 (Solvent); Lauryl glucoside 110615-47-9 "
                "(Surfactant); Caprylyl/capryl glucoside 68515-73-1 (Surfactant); Cocamidopropylamine oxide "
                "68155-09-9 (Surfactant); Cocamidopropyl dimethylamine 68140-01-2 (Surfactant); "
                "Benzisothiazolinone 2634-33-5 (Preservative); Methylisothiazolinone 2682-20-4 "
                "(Preservative); Triethanolamine 102-71-6 (pH adjuster); Fragrances (see below). Fragrance "
                "components disclosed at or above 100 ppm: Butylphenyl methylpropional (80-54-6, EU CMRs); "
                "Dipropylene glycol (25265-71-8); Ethoxydiglycol (111-90-0, CA TACs); Limonene (5989-27-5, "
                "EU Fragrance Allergens)."),
        note=("The Orange Glo surface and floor cleaner, and a useful contrast with the other Orange Glo "
              "record in this same fire, which is a solvent polish: this one is water-based and built "
              "entirely on sugar surfactants, a lauryl glucoside with a caprylyl/capryl glucoside, plus a "
              "cocamidopropylamine oxide and a cocamidopropyl dimethylamine. There is no chelator and no "
              "solvent. The line to read is the preservative pair, benzisothiazolinone and "
              "methylisothiazolinone, which is the contact-allergen pair this database grades on the severe "
              "end for skin, and it is declared here rather than hidden behind the word preservative."),
        ings=["Water", "Lauryl Glucoside", "Caprylyl/Capryl Glucoside", "Cocamidopropylamine Oxide",
              "Cocamidopropyl Dimethylamine", "Benzisothiazolinone", "Methylisothiazolinone",
              "Triethanolamine", "Fragrance"],
        substitutes=[
            dict(name="ATTITUDE Floor Surface Cleaner, Citrus Zest", tier="natural",
                 note=("Same job and a comparable price. Carries no isothiazolinone preservative pair, which "
                       "is the substitute for the benzisothiazolinone and methylisothiazolinone this record "
                       "declares.")),
            dict(name="Method All-Purpose Surface Cleaner, Ginger Yuzu", tier="mass",
                 note=("Mass-price multi-surface cleaner that discloses its own fragrance components and "
                       "avoids the isothiazolinone pair.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=2, exposure_src=SRC_FLOOR,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household "
                        "figure for the Orange Glo floor and surface line (the brand site, the disclosure "
                        "form, and a general web search) and found none. IndexBox's US Floor Cleaning "
                        "Solution page states that residential households consume roughly 70 to 75% of "
                        "category volume, and that consumers buy the category every 4 to 8 weeks. Orange Glo "
                        "is a small brand inside that category, so the estimate is household penetration of "
                        "the category times the brand's small share, rounded to one significant figure."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Orange Glo Wood Furniture 2-in-1 Clean & Polish",
        brand="Orange Glo", cat="Wood & Stone Care",
        source_url=CD + "cleaning-products/42000283-orange-glo-wood-furniture-2-in-1-clean-and-polish.aspx",
        tier="mass", tier_src=CD_BRANDS,
        tier_note=("National Church & Dwight brand sold through grocery, mass and dollar channels; filed "
                   "under the mass tier with the company's other national brands. The cited page evidences "
                   "brand ownership rather than the shelf; disclosed."),
        source=("Church & Dwight Product Ingredient Communication Form for 'Orange Glo Wood Furniture 2-in-1 "
                "Clean & Polish' (material 42000283, category cleaning products, date of disclosure "
                "2024-11-07), read 2026-10-12 from the served page, HTTP 200. Intentionally added "
                "ingredients with CAS and function: Dearomatized alkanes 64742-47-8 (Cleaning agent); Mineral "
                "oil 8042-47-5 (Cleaning agent); Orange oil 8008-57-9 (Cleaning agent); Dimethicone "
                "63148-62-9 (Polish); Fragrances (see below); Sorbitan oleate 1338-43-8 (Surfactant); "
                "Denatonium benzoate 3734-33-6 (Bitterant); BHT 128-37-0 (Anti-oxidant); Solvent Yellow 72 "
                "4645-07-2 (Colorant); Solvent Red 164 92257-31-3 (Colorant). Mapping notes: the filing's "
                "'Dearomatized alkanes' is CAS 64742-47-8, which this registry already carries as "
                "Hydrotreated light alkanes, so the record uses that key rather than minting a fourth name "
                "for the same CAS. Two things about that are disclosed rather than smoothed: this registry "
                "holds CAS 64742-47-8 on three keys with divergent evidence (C11-15 Alkane/Cycloalkane "
                "records H304, the other two record Not Classified), which is the duplicate-substance class "
                "already filed to Trellis, and the mapping made here is by served name, not by grade. "
                "'Orange oil' maps to the existing graded Orange Oil key. Fragrance components disclosed at "
                "or above 100 ppm: Decanal (112-31-2); Octanal (124-13-0); Limonene (5989-27-5, EU Fragrance "
                "Allergens); Orange oil (8008-57-9, EU Fragrance Allergens)."),
        note=("The solvent furniture polish from the Orange Glo line, and a different animal from the "
              "water-based Orange Glo record beside it: this one is a mineral-oil and dearomatized-alkane "
              "solvent system with orange oil, dimethicone as the polish film, sorbitan oleate as the "
              "emulsifier, BHT as the anti-oxidant and two solvent dyes. Denatonium benzoate is in it as a "
              "bittering agent, the same safety chemistry that keeps children from drinking laundry pods. "
              "Recorded honestly: an oil-based polish leaves a film by design, so the exposure is dermal and "
              "by inhalation of a mist near the face, and the label does not claim otherwise. This is also "
              "the record where the registry's duplicate-substance problem is most visible, because its "
              "first ingredient carries a CAS that three different keys in this database claim."),
        ings=["Hydrotreated light alkanes", "Mineral Oil", "Orange Oil", "Dimethicone", "Fragrance",
              "Sorbitan Monooleate", "Denatonium Benzoate", "BHT", "Solvent Yellow 72", "Solvent Red 164"],
        substitutes=[
            dict(name="Howard Butcher Block Conditioner", tier="mass",
                 note=("Food-safe oil and wax finish for wood at a comparable price; avoids the petroleum "
                       "distillate solvent and the two solvent dyes, which is the substitution for a "
                       "household that wants the wood fed without a mineral-spirit carrier.")),
            dict(name="Old English Lemon Oil Furniture Polish", tier="mass",
                 note=("The other mainstream lemon-oil furniture treatment already in this corpus, and the "
                       "better-graded one; named as the same-aisle alternative for the solvent load rather "
                       "than for the brand.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=2, exposure_src=SRC_FLOOR,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household "
                        "figure for the Orange Glo furniture polish (the brand site, the disclosure form, "
                        "and a general web search) and found none. Furniture polish is a specialty niche "
                        "that IndexBox's US Household Surface Cleaners page lists alongside stone, stainless "
                        "steel and grout as the small remainder of the category after all-purpose, "
                        "disinfectant and specialised cleaners are counted. The estimate is that small "
                        "remainder times the brand's share, rounded to one significant figure."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Arm & Hammer Clean Scentsations Scent Booster, Fresh Burst",
        brand="Arm & Hammer", cat="Laundry",
        source_url=CD + "laundry-fabric-care/42010990-arm-hammer-scent-booster-fresh-burst.aspx",
        tier="mass", tier_src=CD_BRANDS,
        tier_note=("National Church & Dwight brand sold through grocery, mass, club and dollar channels; "
                   "the corpus files both Arm & Hammer and OxiClean under the mass tier. The cited page "
                   "evidences brand ownership rather than the shelf; disclosed."),
        source=("Church & Dwight Product Ingredient Disclosure Form for 'Arm & Hammer Clean Scentsations "
                "with Odor Blasters Scent Booster - Fresh Burst' (material 42010990, category laundry and "
                "fabric care, date of disclosure 2024-03-26), read 2026-10-12 from the served page, HTTP "
                "200. Intentionally added ingredients with CAS and function: Sodium chloride 7647-14-5 "
                "(Builder); Fragrances (see below); Sodium bicarbonate 144-55-8 (Builder); Hydrated silica "
                "112926-00-8 (Process aid); Dipropylene glycol 25265-71-8 (Process aid, CA Non-Cancer "
                "Hazards); Sorbitan oleate 1338-43-8 (Surfactant); Polyoxyalkylene substituted chromophore "
                "(red) (Colorant); and a colorant the form words as a blend of Benzenesulfonic acid, "
                "3-[[4-amino-9,10-dihydro-9,10-dioxo-3-[sulfo-4-(1,1,3,3-tetramethylbutyl)phenoxy]-1-"
                "anthracenyl]amino]-2,4,6-trimethyl-, sodium salt (1:2) and a naphthalenedisulfonic acid "
                "derivative. Mapping notes: 'Hydrated silica' maps to the existing Silica key, 'Sorbitan "
                "oleate' maps to the existing Sorbitan Monooleate key, and the long dye-blend string maps to "
                "the existing Colorant key with the served wording quoted here rather than minted as a new "
                "key. Fragrance components disclosed at or above 100 ppm, 23 of them, recorded here rather "
                "than minted as keys because the fragrance-components question is an open ruling: "
                "(2,2,2-Trichloro-1-phenylethyl) acetate (90-17-5); 2,4-Dimethyl-3-cyclohexene "
                "carboxaldehyde (68039-49-6); 2,6-Dimethyl-7-octen-2-ol (18479-58-8); "
                "2-Cyclohexylidene-2-phenylacetonitrile (10461-98-0); 2-Ethoxynaphthalene (93-18-5); "
                "2-Methoxynaphthalene (93-04-9); 2-t-Butylcyclohexyl acetate (88-41-5); Verdyl Acetate "
                "(5413-60-5); Benzyl acetate (140-11-4); Butylphenyl methylpropional (80-54-6, EU Fragrance "
                "Allergens and EU CMRs); Citrus aurantium dulcis (Orange) peel oil (8008-57-9); Cyclamen "
                "aldehyde (103-95-7); Dipropylene glycol (25265-71-8); Ethyl 2-methylbutanoate (7452-79-1); "
                "Ethyl 2-methylpentanoate (39255-32-8); Gamma-undecalactone (104-67-6); "
                "Hexamethylindanopyran (1222-05-5, EU Fragrance Allergens and US EPA PBTs); Hexyl cinnamal "
                "(101-86-0, EU Fragrance Allergens); Hexyl salicylate (6259-76-3); Isobornyl acetate "
                "(125-12-2); Lauraldehyde (112-54-9); d-Limonene (5989-27-5, EU Fragrance Allergens); Methyl "
                "decenol (81782-77-6); Methylbenzyl acetate (93-92-5); Methyldihydrojasmonate (24851-98-7); "
                "Pogostemon cablin leaf oil (8014-09-3, EU Fragrance Allergens); Polysorbate 80 (9005-65-6); "
                "Allyl cyclohexanepropionate (2705-87-5); Tetramethyl acetyloctahydronaphthalenes "
                "(54464-57-2, EU Fragrance Allergens)."),
        note=("The in-wash scent booster from Arm & Hammer, and the sharpest example in this fire of what a "
              "scent booster actually is: the functional ingredients are two builders and a process aid, "
              "and everything else is fragrance and dye. There is no cleaning chemistry in the product at "
              "all, which is worth stating plainly rather than implying otherwise. The form discloses 23 "
              "fragrance components at or above 100 ppm against designated lists, which is more than any "
              "other record added tonight. Recorded honestly: this record carries Fragrance as one key and "
              "the 23 components live in the source text, because minting them would deepen an unruled "
              "decision. A reader who wants the scent load should be able to see it, and that is what the "
              "component list in the source field is for."),
        ings=["Sodium Chloride", "Fragrance", "Sodium Bicarbonate", "Silica", "Dipropylene Glycol",
              "Sorbitan Monooleate", "Polyoxyalkylene Substituted Chromophore", "Colorant"],
        substitutes=[
            dict(name="Seventh Generation Liquid Laundry Detergent, Free & Clear", tier="mass",
                 note=("The honest substitute for a scent booster is not another scent booster, because the "
                       "product is fragrance by design. This is a fragrance-free liquid at a comparable "
                       "price for a household that wants the laundry to smell of nothing; it avoids the "
                       "fragrance class this record declares.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=2, exposure_src=SRC_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household "
                        "figure for the Arm & Hammer scent booster line (the brand site, the disclosure "
                        "form, and a general web search) and found none. IndexBox's US Laundry & Home "
                        "Products page states category household penetration above 98%. In-wash boosters are "
                        "an additive used by a minority of households on top of detergent, and this is one "
                        "SKU inside one brand inside that minority, so the estimate is category penetration "
                        "times a small booster-use share times the brand's share, rounded to one significant "
                        "figure."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Xtra Plus OxiClean Powder Laundry Detergent, Summer Breeze",
        brand="Xtra", cat="Laundry",
        source_url=CD + "laundry-fabric-care/42010948-xtra-plus-oxiclean-powder-laundry-detergent-summer-breeze.aspx",
        tier="mass", tier_src=CD_BRANDS,
        tier_note=("Xtra is Church & Dwight's value laundry brand, sold through grocery, mass, club and "
                   "dollar channels; filed under the mass tier with the company's other national brands. "
                   "The cited page evidences brand ownership rather than the shelf; disclosed. The value "
                   "position inside the mass channel is recorded here rather than given its own tier, "
                   "because tier naming follows the breakpoints that appear in the data."),
        source=("Church & Dwight Product Ingredient Disclosure Form for 'Xtra Plus OxiClean Powder Laundry "
                "Detergent - Summer Breeze' (material 42010948, category laundry and fabric care, date of "
                "disclosure 2026-03-24), read 2026-10-12 from the served page, HTTP 200. Intentionally added "
                "ingredients with CAS and function: Sodium carbonate 497-19-8 (Builder); Water 7732-18-5 "
                "(Solvent); Sodium laureth sulfate 68585-34-2 (Surfactant); Potassium chloride 7447-40-7 "
                "(Bulking agent); C10-16 alketh, which the filing words as possibly C12-15 alcohols "
                "ethoxylated 68131-39-5 or C10-16 alcohol ethoxylate 68002-97-1 (Surfactant); Sodium sulfate "
                "7757-82-6 (Processing aid, CA Non-Cancer Hazards); Modified acrylic copolymer 52255-49-9 "
                "(Dispersing agent); Disodium distyrylbiphenyl disulfonate 27344-41-8 (Optical brightener); "
                "Sodium carbonate peroxide 15630-89-4 (Oxygen bleach); Fragrances (see below). Mapping "
                "notes: the filing prints 'Sodium laureth sulfate' against CAS 68585-34-2, the C10-16 "
                "alketh-2 sulfate rather than the CAS 9004-82-4 substance of that name, so the record "
                "carries SODIUM C10-16 ALKETH-2 SULFATE, the CAS match. The filing's own hedged C10-16 "
                "alketh line maps to the existing C12-15 Alcohols Ethoxylated key, which is the first "
                "alternative the form itself names. Fragrance components disclosed at or above 100 ppm: "
                "Benzyl benzoate (120-51-4, EU Fragrance Allergens); Butylphenyl methylpropional (80-54-6, "
                "EU Fragrance Allergens and EU CMRs); Dipropylene glycol (25265-71-8); Hexamethylindanopyran "
                "(1222-05-5, EU Fragrance Allergens and US EPA PBTs); Limonene (5989-27-5, EU Fragrance "
                "Allergens); Linalool (78-70-6, EU Fragrance Allergens); Orange terpenes (68647-72-3); "
                "p-Cresol (106-44-5, CA Non-Cancer Hazards and CA TACs); Phenoxyethyl isobutyrate (103-60-6, "
                "CA TACs); Tetramethyl acetyloctahydronaphthalenes (54464-57-2, EU Fragrance Allergens); "
                "Verdyl acetate (5413-60-5)."),
        note=("The value powder detergent from Xtra with OxiClean added, and the record that covers a "
              "format the corpus was thin on: laundry powder at a value price. The wash system is a "
              "carbonate builder with sodium carbonate peroxide as the oxygen bleach, a sodium laureth "
              "sulfate and an alcohol ethoxylate as the surfactants, potassium chloride as the bulking "
              "agent, a modified acrylic copolymer as the anti-redeposition dispersant, and an optical "
              "brightener. The filing flags its own sodium sulfate and its own p-cresol fragrance component "
              "against California lists. Recorded honestly: this is the value shelf, where the products are "
              "not worse by design but are simpler, and the difference the reader is paying for is mostly "
              "in the fragrance and the builder set rather than in the cleaning chemistry."),
        ings=["Sodium Carbonate", "Water", "SODIUM C10-16 ALKETH-2 SULFATE", "Potassium Chloride",
              "C12-15 Alcohols Ethoxylated", "Sodium Sulfate", "Modified Acrylic Copolymer",
              "Disodium Distyrylbiphenyl Disulfonate", "Sodium Carbonate Peroxide", "Fragrance"],
        substitutes=[
            dict(name="all free clear Original Concentrated Liquid Laundry Detergent", tier="mass",
                 note=("Free-and-clear liquid at a mass price, formulated for sensitive skin and with no "
                       "fragrance or dye; avoids the fragrance class, the optical brightener and the p-cresol "
                       "component the form itself flags.")),
            dict(name="Great Value Ultimate Fresh Original Clean Laundry Detergent", tier="grocery",
                 note=("Store-brand liquid in the same value band for a household that wants the lower price "
                       "without the brightener and the flagged fragrance component.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=2, exposure_src=SRC_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household "
                        "figure for the Xtra Plus OxiClean powder (the brand site, the disclosure form, and a "
                        "general web search) and found none. IndexBox's US Laundry & Home Products page "
                        "states category household penetration above 98% and names the value and private "
                        "label segment as a large share of unit volume. Xtra is a leading value brand but "
                        "powder is now a minority format, so the estimate is category penetration times the "
                        "value-segment share times the brand's share times the powder-format share, rounded "
                        "to one significant figure."),
        strength_disclosure="full", disclosure_note=None,
    ),
]

ALIASES = {
    # label wording -> existing registry key, where the substance is the same
    "butoxydiglycol": "Diethylene Glycol Monobutyl Ether",
    "sodium xylene sulfonate": "Sodium Xylenesulfonate",
    "hydrated silica": "Silica",
    "sorbitan oleate": "Sorbitan Monooleate",
    "dearomatized alkanes": "Hydrotreated light alkanes",
}

MINT_NOTE = ("Minted {today} from a manufacturer's own California SB-258 disclosure form and recorded "
             "ungraded. No PubChem or ECHA grade has been resolved for this entry yet, so g is null rather "
             "than a guess.")


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
                aliased.append((term, key))
                resolved.append(key)
                continue
            if norm(term) in folded:
                key = folded[norm(term)]
                aliased.append((term, key))
                resolved.append(key)
                continue
            if term not in minted:
                minted.append(term)
            if not args.dry_run:
                ingredients[term] = {
                    "ev": "Low", "g": None, "gr": {}, "impacts": [],
                    "note": MINT_NOTE.format(today=TODAY),
                    "s": f"{term}. Named in a manufacturer California SB-258 disclosure; not yet graded.",
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

    # owner record: extend brands and upgrade the record-level src
    rec = owners["owners"].get(OWNER_NAME)
    if rec is None:
        raise SystemExit(f"owner record {OWNER_NAME!r} not found; refusing to guess")
    extended, src_changed = [], False
    for b in OWNER_ADD_BRANDS:
        if b not in rec.get("brands", []):
            extended.append(b)
            if not args.dry_run:
                rec.setdefault("brands", []).append(b)
    if rec.get("src") != OWNER_NEW_SRC:
        src_changed = True
        if not args.dry_run:
            rec["src"] = OWNER_NEW_SRC

    # duplicate-key guard: report pre-existing collisions, refuse only new ones
    groups = {}
    for k in ingredients:
        groups.setdefault(norm(k), []).append(k)
    preexisting = {n: ks for n, ks in groups.items() if len(ks) > 1}
    if preexisting:
        for n, ks in sorted(preexisting.items()):
            print(f"  pre-existing duplicate-key group (not caused by this fire): {ks}")
    created = [n for n in preexisting if any(k in minted for k in preexisting[n])]
    if created:
        print(f"REFUSING: this fire would create duplicate-key groups: {created}")
        return 1

    print(f"products added: {len(added_records)}  skipped(existing): {len(skipped)}")
    for r in added_records:
        print(f"   + {r['name']}  ({len(r['ings'])} ingredients)")
    print(f"ingredient keys minted: {len(minted)} -> {minted}")
    print(f"ingredient keys aliased: {len(aliased)}")
    for a, b in aliased:
        print(f"   {a!r} -> {b!r}")
    print(f"owner record {OWNER_NAME!r}: brands extended {extended}, src changed {src_changed}")

    if args.dry_run:
        print("dry run: no files written")
        return 0

    def dump(path, obj, indent, trailing_newline):
        text = json.dumps(obj, ensure_ascii=False, indent=indent)
        if trailing_newline:
            text += "\n"
        path.write_text(text, encoding="utf-8")

    # measured at upstream HEAD 8c3ee45, 2026-10-12: products.json,
    # ingredients.json, owners.json and changelog.json are all written with
    # indent 1 for the first three and 2 for the changelog, and NONE of the four
    # ends with a trailing newline. Check each file before writing rather than
    # assuming; the previous night's note about trailing newlines was wrong.
    dump(prods_path, products, 1, False)
    dump(ings_path, ingredients, 1, False)
    dump(owners_path, owners, 1, False)

    changed = bool(added_records or extended or src_changed)
    if not args.no_changelog and changed:
        cl = json.loads((REPO / "data/changelog.json").read_text(encoding="utf-8"))
        if not cl or cl[0].get("date") != TODAY:
            cl.insert(0, {
                "date": TODAY,
                "text": (f"Spectrum harvest station 2 (Dolman {TODAY}): {len(added_records)} high-exposure "
                         "household products added from Church & Dwight's own California SB-258 disclosure "
                         "index, covering the two thinnest categories in the corpus (floor and wood care) "
                         "plus bathroom, disinfectant and laundry. Every ingredient list read from the "
                         "manufacturer's own per-product filing, with CAS numbers. The 'Church & Dwight' "
                         "owner record gains Kaboom, Xtra and Orange Glo and its source is upgraded to the "
                         "company's consumer brand page, which names all of them. "
                         f"{len(minted)} new ingredient keys minted, all ungraded."),
            })
            dump(REPO / "data/changelog.json", cl, 2, False)

    return 0


if __name__ == "__main__":
    sys.exit(main())
