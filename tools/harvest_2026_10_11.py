#!/usr/bin/env python3
"""Spectrum harvest, night-shift station 2, 2026-10-11.

HARVEST -- six missing high-exposure products, each read from a primary
source (the manufacturer's own published declaration, an FDA/EPA label, or the
manufacturer's own product page).

Why these six. The spectrum data build is complete across all four channel
tiers; the KIK value-brand index is exhausted for household products; and the
largest remaining category gap (air care) is blocked on the open
fragrance-components ruling, not on a route. What is genuinely missing is a
handful of high-exposure NAME-BRAND staples. This fire takes the laundry aisle
(the highest-penetration category there is -- IndexBox's US Laundry & Home
Products page states household penetration above 98%) plus one EPA-registered
heavy-duty cleaner and one mass hand wash:

  1. Seventh Generation Liquid Laundry Detergent, Free & Clear  (manufacturer page)
  2. Method Laundry Detergent, Free + Clear                     (es.cvs.com SB-258)
  3. Arm & Hammer Plus OxiClean 4-in-1 Power Paks               (C&D disclosure form)
  4. Spray Nine Heavy-Duty Cleaner, Degreaser & Disinfectant    (EPA label + CA SB-258)
  5. ECOS Hypoallergenic Laundry Detergent, Free & Clear        (manufacturer page)
  6. Dove Foaming Hand Wash, Aloe & Eucalyptus                  (es.cvs.com SB-258)

Mapping discipline. A label term is mapped to the closest EXISTING key wherever
the substance is the same, so a graded key is never bypassed by an ungraded twin
(this is the recorded duplicate-substance defect class). The enzyme "blends" are
protease/amylase/mannanase and map onto the registry's graded enzyme keys. The
fragrance components of the Arm & Hammer filing are recorded in prose only,
because the fragrance-components-as-ingredient-keys question is an open ruling
and minting 18 further fragrance keys would deepen an unruled decision.

Idempotent: a product already present by name is skipped, an ingredient key that
already exists (case-insensitively, or through the alias map) is never re-minted,
and an owner record is only extended if the brand string is absent.

Usage:
  python3 tools/harvest_2026_10_11.py [--dry-run] [--no-changelog]
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TODAY = "2026-10-11"

SRC_LAUNDRY = ("https://www.indexbox.io/store/united-states-laundry-home-products-"
               "market-analysis-forecast-size-trends-and-insights/")
SRC_SURFACE = ("https://www.indexbox.io/store/united-states-household-surface-cleaners-"
               "market-analysis-forecast-size-trends-and-insights/")

CVS = "https://es.cvs.com/shop/ingredients/"

# --- new owner record ------------------------------------------------------
# Spray Nine's own site states the trademark ownership in its footer, read
# 2026-10-11: "Spray Nine is a TM of Illinois Tool Works Inc. Copyright (c) 2023.
# Permatex, a division of Illinois Tool Works Inc." A brand's own published page
# read directly -> `verified` per the ownership rule.
NEW_OWNER_NAME = "Illinois Tool Works Inc."
NEW_OWNER = {
    "type": "public company",
    "detail": "Illinois Tool Works Inc. (ITW), Glenview, IL. Spray Nine and Permatex are ITW "
              "brands; spraynine.com's own footer states the trademark ownership and names Permatex "
              "as a division of ITW. Permatex hosts the California SB-258 ingredient disclosure for "
              "the Spray Nine line at permatex.com/tech-documents/ca-right-to-know-act/.",
    "ev": "verified",
    "src": "https://www.spraynine.com/",
    "brands": ["Spray Nine"],
}

# --- brand-string extension on an EXISTING owner record --------------------
# Unilever owns Dove; dove.com's own site footer reads "Dove and other Unilever
# brands", read 2026-10-11. The Unilever record's record-level src does not name
# Dove, which is the already-filed apply_owners src-precision defect; recorded in
# the finding rather than papered over. The stamp inherits the record's own ev.
OWNER_BRAND_EXTENSIONS = {
    "Unilever": ["Dove"],
}

PRODUCTS = [
    dict(
        name="Seventh Generation Liquid Laundry Detergent, Free & Clear",
        brand="Seventh Generation", cat="Laundry",
        source_url="https://www.seventhgeneration.com/liquid-laundry-detergent-free-clear",
        tier="mass", tier_src="https://www.seventhgeneration.com/liquid-laundry-detergent-free-clear",
        tier_note=("National brand sold through grocery, mass and drugstore channels; the corpus already "
                   "files Seventh Generation under the mass tier, and this record follows that convention."),
        source=("Manufacturer's own product page for Seventh Generation Liquid Laundry Detergent, Free & "
                "Clear, which prints the full ingredient list under an 'Ingredients & Scents' heading, read "
                "2026-10-11 from the served page (HTTP 200): Water, laureth-6 (plant-derived cleaning agent), "
                "sodium citrate (plant-derived water softener), sodium lauryl sulfate (plant-derived cleaning "
                "agent), sodium chloride (mineral-based viscosity modifier), sodium oleate (plant-derived "
                "anti-foaming agent), sodium sulfate (mineral-based processing aid), citric acid (plant-derived "
                "pH adjuster), protease enzyme blend (plant-based cleaning agent), amylase enzyme blend "
                "(plant-based cleaning agent), mannanase enzyme blend (plant-based cleaning agent), "
                "benzisothiazolinone (synthetic preservative), methylisothiazolinone (synthetic preservative). "
                "The page also links English, Spanish and French safety data sheets. Every line the maker "
                "prints is recorded; nothing is added from elsewhere."),
        note=("The Free & Clear liquid from the leading plant-based laundry brand, and it is a completely "
              "different formula from the brand's dish liquid already in the corpus. The cleaning system is "
              "enzymes rather than bleach: a protease, an amylase and a mannanase blend, on laureth-6 and "
              "sodium lauryl sulfate, with sodium citrate as the water softener and sodium oleate as the "
              "anti-foam. The two lines to read are the preservative pair, benzisothiazolinone and "
              "methylisothiazolinone. That pair is why this record carries a substitute: methylisothiazolinone "
              "is graded F on dermal and environmental grounds in this database and is the contact allergen "
              "people react to in water-based cleaners, and it is declared here rather than hidden behind "
              "'preservative'. The label names no fragrance and no dye, so a reader avoiding fragrance gets a "
              "clean answer. Recorded honestly: a laundry detergent is diluted in a wash cycle and rinsed, so "
              "the exposure route is dermal contact with the concentrate and the residue on fabric, not "
              "inhalation of a spray."),
        ings=["Water", "Laureth-6", "Sodium Citrate", "Sodium Lauryl Sulfate", "Sodium Chloride",
              "Sodium Oleate", "Sodium Sulfate", "Citric Acid", "Protease Enzyme Blend", "Amylase Enzyme Blend",
              "Mannanase Enzyme Blend", "Benzisothiazolinone", "Methylisothiazolinone"],
        substitutes=[
            dict(name="Earth Breeze Laundry Detergent Sheets, Fragrance Free", tier="mass",
                 note=("Sheet-format detergent at a comparable per-load price that carries no isothiazolinone "
                       "preservative pair; the substitute is for the benzisothiazolinone and "
                       "methylisothiazolinone this record declares.")),
            dict(name="Total Home Free & Clear Liquid Laundry Detergent, Unscented, 100 fl oz", tier="drugstore",
                 note=("Store-brand free-and-clear liquid at a lower price; a free-and-clear answer for a "
                       "household avoiding the isothiazolinone pair and fragrance.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=3, exposure_src=SRC_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household "
                        "figure for Seventh Generation laundry detergent (the brand site, the CVS and Target "
                        "listings, and a general web search) and found none. IndexBox's US Laundry & Home "
                        "Products page states household penetration above 98% for the category across an "
                        "estimated 130-135 million households. Seventh Generation is the leading plant-based "
                        "laundry brand but plant-based/eco-labelled premium is roughly 25% of category value, "
                        "and this is one SKU inside the brand, so the estimate is category penetration times "
                        "the natural-segment share times the brand's share of that segment. Rounded to one "
                        "significant figure because nothing more specific is published."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Method Laundry Detergent, Free + Clear",
        brand="Method", cat="Laundry",
        source_url=CVS + "method-free-clear-liquid-laundry-detergent-unscented-53-5-fl-oz-prodid-164021",
        tier="mass", tier_src=CVS + "method-free-clear-liquid-laundry-detergent-unscented-53-5-fl-oz-prodid-164021",
        tier_note=("National brand sold through grocery, mass and drugstore channels; the corpus files Method "
                   "under the mass tier, and this record follows that convention. The tile records where the "
                   "declaration was read, not a single-shelf claim."),
        source=("Manufacturer ingredient declaration for Method Laundry Detergent, Free + Clear (53.5 fl oz), "
                "read 2026-10-11 from the served page on the CVS Spanish-locale host es.cvs.com in the "
                "`vendorIngredientsParagraph` field: Water (Aqua), Laureth-7, Sodium Lauryl Sulfate, Glycerin, "
                "Alcohol Denat., Protease Enzyme Blend, Trisodium Salt of Methylglycinediacetic Acid, Sodium "
                "Cocoate, Amylase Enzyme Blend, Calcium Chloride, Sodium Carboxymethyl Inulin, Citric Acid, "
                "Denatonium Benzoate, Mannanase Enzyme Blend, Pectinase Enzyme Blend, Nonionic Polyester, "
                "Propylene Glycol, Methylisothiazolinone. This is the manufacturer's California Cleaning "
                "Product Right to Know Act (SB-258) declaration as served by the retailer that lists the "
                "product; the same label is printed on the brand's own product page."),
        note=("The Free + Clear liquid from Method, and the cleanest label in this fire: no fragrance line, "
              "no dye, and the only substance in it this database grades F is the preservative "
              "methylisothiazolinone. The cleaning system is five enzymes (protease, amylase, mannanase, "
              "pectinase) plus laureth-7 and sodium lauryl sulfate, with trisodium MGDA as the chelator, "
              "sodium cocoate as the soap, calcium chloride as the enzyme stabiliser and denatonium benzoate "
              "as the bittering agent that keeps children from drinking it. Two mapping notes, both "
              "deliberate: the label's 'Trisodium Salt of Methylglycinediacetic Acid' is the substance this "
              "database already carries as Trisodium MGDA, and the three enzyme blends map onto the "
              "registry's graded enzyme keys rather than minting ungraded twins, so a known respiratory "
              "sensitizer is not turned into a blank by a label wording."),
        ings=["Water", "Laureth-7", "Sodium Lauryl Sulfate", "Glycerin", "Alcohol Denat.",
              "Protease Enzyme Blend", "Trisodium Salt of Methylglycinediacetic Acid", "Sodium Cocoate",
              "Amylase Enzyme Blend", "Calcium Chloride", "Sodium Carboxymethyl Inulin", "Citric Acid",
              "Denatonium Benzoate", "Mannanase Enzyme Blend", "Pectinase Enzyme", "Nonionic Polyester",
              "Propylene Glycol", "Methylisothiazolinone"],
        substitutes=[
            dict(name="Earth Breeze Laundry Detergent Sheets, Fragrance Free", tier="mass",
                 note=("Sheet-format detergent at a comparable per-load price with no methylisothiazolinone; "
                       "the substitute is for the preservative this record declares.")),
            dict(name="all free clear Original Concentrated Liquid Laundry Detergent", tier="mass",
                 note=("Free-and-clear liquid at a mass price that is formulated for sensitive skin and does "
                       "not carry the methylisothiazolinone line here.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=1, exposure_src=SRC_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household "
                        "figure for Method laundry detergent (the brand site, the CVS listing, and a general "
                        "web search) and found none. IndexBox's US Laundry & Home Products page states "
                        "category household penetration above 98%. Method is well known in the natural "
                        "segment but is a small share of the national laundry market -- smaller than Seventh "
                        "Generation in this category -- and this is one SKU inside it, so the estimate is "
                        "category penetration times the natural-segment share times Method's small share of "
                        "that segment, rounded to one significant figure."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Arm & Hammer Plus OxiClean 4-in-1 Power Paks",
        brand="Arm & Hammer", cat="Laundry",
        source_url=("https://www.churchdwight.com/ingredient-disclosure/laundry-fabric-care/"
                    "40500935-ah-plus-oxiclean-4-in-1-power-paks.aspx"),
        tier="mass", tier_src="https://www.churchdwight.com/our-brands/",
        tier_note=("Church & Dwight's own brand page names Arm & Hammer and OxiClean among its consumer "
                   "brands, and the product is sold through grocery, mass and dollar channels, so the tier is "
                   "the broad mass channel."),
        source=("Manufacturer's own Product Ingredient Disclosure Form for 'Arm & Hammer 4-in1 Power Paks' "
                "(material number 42012368, category Laundry/fabric care), published by Church & Dwight on "
                "its California Cleaning Product Right to Know Act disclosure site and read 2026-10-11 "
                "(HTTP 200, date of disclosure 2024-03-26). Intentionally added ingredients with CAS and "
                "function: Sodium bicarbonate 144-55-8 (Builder); Sodium carbonate 497-19-8 (Builder); "
                "Zeolite 1318-02-1 (Water softener); C12-15 Alcohols ethoxylated 68131-39-5 (Surfactant); "
                "Polyvinyl alcohol film (Water soluble film); Sodium C10-16 alkylbenzenesulfonate 68081-81-2 "
                "(Surfactant); Hydrated silica 112926-00-8 (Tableting agent); Propylene glycol 57-55-6 "
                "(Stabilizer, US NTP Reproductive or Developmental Toxicants); Fluorescent brightener 71 "
                "16090-02-1 (Brightener); Sodium carbonate peroxide 15630-89-4 (Oxygen bleach); Fragrances "
                "(see below); Protease enzyme 9014-01-1 (Enzyme, EU Respiratory Sensitizer); Amylase enzyme "
                "9000-90-2 (Enzyme, EU Respiratory Sensitizer); Acrylic acid homopolymer 68479-09-4 "
                "(Dispersing agent); Polyoxyalkylene substituted chromophore (blue) (Colorant). The form's "
                "own designated-list column flags Propylene glycol under the US NTP Reproductive or "
                "Developmental Toxicants list and both enzymes under the EU respiratory-sensitizer list. The "
                "filing additionally discloses 18 fragrance components at or above 100 ppm or on a "
                "designated list (2,6-Dimethyl-7-octen-2-ol; 2-Methoxynaphthalene; 2-t-Butylcyclohexyl "
                "acetate; 3,7-dimethyloctyl acetate; Acetyl hexamethyl tetralin; Benzyl acetate; "
                "Butylphenyl methylpropional; C13-14 isoparaffin; Dipropylene glycol; Hexamethylindanopyran; "
                "Isopropyl myristate; Phenethyl alcohol; Sandalore; Terpineol acetate; Tetramethyl "
                "acetyloctahydronaphthalenes; Verdyl acetate), three of them flagged as EU fragrance "
                "allergens."),
        note=("The powdered laundry pod from the Arm & Hammer plus OxiClean line, and the form is unusually "
              "frank: it flags its own ingredients against designated lists rather than leaving the reader "
              "to look them up. The wash system is a carbonate builder set (sodium bicarbonate, sodium "
              "carbonate, zeolite, sodium carbonate peroxide as the oxygen bleach) on a C12-15 alcohol "
              "ethoxylate and a linear alkylbenzene sulfonate, with PVA as the pod film, a fluorescent "
              "brightener, an acrylic dispersing agent and a blue chromophore tint. The two enzymes carry the "
              "respiratory-sensitizer flag the maker prints itself, and propylene glycol carries the US NTP "
              "reproductive/developmental flag. Recorded honestly: the disclosure is a full intentionally-added "
              "list, but the fragrance is declared as a class plus a separate component table, so this record "
              "carries 'Fragrance' as the key and names the disclosed components in the source text rather "
              "than minting 18 fragrance keys, because the fragrance-components question is an open ruling "
              "in this repo."),
        ings=["Sodium Bicarbonate", "Sodium Carbonate", "Zeolite", "C12-15 Alcohols Ethoxylated",
              "Polyvinyl Alcohol Film", "Sodium (C10-16) Alkylbenzenesulfonate", "Hydrated Silica",
              "Propylene Glycol", "Fluorescent Brightener 71", "Sodium Carbonate Peroxide", "Fragrance",
              "Protease Enzyme", "Amylase Enzyme", "Acrylic Acid Homopolymer",
              "Polyoxyalkylene Substituted Chromophore"],
        substitutes=[
            dict(name="Earth Breeze Laundry Detergent Sheets, Fragrance Free", tier="mass",
                 note=("Fragrance-free sheet detergent at a comparable per-load price; the substitute drops "
                       "the fragrance class and the fluorescent brightener this record declares.")),
            dict(name="Total Home Free & Clear Liquid Laundry Detergent, Unscented, 100 fl oz", tier="drugstore",
                 note=("Unscented store-brand liquid at a lower price for a household avoiding the fragrance "
                       "and the brightener this pod carries.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=3, exposure_src=SRC_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household "
                        "figure for the Arm & Hammer plus OxiClean pod line (the Church & Dwight brand site, "
                        "the disclosure form, and a general web search) and found none. IndexBox's US "
                        "Laundry & Home Products page states category household penetration above 98% and "
                        "names Arm & Hammer as one of the incumbent brands supplying the mass channel. Unit-dose "
                        "pods are a minority of the format mix, and this is one pod SKU inside a sub-line, so "
                        "the estimate is category penetration times the brand's share times the pod-format "
                        "share times the SKU fraction, rounded to one significant figure."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Spray Nine Heavy-Duty Cleaner, Degreaser & Disinfectant",
        brand="Spray Nine", cat="Disinfectant",
        source_url="https://www3.epa.gov/pesticides/chem_search/ppls/006659-00003-20220505.pdf",
        tier="mass", tier_src="https://www.spraynine.com/",
        tier_note=("Sold through automotive, hardware, home-center and mass channels; the brand's own site "
                   "describes a formula developed for the automotive, industrial, military and do-it-yourself "
                   "marketplace, so the tier is the broad mass/hardware channel rather than any one shelf."),
        source=("Manufacturer's own EPA-registered label (EPA Reg. No. 6659-3, registrant Permatex / Illinois "
                "Tool Works), label revision 2022-05-05, read 2026-10-11 from the EPA pesticide product label "
                "PDF (HTTP 200, 17 pages, application/pdf). The label's own ingredient statement reads: "
                "'Ingredients: water, alcohols C9-C11 ethoxylated, dipropylene glycol butyl ether, sodium "
                "metasilicate, lauramine oxide, tetrasodium pyrophosphate, alkyl dimethyl benzyl ammonium "
                "chlorides, tetrasodium EDTA, sodium hydroxide. Contains fragrance allergens.' The label's "
                "active-ingredient panel gives the two quaternaries as n-Alkyl (60% C14, 30% C16, 5% C12, "
                "5% C18) dimethyl benzyl ammonium chloride 0.178% and n-Alkyl (68% C12, 32% C14) dimethyl "
                "ethylbenzyl ammonium chloride 0.178%. The named fragrance allergens come from the same "
                "manufacturer's California SB-258 disclosure sheet for the Spray Nine line (part numbers "
                "26832, 26801, 26805, 26810, 26855, 26825, 26705), read 2026-10-11 (HTTP 200): Sodium "
                "metasilicate 6834-92-0; Sodium hydroxide 1310-73-2; Tetrasodium EDTA 64-02-8; Linalool "
                "78-70-6; Coumarin 91-64-5; Benzyl Alcohol 100-51-6; Cinnamal 104-55-2; Anisyl Alcohol "
                "105-13-2; Citronellol 106-22-9; Geraniol 106-24-1; Benzyl Benzoate 120-51-4; Citral "
                "5392-40-5; D-limonene 5989-27-5."),
        note=("An EPA-registered heavy-duty cleaner, degreaser and disinfectant, and it is the caustic end of "
              "the corpus rather than the middle. The alkaline system is sodium metasilicate and sodium "
              "hydroxide on a lauramine oxide and a C9-11 alcohol ethoxylate, with tetrasodium pyrophosphate "
              "and tetrasodium EDTA as builders and two quaternary ammonium actives at 0.178% each for the "
              "disinfecting claim. Sodium hydroxide and sodium metasilicate are the two lines that matter: "
              "both are graded F on dermal grounds in this database, the label carries a corrosive hazard, "
              "and the fragrance is declared as a named allergen set rather than a class. It is why this "
              "record carries substitutes for the caustic rather than a different brand of the same thing. "
              "Recorded honestly: the actives are given as two specific chain distributions on the label, and "
              "the ingredient statement names them generically; this record keys the generic term the "
              "statement uses so the chain distribution is not invented."),
        ings=["Water", "Alcohols C9-C11 Ethoxylated", "Dipropylene Glycol Butyl Ether", "Sodium Metasilicate",
              "Lauramine Oxide", "Tetrasodium Pyrophosphate", "Alkyl Dimethyl Benzyl Ammonium Chlorides",
              "Tetrasodium EDTA", "Sodium Hydroxide", "Linalool", "Coumarin", "Benzyl Alcohol", "Cinnamal",
              "Anisyl Alcohol", "Citronellol", "Geraniol", "Benzyl Benzoate", "Citral", "Limonene"],
        substitutes=[
            dict(name="Simple Green All-Purpose Cleaner", tier="mass",
                 note=("Non-caustic all-purpose cleaner and degreaser at a comparable price; the substitute "
                       "avoids the sodium hydroxide and sodium metasilicate this record is built on.")),
            dict(name="Krud Kutter Original Cleaner & Degreaser", tier="mass",
                 note=("Degreaser at a comparable price without the caustic alkaline builders or the "
                       "quaternary actives, for a household that wants the grease job without the corrosives.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=1, exposure_src=SRC_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household "
                        "figure for Spray Nine (the brand site, the ITW Pro Brands site, and a general web "
                        "search) and found none. Spray Nine is a heavy-duty/professional cleaner sold mainly "
                        "through automotive and hardware channels rather than the grocery cleaning aisle, so "
                        "it is used by a small share of households. The estimate is the share of households "
                        "that buy a heavy-duty degreaser at all, times this brand's share of that shelf, "
                        "rounded to one significant figure."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="ECOS Hypoallergenic Laundry Detergent, Free & Clear",
        brand="ECOS", cat="Laundry",
        source_url="https://www.ecos.com/laundry/hypoallergenic-laundry-detergent-free-clear/",
        tier="natural", tier_src="https://www.ecos.com/laundry/hypoallergenic-laundry-detergent-free-clear/",
        tier_note=("Plant-based brand sold through natural, grocery and mass channels; the corpus files ECOS "
                   "under the natural tier, and this record follows that convention."),
        source=("Manufacturer's own product page for ECOS Hypoallergenic Laundry Detergent, Free & Clear, "
                "which prints the full ingredient list under a 'Full Ingredients List' heading with a "
                "CAS-number table beneath it, read 2026-10-11 (HTTP 200): Water (7732-18-5, Solvent), "
                "Cocamidopropyl Betaine (61789-40-0, Surfactant), Sodium Coco-Sulfate (68955-19-1, "
                "Surfactant), Cocamidopropylamine Oxide (68155-09-9, Surfactant), Phenoxyethanol "
                "(122-99-6, Preservative), Methylisothiazolinone (2682-20-4, Preservative). The page states "
                "the formula is EPA Safer Choice certified and contains only six ingredients."),
        note=("The shortest laundry label in this fire, and that is the point of it: six substances, all "
              "named, with CAS numbers printed by the maker on its own page. There is no fragrance, no dye "
              "and no brightener, and the cleaning system is coconut-derived surfactants (cocamidopropyl "
              "betaine, sodium coco-sulfate, cocamidopropylamine oxide) rather than an enzyme blend. The one "
              "line to read is the preservative methylisothiazolinone, which this database grades F on "
              "dermal and environmental grounds; it is why the record carries a substitute, and it is worth "
              "saying that a six-ingredient label is not the same thing as a hazard-free one. The maker's "
              "own page and its published sustainability report are the sources, both read directly."),
        ings=["Water", "Cocamidopropyl Betaine", "Sodium Coco-Sulfate", "Cocamidopropylamine Oxide",
              "Phenoxyethanol", "Methylisothiazolinone"],
        substitutes=[
            dict(name="Earth Breeze Laundry Detergent Sheets, Fragrance Free", tier="mass",
                 note=("Sheet-format detergent at a comparable per-load price with no methylisothiazolinone; "
                       "the substitute is for the preservative this record declares.")),
            dict(name="all free clear Original Concentrated Liquid Laundry Detergent", tier="mass",
                 note=("Free-and-clear liquid at a mass price, formulated for sensitive skin and without the "
                       "methylisothiazolinone line here.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=1, exposure_src=SRC_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household "
                        "figure for ECOS laundry detergent (the brand site, the Sam's Club and Walmart "
                        "listings, and a general web search) and found none. IndexBox's US Laundry & Home "
                        "Products page states category household penetration above 98%. ECOS is a mid-sized "
                        "plant-based brand distributed through Walmart, Sam's Club and natural channels, a "
                        "small share of the national laundering market, and this is one SKU inside it, so the "
                        "estimate is category penetration times the natural-segment share times the brand's "
                        "share, rounded to one significant figure."),
        strength_disclosure="full", disclosure_note=None,
    ),
    dict(
        name="Dove Foaming Hand Wash, Aloe & Eucalyptus",
        brand="Dove", cat="Hand Soap",
        source_url=CVS + "dove-foaming-hand-wash-aloe-eucalyptus-10-1-oz-prodid-584204",
        tier="mass", tier_src=CVS + "dove-foaming-hand-wash-aloe-eucalyptus-10-1-oz-prodid-584204",
        tier_note=("National brand sold through grocery, mass and drugstore channels; the corpus files the "
                   "mass-market hand soaps under the mass tier, and this record follows that convention."),
        source=("Manufacturer ingredient declaration for Dove Foaming Hand Wash, Aloe & Eucalyptus (10.1 oz), "
                "read 2026-10-11 from the served page on the CVS Spanish-locale host es.cvs.com in the "
                "`vendorIngredientsParagraph` field: Water (Eau), Glycerin, Cocamidopropyl Betaine, Sodium "
                "Lauroyl Glycinate, Sodium Chloride, Lauric Acid, Stearic Acid, Hydroxystearic Acid, Palmitic "
                "Acid, Aloe Barbadensis Leaf Juice, Eucalyptus Globulus Leaf Extract, Polysorbate 20, "
                "Fragrance (Parfum), Phenoxyethanol, Iodopropynyl Butylcarbamate, Sodium Gluconate, Citric "
                "Acid, Hexyl Cinnamal, Limonene, Linalool. This is the manufacturer's California Cleaning "
                "Product Right to Know Act (SB-258) declaration as served by the retailer that lists the "
                "product."),
        note=("A mass-market foaming hand wash, and it is a syndet bar in a pump rather than a soap: "
              "cocamidopropyl betaine and sodium lauroyl glycinate as the surfactants, with lauric, stearic, "
              "hydroxystearic and palmitic acids as the fatty-acid blend that makes the lather creamy and "
              "leaves the skin barrier intact. That is why a hand wash can be the mildest thing in the "
              "corpus and still carry a flag. The lines to read are the fragrance and its named allergens. "
              "Hexyl Cinnamal and Limonene are both graded F on environmental grounds in this database and "
              "are contact allergens, and the maker declares them individually rather than behind the word "
              "'fragrance', which is the disclosure that makes this record honest. Recorded honestly: this "
              "is a leave-on-adjacent product used many times a day, so the allergen route is repeated "
              "dermal contact rather than a single exposure."),
        ings=["Water", "Glycerin", "Cocamidopropyl Betaine", "Sodium Lauroyl Glycinate", "Sodium Chloride",
              "Lauric Acid", "Stearic Acid", "Hydroxystearic Acid", "Palmitic Acid", "Aloe Barbadensis Leaf Juice",
              "Eucalyptus Globulus Leaf Extract", "Polysorbate 20", "Fragrance", "Phenoxyethanol",
              "Iodopropynyl Butylcarbamate", "Sodium Gluconate", "Citric Acid", "Hexyl Cinnamal", "Limonene",
              "Linalool"],
        substitutes=[
            dict(name="Gel Hand Soap", tier="natural",
                 note=("Fragrance-free hand soap at a comparable price; the substitute drops the fragrance "
                       "line and the named allergens this record declares.")),
            dict(name="CVS Health Moisturizing Antibacterial Hand Soap", tier="drugstore",
                 note=("Store-brand hand soap at a lower price without the declared hexyl cinnamal and "
                       "limonene, for a household avoiding fragrance allergens.")),
        ],
        no_substitute_known=None, no_substitute_note=None,
        exposure=3, exposure_src=SRC_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household "
                        "figure for Dove foaming hand wash (the brand site, the CVS listing, and a general "
                        "web search) and found none. Liquid hand soap is a near-universal household category "
                        "and Dove is one of the largest personal-care brands, but this is the foaming hand-wash "
                        "format inside that brand, which is a fraction of Dove's body-wash and bar volume, so "
                        "the estimate is category penetration times the brand's share times the foaming-format "
                        "share, rounded to one significant figure."),
        strength_disclosure="full", disclosure_note=None,
    ),
]

ALIASES = {
    "protease enzyme blend": "Protease Enzyme",
    "amylase enzyme blend": "Amylase Enzyme",
    "mannanase enzyme blend": "Mannanase Enzyme",
    "trisodium salt of methylglycinediacetic acid": "Trisodium MGDA",
    "polyvinyl alcohol film": "Polyvinyl Alcohol",
    "hydrated silica": "Silica",
    "alcohols c9-c11 ethoxylated": "Alcohols, C9-11, ethoxylated",
}

MINT_NOTE = ("Minted {today} from a manufacturer disclosure or a manufacturer's own product page and "
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

    # brand-string extensions on existing owner records
    extended = []
    for owner_name, brands in OWNER_BRAND_EXTENSIONS.items():
        rec = owners["owners"].get(owner_name)
        if not rec:
            continue
        for b in brands:
            if b not in rec.get("brands", []):
                extended.append((owner_name, b))
                if not args.dry_run:
                    rec.setdefault("brands", []).append(b)

    print(f"products added: {len(added_records)}  skipped(existing): {len(skipped)}")
    for r in added_records:
        print(f"   + {r['name']}  ({len(r['ings'])} ingredients)")
    print(f"ingredient keys minted: {len(minted)} -> {minted}")
    print(f"ingredient keys aliased: {len(aliased)}")
    for a, b in aliased:
        print(f"   {a!r} -> {b!r}")
    print(f"owner record added: {owner_added} ({NEW_OWNER_NAME!r})")
    print(f"owner brand extensions: {extended}")

    if args.dry_run:
        print("dry run: no files written")
        return

    def dump(path, obj, indent, trailing_newline):
        text = json.dumps(obj, ensure_ascii=False, indent=indent)
        if trailing_newline:
            text += "\n"
        path.write_text(text, encoding="utf-8")

    # measured at upstream HEAD 2026-10-11: products.json / ingredients.json /
    # owners.json are indent=1; changelog.json is indent=2. Trailing byte:
    # products.json ends `]` no newline; ingredients.json ends `}` WITH a newline;
    # owners.json ends `}` no newline; changelog.json ends `]` WITH a newline.
    dump(prods_path, products, 1, False)
    dump(ings_path, ingredients, 1, True)
    dump(owners_path, owners, 1, False)

    changed = bool(added_records or owner_added or extended)
    if not args.no_changelog and changed:
        cl = json.loads((REPO / "data/changelog.json").read_text(encoding="utf-8"))
        if not cl or cl[0].get("date") != TODAY:
            cl.insert(0, {
                "date": TODAY,
                "text": (f"Spectrum harvest station 2 (Dolman {TODAY}): {len(added_records)} missing "
                         "high-exposure name-brand products added -- the laundry aisle (Seventh Generation, "
                         "Method, Arm & Hammer plus OxiClean, ECOS), one EPA-registered heavy-duty cleaner "
                         "(Spray Nine) and one mass hand wash (Dove), every list read from the manufacturer's "
                         "own declaration or product page. New owner record: Illinois Tool Works Inc. "
                         f"(Spray Nine). {len(minted)} new ingredient keys minted, all ungraded."),
            })
            dump(REPO / "data/changelog.json", cl, 2, True)


if __name__ == "__main__":
    main()
