#!/usr/bin/env python3
"""Night-shift station 2 harvest, 2026-10-14 (Dolman).

Shelf: the Church & Dwight household laundry/stain/carpet shelf, ordered by EXPOSURE.
Route: the manufacturer's own California Cleaning Product Right to Know Act
(SB-258) per-product ingredient-disclosure index,
https://www.churchdwight.com/ingredient-disclosure/ (HTTP 200, 153,624 bytes,
requires curl -L / a redirect-following client -- a bare fetch 301s).

Why this shelf: the four channel tiers are built, the KIK value-brand index is
exhausted for household products, and air care remains blocked on the open
fragrance-components-as-ingredient-keys ruling rather than on a route. The
remaining work is ABSENT HIGH-EXPOSURE STAPLES. OxiClean is the #2 brand by
unit volume in the Amazon US detergent category (22.5% of top-10 volume) and
the single highest-volume absent listing in that category is an OxiClean Odor
Blasters powder (100,000 units in July 2026). These are mainstream mass-market
products at mass price points, not a drift back to premium brands.

Fragrance discipline: each filing discloses individual fragrance components at
or above 100 ppm. Per the standing discipline while the
fragrance-components-as-ingredient-keys ruling is open, the components are
recorded as the single 'Fragrance' key with the component list named in the
record's `source` prose only. No fragrance keys are minted.

Idempotent: a second run adds nothing and mints nothing.
"""
import json, os, sys, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")
TODAY = "2026-10-14"
IDX = "https://www.churchdwight.com/ingredient-disclosure/"
CANDY = "https://churchdwight.com/our-brands/consumer-brands/"
IDXBOX_LAUNDRY = "https://www.indexbox.io/store/united-states-laundry-home-products-market-analysis-forecast-size-trends-and-insights/"
IDXBOX_SURFACE = "https://www.indexbox.io/store/united-states-household-surface-cleaners-market-analysis-forecast-size-trends-and-insights/"
IDXBOX_CARPET = "https://www.indexbox.io/store/united-states-carpet-cleaning-products-market-analysis-forecast-size-trends-and-insights/"
ASINSIGHT_DET = "https://www.asinsight.com/market-analysis/US/detergent"
ASINSIGHT_LAUNDRY = "https://www.asinsight.com/report/US/laundry-detergents"
SIMPORTER = "https://simporter.com/trends/household-care/"

# name -> (key, cas, function) ; key None means "map to this existing key"
ALIAS = {
    "Sodium carbonate": ("Sodium Carbonate", "497-19-8", "Builder"),
    "Sodium carbonate peroxide": ("Sodium Carbonate Peroxide", "15630-89-4", "Oxygen bleach"),
    "C10-16 alketh": ("C10-16 Pareth", "68131-39-5 / 68002-97-1 / 68551-12-2", "Surfactant"),
    "Fragrances": ("Fragrance", None, "Fragrance"),
    "Sodium chloride": ("Sodium Chloride", "7647-14-5", "Builder"),
    "C.I. Pigment Blue 15:1": ("C.I. Pigment Blue 15:1", "Withheld as CBI", "Colorant"),
    "Acrylic acid homopolymer": ("Acrylic Acid Homopolymer", "68479-09-4", "Dispersing agent"),
    "Disodium distyrylbiphenyl disulfonate": ("Disodium Distyrylbiphenyl Disulfonate", "27344-41-8", "Brightening agent"),
    "Protease enzyme": ("Protease Enzyme", "9014-01-1", "Enzyme"),
    "Amylase enzyme": ("Amylase Enzyme", "9000-90-2", "Enzyme"),
    "Water": ("Water", "7732-18-5", "Solvent"),
    "Sodium laureth sulfate": ("Sodium Laureth Sulfate", "68585-34-2", "Surfactant"),
    "Glycerin": ("Glycerin", "56-81-5", "Enzyme stabilizer"),
    "Sodium borate": ("Sodium Borate", "12179-04-3", "Enzyme stabilizer"),
    "Sodium bicarbonate": ("Sodium Bicarbonate", "144-55-8", "pH adjuster"),
    "Sodium C10-16 alkylbenzenesulfonate": ("Sodium (C10-16) Alkylbenzenesulfonate", "68081-81-2", "Surfactant"),
    "C12-13 alcohols ethoxylated": ("C12-13 Alcohols Ethoxylated", "66455-14-9", "Surfactant"),
    "Calcium chloride": ("Calcium Chloride", "10035-04-8", "Enzyme stabilizer"),
    "Sodium formate": ("Sodium Formate", "141-53-7", "Enzyme stabilizer"),
    "Citric acid": ("Citric Acid", "77-92-9", "pH adjuster"),
    "Pentasodium DTPA": ("Pentasodium DTPA", "140-01-2", "Chelating agent"),
    "Benzisothiazolinone": ("Benzisothiazolinone", "2634-33-5", "Preservative"),
    "Methylisothiazolinone": ("Methylisothiazolinone", "2682-20-4", "Preservative"),
    "Polyoxyalkylene substituted chromophore (blue) or modified anthraquinone": ("Polyoxyalkylene Substituted Chromophore", "Not available", "Colorant"),
    "Polyoxyalkylene substituted chromophore (blue)": ("Polyoxyalkylene Substituted Chromophore", "Not available", "Colorant"),
    "Polyoxyalkylene substituted chromophore (violet)": ("Polyoxyalkylene Substituted Chromophore", "Not available", "Colorant"),
    "Polyvinyl alcohol": ("Polyvinyl Alcohol", "25213-24-5", "Substrate"),
    "Sodium C14-16 olefin sulfonate": ("Sodium C14-16 Olefin Sulfonate", "68439-57-6", "Surfactant"),
    "Sodium lauryl sulfate": ("Sodium Lauryl Sulfate", "151-21-3", "Surfactant"),
    "Sodium fatty acid methyl ester sulfonate": ("Sodium Fatty Acid Methyl Ester Sulfonate", "93348-22-2", "Surfactant"),
    "C12-14 alcohols ethoxylated": ("C12-14 Alcohols Ethoxylate", "68439-50-9", "Surfactant"),
    "Sodium polyacrylate": ("Sodium Polyacrylate", "9003-04-7", "Dispersing agent"),
    "PEG-12 dimethicone": ("PEG-12 Dimethicone", "68937-54-2", "Defoamer"),
    "Polypropylene terephthalate": ("Polypropylene Terephthalate", "139755-78-5", "Emulsifying agent"),
    "Saponins": ("Saponins", "8047-15-2", "Surfactant"),
    "Mannanase enzyme": ("Mannanase Enzyme", "37288-54-3", "Enzyme"),
    "Colorants": ("Colorant", "Not available", "Colorants"),
    "Hydrated silica": ("Silica", "112926-00-8", "Process aid"),
    "Propylene glycol": ("Propylene Glycol", "57-55-6", "Enzyme stabilizer"),
    "Ethanolamine": ("Ethanolamine", "141-43-5", "pH adjuster"),
    "Tetrasodium EDTA": ("Tetrasodium EDTA", "64-02-8", "Chelating agent"),
    "Palm kernel fatty acid": ("Palm Kernel Fatty Acid", "101403-98-9", "Anti-foam"),
    "Cellulase enzyme": ("Cellulase Enzyme", "9012-54-8", "Enzyme"),
    "Acrylic copolymer blend": ("Acrylic Copolymer", "Withheld as CBI", "Water sheeting polymer"),
    "Caprylyl/capryl glucoside": ("Caprylyl/Capryl Glucoside", "68515-73-1", "Surfactant"),
    "Lauryl glucoside": ("Lauryl Glucoside", "110615-47-9", "Surfactant"),
    "EDTA": ("EDTA", "60-00-4", "Chelator"),
    "Alkyl C12-16 dimethylbenzyl ammonium chloride": ("Alkyl C12-16 Dimethylbenzyl Ammonium Chloride", "68424-85-1", "Surfactant"),
    "Dicapryl/dicaprylyl dimonium chloride": ("Dicapryl/Dicaprylyl Dimonium Chloride", "68424-95-3", "Surfactant"),
    "3-Bromo-1-chloro-5, 5-dimethylimidazolidine-2,4-dione": ("1-Bromo-3-chloro-5,5-dimethylhydantoin", "126-06-7", "Cleaning agent"),
    "1,3-Dichloro-5, 5-dimethlyhydantoin": ("1,3-Dichloro-5,5-dimethylhydantoin", "118-52-5", "Cleaning agent"),
    "1,3-Dichloro-5-ethyl-5-methylimidazolidine-2,4-dione": ("1,3-Dichloro-5-ethyl-5-methylhydantoin", "89415-87-2", "Cleaning agent"),
}

NEW_KEY_NOTE = ("Added by the {date} night-shift harvest from a manufacturer's California Cleaning Product "
                "Right to Know Act disclosure. No PubChem or ECHA grade has been resolved for this entry yet, "
                "so g is null rather than a guess. It enters ungraded, which is the honest state until the "
                "grading lane reaches it.")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def dump(name, obj, indent):
    p = os.path.join(DATA, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=indent))
    # products/ingredients/owners/reg have no trailing newline; changelog none either


PRODUCTS = [
    dict(
        name="OxiClean Versatile Stain Remover with Odor Blasters",
        brand="OxiClean", cat="Stain & Odor", safe=None,
        ings=["Sodium Carbonate", "Sodium Carbonate Peroxide", "C10-16 Pareth", "Fragrance",
              "Sodium Chloride", "C.I. Pigment Blue 15:1", "Acrylic Acid Homopolymer"],
        slug="laundry-fabric-care/40500711-oxiclean-versatile-stain-remover-odor-blaster.aspx",
        served="OxiClean Versatile Stain Remover with Odor Blasters",
        cas=[("Sodium carbonate", "497-19-8", "Builder"),
             ("Sodium carbonate peroxide", "15630-89-4", "Oxygen bleach"),
             ("C10-16 alketh (the filing's own alias list: C12-15 alcohols ethoxylated 68131-39-5, C10-16 alcohol ethoxylate 68002-97-1, C12-16 alcohols ethoxylated 7EO 68551-12-2)", None, "Surfactant"),
             ("Sodium chloride", "7647-14-5", "Builder"),
             ("C.I. Pigment Blue 15:1", "withheld as CBI", "Colorant"),
             ("Acrylic acid homopolymer", "68479-09-4", "Dispersing agent")],
        frag=["4-tert-Butylcyclohexyl acetate 32210-23-4", "2,6-Dimethyl-7-octen-2-ol 18479-58-8",
              "Dipropylene glycol 25265-71-8", "Hexamethylindanopyran 1222-05-5 (EU Fragrance Allergens; US EPA PBTs)",
              "Hexyl cinnamal 101-86-0 (EU Fragrance Allergens)",
              "Tetramethyl acetyloctahydronaphthalenes 54464-57-2 (EU Fragrance Allergens)",
              "4,7-Methano-1H-inden-5-ol, 3a,4,5,6,7,7a-hexahydro-, 5-acetate and verdyl acetate 2500-83-6 / 5413-60-5",
              "Butylphenyl methylpropional 80-54-6 (EU Fragrance Allergens; EU CMRs)",
              "d-Limonene 5989-27-5 (EU Fragrance Allergens)"],
        note=("The single highest-volume absent listing in the US Amazon detergent category: 100,000 units in "
              "July 2026, the #1 ranked ASIN in that category. An oxygen-bleach stain-remover powder. Recorded "
              "because it is the mainstream product a household is most likely to actually own and the corpus "
              "should carry it with the manufacturer's own filing behind it. Entered ungraded: product grading is "
              "the Sifter lane. Note the filing names a twin, 'OxiClean Triple Action Odor Blasters Odor & Stain "
              "Remover' (material 42018220), with an identical seven-line intentionally-added list; that twin was "
              "not entered as a second record because the formula is identical."),
        exposure=5,
        exposure_src=ASINSIGHT_DET,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for OxiClean "
                        "Odor Blasters (the Church & Dwight filing, the brand site, and a general web search) and "
                        "found none. IndexBox's US Laundry & Home Products page states household penetration above "
                        "98 percent. asinsight's Amazon US detergent analysis for July 2026 puts this listing at "
                        "100,000 units, the top-ranked ASIN, and OxiClean at 22.5 percent of top-10 unit volume "
                        "(second only to Tide). Estimate is category penetration times a leading stain-remover "
                        "share, rounded to one significant figure."),
        substitutes=[dict(name="OxiClean Triple Action Versatile Stain Remover, Free", tier="mass",
                          note=("Same brand, same shelf, same price band, and the fragrance-free member of the "
                                "same family. Avoids the whole fragrance class (nine disclosed components here, "
                                "four of them EU fragrance allergens and one an EU CMR).")),
                     dict(name="up&up Stain Remover", tier="grocery",
                          note=("Lower price, same aisle, same oxygen-bleach stain-removing job. A store-brand "
                                "powder, so it is the substitute for a household watching the price rather than "
                                "the ingredient list."))],
    ),
    dict(
        name="OxiClean White Revive Whitener and Stain Remover",
        brand="OxiClean", cat="Stain & Odor", safe=None,
        ings=["Sodium Carbonate", "Sodium Carbonate Peroxide", "Acrylic Acid Homopolymer", "C10-16 Pareth",
              "Protease Enzyme", "Disodium Distyrylbiphenyl Disulfonate", "Amylase Enzyme", "Fragrance"],
        slug="laundry-fabric-care/40501171-oxiclean-white-revive-whitener-and-stain-remover.aspx",
        served="OxiClean White Revive Whitener and Stain Remover",
        cas=[("Sodium carbonate", "497-19-8", "Builder"),
             ("Sodium carbonate peroxide", "15630-89-4", "Oxygen bleach"),
             ("Acrylic acid homopolymer", "68479-09-4", "Dispersing agent"),
             ("C10-16 alketh", "68131-39-5 / 68002-97-1 / 68551-12-2", "Surfactant"),
             ("Protease enzyme", "9014-01-1", "Enzyme"),
             ("Disodium distyrylbiphenyl disulfonate", "27344-41-8", "Brightening agent"),
             ("Amylase enzyme", "9000-90-2", "Enzyme")],
        frag=["2,6-Dimethyl-7-octen-2-ol 18479-58-8", "Butylphenyl methylpropional 80-54-6 (EU Fragrance Allergens; EU CMRs)",
              "Dipropylene glycol 25265-71-8", "Hexamethylindanopyran 1222-05-5 (US EPA PBTs)"],
        note=("A chlorine-free whitening powder, ranked in the top ten of the US Amazon laundry-detergent "
              "category in August 2026. Recorded because it is a mainstream whitening product and because its "
              "brightener chemistry (a stilbene optical brightener) is the ingredient households ask about. "
              "Entered ungraded. The filing names a twin, 'Oxiclean Triple Action White Revive Laundry Whitener "
              "and Stain Remover' (material 42018217), with the same eight-line list; not entered separately."),
        exposure=3,
        exposure_src=ASINSIGHT_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for OxiClean "
                        "White Revive (the manufacturer filing, the brand site, a general web search) and found "
                        "none. IndexBox's US Laundry & Home Products page states household penetration above 98 "
                        "percent; asinsight's August 2026 Amazon laundry-detergent report puts White Revive in the "
                        "top ten tracked products at roughly 50,000 to 100,000 monthly units. Estimate is category "
                        "penetration times a whitening-subsegment share, rounded to one significant figure."),
        substitutes=[dict(name="OxiClean Triple Action Versatile Stain Remover, Free", tier="mass",
                          note=("Same brand, same shelf, same price band. Avoids both the fragrance and the "
                                "stilbene optical brightener, which is the ingredient a household avoiding "
                                "brighteners is usually trying to get away from.")),
                     dict(name="Baking Soda (bulk)", tier="apothecary-bulk",
                          note=("Far lower price, and the honest alternative for whitening by oxygen bleach "
                                "without fragrance or brightener. Plain sodium bicarbonate is not an oxygen "
                                "bleach on its own, so this is the alternative for a household choosing "
                                "unscented and unadditised rather than for the same whitening performance."))],
    ),
    dict(
        name="Arm & Hammer plus OxiClean Odor Blasters Liquid Laundry Detergent, Fresh Burst",
        brand="Arm & Hammer", cat="Laundry", safe=None,
        ings=["Water", "C10-16 Pareth", "Sodium Laureth Sulfate", "Glycerin", "Fragrance", "Sodium Borate",
              "Sodium Bicarbonate", "Sodium (C10-16) Alkylbenzenesulfonate", "Acrylic Acid Homopolymer",
              "C12-13 Alcohols Ethoxylated", "Calcium Chloride", "Sodium Formate", "Citric Acid",
              "Disodium Distyrylbiphenyl Disulfonate", "Pentasodium DTPA", "Amylase Enzyme", "Protease Enzyme",
              "Benzisothiazolinone", "Methylisothiazolinone", "Polyoxyalkylene Substituted Chromophore"],
        slug="laundry-fabric-care/42015533-ah-plus-oxiclean-liquid-laundry-odor-blasters.aspx",
        served="Arm & Hammer plus OxiClean Odor Blasters Liquid Laundry Detergent - Fresh Burst",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("C10-16 alketh", "68131-39-5 / 68002-97-1 / 68551-12-2", "Surfactant"),
             ("Sodium laureth sulfate", "68585-34-2", "Surfactant"),
             ("Glycerin", "56-81-5", "Enzyme stabilizer"),
             ("Sodium borate", "12179-04-3", "Enzyme stabilizer"),
             ("Sodium bicarbonate", "144-55-8", "pH adjuster"),
             ("Sodium C10-16 alkylbenzenesulfonate", "68081-81-2", "Surfactant"),
             ("Acrylic acid homopolymer", "66019-18-9", "Dispersing agent"),
             ("C12-13 alcohols ethoxylated", "66455-14-9", "Surfactant"),
             ("Calcium chloride", "10035-04-8", "Enzyme stabilizer"),
             ("Sodium formate", "141-53-7", "Enzyme stabilizer"),
             ("Citric acid", "77-92-9", "pH adjuster"),
             ("Disodium distyrylbiphenyl disulfonate", "27344-41-8", "Optical brightener"),
             ("Pentasodium DTPA", "140-01-2", "Chelating agent"),
             ("Amylase enzyme", "9000-90-2", "Enzyme"),
             ("Protease enzyme", "9014-01-1", "Enzyme"),
             ("Benzisothiazolinone", "2634-33-5", "Preservative"),
             ("Methylisothiazolinone", "2682-20-4", "Preservative"),
             ("Polyoxyalkylene substituted chromophore (blue) or modified anthraquinone", "Not available", "Colorant")],
        frag=["Dipropylene glycol 25265-71-8", "Tetramethyl acetyloctahydronaphthalenes 54464-57-2 (EU Fragrance Allergens)",
              "Isopropylideneglycerol 100-79-8", "2-t-Butylcyclohexyl acetate 88-41-5",
              "Limonene 68647-72-3 (EU Fragrance Allergens)", "Hexyl cinnamal 101-86-0 (EU Fragrance Allergens)",
              "2,6-Dimethyl-7-octen-2-ol 18479-58-8",
              "3a,4,5,6,7,7a-hexahydro-4,7-methano-1h-inden-5(or 6)-yl acetate 54830-99-8",
              "Hexamethylindanopyran 1222-05-5 (EU Fragrance Allergens; US EPA PBTs)",
              "Linalool 78-70-6 (EU Fragrance Allergens)", "Ethyl beta-naphthyl ether 93-18-5",
              "Tricyclodecenyl propionate 17511-60-3", "Methyl beta-naphthyl ether 93-04-9",
              "Trichloromethyl phenyl carbinyl acetate 90-17-5", "Ethyl 2,2-dimethylhydrocinnamal 67634-15-5",
              "4-tert-Butylcyclohexyl acetate 32210-23-4", "Citronellyl nitrile 51566-62-2",
              "Citronellol 106-22-9 (EU Fragrance Allergens)", "Ethyl trimethylcyclopentene butenol 28219-61-6",
              "Isobornyl acetate 125-12-2", "2,4-Dimethyl-3-cyclohexene carboxaldehyde 68039-49-6",
              "Butylphenyl methylpropional 80-54-6 (EU Fragrance Allergens; EU CMRs)"],
        note=("A mainstream value-priced liquid laundry detergent, one of the top ten tracked listings in the US "
              "Amazon detergent category in July 2026. Recorded because it is a high-volume mass-market detergent "
              "carrying both the OxiClean oxygen-bleach line and the full enzyme set, and because the corpus "
              "already carries its sibling (Arm & Hammer Liquid Laundry Detergent, Baking Soda Fresh). Entered "
              "ungraded. The filing names a second scent, 'Arm & Hammer plus OxiClean Liquid Laundry Detergent - "
              "Odor Blasters Fresh Burst' (material 42018178), with a near-identical list differing by sodium "
              "chloride, tromethamine, sodium borate and sodium formate; not entered separately as the formula "
              "family is already present."),
        exposure=8,
        exposure_src=ASINSIGHT_DET,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for the Arm & "
                        "Hammer plus OxiClean Odor Blasters liquid (the manufacturer filing, the brand site, a "
                        "general web search) and found none. IndexBox's US Laundry & Home Products page states "
                        "household penetration above 98 percent; asinsight's July 2026 Amazon detergent analysis "
                        "ranks this line in the top ten at roughly 50,000 to 100,000 monthly units and puts "
                        "Arm & Hammer's owner Church & Dwight among the top three brands by top-10 unit volume. "
                        "Estimate is category penetration times a mid-tier brand share, rounded to one "
                        "significant figure, and set at the same band as the corpus's existing Arm & Hammer "
                        "liquid record."),
        substitutes=[dict(name="all free clear Original Concentrated Liquid Laundry Detergent", tier="mass",
                          note=("Same price band, same shelf, same mainstream liquid-detergent job. Avoids the "
                                "fragrance class entirely (22 disclosed components here, seven of them EU "
                                "fragrance allergens and one an EU CMR) and the optical brightener.")),
                     dict(name="Xtra Liquid Laundry Detergent, Tropical Passion", tier="mass",
                          note=("Lower price, same aisle, same wash. The alternative for a household watching "
                                "the price rather than the ingredient list; it carries its own fragrance, so it "
                                "does not avoid the fragrance class."))],
    ),
    dict(
        name="Arm & Hammer plus OxiClean Power Sheets Laundry Detergent, Sparkling Fresh",
        brand="Arm & Hammer", cat="Laundry", safe=None,
        ings=["Polyvinyl Alcohol", "Sodium C14-16 Olefin Sulfonate", "Water", "Sodium Lauryl Sulfate",
              "Sodium Fatty Acid Methyl Ester Sulfonate", "Fragrance", "C12-14 Alcohols Ethoxylate",
              "Pentasodium DTPA", "Sodium Polyacrylate", "C10-16 Pareth", "PEG-12 Dimethicone",
              "Sodium Bicarbonate", "Polypropylene Terephthalate", "Glycerin", "Saponins", "Amylase Enzyme",
              "Mannanase Enzyme", "Protease Enzyme", "Benzisothiazolinone", "Colorant"],
        slug="laundry-fabric-care/42018968-OxiClean-Power-Sheets-Laundry-Detergent-Sparkling-Fresh.aspx",
        served="Arm & Hammer plus OxiClean Power Sheets Laundry Detergent - Sparkling Fresh",
        cas=[("Polyvinyl alcohol", "25213-24-5", "Substrate (the water-soluble sheet film)"),
             ("Sodium C14-16 olefin sulfonate", "68439-57-6", "Surfactant"),
             ("Water", "7732-18-5", "Solvent"),
             ("Sodium lauryl sulfate", "151-21-3", "Surfactant"),
             ("Sodium fatty acid methyl ester sulfonate", "93348-22-2", "Surfactant"),
             ("C12-14 alcohols ethoxylated", "68439-50-9", "Surfactant"),
             ("Pentasodium DTPA", "140-01-2", "Chelating agent"),
             ("Sodium polyacrylate", "9003-04-7", "Dispersing agent"),
             ("C10-16 alketh (the filing's alias line: C12-16 alcohols ethoxylated 7EO)", "68551-12-2", "Surfactant"),
             ("PEG-12 dimethicone", "68937-54-2", "Defoamer"),
             ("Sodium bicarbonate", "144-55-8", "pH adjuster"),
             ("Polypropylene terephthalate", "139755-78-5", "Emulsifying agent"),
             ("Glycerin", "56-81-5", "Solvent"),
             ("Saponins", "8047-15-2", "Surfactant"),
             ("Amylase enzyme", "9000-90-2", "Enzyme"),
             ("Mannanase enzyme", "37288-54-3", "Enzyme"),
             ("Protease enzyme", "9014-01-1", "Enzyme"),
             ("Benzisothiazolinone", "2634-33-5", "Preservative"),
             ("Colorants", "Not available", "Colorants")],
        frag=["42 components disclosed at or above 100 ppm, including 2-methyl butyl salicylate 51115-63-0, "
              "lauraldehyde 112-54-9, 2-methylundecanal 110-41-8, allyl cyclohexanepropionate 2705-87-5, "
              "Ambroxan 6790-58-5, amyl salicylate 2050-08-0 (EU Fragrance Allergens; US EPA PBTs), "
              "benzyl acetate 140-11-4, benzylacetone 2550-26-7, Cedrus atlantica wood oil 8000-27-9 "
              "(EU Fragrance Allergens), citronellol 106-22-9 (EU Fragrance Allergens), coumarin 91-64-5 "
              "(EU Fragrance Allergens), cyclamen aldehyde 103-95-7, gamma-decalactone 706-14-9, "
              "2,6-dimethyl-7-octen-2-ol 18479-58-8 and benzyl dimethyl carbinyl acetate 151-05-3 "
              "(EU Fragrance Allergens). Full list in the cited filing."],
        note=("A laundry-detergent sheet: a water-soluble polyvinyl alcohol film carrying a full detergent, so "
              "the household handles no jug and no plastic. Recorded because it is the fastest-growing format on "
              "the shelf and because its substrate is the ingredient households are least likely to expect in a "
              "detergent. Entered ungraded. The filing discloses 42 fragrance components at or above 100 ppm, the "
              "largest fragrance disclosure in this fire, which is why it carries a fragrance-free substitute "
              "rather than none."),
        exposure=2,
        exposure_src=ASINSIGHT_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level or format-level US household figure "
                        "for laundry detergent sheets (the manufacturer filing, the brand site, a general web "
                        "search) and found none. IndexBox's US Laundry & Home Products page states household "
                        "penetration above 98 percent. Sheets are a recent format with a small share of that "
                        "base; the estimate is category penetration times a low single-digit format share, "
                        "rounded to one significant figure."),
        substitutes=[dict(name="Earth Breeze Laundry Detergent Sheets, Fragrance Free", tier="mass",
                          note=("Same format, same job, same shelf. Avoids the entire fragrance class and its 42 "
                                "disclosed components; still a polyvinyl alcohol sheet, so it does not avoid the "
                                "film substrate.")),
                     dict(name="OxiClean Triple Action Versatile Stain Remover, Free", tier="mass",
                          note=("Same brand family, same price band, a powder rather than a sheet. Fragrance-free, "
                                "and it avoids the polyvinyl alcohol film entirely."))],
    ),
    dict(
        name="OxiClean Max Force Power Paks",
        brand="OxiClean", cat="Laundry", safe=None,
        ings=["Sodium Carbonate Peroxide", "Sodium Bicarbonate", "Sodium Carbonate", "C10-16 Pareth",
              "Polyvinyl Alcohol", "Silica", "Acrylic Acid Homopolymer", "Disodium Distyrylbiphenyl Disulfonate",
              "Sodium Chloride", "Propylene Glycol", "Protease Enzyme", "Amylase Enzyme", "Fragrance",
              "C.I. Pigment Blue 15:1"],
        slug="laundry-fabric-care/42018346-OxiClean-Max-Force-Power-Paks.aspx",
        served="OxiClean Max Force Power Paks",
        cas=[("Sodium carbonate peroxide", "15630-89-4", "Oxygen bleach"),
             ("Sodium bicarbonate", "144-55-8", "Builder"),
             ("Sodium carbonate", "497-19-8", "Builder"),
             ("C10-16 alketh", "68131-39-5 / 68002-97-1 / 68551-12-2", "Surfactant"),
             ("Polyvinyl alcohol", "not available", "Water-soluble film"),
             ("Hydrated silica", "112926-00-8", "Process aid"),
             ("Acrylic acid homopolymer", "68479-09-4", "Dispersing agent"),
             ("Disodium distyrylbiphenyl disulfonate", "27344-41-8", "Brightening agent"),
             ("Sodium chloride", "7647-14-5", "Builder"),
             ("Propylene glycol", "57-55-6", "Enzyme stabilizer"),
             ("Protease enzyme", "9014-01-1", "Enzyme"),
             ("Amylase enzyme", "9000-90-2", "Enzyme"),
             ("C.I. Pigment Blue 15:1", "withheld as CBI", "Colorant")],
        frag=["12 components disclosed at or above 100 ppm; the filing lists them in full. Not repeated here "
              "as ingredient keys per the standing fragrance discipline."],
        note=("A pre-measured oxygen-bleach stain-remover pac, the pod-format member of the OxiClean stain-remover "
              "line. Recorded because the pac format is where the mainstream shelf has moved and the corpus's "
              "OxiClean coverage was powder-and-spray only. Entered ungraded."),
        exposure=3,
        exposure_src=IDXBOX_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for OxiClean "
                        "Max Force Power Paks (the manufacturer filing, the brand site, a general web search) and "
                        "found none. IndexBox's US Laundry & Home Products page states household penetration "
                        "above 98 percent and notes pods gaining share in dish and laundry care. Estimate is "
                        "category penetration times a stain-remover pod share, rounded to one significant "
                        "figure."),
        substitutes=[dict(name="AspenClean Laundry Detergent Pods, Unscented", tier="natural",
                          note=("A fragrance-free laundry pod, so it avoids the fragrance class and the C.I. "
                                "pigment dye. It sits a price band above the mass pods, so this is the "
                                "fragrance-avoiding choice rather than the same-price one.")),
                     dict(name="Arm & Hammer Plus OxiClean 4-in-1 Power Paks", tier="mass",
                          note=("Same price band, same shelf, same pac format and the same oxygen-bleach core. "
                                "Carries its own fragrance, so it does not avoid the fragrance class."))],
    ),
    dict(
        name="OxiClean Dark Protect Liquid Laundry Booster",
        brand="OxiClean", cat="Laundry", safe=None,
        ings=["Water", "Sodium Laureth Sulfate", "C10-16 Pareth", "Glycerin",
              "Sodium (C10-16) Alkylbenzenesulfonate", "Sodium Chloride", "Ethanolamine", "Citric Acid",
              "Sodium Borate", "Tetrasodium EDTA", "Sodium Formate", "Acrylic Acid Homopolymer",
              "Palm Kernel Fatty Acid", "Cellulase Enzyme", "Benzisothiazolinone", "Methylisothiazolinone",
              "Calcium Chloride", "Sodium Carbonate", "Polyoxyalkylene Substituted Chromophore", "Fragrance",
              "Amylase Enzyme", "Mannanase Enzyme"],
        slug="laundry-fabric-care/42011772-oxiclean-dark-protect-liquid.aspx",
        served="OxiClean Dark Protect Liquid Laundry Booster",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("Sodium laureth sulfate", "68585-34-2", "Surfactant"),
             ("C10-16 alketh", "68131-39-5 / 68002-97-1 / 68551-12-2", "Surfactant"),
             ("Glycerin", "56-81-5", "Enzyme stabilizer"),
             ("Sodium C10-16 alkylbenzenesulfonate", "68081-81-2", "Surfactant"),
             ("Sodium chloride", "7647-14-5", "Builder"),
             ("Ethanolamine", "141-43-5", "pH adjuster"),
             ("Citric acid", "77-92-9", "pH adjuster"),
             ("Sodium borate", "12179-04-3", "Enzyme stabilizer"),
             ("Tetrasodium EDTA", "64-02-8", "Chelating agent"),
             ("Sodium formate", "141-53-7", "Enzyme stabilizer"),
             ("Acrylic acid homopolymer", "66019-18-9", "Dispersing agent"),
             ("Palm kernel fatty acid", "101403-98-9", "Anti-foam"),
             ("Cellulase enzyme", "9012-54-8", "Enzyme"),
             ("Benzisothiazolinone", "2634-33-5", "Preservative"),
             ("Methylisothiazolinone", "2682-20-4", "Preservative"),
             ("Calcium chloride", "10035-04-8", "Enzyme stabilizer"),
             ("Sodium carbonate", "497-19-8", "Builder"),
             ("Polyoxyalkylene substituted chromophore (violet / blue)", "Not available", "Colorant"),
             ("Amylase enzyme", "9000-90-2", "Enzyme"),
             ("Mannanase enzyme", "37288-54-3", "Enzyme")],
        frag=["Five components disclosed at or above 100 ppm, listed in full in the cited filing."],
        note=("A liquid colour-protection booster added alongside detergent to cut dye transfer between garments. "
              "Recorded because the corpus carries no colour-protection booster and the class is common on the "
              "shelf. It is the one record in this fire with no fragrance-free counterpart in the corpus, so it "
              "carries no_substitute_known with the reasoning stated rather than an empty field. Entered "
              "ungraded."),
        exposure=2,
        exposure_src=IDXBOX_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for OxiClean "
                        "Dark Protect (the manufacturer filing, the brand site, a general web search) and found "
                        "none, and searched for a category figure for laundry colour-protection additives and "
                        "found none published. IndexBox's US Laundry & Home Products page states household "
                        "penetration above 98 percent. Estimate is category penetration times a small "
                        "specialty-additive share, rounded to one significant figure."),
        substitutes=[],
        no_substitute_known=True,
        no_substitute_note=("No same-price fragrance-free colour-protection booster exists in the corpus. The "
                            "product's job is dye-transfer inhibition in a wash, and the fragrance-free laundry "
                            "products the corpus carries (all free clear, ECOS, Seventh Generation, AspenClean) "
                            "are full detergents rather than boosters, so they substitute for the detergent, not "
                            "for this product. Recorded as a known gap rather than filled with a substitute that "
                            "does not do the job."),
    ),
    dict(
        name="OxiClean Triple Action Versatile Stain Remover, Free",
        brand="OxiClean", cat="Stain & Odor", safe=None,
        ings=["Sodium Carbonate", "Sodium Carbonate Peroxide", "C10-16 Pareth"],
        slug="laundry-fabric-care/42018219-Oxiclean-3X-Versatile-Stain-Remover-Free.aspx",
        served="Oxiclean Triple Action Versatile Stain Remover - Free",
        cas=[("Sodium carbonate", "497-19-8", "Builder"),
             ("Sodium carbonate peroxide", "15630-89-4", "Oxygen bleach"),
             ("C10-16 alketh", "68131-39-5 / 68002-97-1 / 68551-12-2", "Surfactant")],
        frag=[],
        note=("The fragrance-free member of the OxiClean Versatile Stain Remover family: three disclosed "
              "ingredients and no fragrance at all. Recorded deliberately because it is the honest alternative "
              "for a household that wants the oxygen-bleach stain remover without the scent, and because a "
              "corpus that only carries the scented version leaves the reader with no safe swap. This record is "
              "itself the substitute for OxiClean Versatile Stain Remover with Odor Blasters and OxiClean White "
              "Revive. Entered ungraded."),
        exposure=3,
        exposure_src=ASINSIGHT_DET,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for the "
                        "fragrance-free OxiClean variant (the manufacturer filing, the brand site, a general web "
                        "search) and found none; no fragrance-free-subsegment figure is published. IndexBox's US "
                        "Laundry & Home Products page states household penetration above 98 percent and "
                        "asinsight's July 2026 Amazon detergent analysis puts OxiClean at 22.5 percent of top-10 "
                        "unit volume. Estimate is category penetration times the OxiClean brand share times a "
                        "small unscented-subsegment share, rounded to one significant figure."),
        substitutes=[dict(name="OxiClean Versatile Stain Remover with Odor Blasters", tier="mass",
                          note=("Same brand, same shelf, same price band, the scented version. Named as the "
                                "substitute in the other direction: a household that wants the scent and does not "
                                "mind the fragrance class can take this one instead.")),
                     dict(name="Baking Soda (bulk)", tier="apothecary-bulk",
                          note=("Far lower price and fully unscented. Plain sodium bicarbonate is a builder and a "
                                "deodoriser, not an oxygen bleach, so it is the cheap unscented option rather "
                                "than an equivalent stain remover."))],
    ),
    dict(
        name="OxiClean Shower Guard",
        brand="OxiClean", cat="Bathroom", safe=None,
        ings=["Water", "Acrylic Copolymer", "Caprylyl/Capryl Glucoside", "Lauryl Glucoside", "EDTA",
              "Ethanolamine", "Propylene Glycol", "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride",
              "Dicapryl/Dicaprylyl Dimonium Chloride", "Fragrance"],
        slug="cleaning-products/40500415-OxiClean-shower-guard.aspx",
        served="OxiClean Shower Guard",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("Acrylic copolymer blend", "withheld as CBI", "Water-sheeting polymer"),
             ("Caprylyl/capryl glucoside", "68515-73-1", "Surfactant"),
             ("Lauryl glucoside", "110615-47-9", "Surfactant"),
             ("EDTA", "60-00-4", "Chelator"),
             ("Ethanolamine", "141-43-5", "pH adjuster"),
             ("Propylene glycol", "57-55-6", "Processing aid"),
             ("Alkyl C12-16 dimethylbenzyl ammonium chloride", "68424-85-1", "Surfactant"),
             ("Dicapryl/dicaprylyl dimonium chloride", "68424-95-3", "Surfactant")],
        frag=["Five components disclosed at or above 100 ppm, listed in full in the cited filing."],
        note=("A leave-on shower treatment: a water-sheeting polymer plus sugar-derived surfactants, applied to "
              "the shower after use so water runs off and soap scum does not build. Recorded because it is a "
              "different cleaning model from a spray-and-scrub bathroom cleaner and the corpus's bathroom "
              "coverage was all spray-and-scrub. Note the mapping: the filing's 'acrylic copolymer blend' is "
              "recorded against the registry's existing Acrylic Copolymer key, same polymer class, and the "
              "filing withholds the CAS as CBI. Entered ungraded."),
        exposure=2,
        exposure_src=IDXBOX_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household figure "
                        "for OxiClean Shower Guard (the manufacturer filing, the brand site, a general web "
                        "search) and found none. IndexBox's US Household Surface Cleaners page states "
                        "approximately 95 percent of US households use at least one surface cleaner product per "
                        "month, puts specialised cleaners including bathroom at 30 to 35 percent of value with "
                        "bathroom the largest sub-segment. Estimate is category penetration times the bathroom "
                        "sub-segment times a small leave-on-treatment share, rounded to one significant figure."),
        substitutes=[dict(name="ECOS Shower Kleener", tier="natural",
                          note=("Same job on the same surface, same shelf. Avoids the quaternary ammonium active "
                                "and the acrylic polymer, and carries no registered-disinfectant claim, so it "
                                "cleans without making a kill claim.")),
                     dict(name="Wet & Forget Shower Cleaner, Vanilla Scent", tier="mass",
                          note=("Same leave-on shower-treatment model at a similar price. The alternative when "
                                "the choice is between two leave-on treatments rather than between leave-on and "
                                "spray-and-scrub; it carries its own fragrance."))],
    ),
    dict(
        name="OxiClean Washing Machine Cleaner with Odor Blasters",
        brand="OxiClean", cat="Specialty", safe=None,
        ings=["Sodium Carbonate", "Sodium Carbonate Peroxide", "C10-16 Pareth", "Fragrance", "Sodium Chloride",
              "C.I. Pigment Blue 15:1", "Acrylic Acid Homopolymer"],
        slug="laundry-fabric-care/40500547-oxiclean-washing-machine-cleaner.aspx",
        served="OxiClean Washing Machine Cleaner with Odor Blasters",
        cas=[("Sodium carbonate", "497-19-8", "Builder"),
             ("Sodium carbonate peroxide", "15630-89-4", "Oxygen bleach"),
             ("C10-16 alketh", "68131-39-5 / 68002-97-1 / 68551-12-2", "Surfactant"),
             ("Sodium chloride", "7647-14-5", "Builder"),
             ("C.I. Pigment Blue 15:1", "withheld as CBI", "Colorant"),
             ("Acrylic acid homopolymer", "68479-09-4", "Dispersing agent")],
        frag=["11 components disclosed at or above 100 ppm, listed in full in the cited filing."],
        note=("A drum-cleaning powder run on an empty cycle to strip biofilm and residue out of the machine "
              "itself. Recorded because the machine-cleaning shelf is high-exposure and the corpus carried only "
              "Glisten and Affresh and Plink before it. Entered ungraded."),
        exposure=3,
        exposure_src=IDXBOX_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level or category-level US household "
                        "figure for washing-machine cleaners (the manufacturer filing, the brand site, a general "
                        "web search) and found none published. IndexBox's US Laundry & Home Products page states "
                        "household penetration above 98 percent; a machine cleaner is used by a fraction of "
                        "households that own a machine. Estimate is category penetration times a low "
                        "single-digit machine-care share, rounded to one significant figure."),
        substitutes=[dict(name="Affresh Washer Cleaner Tablets", tier="mass",
                          note=("Same job, same shelf, same price band, the market-leading alternative. Both are "
                                "oxygen-bleach machine cleaners carrying fragrance, so this substitute addresses "
                                "price and availability rather than the fragrance class.")),
                     dict(name="Glisten Washing Machine Cleaner", tier="mass",
                          note=("Same job at a similar price. A citric-acid and glucoside formula rather than an "
                                "oxygen-bleach powder, so it avoids the peroxide and the C.I. pigment dye."))],
    ),
    dict(
        name="Kaboom Scrub Free",
        brand="Kaboom", cat="Bathroom", safe=None,
        ings=["1-Bromo-3-chloro-5,5-dimethylhydantoin", "1,3-Dichloro-5,5-dimethylhydantoin",
              "1,3-Dichloro-5-ethyl-5-methylhydantoin", "Sodium Chloride"],
        slug="cleaning-products/42000070-kaboom-scrub-free.aspx",
        served="Kaboom Scrub Free",
        cas=[("3-Bromo-1-chloro-5,5-dimethylimidazolidine-2,4-dione (BCDMH)", "126-06-7", "Cleaning agent"),
             ("1,3-Dichloro-5,5-dimethylhydantoin (DCDMH)", "118-52-5", "Cleaning agent"),
             ("1,3-Dichloro-5-ethyl-5-methylimidazolidine-2,4-dione (DCEMH)", "89415-87-2", "Cleaning agent"),
             ("Sodium chloride", "7647-14-5", "Bulk")],
        frag=[],
        note=("A chlorinated-hydantoin bathroom and toilet cleaner: three N-chlorinated hydantoins plus sodium "
              "chloride, and no hypochlorite. Recorded because this is the second member of a chemistry class "
              "the corpus carries only once (The Works Toilet Bowl Cleaner with Bleach tablets), and because "
              "'with bleach' means a different substance family here than it does in a liquid bleach. Entered "
              "ungraded; the hydantoin actives are respiratory and dermal irritants and are not yet graded "
              "against GHS in this registry."),
        exposure=3,
        exposure_src=IDXBOX_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level or brand-level US household figure "
                        "for Kaboom Scrub Free (the manufacturer filing, the brand site, a general web search) "
                        "and found none. IndexBox's US Household Surface Cleaners page states approximately 95 "
                        "percent of US households use at least one surface cleaner product per month and puts "
                        "specialised cleaners including bathroom at 30 to 35 percent of value with bathroom the "
                        "largest sub-segment. Estimate is category penetration times the bathroom sub-segment "
                        "times a mid-tier brand share, rounded to one significant figure."),
        substitutes=[dict(name="ECOS Toilet Kleener, Natural Cedar", tier="natural",
                          note=("Same job on the same fixture. Avoids the chlorinated-hydantoin class entirely, "
                                "which is the point: the hydantoins are strong oxidisers and respiratory "
                                "irritants, and this is the swap for a household that wants the toilet clean "
                                "without them.")),
                     dict(name="Seventh Generation Toilet Bowl Cleaner, Emerald Cypress & Fir", tier="mass",
                          note=("Same job, similar price band, no chlorine chemistry. The alternative where a "
                                "household wants a mainstream brand rather than a natural one."))],
    ),
    dict(
        name="Arm & Hammer Extra Strength Carpet Odor Eliminator",
        brand="Arm & Hammer", cat="Floor & Carpet", safe=None,
        ings=["Sodium Bicarbonate", "Silica", "Fragrance"],
        slug="cleaning-products/40501130-ah-extra-strength-carpet-odor-eliminator.aspx",
        served="Arm & Hammer Extra Strength Carpet Odor Eliminator",
        cas=[("Sodium bicarbonate", "144-55-8", "Deodorizer"),
             ("Hydrated silica", "112926-00-8", "Flow agent")],
        frag=["18 components disclosed at or above 100 ppm, listed in full in the cited filing."],
        note=("A sprinkle-and-vacuum carpet deodorising powder: sodium bicarbonate, a silica flow agent, and "
              "fragrance. Recorded because the corpus's Floor & Carpet category was thin on exposure evidence "
              "and because the product is the clearest example of a category where the active ingredient is "
              "baking soda and the fragrance is the whole product. Entered ungraded. The mapping note: the "
              "filing's 'hydrated silica' is recorded against the registry's existing Silica key."),
        exposure=3,
        exposure_src=IDXBOX_CARPET,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for Arm & "
                        "Hammer carpet odour eliminator (the manufacturer filing, the brand site, a general web "
                        "search) and found none. IndexBox's US Carpet Cleaning Products page puts residential at "
                        "35 to 40 percent of product volume; a sprinkle-and-vacuum deodoriser is a fraction of "
                        "that. Estimate is the carpet-cleaning category base times a powder-deodoriser share, "
                        "rounded to one significant figure."),
        substitutes=[dict(name="Baking Soda (bulk)", tier="apothecary-bulk",
                          note=("Far lower price and the same active ingredient, with no fragrance and no silica "
                                "flow agent. This is a genuine same-job swap: sprinkle, leave, vacuum. It avoids "
                                "the entire fragrance class, which here is 18 disclosed components and the whole "
                                "reason the product exists."))],
    ),
]


def main():
    products = load("products.json")
    ingredients = load("ingredients.json")
    changelog = load("changelog.json")

    have = {p["name"] for p in products}
    added = []
    minted = []

    # 1. mint any missing ingredient keys (before the product-existence check, so a
    #    re-run can never leave a dangling reference)
    for rec in PRODUCTS:
        for key in rec["ings"]:
            if key not in ingredients:
                ingredients[key] = {
                    "s": f"{key}. Named on a Church & Dwight California SB-258 ingredient disclosure, read {TODAY}.",
                    "ev": "Low", "g": None, "gr": {}, "impacts": [],
                    "note": NEW_KEY_NOTE.format(date=TODAY),
                }
                minted.append(key)

    # 2. add products that are absent
    for rec in PRODUCTS:
        if rec["name"] in have:
            continue
        url = IDX + rec["slug"]
        cas_txt = "; ".join(f"{n} {c} ({f})" if c else f"{n} ({f})" for n, c, f in rec["cas"])
        src = (f"Church & Dwight product ingredient disclosure form (California Cleaning Product Right to Know "
               f"Act, SB-258), {url} (HTTP 200), read {TODAY}. The form's own PRODUCT NAME line reads "
               f"\"{rec['served']}\". Served page carries the complete 'Intentionally Added Ingredients' table. "
               f"Ingredients with CAS: {cas_txt}.")
        if rec["frag"]:
            src += (" Fragrance components disclosed at or above 100 ppm: " + "; ".join(rec["frag"]) +
                    ". Recorded in this prose only, not as ingredient keys, per the standing fragrance "
                    "discipline while the fragrance-components-as-ingredient-keys ruling is open.")
        else:
            src += " No fragrance is disclosed and none is listed."
        p = {
            "name": rec["name"], "brand": rec["brand"], "cat": rec["cat"], "safe": None,
            "ings": rec["ings"], "heritage": False,
            "source": src, "source_url": url, "note": rec["note"],
            "owner": "Church & Dwight", "tier": "mass", "tier_ev": "reported", "tier_src": CANDY,
            "tier_note": ("Church & Dwight markets OxiClean, Arm & Hammer, Kaboom and Xtra as national brands "
                          "sold through grocery, mass, drug and dollar channels; evidenced by Church & Dwight's "
                          "own consumer-brands page, which names OxiClean, Arm & Hammer, Kaboom, Xtra, Scrub "
                          "Free, Orange Glo and Clean Shower."),
            "substitutes": rec["substitutes"],
            "no_substitute_known": rec.get("no_substitute_known"),
            "no_substitute_note": rec.get("no_substitute_note"),
            "exposure": rec["exposure"], "exposure_ev": "extrapolated",
            "exposure_src": rec["exposure_src"], "exposure_basis": rec["exposure_basis"],
            "conc": None, "conc_src": None, "conc_ev": "untested",
            "grade_as_sold": None, "grade_as_sold_src": None,
            "strength_disclosure": "full", "disclosure_note": None,
            "added": TODAY, "owner_ev": "verified", "owner_src": CANDY, "updated": TODAY,
        }
        products.append(p)
        added.append(rec["name"])

    if not added and not minted:
        print("no change: nothing to add, nothing to mint (idempotent re-run)")
        return

    # 3. changelog entry, guarded on an actual change
    changelog.insert(0, {
        "date": TODAY,
        "text": (f"Spectrum harvest station 2 (Dolman {TODAY}): {len(added)} Church & Dwight household products "
                 f"added by exposure ({', '.join(added) if added else 'none'})"
                 + (f"; {len(minted)} new ungraded ingredient keys minted ({', '.join(minted)})" if minted else "")
                 + ". Source: Church & Dwight's own California SB-258 ingredient-disclosure index.")
    })

    dump("products.json", products, 1)
    dump("ingredients.json", ingredients, 1)
    dump("changelog.json", changelog, 2)
    print(f"added {len(added)} products: {added}")
    print(f"minted {len(minted)} ingredient keys: {minted}")


if __name__ == "__main__":
    main()
