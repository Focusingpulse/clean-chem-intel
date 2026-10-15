#!/usr/bin/env python3
"""Night-shift station 2 harvest, 2026-10-15 (Dolman).

Shelf: the Church & Dwight household shelf, remainder — ordered by EXPOSURE.

Route: the manufacturer's own California Cleaning Product Right to Know Act
(SB-258) per-product ingredient-disclosure index,
https://www.churchdwight.com/ingredient-disclosure/ (HTTP 200, 153,622 bytes,
requires a redirect-following client -- a bare fetch 301s). 169 of the 716
per-product links on that index are household-relevant (37 cleaning-products,
119 laundry-fabric-care, 8 dryer-sheets, 6 commercial-professional) and 25 of
them were already cited by the corpus, so this fire reads from the remainder.

Why this shelf, and the direction question the night template asks: the four
channel tiers are built, the KIK value-brand index is exhausted for household
products, and air care -- the largest remaining exposure gap -- is still
blocked on the open fragrance-components-as-ingredient-keys ruling rather than
on a route. So the remaining work is ABSENT HIGH-EXPOSURE STAPLES, and Church &
Dwight's household portfolio is exactly that: Arm & Hammer, OxiClean, Kaboom,
Xtra, Scrub Free, Orange Glo and Clean Shower are national mass-market brands at
mass price points. This is exposure-driven gap-filling, NOT a drift back to
premium brands. Every record here is a mainstream product a household is likely
to actually own.

Shelf selection this fire, by gap rather than by brand:
  - daily shower cleaner (the corpus carried three, all of them niche)
  - carpet powder deodoriser (the best-known one in the category was absent)
  - pet stain and odour remover (the corpus's carpet records are stain-only)
  - oxygen-blanch all-purpose and disinfectant sprays (OxiClean's own line)
  - laundry-adjacent fabric care the corpus had none of: a clothing refresher
    mist, a fabric rinse, and a laundry and home sanitizer

Held out, deliberately:
  - Scrub Free Mildew Stain Remover (material 40002295): the served form states
    in its own footer "*Product is not currently sold in the USA." Not entered.
  - Orange Glo 4-in-1 Monthly Polish - Hardwood Floor (material 42018221): a
    real, complete filing, but a monthly floor polish is a thin exposure band
    and its list carries three withheld identities (styrene acrylic copolymer,
    polyethylene emulsion, polypropylene emulsion) plus a 120-character silicone
    name, so it would have minted six marginal keys for one record. Left for a
    later fire with a reason on the record rather than silently skipped.
  - OxiClean All Purpose Cleaner - Diluted Cleaning Solution (material
    21-CK3708): the in-use form of the pod entered here, not the as-sold product.

Fragrance discipline: each filing discloses individual fragrance components at
or above 100 ppm. Per the standing discipline while the
fragrance-components-as-ingredient-keys ruling is open, the components are
recorded as the single 'Fragrance' key with the component list named in the
record's `source` prose only. No fragrance keys are minted.

Idempotent: a second run adds nothing and mints nothing.
"""
import json, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")
TODAY = "2026-10-15"
IDX = "https://www.churchdwight.com/ingredient-disclosure/"
CANDY = "https://churchdwight.com/our-brands/consumer-brands/"
IDXBOX_SURFACE = ("https://www.indexbox.io/store/"
                  "united-states-household-surface-cleaners-market-analysis-forecast-size-trends-and-insights/")
IDXBOX_LAUNDRY = ("https://www.indexbox.io/store/"
                  "united-states-laundry-home-products-market-analysis-forecast-size-trends-and-insights/")
IDXBOX_CARPET = ("https://www.indexbox.io/store/"
                 "united-states-carpet-cleaning-products-market-analysis-forecast-size-trends-and-insights/")
ASINSIGHT_DET = "https://www.asinsight.com/market-analysis/US/detergent"

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
    # products/ingredients/owners/changelog: no trailing newline at head.


PRODUCTS = [
    dict(
        name="Clean Shower Daily Shower Cleaner",
        brand="Clean Shower", cat="Bathroom", safe=None,
        ings=["Water", "Caprylyl/Capryl Glucoside", "Lauryl Glucoside", "EDTA", "Propylene Glycol",
              "Ethanolamine", "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride",
              "Dicapryl/Dicaprylyl Dimonium Chloride", "Ethanol", "Fragrance"],
        slug="cleaning-products/40002488-clean-shower-daily-shower-cleaner.aspx",
        served="Clean Shower\u2122 Daily Shower Cleaner",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("Caprylyl/capryl glucoside", "68515-73-1", "Surfactant"),
             ("Lauryl glucoside", "110615-47-9", "Surfactant"),
             ("EDTA", "60-00-4", "Chelating agent"),
             ("Propylene glycol", "57-55-6", "Process aid (on the US NTP Reproductive or Developmental Toxicants list)"),
             ("Ethanolamine", "141-43-5", "pH adjuster"),
             ("Alkyl C12-16 dimethylbenzyl ammonium chloride", "68424-85-1", "Surfactant (on the Canada PBTs list)"),
             ("Dicapryl/dicaprylyl dimonium chloride", "68424-95-3", "Surfactant"),
             ("Ethanol", "64-17-5", "Solvent")],
        frag=["Butylphenyl methylpropional 80-54-6 (EU Fragrance Allergens; EU CMRs)",
              "Hexamethylindanopyran 1222-05-5 (EU Fragrance Allergens; US EPA PBTs)",
              "Linalyl acetate 115-95-7 (EU Fragrance Allergens)",
              "Linalool 78-70-6 (EU Fragrance Allergens)",
              "Phenoxyethyl isobutyrate 103-60-6 (CA TACs)"],
        note=("A spray-and-leave daily shower cleaner: the household sprays it after the last shower and does "
              "not rinse. Recorded because it is the best-known product in its category and the corpus carried "
              "only three daily-shower cleaners, all of them niche brands. Two disclosure points a reader "
              "should see: it is a quaternary-ammonium product (two quats on the list, one of them on Canada's "
              "PBT list), and its fragrance block carries one EU CMR and one US EPA PBT. Entered ungraded: "
              "product grading is the Sifter lane. The brand string is 'Clean Shower' because that is the brand "
              "on the package; Church & Dwight owns it and names it on its own consumer-brands page."),
        exposure=4,
        exposure_src=IDXBOX_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for Clean "
                        "Shower (the manufacturer filing, the brand site, and a general web search) and found "
                        "none. IndexBox's US Household Surface Cleaners page states that approximately 95 "
                        "percent of US households use at least one surface cleaner product per month and that "
                        "specialised cleaners (bathroom, kitchen, glass, floor) are 30 to 35 percent of "
                        "category value with bathroom the largest sub-segment. Estimate is the bathroom "
                        "sub-segment base times a share for the spray-and-leave format, rounded to one "
                        "significant figure."),
        substitutes=[dict(name="ATTITUDE Daily Shower & Tile Cleaner, Citrus Zest", tier="natural",
                          note=("Same job, same shelf, similar price band, and a plant-based surfactant "
                                "formulation rather than a quat. Avoids the two quaternary-ammonium compounds "
                                "on this list, one of which is on Canada's PBT list.")),
                     dict(name="up&up Bathroom Disinfecting Cleaner, Unscented", tier="grocery",
                          note=("Lower price, same aisle, same daily-bathroom job. The fragrance-free member "
                                "of the category, so it avoids the whole fragrance class (five disclosed "
                                "components here, four of them EU fragrance allergens and one an EU CMR)."))],
    ),
    dict(
        name="Kaboom Shower, Tub & Tile Bathroom Cleaner - Heavy Duty",
        brand="Kaboom", cat="Bathroom", safe=None,
        ings=["Water", "Sulfamic Acid", "Lauramine Oxide", "Fragrance", "C6-12 Alcohol Ethoxylates"],
        slug="cleaning-products/40002493-Hardwater-Trigger-Spray.aspx",
        served="Kaboom\u2122 Shower, Tub & Tile Bathroom Cleaner - Heavy Duty",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("Sulfamic acid", "5329-14-6", "pH adjuster"),
             ("Lauramine oxide", "1643-20-5", "Surfactant"),
             ("C6-12 alcohol ethoxylates", "68439-45-2", "Surfactant")],
        frag=["d-Limonene 5989-27-5 (EU Fragrance Allergens)",
              "2,6-Dimethyl-7-octen-2-ol 18479-58-8",
              "Benzeneethanol 60-12-8",
              "Citronellyl nitrile 51566-62-2",
              "Butylphenyl methylpropional 80-54-6 (EU CMRs)",
              "Hexamethylindanopyran 1222-05-5 (US EPA PBTs)",
              "Orange oil 68916-04-1 / 8008-57-9 (EU Fragrance Allergens)"],
        note=("An acid-based heavy-duty shower, tub and tile cleaner, the mainstream product for hard-water "
              "and soap-scum removal. Recorded because the corpus carried Kaboom only as a foam spray and a "
              "scrub-free cleaner and had no acid-descaler in the bathroom category. The index slug for this "
              "filing is 'Hardwater-Trigger-Spray', which is not the product's own name; the form's PRODUCT "
              "NAME line governs and reads 'Kaboom Shower, Tub & Tile Bathroom Cleaner - Heavy Duty' "
              "(material 40002493). Entered ungraded."),
        exposure=3,
        exposure_src=IDXBOX_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for Kaboom "
                        "Shower, Tub & Tile Heavy Duty (the manufacturer filing, the brand site, a general web "
                        "search) and found none. IndexBox's US Household Surface Cleaners page puts bathroom "
                        "cleaners as the largest specialised sub-segment at 30 to 35 percent of category value "
                        "against approximately 95 percent of US households using a surface cleaner monthly. "
                        "Estimate is the bathroom base times a share for the acid-descaler format, rounded to "
                        "one significant figure, and set below the corpus's mass-market bathroom records "
                        "because a descaler is bought for a specific job rather than routinely."),
        substitutes=[dict(name="Great Value Lemon Scent Foaming Bathroom Cleaner", tier="grocery",
                          note=("Lower price, same aisle, same tub-and-tile job. A non-acid formulation, so it "
                                "avoids sulfamic acid (an irritant acid, H315 and H319) for a household "
                                "cleaning around children or anyone with a sensitivity, at the cost of doing "
                                "less on hard-water scale.")),
                     dict(name="ATTITUDE Daily Shower & Tile Cleaner, Citrus Zest", tier="natural",
                          note=("Same shelf and a plant-based formulation. Avoids both the strong acid and the "
                                "fragrance class (seven disclosed components here, three of them EU fragrance "
                                "allergens and one an EU CMR)."))],
    ),
    dict(
        name="OxiClean Multipurpose Daily Clean",
        brand="OxiClean", cat="All-Purpose", safe=None,
        ings=["Water", "Hydrogen Peroxide", "C10-12 Alcohol Ethoxylates", "Alkylbenzene Sulfonic Acid",
              "Trisodium MGDA", "Citric Acid", "Dipropylene Glycol Butyl Ether", "Fragrance"],
        slug="cleaning-products/42013688-Multipurpose-Daily-Clean.aspx",
        served="OxiClean\u2122 Multipurpose Daily Clean",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("Hydrogen peroxide", "7722-84-1", "Cleaning agent"),
             ("C10-12 alcohol ethoxylates", "66455-15-0", "Surfactant"),
             ("Alkylbenzene sulfonic acid", "68584-22-5", "Surfactant"),
             ("Trisodium dicarboxymethyl alaninate", "164462-16-2", "Chelating agent"),
             ("Citric acid", "77-92-9", "pH balance"),
             ("Dipropylene glycol butyl ether", "29911-28-2", "Solvent")],
        frag=["Tricyclodecenyl propionate 17511-60-3",
              "2,6-Dimethyl-7-octen-2-ol 18479-58-8"],
        note=("A hydrogen-peroxide all-purpose spray, the daily-wipe member of OxiClean's cleaner line. "
              "Recorded because a peroxide all-purpose spray is a different chemistry from the quat and "
              "quat-plus-bleach all-purpose cleaners the corpus already carries, and because the household "
              "choosing peroxide is usually choosing it to avoid bleach. Entered ungraded. One mapping note: "
              "the filing's chelating agent is printed as 'Trisodium dicarboxymethyl alaninate', which is the "
              "trisodium salt of methylglycinediacetic acid, so it is recorded under the registry's existing "
              "'Trisodium MGDA' key rather than minting a synonym."),
        exposure=4,
        exposure_src=IDXBOX_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for OxiClean "
                        "Multipurpose Daily Clean (the manufacturer filing, the brand site, a general web "
                        "search) and found none. IndexBox's US Household Surface Cleaners page states that "
                        "approximately 95 percent of US households use at least one surface cleaner product "
                        "per month and that all-purpose cleaners are the largest segment at an estimated 30 to "
                        "35 percent of value. Estimate is that all-purpose base times a share for the peroxide "
                        "format, rounded to one significant figure."),
        substitutes=[dict(name="up&up Multi-Purpose Cleaner, Free & Clear", tier="grocery",
                          note=("Lower price, same aisle, same wipe-every-surface job, and fragrance-free. "
                                "Avoids the fragrance class (two disclosed components here).")),
                     dict(name="Better Life What-Ever All-Purpose Cleaner (Unscented)", tier="natural",
                          note=("Same job, plant-based surfactants, no fragrance and no peroxide, for a "
                                "household that wants neither the oxidiser nor the scent."))],
    ),
    dict(
        name="OxiClean Multipurpose 3-in-1 Deep Clean",
        brand="OxiClean", cat="Disinfectant", safe=None,
        ings=["Water", "Diethylene Glycol Monobutyl Ether", "Tetrasodium EDTA", "Undeceth-7",
              "Alkyl C12-18 Dimethylbenzyl Ammonium Chloride",
              "Alkyl C12-18 Dimethyl Ethylbenzyl Ammonium Chloride", "Sodium Metasilicate", "Fragrance"],
        slug="cleaning-products/42013706-Multipurpose-3in1-Deep-Clean.aspx",
        served="OxiClean\u2122 Multipurpose 3-in-1 Deep Clean",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("Butoxydiglycol", "112-34-5", "Solvent (on the CA Non-Cancer Hazards list)"),
             ("Tetrasodium EDTA", "64-02-8", "Chelating agent"),
             ("Undeceth-7", "34398-01-1", "Surfactant"),
             ("Alkyl C12-18 dimethylbenzyl ammonium chloride", "68391-01-5", "Biocide (on the Canada PBTs list)"),
             ("Alkyl C12-18 dimethyl ethylbenzyl ammonium chloride", "68956-79-6", "Biocide"),
             ("Sodium metasilicate", "6834-92-0", "Cleaning agent")],
        frag=["Limonene 5989-27-5 (EU Fragrance Allergens)",
              "Hexamethylindanopyran 1222-05-5 (US EPA PBTs)",
              "Myrcene 123-35-3 (CA Prop 65; IARC Carcinogens)"],
        note=("A quaternary-ammonium disinfecting all-purpose cleaner with a silicate builder. Recorded "
              "because it is the disinfecting member of OxiClean's cleaner line and because its two biocides "
              "are the C12-18 chain-distribution quats, which the registry carries as their own keys for "
              "traceability. Entered ungraded. One mapping note: the filing prints 'Butoxydiglycol' against "
              "CAS 112-34-5, which is the substance the registry already carries as 'Diethylene Glycol "
              "Monobutyl Ether', so the CAS governs and the existing key is used."),
        exposure=3,
        exposure_src=IDXBOX_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for OxiClean "
                        "Multipurpose 3-in-1 Deep Clean (the manufacturer filing, the brand site, a general web "
                        "search) and found none. IndexBox's US Household Surface Cleaners page puts "
                        "approximately 95 percent of US households using a surface cleaner monthly and "
                        "specialised cleaners at 30 to 35 percent of category value. Estimate is that base "
                        "times a share for a disinfecting spray, rounded to one significant figure, and set "
                        "below the corpus's plain all-purpose records because a disinfectant is a second "
                        "bottle in most homes rather than the only one."),
        substitutes=[dict(name="Seventh Generation Disinfecting Multi-Surface Cleaner, Lemongrass Citrus",
                          tier="mass",
                          note=("Same shelf, same price band, same disinfecting job. A thymol-based "
                                "disinfectant rather than a quaternary ammonium one, so it avoids both biocides "
                                "on this list, one of which is on Canada's PBT list, and the metasilicate.")),
                     dict(name="up&up Lemon All-Purpose Disinfecting Cleaner without Bleach", tier="grocery",
                          note=("Lower price, same aisle, same disinfecting wipe-down. A store brand, so this "
                                "is the price substitute rather than the quat-avoiding one; it carries its own "
                                "disinfecting active and its own fragrance."))],
    ),
    dict(
        name="OxiClean All Purpose Cleaner - Cleaning Pod",
        brand="OxiClean", cat="All-Purpose", safe=None,
        ings=["Water", "Secondary Alcohol Ethoxylate", "Diethylene Glycol Monohexyl Ether",
              "Triisopropanolamine", "Phenoxyethanol", "Polyvinyl Alcohol", "Fragrance",
              "Denatonium Benzoate", "Colorant", "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride",
              "Octyl Decyl Dimethyl Ammonium Chloride", "Didecyldimethylammonium Chloride", "Ethanol"],
        slug="cleaning-products/21CK3708-Oxiclean-All-Purpose-Cleaner-Cleaning-Pod.aspx",
        served="Oxiclean\u2122 All Purpose Cleaner - Cleaning Pod",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("C12-14-secondary alcohol ethoxylate", "84133-50-6", "Surfactant"),
             ("Diethylene glycol monohexyl ether", "112-59-4", "Solvent (on the CA TACs list)"),
             ("Triisopropanolamine", "122-20-3", "Amine"),
             ("Ethylene glycol phenyl ether", "122-99-6", "Solvent (on the CA TACs list)"),
             ("PVA film", "Not available", "Water-soluble film"),
             ("Denatonium benzoate", "3734-33-6", "Bittering agent"),
             ("Yellow colorant", "Not available", "Colorant (flagged IRIS Neurotoxins, IARC Carcinogens, ATSDR, CA Prop 65)"),
             ("C12-16-alkyl dimethyl benzyl ammonium chloride", "68424-85-1", "Preservative"),
             ("Octyl decyl dimethyl ammonium chloride", "32426-11-2", "Preservative"),
             ("Didecyl dimethyl ammonium chloride", "7173-51-5", "Preservative"),
             ("Ethyl alcohol", "64-17-5", "Preservative (flagged IARC Carcinogens, US NTP Carcinogens, CA Prop 65)"),
             ("Didecyl dimethyl ammonium chloride", "5538-94-3", "Preservative")],
        frag=["26 components listed at or above 100 ppm, including 2-t-butylcyclohexyl acetate 88-41-5, "
              "decanal 112-31-2, octanal 124-13-0, nonanal 124-19-6, citrathal 147060-73-9, citronellal "
              "106-23-0, citronellol 106-22-9 (EU Fragrance Allergen), 2,6-dimethyl-7-octen-2-ol 18479-58-8, "
              "dimethyl octenone 2550-11-0, dipropylene glycol 25265-71-8, eucalyptol 470-82-6, fenchol "
              "1632-73-1, fruitate 80623-07-0 / 80657-64-3, methylbenzyl acetate 93-92-5, geraniol 106-24-1 "
              "(EU Fragrance Allergen), geranyl acetate 105-87-3, methyldihydrojasmonate 24851-98-7, "
              "beta-ionone 79-77-6, jasmacyclene 2500-83-6 / 5413-60-5, homogeranyl nitrile 61792-11-8, "
              "2-ethoxynaphthalene 93-18-5, orange terpenes 68647-72-3, gamma-undecalactone 104-67-6, peonile "
              "10461-98-0, tetrahydrolinalool 78-69-3 and d-limonene 5989-27-5 (IARC Carcinogens; EU "
              "Fragrance Allergen). Full list in the cited filing."],
        note=("A concentrated all-purpose cleaner in a water-soluble pod: the household drops the pod in "
              "water and uses the diluted solution. Recorded because it is a new OxiClean line the corpus did "
              "not carry and because the pod format adds two things a reader will not expect in a cleaner, a "
              "polyvinyl-alcohol film and a bittering agent added to stop anyone drinking it. It is also the "
              "densest preservative stack in this fire: four quaternary-ammonium preservatives plus ethanol. "
              "Entered ungraded. Two mapping notes: the filing prints 'Ethylene glycol phenyl ether' against "
              "CAS 122-99-6, which is the same substance as the registry's existing 'Phenoxyethanol' key, so "
              "the CAS governs; and the filing lists 'Didecyl dimethyl ammonium chloride' twice, under CAS "
              "7173-51-5 and CAS 5538-94-3, so both lines are recorded against the one existing key with both "
              "CAS numbers stated here rather than minting a second key for the same name. The sibling filing "
              "for the in-use form, 'OxiClean All Purpose Cleaner - Diluted Cleaning Solution' (material "
              "21-CK3708), was read and not entered, because the pod is the as-sold product."),
        exposure=3,
        exposure_src=IDXBOX_SURFACE,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for the "
                        "OxiClean All Purpose Cleaner pod (the manufacturer filing, the brand site, a general "
                        "web search) and found none. IndexBox's US Household Surface Cleaners page states that "
                        "approximately 95 percent of US households use at least one surface cleaner product "
                        "per month and that all-purpose cleaners are the largest segment at an estimated 30 to "
                        "35 percent of category value. Estimate is that all-purpose base times a share for a "
                        "single new-format line, rounded to one significant figure."),
        substitutes=[dict(name="up&up Multi-Purpose Cleaner, Free & Clear", tier="grocery",
                          note=("Lower price, same aisle, same wipe-every-surface job. A ready-to-use bottle "
                                "rather than a pod, so it avoids the polyvinyl-alcohol film, the bittering "
                                "agent and the fragrance class (26 disclosed components here).")),
                     dict(name="Branch Basics The Concentrate", tier="natural",
                          note=("Same concentrate-and-dilute idea, and the closest genuine same-job swap for a "
                                "household that wants the concentrate format. Plant-based, fragrance-free, and "
                                "it carries no quaternary-ammonium preservatives."))],
    ),
    dict(
        name="OxiClean Carpet & Area Rug Pet Stain & Odor Remover",
        brand="OxiClean", cat="Floor & Carpet", safe=None,
        ings=["Water", "Hydrogen Peroxide", "SODIUM C10-16 ALKYL SULFATE", "C10-12 Alcohol Ethoxylates",
              "Pentetic Acid", "Fragrance"],
        slug="cleaning-products/42000278-oxiclean-carpet-and-area-rug-pet-stain-and-odor-remover.aspx",
        served="OxiClean\u2122 Carpet & Area Rug Pet Stain & Odor Remover",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("Hydrogen peroxide", "7722-84-1", "Cleaning agent"),
             ("Sodium lauryl sulfate", "68585-47-7", "Surfactant"),
             ("C10-12 alcohol ethoxylates", "66455-15-0", "Surfactant"),
             ("Pentetic acid", "67-43-6", "Chelating agent")],
        frag=["3a,4,5,6,7,7a-Hexahydro-4,7-methano-1H-inden-5(or 6)-yl acetate 54830-99-8",
              "4-tert-Butylcyclohexyl acetate 32210-23-4",
              "Alpha-isomethyl ionone 127-51-5 (EU Fragrance Allergens)",
              "Benzyl acetate 140-11-4",
              "Butylphenyl methylpropional 80-54-6 (EU Fragrance Allergens; EU CMRs)",
              "Dipropylene glycol 25265-71-8",
              "Hexamethylindanopyran 1222-05-5 (EU Fragrance Allergens; US EPA PBTs)",
              "Hexyl cinnamal 101-86-0 (EU Fragrance Allergens)",
              "Hydroxycitronellal 107-75-5 (EU Fragrance Allergens)",
              "Isopropyl myristate 110-27-0",
              "d-Limonene 5989-27-5 (EU Fragrance Allergens)"],
        note=("A hydrogen-peroxide carpet and area-rug spot remover formulated for pet stains and odour. "
              "Recorded because the corpus's carpet records were stain-only and pet accidents are the single "
              "most common reason a household buys one. Entered ungraded. Two notes: the filing prints the "
              "name 'Sodium lauryl sulfate' against CAS 68585-47-7, which is the C10-16 alkyl sulfate the "
              "registry already carries under that CAS, so the CAS governs and the existing key is used rather "
              "than the lauryl-sulfate key (CAS 151-21-3); and the filing's 'Pentetic Acid' is the free-acid "
              "form of DTPA and is a distinct substance from the registry's existing Pentasodium DTPA, so it "
              "enters as its own key. The filing names a formula twin, 'Arm & Hammer plus OxiClean Stain & "
              "Odor Eliminator for Carpet' (material 40500142), whose intentionally-added list and fragrance "
              "list are identical line for line; that twin was read and deliberately not entered as a second "
              "record because the formula is the same."),
        exposure=2,
        exposure_src=IDXBOX_CARPET,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for the "
                        "OxiClean pet carpet spot remover (the manufacturer filing, the brand site, a general "
                        "web search) and found none. IndexBox's US Carpet Cleaning Products page puts "
                        "residential cleaning, including DIY carpet cleaning and retail purchases, at an "
                        "estimated 35 to 40 percent of total product volume, with consumers favouring spot and "
                        "stain removers. Estimate is that residential base times a share for the pet-stain "
                        "segment, rounded to one significant figure, and set below the corpus's OxiClean "
                        "general carpet stain remover record because the pet version is the narrower buy."),
        substitutes=[dict(name="Folex Instant Carpet Spot Remover", tier="mass",
                          note=("Same shelf and price band, same carpet spot job, and a fragrance-free "
                                "formulation. Avoids the whole fragrance class (11 disclosed components here, "
                                "five of them EU fragrance allergens and one an EU CMR).")),
                     dict(name="Baking Soda (bulk)", tier="apothecary-bulk",
                          note=("Far lower price and the honest first move on a fresh pet accident: blot, "
                                "then a bicarbonate paste. No fragrance and no peroxide, at the cost of doing "
                                "much less on an old set stain."))],
    ),
    dict(
        name="Arm & Hammer Pet Fresh Carpet Odor Eliminator",
        brand="Arm & Hammer", cat="Floor & Carpet", safe=None,
        ings=["Sodium Bicarbonate", "Silica", "Fragrance"],
        slug="cleaning-products/40002783-ah-pet-fresh-carpet-odor-eliminator.aspx",
        served="Arm & Hammer\u2122 Pet Fresh Carpet Odor Eliminator",
        cas=[("Sodium bicarbonate", "144-55-8", "Deodorizer"),
             ("Hydrated silica", "112926-00-8", "Flow agent")],
        frag=["Benzyl acetate 140-11-4", "Benzyl alcohol 100-51-6 (EU Fragrance Allergen)",
              "Benzyl benzoate 120-51-4 (EU Fragrance Allergen)",
              "Benzyl salicylate 118-58-1 (EU Fragrance Allergen)",
              "Dipropylene glycol 25265-71-8",
              "Hexamethylindanopyran 1222-05-5 (EU Fragrance Allergen; US EPA PBTs)",
              "Tricyclodecenyl propionate 68912-13-0 / 17511-60-3",
              "Isopropyl myristate 110-27-0", "Methyl ionone 1335-46-2",
              "Butylphenyl methylpropional 80-54-6 (EU Fragrance Allergen; EU CMRs)",
              "Linalool 78-70-6 (EU Fragrance Allergen)",
              "Phenethyl alcohol 60-12-8",
              "Limonene 5989-27-5 / 138-86-3 (EU Fragrance Allergen)",
              "alpha-Isomethyl ionone 127-51-5 (EU Fragrance Allergen)",
              "Isoeugenol 97-54-1 (IARC Carcinogens)",
              "Phenoxyethanol 122-99-6 (CA TACs)"],
        note=("A sprinkle-and-vacuum carpet deodorising powder, the pet version of the best-known product in "
              "its category. Recorded because it is a three-line formula that any household can read in full "
              "in five seconds, and because that is the whole point: the entire product is baking soda, a "
              "flow agent, and 16 fragrance components. It is the clearest example in the corpus of a product "
              "whose ingredient list is honest about being mostly scent. Entered ungraded. The filing's "
              "'Hydrated silica' is recorded under the registry's existing 'Silica' key, per the standing "
              "mapping rule; the flow agent is a dust-inhalation concern in the bag, not on the carpet."),
        exposure=4,
        exposure_src=IDXBOX_CARPET,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for Arm & "
                        "Hammer Pet Fresh (the manufacturer filing, the brand site, a general web search) and "
                        "found none. IndexBox's US Carpet Cleaning Products page puts residential cleaning at "
                        "an estimated 35 to 40 percent of total product volume. Estimate is that residential "
                        "base times a share for the sprinkle-powder format, rounded to one significant figure, "
                        "and set at the top of this fire's carpet band because a carpet deodorising powder is "
                        "bought by households with pets and by households without them, and because the corpus "
                        "already carries its sibling, Arm & Hammer Extra Strength Carpet Odor Eliminator."),
        substitutes=[dict(name="Baking Soda (bulk)", tier="apothecary-bulk",
                          note=("The same active ingredient, far lower price, and no fragrance at all. This is "
                                "a genuine one-for-one swap: sprinkle, leave, vacuum. It avoids the entire "
                                "fragrance class, which here is 16 disclosed components including one EU CMR, "
                                "one IARC-listed component and one US EPA PBT.")),
                     dict(name="Arm & Hammer Extra Strength Carpet Odor Eliminator", tier="mass",
                          note=("Same brand, same shelf, same price band, same sprinkle-and-vacuum job. The "
                                "alternative for a household that wants a different scent rather than no "
                                "scent; it carries its own fragrance, so it does not avoid the fragrance "
                                "class."))],
    ),
    dict(
        name="OxiClean Laundry & Home Sanitizer",
        brand="OxiClean", cat="Laundry", safe=None,
        ings=["Sodium Carbonate", "Sodium Carbonate Peroxide", "TAED", "C12-15 Alcohols Ethoxylated",
              "Acrylic Acid Homopolymer", "Fragrance"],
        slug="laundry-fabric-care/42013603 -Laundry-Home-Sanitizer.aspx",
        served="OxiClean\u2122 Laundry & Home Sanitizer",
        cas=[("Sodium carbonate", "497-19-8", "Builder"),
             ("Sodium carbonate peroxide", "15630-89-4", "Oxygen bleach"),
             ("TAED", "10543-57-4", "Activating agent"),
             ("C12-15 alcohols ethoxylated", "68131-39-5", "Surfactant"),
             ("Acrylic acid homopolymer", "68479-09-4", "Dispersing agent")],
        frag=["Hexamethylindanopyran 1222-05-5 (US EPA PBTs)"],
        note=("A powder sanitiser for laundry and hard surfaces, built on sodium percarbonate with TAED as the "
              "bleach activator. Recorded because it is the oxygen-sanitiser member of the shelf the corpus "
              "already carries heavily as detergent and stain remover, and because TAED is the ingredient "
              "that makes a percarbonate work at low wash temperatures, which is the thing a household "
              "choosing a cold wash actually needs to know. Entered ungraded. One note on the citation: the "
              "index link for this filing carries a space in its path, "
              "'/laundry-fabric-care/42013603 -Laundry-Home-Sanitizer.aspx'; the served form returns HTTP 200 "
              "at the encoded form of that exact path."),
        exposure=2,
        exposure_src=IDXBOX_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for OxiClean "
                        "Laundry & Home Sanitizer (the manufacturer filing, the brand site, a general web "
                        "search) and found none. IndexBox's US Laundry & Home Products page states household "
                        "penetration above 98 percent. Estimate is that base times a share for the additive "
                        "sanitiser segment, rounded to one significant figure, and set low because a sanitiser "
                        "is an addition to a wash rather than the wash itself."),
        substitutes=[dict(name="OxiClean Triple Action Versatile Stain Remover, Free", tier="mass",
                          note=("Same brand, same shelf, same price band, and the fragrance-free member of the "
                                "same percarbonate family. Avoids the fragrance class entirely; note it is a "
                                "stain remover rather than a registered sanitiser, so it does the wash job "
                                "without the sanitising claim.")),
                     dict(name="Lysol Laundry Sanitizer, Free & Clear", tier="mass",
                          note=("Same shelf and same job, a laundry sanitiser, and fragrance-free. The genuine "
                                "same-job swap for a household that wants the sanitising step without the "
                                "scent."))],
    ),
    dict(
        name="Arm & Hammer Odor Blasters Fabric Rinse Fresh Burst",
        brand="Arm & Hammer", cat="Laundry", safe=None,
        ings=["Water", "Hexyl Ethoxylate", "Dipropylene Glycol", "C10-16 Pareth", "Fragrance",
              "Sodium Xylenesulfonate", "Sodium Bicarbonate", "Tromethamine", "Pentasodium DTPA",
              "Citric Acid", "Sodium Sulfate", "Benzisothiazolinone", "Methylisothiazolinone"],
        slug="laundry-fabric-care/42018468-Odor-Blasters-Fabric-Rinse-Fresh-Burst.aspx",
        served="Arm & Hammer\u2122 Odor Blasters\u2122 Fabric Rinse Fresh Burst",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("Hexyl ethoxylate", "31726-34-8", "Surfactant"),
             ("Dipropylene glycol", "25265-71-8", "Solvent"),
             ("C10-16 alketh", "68131-39-5 / 68002-97-1 / 68551-12-2", "Surfactant"),
             ("Sodium xylene sulfonate", "1300-72-7", "Solubilizer"),
             ("Sodium bicarbonate", "144-55-8", "pH adjuster"),
             ("Tromethamine", "77-86-1", "pH adjuster"),
             ("Pentasodium DTPA", "140-01-2", "Chelating agent (on the EU CMRs list)"),
             ("Citric acid", "77-92-9", "pH adjuster"),
             ("Sodium sulfate", "7757-82-6", "Solubilizer (on the CA Non-Cancer Hazards list)"),
             ("Benzisothiazolinone", "2634-33-5", "Preservative"),
             ("Methylisothiazolinone", "2682-20-4", "Preservative")],
        frag=["21 components listed in the fragrance table, including hexyl acetate 142-92-7, 2-t-butylcyclohexyl "
              "acetate 88-41-5, amyl salicylate 2050-08-0 (EU Fragrance Allergen), benzyl acetate 140-11-4, "
              "cyclamen aldehyde 103-95-7, 2,6-dimethyl-7-octen-2-ol 18479-58-8, methyldihydrojasmonate "
              "24851-98-7, hexyl cinnamal 101-86-0 (EU Fragrance Allergen), hexyl salicylate 6259-76-3, "
              "tetramethyl acetyloctahydronaphthalenes 54464-57-2 (EU Fragrance Allergen), verdyl acetate "
              "2500-83-6 / 5413-60-5, 1-(3-methyl-benzofuranyl)-ethanone 23911-56-0, orange terpenes "
              "68647-72-3, 2-acetonaphthone 93-08-3, gamma-undecalactone 104-67-6, PEG-40 hydrogenated castor "
              "oil 61788-85-0, 2-cyclohexylidene-2-phenylacetonitrile 10461-98-0, polysorbate 20 9005-64-5, "
              "2,4-dimethyl-3-cyclohexene carboxaldehyde 68039-49-6, methyl dihydroxy-dimethylbenzoate "
              "4707-47-5 and 2-methoxynaphthalene 93-04-9. Two of those lines, PEG-40 hydrogenated castor oil "
              "and polysorbate 20, are solubilisers rather than odorants and appear in the fragrance table "
              "because they carry the fragrance."],
        note=("A rinse-cycle additive that removes odour rather than softening fabric. Recorded because the "
              "corpus had no fabric-rinse product at all and because the rinse step is where most of the "
              "scent in a load comes from. The disclosed list is worth reading: the fragrance table is 21 "
              "lines against a 13-line formula, so more of the product by ingredient count is scent than "
              "cleaning. Entered ungraded. Two mapping notes: the filing's 'C10-16 alketh could include' line "
              "names the same three aliases the registry already carries under 'C10-16 Pareth'; and 'Sodium "
              "xylene sulfonate' is recorded under the registry's existing 'Sodium Xylenesulfonate' key, the "
              "canonical spelling merged on 2026-10-10."),
        exposure=2,
        exposure_src=IDXBOX_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for Arm & "
                        "Hammer Odor Blasters Fabric Rinse (the manufacturer filing, the brand site, a "
                        "general web search) and found none. IndexBox's US Laundry & Home Products page "
                        "states household penetration above 98 percent. Estimate is that base times a share "
                        "for the rinse-additive segment, rounded to one significant figure, and set low "
                        "because a fabric rinse is an addition to a wash rather than the wash itself."),
        substitutes=[dict(name="Distilled White Vinegar (5%)", tier="apothecary-bulk",
                          note=("The traditional fragrance-free rinse additive, at a fraction of the price. "
                                "It avoids the entire fragrance class, which here is 21 disclosed lines, plus "
                                "both isothiazolinone preservatives (benzisothiazolinone and "
                                "methylisothiazolinone), which are among the more common sensitisers on the "
                                "shelf.")),
                     dict(name="Downy Ultra Free & Gentle Liquid Fabric Conditioner", tier="mass",
                          note=("Same shelf, same price band, same rinse step, and the fragrance-free member "
                                "of the fabric-conditioner family. Avoids the fragrance class and the "
                                "preservatives; note it conditions rather than deodorises, so it is the "
                                "same-step swap rather than the same-function one."))],
    ),
    dict(
        name="Arm & Hammer plus OxiClean Liquid Laundry Detergent - Fresh Scent",
        brand="Arm & Hammer", cat="Laundry", safe=None,
        ings=["Water", "C10-16 Pareth", "Sodium Laureth Sulfate", "Sodium Chloride", "Fragrance",
              "Sodium Bicarbonate", "Sodium (C10-16) Alkylbenzenesulfonate", "Acrylic Acid Homopolymer",
              "C12-13 Alcohols Ethoxylated", "Calcium Chloride", "Disodium Distyrylbiphenyl Disulfonate",
              "Pentasodium DTPA", "Tromethamine", "Amylase Enzyme", "Protease Enzyme",
              "Benzisothiazolinone", "Methylisothiazolinone", "Polyoxyalkylene Substituted Chromophore"],
        slug="laundry-fabric-care/42018176-Plus-Oxiclean-Liquid-Laundry-Detergent-Fresh-Scent.aspx",
        served="Arm & Hammer\u2122 plus OxiClean\u2122 Liquid Laundry Detergent - Fresh Scent",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("C10-16 alketh", "68131-39-5 / 68002-97-1 / 68551-12-2", "Surfactant"),
             ("Sodium laureth sulfate", "68585-34-2", "Surfactant"),
             ("Sodium chloride", "7647-14-5", "Viscosity agent"),
             ("Sodium bicarbonate", "144-55-8", "pH adjuster"),
             ("Sodium C10-16 alkylbenzenesulfonate", "68081-81-2", "Surfactant"),
             ("Acrylic acid homopolymer", "66019-18-9", "Dispersing agent"),
             ("C12-13 alcohols ethoxylated", "66455-14-9", "Surfactant"),
             ("Calcium chloride", "10035-04-8", "Enzyme stabilizer"),
             ("Disodium distyrylbiphenyl disulfonate", "27344-41-8", "Optical brightener"),
             ("Pentasodium DTPA", "140-01-2", "Chelating agent"),
             ("Tromethamine", "77-86-1", "Enzyme stabilizer"),
             ("Amylase enzyme", "9000-90-2", "Enzyme (EU Respiratory Sensitizer)"),
             ("Protease enzyme", "9014-01-1", "Enzyme (EU Respiratory Sensitizer)"),
             ("Benzisothiazolinone", "2634-33-5", "Preservative"),
             ("Methylisothiazolinone", "2682-20-4", "Preservative"),
             ("Polyoxyalkylene substituted chromophore (blue) or modified anthraquinone", "Not available", "Colorant")],
        frag=["27 components listed at or above 100 ppm, including 2,6-dimethyl-7-octen-2-ol 18479-58-8, "
              "propylene glycol 57-55-6, dipropylene glycol 25265-71-8, hexamethylindanopyran 1222-05-5 (EU "
              "Fragrance Allergen; US EPA PBTs), hexyl cinnamal 101-86-0 (EU Fragrance Allergen), tetramethyl "
              "acetyloctahydronaphthalenes 54464-57-2 (EU Fragrance Allergen), terpineol 8000-41-7 (EU "
              "Fragrance Allergen), verdyl acetate 5413-60-5, cyclamen aldehyde 103-95-7, tricyclodecenyl "
              "propionate 68912-13-0, benzyl salicylate 118-58-1 (EU Fragrance Allergen), orange oil "
              "8008-57-9 (EU Fragrance Allergen), 2-methoxynaphthalene 93-04-9, isoamyl salicylate 87-20-7, "
              "2-t-butylcyclohexyl acetate 88-41-5, geraniol 106-24-1 (EU Fragrance Allergen), decanal "
              "112-31-2, (Z)-3-methyl-5-phenylpent-2-enenitrile 53243-59-7, isobornyl acetate 125-12-2, lemon "
              "oil terpenes 68917-33-9, benzyl acetate 140-11-4, acetyl cedrene 32388-55-9, nerol 106-25-2, "
              "amyl salicylate 2050-08-0 (EU Fragrance Allergen) and limonene 5989-27-5 (EU Fragrance "
              "Allergen). Full list in the cited filing."],
        note=("The mainline 'Fresh Scent' member of the Arm & Hammer plus OxiClean liquid detergent line. "
              "Recorded because the corpus carried the Odor Blasters variant of the same line but not the "
              "plain Fresh Scent bottle, which is the one a household is most likely to have bought. Entered "
              "ungraded. It is a full modern detergent: three surfactants, an optical brightener, a chelant, "
              "two enzymes flagged as EU respiratory sensitisers in the filing's own designated-list column, "
              "and two isothiazolinone preservatives. Its fragrance table is 27 lines, so the fragrance-free "
              "substitute below is the meaningful swap for a household reacting to scent."),
        exposure=8,
        exposure_src=ASINSIGHT_DET,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for the Arm & "
                        "Hammer plus OxiClean Fresh Scent liquid (the manufacturer filing, the brand site, a "
                        "general web search) and found none. IndexBox's US Laundry & Home Products page states "
                        "household penetration above 98 percent; asinsight's July 2026 US Amazon detergent "
                        "analysis ranks the Arm & Hammer plus OxiClean line in the top ten at roughly 50,000 "
                        "to 100,000 monthly units and puts Church & Dwight among the top three brands by "
                        "top-10 unit volume. Estimate is category penetration times a mid-tier brand share, "
                        "rounded to one significant figure, and set at the same band as the corpus's existing "
                        "Arm & Hammer liquid detergent record so the two read consistently."),
        substitutes=[dict(name="all free clear Original Concentrated Liquid Laundry Detergent", tier="mass",
                          note=("Same price band, same shelf, same mainstream liquid-detergent job. Avoids the "
                                "fragrance class entirely (27 disclosed components here, eight of them EU "
                                "fragrance allergens) and the optical brightener.")),
                     dict(name="Xtra Liquid Laundry Detergent, Tropical Passion", tier="mass",
                          note=("Lower price, same aisle, same wash. The alternative for a household watching "
                                "the price rather than the ingredient list; it carries its own fragrance, so it "
                                "does not avoid the fragrance class."))],
    ),
    dict(
        name="Arm & Hammer Care & Rewear Clothing Refresher Mist - Original Fresh",
        brand="Arm & Hammer", cat="Laundry", safe=None,
        ings=["Water", "Ethanol", "PEG-12 Dimethicone", "Dipropylene Glycol", "Alcohols, C9-11, ethoxylated",
              "Fragrance", "Phenoxyethanol", "Caprylyl Glycol", "Sodium Benzoate"],
        slug="laundry-fabric-care/42012561-Care-Rewear-Clothing-Refresher-Mist-Original.aspx",
        served="Arm & Hammer\u2122 Care & Rewear Clothing Refresher Mist - Original Fresh",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("Ethanol", "64-17-5", "Solvent (on the IARC Carcinogens list)"),
             ("PEG-12 dimethicone", "68937-54-2", "Lubricant"),
             ("Dipropylene glycol", "25265-71-8", "Solubilizer"),
             ("C9-11 alcohols ethoxylated", "68439-46-3", "Surfactant"),
             ("Phenoxyethanol", "122-99-6", "Anti-microbial (on the CA TACs list)"),
             ("Caprylyl glycol", "1117-86-8", "Anti-microbial"),
             ("Sodium benzoate", "532-32-1", "Anti-microbial")],
        frag=["2,6-Dimethyl-7-octen-2-ol 18479-58-8",
              "Hexamethylindanopyran 1222-05-5 (US EPA PBTs)"],
        note=("A spray that refreshes worn clothing between washes, in the 'wear it again' category rather "
              "than the laundry category. Recorded because the corpus had no fabric refresher at all and "
              "because it is a different kind of product: it is not a cleaner, and its own filing shows it, "
              "with two of its nine lines being preservatives and a third being the ethanol that carries the "
              "scent. Entered ungraded. One mapping note: the filing's 'C9-11 alcohols ethoxylated' is "
              "recorded under the registry's graded 'Alcohols, C9-11, ethoxylated' key rather than the "
              "ungraded near-duplicate spelling, per the standing rule that a label term maps to the closest "
              "existing key where the substance is the same."),
        exposure=2,
        exposure_src=IDXBOX_LAUNDRY,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for the Arm & "
                        "Hammer Care & Rewear mist (the manufacturer filing, the brand site, a general web "
                        "search) and found none. IndexBox's US Laundry & Home Products page states household "
                        "penetration above 98 percent. Estimate is that base times a share for the "
                        "wear-again-and-refresh segment, rounded to one significant figure, and set low "
                        "because the category is new and the product is an alternative to washing rather than "
                        "a replacement for it."),
        substitutes=[dict(name="Downy WrinkleGuard Wrinkle Releaser Fabric Spray, Fresh", tier="mass",
                          note=("Same shelf, same price band, same spray-a-worn-garment job. The same-shelf "
                                "alternative rather than the fragrance-avoiding one; it carries its own "
                                "fragrance, so it does not avoid the scent.")),
                     dict(name="Distilled White Vinegar (5%)", tier="apothecary-bulk",
                          note=("The fragrance-free route to the same outcome, diluted in a spray bottle for "
                                "odour or added to a rinse. It avoids the whole fragrance class, the ethanol "
                                "carrier and all three preservatives, at the cost of not leaving a scent."))],
    ),
]


def main():
    products = load("products.json")
    ingredients = load("ingredients.json")
    owners = load("owners.json")
    changelog = load("changelog.json")

    have = {p["name"] for p in products}
    added, minted = [], []

    # 1. mint any missing ingredient keys BEFORE the product-existence check, so a
    #    re-run can never leave a dangling reference on an already-present record.
    for rec in PRODUCTS:
        for key in rec["ings"]:
            if key not in ingredients:
                ingredients[key] = {
                    "s": f"{key}. Named on a Church & Dwight California SB-258 ingredient disclosure, read {TODAY}.",
                    "ev": "Low", "g": None, "gr": {}, "impacts": [],
                    "note": NEW_KEY_NOTE.format(date=TODAY),
                }
                minted.append(key)

    # 2. the owner record must name the brand string, or the product silently
    #    stamps owner=null / owner_ev=untested. Clean Shower was missing.
    cd = owners["owners"]["Church & Dwight"]
    for rec in PRODUCTS:
        if rec["brand"] not in cd["brands"]:
            cd["brands"].append(rec["brand"])

    # 3. add products that are absent
    for rec in PRODUCTS:
        if rec["name"] in have:
            continue
        url = IDX + rec["slug"].replace(" ", "%20")
        cas_txt = "; ".join(f"{n} {c} ({f})" for n, c, f in rec["cas"])
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
            "tier_note": ("Church & Dwight markets Arm & Hammer, OxiClean, Kaboom, Xtra, Scrub Free, Orange Glo "
                          "and Clean Shower as national consumer brands sold through grocery, mass, drug and "
                          "dollar channels; evidenced by Church & Dwight's own consumer-brands page, which "
                          "names all seven."),
            "substitutes": rec["substitutes"],
            "no_substitute_known": False,
            "no_substitute_note": None,
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

    # 4. changelog entry, guarded on an actual change
    changelog.insert(0, {
        "date": TODAY,
        "text": (f"Spectrum harvest station 2 (Dolman {TODAY}): {len(added)} Church & Dwight household products "
                 f"added by exposure ({', '.join(added) if added else 'none'})"
                 + (f"; {len(minted)} new ungraded ingredient keys minted ({', '.join(minted)})" if minted else "")
                 + ". Source: Church & Dwight's own California SB-258 ingredient-disclosure index.")
    })

    dump("products.json", products, 1)
    dump("ingredients.json", ingredients, 1)
    dump("owners.json", owners, 1)
    dump("changelog.json", changelog, 2)
    print(f"added {len(added)} products: {added}")
    print(f"minted {len(minted)} ingredient keys: {minted}")
    print(f"owner record brands now: {cd['brands']}")


if __name__ == "__main__":
    main()
