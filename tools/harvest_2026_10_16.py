#!/usr/bin/env python3
"""Night-shift station 2 harvest, 2026-10-16 (Dolman).

Shelf: AIR CARE, ordered by EXPOSURE.

Why this shelf, and the direction question the night template asks. The mandate is
"order by exposure, not price tier" and "the goal is exposure". The four channel
tiers (dollar-store, drugstore, grocery/mass, apothecary-bulk) are built. The KIK
value-brand index is exhausted for household products. Home fragrance is the
largest documented exposure gap left in the corpus: as of 2026 the IndexBox US Air
Fresheners & Candles page states household penetration for at least one home
fragrance format "exceeds 85%", and that bathroom air freshener sprays and
continuous-release devices are "near-ubiquitous, with over 70% of households
reporting regular use" -- against THREE air-care records in a corpus of 428.

This shelf has been deferred for several fires on the open
`fragrance-components-as-ingredient-keys` ruling. That ruling is real but it does
NOT block the work: its own gap file says "nothing is blocked... the data is
correct as entered", and the standing discipline already in use for the last
twenty-plus records (record `Fragrance` as the single registry key, name the
disclosed components in the record's `source` prose only, mint NO fragrance keys)
applies here unchanged. What this fire therefore tests is a format spread inside
one category, not a new convention.

Routes used, both manufacturer-published California SB-258 declarations:
  - Essential Home / Vestacy, https://www.vestacyinfo.com/product.php?productLineId=<id>
    (served HTML, no JavaScript; base substances and fragrance components are
    separated by the page's own function labels). Air Wick ids are enumerable from
    https://www.vestacyinfo.com/brand.php?brandId=2 (834 ids, 245 current).
  - SC Johnson, https://whatsinsidescjohnson.com/en-us/brands/glade/... (SC Johnson's
    own ingredient-communication pages; 429 to curl, read in full by the fetch tool,
    the recorded "the answer can be a different TOOL" case).
  - Church & Dwight, https://www.churchdwight.com/ingredient-disclosure/ (already in
    docs/source-policy.md).

Formats covered, deliberately, because the chemistry differs by format and that is
the comparison value the database offers:
  - pressurised aerosol, hydrocarbon propellant (Air Wick Automatic Spray)
  - pressurised aerosol, nitrogen propellant (Glade Soft Mist)
  - pressurised aerosol, propane/isobutane propellant over bicarbonate (Arm & Hammer)
  - passive evaporative diffuser, petroleum-isoparaffin carrier (Air Wick Essential Mist)
  - passive aqueous gel (Air Wick STICK UPS)
The 100%-fragrance plug-in refill format (Air Wick Scented Oil) is deliberately NOT
re-entered: its disclosure is a single line, `Fragrance/Parfum`, plus 32-62 fragrance
components and nothing else, and the corpus already carries one such record. The
observation is filed instead.

Held out, read and recorded, NOT entered:
  - every Air Wick Scented Oil refill (page after page confirms base = 1 line)
  - the Great Value and Church & Dwight fabric-softener dryer sheets, whose disclosed
    list is class-name actives (HMIRA/LCMRD trade-secret lines) plus fragrance.

Fragrance discipline: no fragrance keys are minted. Each record's `source` prose
carries the component list as served. Fragrance-table lines that are carriers or
non-odorants (dipropylene glycol, propylene glycol, an isoparaffin, denatonium
benzoate, BHT) are named as such, since they are disclosed in the fragrance table
because they carry the blend, not because they are odourants.

Idempotent: a second run adds nothing and mints nothing.
"""
import json, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")
TODAY = "2026-10-16"

IDXBOX_AIR = ("https://www.indexbox.io/store/"
              "united-states-air-fresheners-candles-market-analysis-forecast-size-trends-and-insights/")
SIMPORTER = "https://simporter.com/trends/plug-in-air-freshener/"
VESTACY_BRANDS = "https://www.vestacy.com/our-brands/"
CANDY = "https://churchdwight.com/our-brands/consumer-brands/"

NEW_KEY_NOTE = ("Added by the {date} night-shift harvest from a manufacturer's California Cleaning Product "
                "Right to Know Act disclosure. No PubChem or ECHA grade has been resolved for this entry yet, "
                "so g is null rather than a guess. It enters ungraded, which is the honest state until the "
                "grading lane reaches it.")

AW_TIER_NOTE = ("Air Wick is a national US consumer brand sold through grocery, mass, drug and dollar "
                "channels. Evidenced by Vestacy's own portfolio page, which describes Air Wick as one of the "
                "leading global players in the Air Care category with products available in more than 80 "
                "countries. Channel evidence is brand-level, not per-SKU.")
GL_TIER_NOTE = ("Glade is a national US consumer brand sold through grocery, mass and drug channels. "
                "Evidenced by Simporter's US plug-in air freshener category report, which measures Glade's "
                "share of that US retail category at 14.5% (September 2026). Channel evidence is brand-level, "
                "not per-SKU. Note: SC Johnson's own corporate pages (scjohnson.com, glade.com) return HTTP "
                "429 to a machine fetch from this sandbox and were not used as the citation for that reason.")
CD_TIER_NOTE = ("Arm & Hammer is a national US consumer brand. Evidenced by Church & Dwight's own "
                "consumer-brands page, which names Arm & Hammer among its seven household brands sold through "
                "grocery, mass, drug and dollar channels. Channel evidence is brand-level, not per-SKU.")

# ---------------------------------------------------------------- records

PRODUCTS = [
    dict(
        name="Air Wick Essential Mist Air Freshener Refill, Fresh Water",
        brand="Air Wick", cat="Specialty",
        ings=["Isoparaffin", "Trimethylhexyl Acetate", "Fragrance"],
        url="https://www.vestacyinfo.com/product.php?productLineId=2255",
        served="AIR WICK\u00ae Essential Mist - Fresh Water",
        cas=[("C13-14 isoparaffin", "64742-47-8", "Solvent"),
             ("C13-16 isoparaffin", "68551-20-2", "Solvent"),
             ("C11-13 isoparaffin", "64742-48-9",
              "Solvent (on the EU CMRs and Canada PBTs lists as served)"),
             ("3,5,5-Trimethylhexyl acetate", "58430-94-7", "Solvent")],
        frag=["Benzyl acetate 140-11-4", "Jasmacyclene 2500-83-6",
              "(E)-1-(2,6,6-trimethyl-2-cyclohexen-1-yl)-2-buten-1-one 24720-09-0",
              "2,4-Dimethyl-3-cyclohexene carboxaldehyde 68039-49-6",
              "2,6-Dimethyl-2-heptanol 13254-34-7", "2,6-Dimethyl-5-heptenal 106-72-9",
              "2,6-Octadienal, 3,7-dimethyl-, reaction products with ethyl alcohol 147060-73-9",
              "2-Methyl-3-(p-isopropylphenyl) propionaldehyde 103-95-7", "2-Methylundecanal 110-41-8",
              "2-tert-Butylcyclohexyl acetate 88-41-5", "3-Hexenol 928-96-1",
              "4-tert-Butylcyclohexyl acetate 32210-23-4",
              "6,6-Dimethoxy-2,5,5-trimethylhex-2-ene 67674-46-8",
              "Allyl (cyclohexyloxy)acetate 68901-15-5", "Allyl hexanoate 123-68-2",
              "beta-Pinene 127-91-3", "cis-3-Hexenyl methyl carbonate 67633-96-9",
              "d-Limonene 5989-27-5", "Decanal 112-31-2", "Dihydromyrcenol 18479-58-8",
              "Dipropylene glycol 25265-71-8 (a carrier present in the fragrance table, not an odourant)",
              "Ethyl 2-methylpentanoate 39255-32-8", "Eucalyptol 470-82-6",
              "Eucalyptus oil 8000-48-4", "Floral pyranol 63500-71-0", "gamma-Undecalactone 104-67-6",
              "Hexenyl acetate 3681-71-8", "Hexyl acetate 142-92-7", "Hydroxycitronellol 107-74-4",
              "Isopropylphenylbutanal 125109-85-5", "Linalool 78-70-6",
              "Methyl benzodioxepinone 28940-11-6", "Methyldihydrojasmonate 24851-98-7",
              "Nona-2-trans-6-cis-dienal 557-48-2", "Octanal 124-13-0",
              "Orange oil, sweet, terpenes 68647-72-3", "Phenethyl alcohol 60-12-8",
              "Terpineol 8000-41-7", "Triethyl citrate 77-93-0"],
        note=("A refill for a passive ultrasonic diffuser: the household drops the bottle in the unit and it "
              "evaporates without heat, flame or propellant. Recorded because the corpus carried no diffuser "
              "format at all, and because this format's carrier is a petroleum isoparaffin rather than water. "
              "Three isoparaffin grades are disclosed (C13-14, C13-16, C11-13) with three different CAS "
              "numbers; they are recorded under the registry's single existing 'Isoparaffin' key, with each "
              "CAS named here, following the precedent set when C13-14 isoparaffin was mapped to that key on "
              "2026-10-07. That is a traceability compromise and is flagged for the verifier rather than "
              "resolved here. One disclosure point a reader should see: the served filing marks C11-13 "
              "isoparaffin on both the EU CMRs list and Canada's PBT list. Entered ungraded: product grading "
              "is the Sifter lane; no PubChem or ECHA grade was resolved for the new key this fire."),
        exposure=5,
        exposure_src=IDXBOX_AIR,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for Air Wick "
                        "Essential Mist (the manufacturer filing, the brand site, a general web search) and "
                        "found none. IndexBox's US Air Fresheners & Candles page states household penetration "
                        "for at least one home fragrance format exceeds 85%, and puts app-controlled "
                        "ultrasonic diffusers and programmable plug-in devices at an estimated 5 to 7 percent "
                        "of active diffusion unit sales. Estimate is that device share against the 85 percent "
                        "base, rounded to one significant figure. Note: the served Simporter plug-in "
                        "air-freshener page (October 2026 snapshot) names Air Wick on its brand chart but "
                        "states NO numeric share for it in the page text, so no brand share is used here."),
        substitutes=[dict(name="Glade Soft Mist Air Freshener Spray, Clean Linen", tier="mass",
                          note=("Same job, same shelf, similar price band, and an aqueous formula with a "
                                "nitrogen propellant. Avoids the whole petroleum-isoparaffin carrier class, "
                                "including the C11-13 grade the filing marks on the EU CMRs and Canada PBTs "
                                "lists.")),
                     dict(name="DampRid Fragrance Free Moisture Absorber", tier="mass",
                          note=("A different route to the same goal. If the household wants the room to smell "
                                "of nothing rather than of something, this controls odour without adding any "
                                "fragrance, at a comparable price."))],
    ),
    dict(
        name="Air Wick Automatic Spray Refill, Fresh Linen",
        brand="Air Wick", cat="Specialty",
        ings=["Butane", "Propane", "Hydrofluorocarbon 152A", "Isoparaffin", "Fragrance"],
        url="https://www.vestacyinfo.com/product.php?productLineId=2547",
        served="AIR WICK\u00ae Automatic Spray - Fresh Linen",
        cas=[("Butane", "106-97-8", "Propellant"),
             ("Propane", "74-98-6", "Propellant (on the EU CMRs list as served)"),
             ("1,1-Difluoroethane (HFC-152a)", "75-37-6", "Propellant"),
             ("C13-14 isoparaffin", "64742-47-8", "Solvent"),
             ("C11-13 isoparaffin", "64742-48-9",
              "Solvent (on the EU CMRs and Canada PBTs lists as served)")],
        frag=["1,1-Dimethyl-2-phenylethyl acetate 151-05-3",
              "2-Methyl-3-(p-isopropylphenyl) propionaldehyde 103-95-7",
              "2-tert-Butylcyclohexyl acetate 88-41-5",
              "3-(4-Ethylphenyl)-2,2-dimethylpropanal 67634-15-5",
              "alpha-Isomethyl ionone 127-51-5", "Benzyl acetate 140-11-4",
              "C13-14 isoparaffin 64742-47-8 (carrier in the fragrance table, not an odourant)",
              "Citral 5392-40-5", "Citrus limon (lemon) peel oil 8008-56-8", "d-Limonene 5989-27-5",
              "Denatonium benzoate 3734-33-6 (bittering agent, present in the fragrance table)",
              "Dihydromyrcenol 18479-58-8",
              "Dipropylene glycol 25265-71-8 (carrier in the fragrance table, not an odourant)",
              "Fructone 6413-10-1", "Linalool 78-70-6", "Litsea cubeba oil 68855-99-2",
              "Majantol 103694-68-4", "Methyl ionone 1335-46-2",
              "Propylene glycol 57-55-6 (carrier in the fragrance table, not an odourant)",
              "Terpineol acetate 8007-35-0", "Tetramethyl acetyloctahydronaphthalenes 54464-57-2",
              "Tricyclodecenyl acetate 5413-60-5", "Tricyclodecenyl propionate 17511-60-3",
              "3,5,5-Trimethylhexyl acetate 58430-94-7"],
        note=("A refill for the brand's timed automatic aerosol dispenser, the format that sprays on a timer "
              "with nobody in the room. Recorded because it is the mainstream continuous-release aerosol and "
              "because its propellant stack is the part a reader will not expect in an air freshener: butane, "
              "propane and HFC-152a together, two of them flammable and the third a fluorinated greenhouse "
              "gas. The same filing carries a bittering agent, denatonium benzoate, in the fragrance table. "
              "Entered ungraded."),
        exposure=11,
        exposure_src=IDXBOX_AIR,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for Air Wick "
                        "Automatic Spray (the manufacturer filing, the brand site, a general web search) and "
                        "found none. IndexBox's US Air Fresheners & Candles page states household penetration "
                        "for at least one home fragrance format exceeds 85% and that bathroom air freshener "
                        "sprays and continuous-release devices are used regularly by over 70% of households. "
                        "No numeric share for Air Wick is stated in the served Simporter plug-in "
                        "air-freshener page text (October 2026); Air Wick appears only as a label on that "
                        "page's brand chart. The brand share used is therefore derived from the same page's "
                        "stated category concentration, that the top brands account for 77.5% of the category "
                        "across six named brands, giving roughly 12.9% each. Estimate is the 85 percent "
                        "penetration base times that share, rounded to one significant figure, and it is a "
                        "lower-confidence figure than the Glade records, which do have a published share."),
        substitutes=[dict(name="Glade Soft Mist Air Freshener Spray, Clean Linen", tier="mass",
                          note=("Same job, same shelf, similar price band, and the propellant is nitrogen, "
                                "which SC Johnson's own ingredient page describes as a non-flammable, non-VOC "
                                "compressed gas. Avoids all three propellants on this list, including the "
                                "fluorinated HFC-152a.")),
                     dict(name="Air Wick STICK UPS Air Freshener, Sparkling Citrus", tier="mass",
                          note=("Same brand and price band, and no aerosol at all, so it avoids butane, "
                                "propane and HFC-152a together. It is a passive gel, so the trade is that it "
                                "has to be placed rather than timed."))],
    ),
    dict(
        name="Air Wick Automatic Spray Refill, Lavender & Chamomile",
        brand="Air Wick", cat="Specialty",
        ings=["Butane", "Propane", "Hydrofluorocarbon 152A", "Isoparaffin", "Fragrance"],
        url="https://www.vestacyinfo.com/product.php?productLineId=2538",
        served="AIR WICK\u00ae Automatic Spray - Lavender & Chamomile",
        cas=[("Butane", "106-97-8", "Propellant"),
             ("Propane", "74-98-6", "Propellant (on the EU CMRs list as served)"),
             ("1,1-Difluoroethane (HFC-152a)", "75-37-6", "Propellant"),
             ("C13-14 isoparaffin", "64742-47-8", "Solvent"),
             ("C11-13 isoparaffin", "64742-48-9",
              "Solvent (on the EU CMRs and Canada PBTs lists as served)")],
        frag=["1,1-Dimethyl-2-phenylethyl acetate 151-05-3", "2-tert-Butylcyclohexyl acetate 88-41-5",
              "4-Carvomenthenol 562-74-3", "alpha-Amylcinnamaldehyde 122-40-7",
              "alpha-Hexylcinnamaldehyde 101-86-0", "Benzyl acetate 140-11-4",
              "BHT (butylated hydroxytoluene) 128-37-0 (antioxidant in the fragrance table)",
              "C13-14 isoparaffin 64742-47-8 (carrier in the fragrance table, not an odourant)",
              "Camphor 76-22-2", "Coumarin 91-64-5", "d-Limonene 5989-27-5", "delta-3-Carene 13466-78-9",
              "Denatonium benzoate 3734-33-6 (bittering agent, present in the fragrance table)",
              "Dipropylene glycol 25265-71-8 (carrier in the fragrance table, not an odourant)",
              "Eucalyptol 470-82-6", "Eucalyptus oil 8000-48-4", "Eugenol 97-53-0",
              "Fenchyl acetate 13851-11-1", "Hexyl salicylate 6259-76-3",
              "Isoamyl allylglycolate 67634-00-8", "Isobornyl acetate 125-12-2", "l-Borneol 464-45-9",
              "Limonene 138-86-3", "Linalool 78-70-6", "Linalyl acetate 115-95-7",
              "Methyldihydrojasmonate 24851-98-7", "p-Cresol 106-44-5", "Terpineol 8000-41-7",
              "and one line the filing withholds as 'Total Allyl Esters Proprietary'"],
        note=("The same timed aerosol dispenser as the Fresh Linen refill, in a different scent: identical "
              "propellant and carrier list, so the two records are a same-product scent swap. Recorded as a "
              "pair deliberately, because the useful comparison is what does not change between scents. Two "
              "things this scent adds that the plain one does not: p-cresol, and a proprietary withheld line "
              "the filing names only as 'Total Allyl Esters Proprietary'. Entered ungraded."),
        exposure=11,
        exposure_src=IDXBOX_AIR,
        exposure_basis=("Derived, not measured, and identical to its Fresh Linen sibling because the product "
                        "is the same device and formula in another scent. IndexBox's US Air Fresheners & "
                        "Candles page gives household penetration for at least one home fragrance format "
                        "above 85% and regular use of sprays and continuous-release devices by over 70% of "
                        "households. No numeric Air Wick share is stated in the served Simporter page text "
                        "(October 2026), so the share used is that page's stated category concentration, "
                        "77.5% across six named brands, giving roughly 12.9% each. Estimate is the 85 percent "
                        "base times that share, rounded to one significant figure."),
        substitutes=[dict(name="Glade Soft Mist Air Freshener Spray, Lavender & Vanilla", tier="mass",
                          note=("The nearest same-scent swap on the same shelf and price band, with a nitrogen "
                                "propellant instead of three hydrocarbon and fluorinated ones, so it avoids "
                                "the entire propellant stack on this record.")),
                     dict(name="Air Wick STICK UPS Air Freshener, Lavender & Chamomile", tier="mass",
                          note=("Same brand, same scent, same price band, and no aerosol. Avoids butane, "
                                "propane and HFC-152a; the trade is a passive gel rather than a timer."))],
    ),
    dict(
        name="Air Wick STICK UPS Air Freshener, Lavender & Chamomile",
        brand="Air Wick", cat="Specialty",
        ings=["Water", "Carrageenan", "Carob Gum", "Polysorbate 80", "Benzisothiazolinone", "Fragrance"],
        url="https://www.vestacyinfo.com/product.php?productLineId=3398",
        served="AIR WICK\u00ae STICK UPS\u00ae - Lavender & Chamomile",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("Carrageenan", "9000-07-1", "Gelling agent"),
             ("Carob gum", "9000-40-2", "Gelling agent"),
             ("Polysorbate 80", "9005-65-6", "Emulsifier"),
             ("Benzisothiazolinone", "2634-33-5", "Preservative (a skin sensitiser)")],
        frag=["Dipropylene glycol 25265-71-8 (carrier in the fragrance table, not an odourant)",
              "2-Octanone 111-13-7", "2-tert-Butylcyclohexyl acetate 88-41-5",
              "3,7-Dimethyl-1-octanol 106-21-8", "4-tert-Butylcyclohexyl acetate 32210-23-4",
              "alpha-Terpineol acetate 80-26-2", "Camphene 79-92-5", "Camphor 76-22-2",
              "Citronellyl acetate 150-84-5", "Coumarin 91-64-5", "Cyclohexaneethyl acetate 21722-83-8",
              "delta-3-Carene 13466-78-9", "Dihydromyrcenol 18479-58-8",
              "Dihydroterpinyl acetate 58985-18-5", "dl-Citronellol 106-22-9", "Eucalyptol 470-82-6",
              "Geraniol 106-24-1", "Geranyl acetate 105-87-3", "Hexyl acetate 142-92-7",
              "Isobornyl acetate 125-12-2", "Jasmacyclene 2500-83-6", "Lavandin oil 8022-15-9",
              "Linalool 78-70-6", "Linalyl acetate 115-95-7", "Nerol 106-25-2",
              "Siberian fir needle oil 8021-29-2"],
        note=("A passive gel air freshener: an aqueous carrageenan and carob-gum gel that releases fragrance "
              "with no propellant, no heat and no power. Recorded because it is the no-aerosol member of the "
              "category and therefore the concrete alternative offered to the two Automatic Spray records. "
              "Its chemistry is genuinely different: water, two food-grade gums, an emulsifier and one "
              "preservative, with no petroleum solvent and no propellant. The preservative, "
              "benzisothiazolinone, is the one thing here a sensitive household would want to know about, "
              "since it is a recognised skin sensitiser and it is disclosed at formulation level rather than "
              "inside the fragrance. Entered ungraded."),
        exposure=4,
        exposure_src=IDXBOX_AIR,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for Air Wick "
                        "STICK UPS (the manufacturer filing, the brand site, a general web search) and found "
                        "none. IndexBox's US Air Fresheners & Candles page gives household penetration for at "
                        "least one home fragrance format above 85% but splits its regular-use figure between "
                        "sprays and continuous-release devices, neither of which is a passive gel, so only the "
                        "85% base is used. The product does not appear in the served Simporter page's top-six "
                        "brand chart, so it is treated as outside the pack. Estimate is the 85 percent base "
                        "times a small share for this format, rounded to one significant figure, and is a "
                        "low-confidence floor."),
        substitutes=[dict(name="Arm & Hammer Deodorizing Air Freshener with Baking Soda", tier="mass",
                          note=("Same price band and a different tack: a bicarbonate deodoriser rather than a "
                                "perfumed gel. It still carries fragrance, so this is a price-and-format swap "
                                "rather than a fragrance-free one, but it avoids benzisothiazolinone.")),
                     dict(name="DampRid Fragrance Free Moisture Absorber", tier="mass",
                          note=("For a household reacting to the preservative or to fragrance itself, this "
                                "controls odour with neither, at a comparable price."))],
    ),
    dict(
        name="Air Wick STICK UPS Air Freshener, Sparkling Citrus",
        brand="Air Wick", cat="Specialty",
        ings=["Water", "Carrageenan", "Carob Gum", "Polysorbate 80", "Benzisothiazolinone", "Fragrance"],
        url="https://www.vestacyinfo.com/product.php?productLineId=3399",
        served="AIR WICK\u00ae STICK UPS\u00ae - Sparkling Citrus",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("Carrageenan", "9000-07-1", "Gelling agent"),
             ("Carob gum", "9000-40-2", "Gelling agent"),
             ("Polysorbate 80", "9005-65-6", "Emulsifier"),
             ("Benzisothiazolinone", "2634-33-5", "Preservative (a skin sensitiser)")],
        frag=["Dipropylene glycol 25265-71-8 (carrier in the fragrance table, not an odourant)",
              "(E)-6,10-Dimethylundeca-5,9-dien-2-yl acetate 3239-35-8",
              "2,4-Dimethyl-3-cyclohexene carboxaldehyde 68039-49-6",
              "2-tert-Butylcyclohexyl acetate 88-41-5",
              "3a,4,5,6,7,7a-Hexahydro-4,7-methano-1H-indenyl propionate (mixture of isomers) 68912-13-0",
              "Acetophenone 98-86-2", "Allyl cyclohexanepropionate 2705-87-5",
              "Allyl heptanoate 142-19-8", "Allyl hexanoate 123-68-2", "Benzaldehyde 100-52-7",
              "Benzyl acetate 140-11-4", "Benzyl salicylate 118-58-1", "Citral 5392-40-5",
              "d-Limonene 5989-27-5", "Decanal 112-31-2", "Ethyl 2-methylbutyrate 7452-79-1",
              "Ethyl butyrate 105-54-4", "Ethyl hexanoate 123-66-0", "gamma-Decalactone 706-14-9",
              "gamma-Nonalactone 104-61-0", "gamma-Undecalactone 104-67-6", "Geranyl acetate 105-87-3",
              "Grapefruit oil, rectified 8016-20-4", "Jasmacyclene 2500-83-6", "Linalool 78-70-6",
              "Methylbenzyl acetate 93-92-5", "Octanal 124-13-0", "Orange oil, sweet 8008-57-9",
              "Phenoxyethyl isobutyrate 103-60-6", "Triethyl citrate 77-93-0", "Vanillin 121-33-5"],
        note=("The same passive gel as the Lavender & Chamomile STICK UPS, in a different scent: identical "
              "base list, so the two are a same-product scent swap and the useful comparison is what does not "
              "change. Recorded as a pair for the same reason as the Automatic Spray pair. The one "
              "formulation line worth naming here is acetophenone, which is not a pleasant-smelling trace "
              "but a real solvent-grade aromatic in the fragrance blend. Entered ungraded."),
        exposure=4,
        exposure_src=IDXBOX_AIR,
        exposure_basis=("Derived, not measured, and identical to its Lavender & Chamomile sibling because the "
                        "product is the same passive gel in another scent. IndexBox's US Air Fresheners & "
                        "Candles page gives household penetration for at least one home fragrance format "
                        "above 85%; its regular-use figure covers sprays and continuous-release devices, not "
                        "passive gels, so only the 85% base is used. The product is absent from the served "
                        "Simporter page's top-six brand chart. Estimate is the 85 percent base times a small "
                        "share for this format, rounded to one significant figure, and is a low-confidence "
                        "floor."),
        substitutes=[dict(name="Arm & Hammer Deodorizing Air Freshener with Baking Soda", tier="mass",
                          note=("Same price band, a bicarbonate deodoriser rather than a perfumed gel, and it "
                                "avoids the benzisothiazolinone preservative.")),
                     dict(name="DampRid Fragrance Free Moisture Absorber", tier="mass",
                          note=("For a household reacting to the preservative or to fragrance itself: odour "
                                "control with neither, at a comparable price."))],
    ),
    dict(
        name="Glade Soft Mist Air Freshener Spray, Lavender & Vanilla",
        brand="Glade", cat="Specialty",
        ings=["Water", "Ethanol", "Nitrogen", "PEG-60 Hydrogenated Castor Oil", "Ethoxylated Alcohol",
              "Triethylene Glycol", "Propylene Glycol", "Sodium Phosphate", "Sodium Carbonate",
              "Steartrimonium Chloride", "Fragrance"],
        url="https://whatsinsidescjohnson.com/en-us/brands/glade/sprays/odor-fighting-soft-mist-air-freshener/lavender-vanilla",
        served="Lavender & Vanilla Glade\u00ae Soft Mist Air Freshener Spray",
        cas=[("Water", "not stated on the served page", "Carrier"),
             ("Ethanol", "not stated on the served page", "Carrier"),
             ("Nitrogen", "not stated on the served page", "Propellant"),
             ("PEG-60 hydrogenated castor oil", "not stated on the served page", "Emulsifier"),
             ("Ethoxylated alcohol", "not stated on the served page", "Emulsifier"),
             ("Triethylene glycol", "not stated on the served page", "Solubilizer"),
             ("Propylene glycol", "not stated on the served page", "Solubilizer"),
             ("Sodium phosphate", "not stated on the served page", "pH adjuster"),
             ("Sodium carbonate", "not stated on the served page", "pH adjuster"),
             ("Steartrimonium chloride", "112-03-8",
              "Stabilizer (CAS not stated on the served page; resolved against PubChem CID 8155)")],
        frag=["c12-14 sec-pareth-3 (a surfactant present in the fragrance table, not an odourant)",
              "Dipropylene glycol (carrier in the fragrance table, not an odourant)",
              "Terpineol acetate", "Ethyl linalool", "Ethylene brassylate", "Anisaldehyde",
              "4-tert-Butylcyclohexyl acetate (SC Johnson marks this on its own skin-allergen list)",
              "Tetramethyl acetyloctahydronaphthalenes (SC Johnson marks this on its own skin-allergen list)",
              "Lavandula hybrida oil (SC Johnson marks this on its own skin-allergen list)",
              "Linalyl acetate (SC Johnson marks this on its own skin-allergen list)",
              "Linalool (SC Johnson marks this on its own skin-allergen list)",
              "2,6-Dimethyl-7-octen-2-ol", "gamma-Undecalactone", "Methyldihydrojasmonate",
              "gamma-Nonalactone", "Coumarin (SC Johnson marks this on its own skin-allergen list)"],
        note=("An aerosol air freshener whose propellant is nitrogen rather than a hydrocarbon, which is the "
              "one structural difference from the Air Wick aerosol records and the reason it is the "
              "substitute offered for them. The household gets a pressurised spray with no flammable "
              "propellant and no fluorinated gas, at the cost of a formula that still carries propylene "
              "glycol, an emulsifier, two pH adjusters and a quaternary stabiliser. It is also the second "
              "product in this corpus, after the OxiClean pod, whose label discloses a bittering-agent class "
              "of additive rather than an ingredient. The served page states each ingredient's identity and "
              "function but no CAS for any line, so no CAS is asserted here except where it was resolved "
              "against a registry. No date of disclosure is stated on the served page. Entered ungraded."),
        exposure=16,
        exposure_src=SIMPORTER,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for Glade "
                        "Soft Mist (the manufacturer page, the brand site, a general web search) and found "
                        "none. The served Simporter plug-in air freshener page (October 2026 snapshot) states "
                        "verbatim that Glade holds 19.3% share of the US plug-in air freshener category, "
                        "ahead of private label at 19.0% and Febreze Plug at 16.8%; that is the brand-strength "
                        "proxy used here, and the plug-in share is the wrong format for a spray, so it is a "
                        "proxy and not a measurement. IndexBox's US Air Fresheners & Candles page gives "
                        "household penetration for at least one home fragrance format above 85%. Estimate is "
                        "the 85 percent base times the 19.3 percent brand share, rounded to one significant "
                        "figure."),
        substitutes=[dict(name="DampRid Fragrance Free Moisture Absorber", tier="mass",
                          note=("Same goal, no fragrance and no propellant, at a comparable price. Avoids the "
                                "whole sixteen-line fragrance block, five of whose components SC Johnson itself "
                                "marks on its skin-allergen list.")),
                     dict(name="Air Wick Essential Mist Air Freshener Refill, Fresh Water", tier="mass",
                          note=("A same-price alternative on the same shelf for a household that wants a "
                                "scented product but not an aerosol. The trade is that it swaps nitrogen for a "
                                "petroleum-isoparaffin carrier, so it is a real choice rather than a strictly "
                                "better one."))],
    ),
    dict(
        name="Glade Soft Mist Air Freshener Spray, Clean Linen",
        brand="Glade", cat="Specialty",
        ings=["Water", "Ethanol", "Nitrogen", "PEG-60 Hydrogenated Castor Oil", "Ethoxylated Alcohol",
              "Triethylene Glycol", "Propylene Glycol", "Sodium Phosphate", "Sodium Carbonate",
              "Steartrimonium Chloride", "Fragrance"],
        url="https://whatsinsidescjohnson.com/en-us/brands/glade/sprays/odor-fighting-soft-mist-air-freshener/clean-linen-air-freshener-spray",
        served="Clean Linen\u00ae Glade\u00ae Soft Mist Air Freshener Spray",
        cas=[("Water", "not stated on the served page", "Carrier"),
             ("Ethanol", "not stated on the served page", "Carrier"),
             ("Nitrogen", "not stated on the served page", "Propellant"),
             ("PEG-60 hydrogenated castor oil", "not stated on the served page", "Emulsifier"),
             ("Ethoxylated alcohol", "not stated on the served page", "Emulsifier"),
             ("Triethylene glycol", "not stated on the served page", "Solubilizer"),
             ("Propylene glycol", "not stated on the served page", "Solubilizer"),
             ("Sodium phosphate", "not stated on the served page", "pH adjuster"),
             ("Sodium carbonate", "not stated on the served page", "pH adjuster"),
             ("Steartrimonium chloride", "112-03-8",
              "Stabilizer (CAS not stated on the served page; resolved against PubChem CID 8155)")],
        frag=["Dipropylene glycol (carrier in the fragrance table, not an odourant)",
              "Isobutyl methyl tetrahydropyranol", "Ethylene brassylate", "Methyldihydrojasmonate",
              "2,6-Dimethyl-7-octen-2-ol",
              "3a,4,5,6,7,7a-Hexahydro-4,7-methano-1H-inden-1-yl acetate", "Methyl ionones",
              "Linalool (SC Johnson marks this on its own skin-allergen list)",
              "Benzyl acetate",
              "3-alpha,4,5,6,7,7-alpha-Hexahydro-4,7-methano-1H-indenyl propionate",
              "Citrus aurantium dulcis (orange) peel oil (SC Johnson marks this on its own skin-allergen list)",
              "Hexyl cinnamal (SC Johnson marks this on its own skin-allergen list)"],
        note=("The same Glade Soft Mist formula as the Lavender & Vanilla record in a different scent: the "
              "eleven-line base list is identical line for line, so the two records are a same-product scent "
              "swap and the comparison value is what does not change. Recorded as a pair for the same reason "
              "as the two Air Wick pairs. The served page states each ingredient's identity and function but "
              "no CAS for any line, so no CAS is asserted here except where it was resolved against a "
              "registry. No date of disclosure is stated on the served page. Entered ungraded."),
        exposure=16,
        exposure_src=SIMPORTER,
        exposure_basis=("Derived, not measured, and identical to its Lavender & Vanilla sibling because the "
                        "product is the same formula in another scent. The served Simporter plug-in air "
                        "freshener page (October 2026 snapshot) states Glade's share of that category at "
                        "19.3%, used here as the brand-strength proxy; IndexBox's US Air Fresheners & Candles "
                        "page gives household penetration for at least one home fragrance format above 85%. "
                        "Estimate is the 85 percent base times the 19.3 percent brand share, rounded to one "
                        "significant figure."),
        substitutes=[dict(name="DampRid Fragrance Free Moisture Absorber", tier="mass",
                          note=("Same goal, no fragrance and no propellant, at a comparable price. Avoids the "
                                "entire fragrance block, three of whose components SC Johnson itself marks on "
                                "its skin-allergen list.")),
                     dict(name="Air Wick Essential Mist Air Freshener Refill, Fresh Water", tier="mass",
                          note=("A same-price scented alternative with no aerosol. The trade is a petroleum "
                                "isoparaffin carrier in place of nitrogen."))],
    ),
    dict(
        name="Arm & Hammer Deodorizing Air Freshener with Baking Soda",
        brand="Arm & Hammer", cat="Specialty",
        ings=["Water", "Isobutane", "Propane", "Potassium Bicarbonate", "Sodium Bicarbonate",
              "Ammonium Hydroxide", "Fragrance"],
        url=("https://www.churchdwight.com/ingredient-disclosure/commercial-professional/"
             "42000025-ah-deodorizing-air-freshener.aspx"),
        served="Arm & Hammer\u2122 Deodorizing Air Freshener with Baking Soda",
        cas=[("Water", "7732-18-5", "Solvent"),
             ("Isobutane", "75-28-5", "Propellant"),
             ("Propane", "74-98-6", "Propellant"),
             ("Potassium bicarbonate", "298-14-6", "pH adjuster"),
             ("Sodium bicarbonate", "144-55-8", "Deodorizer"),
             ("Ammonium hydroxide", "1336-21-6", "pH adjuster (on the Canada PBTs list as served)")],
        frag=["Hexyl cinnamal 101-86-0 (EU Fragrance Allergens)",
              "Butylphenyl methylpropional 80-54-6 (EU CMRs)",
              "Isoeugenol 97-54-1 (IARC Carcinogens)"],
        note=("An aerosol room deodoriser built on the brand's baking soda, so the odour chemistry is "
              "bicarbonate rather than a masking perfume, with a small fragrance on top. Recorded because it "
              "is the bicarbonate-based member of the category and the only air-care record in the corpus "
              "whose deodorising action is not purely fragrance. Two disclosure points a reader should see: "
              "the propellant is isobutane and propane, and the three disclosed fragrance components are "
              "each on a designated list, including one IARC carcinogen and one EU CMR. The manufacturer "
              "files this form under its commercial-professional index, but the product name is a consumer "
              "one. Entered ungraded."),
        exposure=2,
        exposure_src=IDXBOX_AIR,
        exposure_basis=("Derived, not measured. Searched for a product-level US household figure for the Arm "
                        "& Hammer deodorising air freshener (the manufacturer filing, the brand site, a "
                        "general web search) and found none, and no per-brand share for this aerosol exists in "
                        "the sources used. IndexBox's US Air Fresheners & Candles page gives household "
                        "penetration for at least one home fragrance format above 85%, but Arm & Hammer is a "
                        "baking-soda brand with no measured air-care share, and Simporter's reported shares "
                        "for that category name only Glade, Febreze, Pura, Air Wick and private label. "
                        "Estimate is a small share of the 85% base, rounded to one significant figure, and is "
                        "explicitly a low-confidence floor rather than a measured value."),
        substitutes=[dict(name="DampRid Fragrance Free Moisture Absorber", tier="mass",
                          note=("Same price band, odour control with no fragrance and no propellant. Avoids "
                                "both propellants and all three listed fragrance components, at the cost of "
                                "not being a spray.")),
                     dict(name="Air Wick STICK UPS Air Freshener, Sparkling Citrus", tier="mass",
                          note=("A no-aerosol alternative on the same shelf and price band, so it avoids the "
                                "isobutane and propane. It is itself perfumed, so this is the propellant swap "
                                "rather than the fragrance-free one."))],
    ),
]

NEW_KEYS = {
    "Trimethylhexyl Acetate": {
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "s": "CAS 58430-94-7, as disclosed by the manufacturer.",
        "note": NEW_KEY_NOTE.format(date=TODAY),
    },
    "Carrageenan": {
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "s": "CAS 9000-07-1, as disclosed by the manufacturer.",
        "note": NEW_KEY_NOTE.format(date=TODAY),
    },
    "Carob Gum": {
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "s": "CAS 9000-40-2, as disclosed by the manufacturer.",
        "note": NEW_KEY_NOTE.format(date=TODAY),
    },
    "Potassium Bicarbonate": {
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "s": "CAS 298-14-6, as disclosed by the manufacturer.",
        "note": NEW_KEY_NOTE.format(date=TODAY),
    },
    "Steartrimonium Chloride": {
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "s": ("CAS 112-03-8 (resolved against PubChem CID 8155, trimethyl(octadecyl)azanium chloride). The "
              "served SC Johnson page states the identity but not the CAS, so the CAS was resolved against "
              "the registry. No PubChem or ECHA grade applied."),
        "note": NEW_KEY_NOTE.format(date=TODAY),
    },
}


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def dump(name, obj, indent):
    p = os.path.join(DATA, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=indent))
    # products/ingredients/owners are indent=1, changelog is indent=2, and none of
    # the four carries a trailing newline at head (measured 2026-10-12/13/16).


def main():
    products = load("products.json")
    ingredients = load("ingredients.json")
    owners = load("owners.json")
    changelog = load("changelog.json")

    have = {p["name"] for p in products}

    # Assert the brand strings resolve to an owner record, or the product silently
    # stamps owner=null / owner_ev=untested. Checked before writing anything.
    brand_to_owner = {}
    for oname, orec in owners["owners"].items():
        for b in orec.get("brands") or []:
            brand_to_owner[b] = oname
    for rec in PRODUCTS:
        if rec["brand"] not in brand_to_owner:
            raise SystemExit(f"brand {rec['brand']!r} matches no owner record -> would stamp untested")

    # Mint keys BEFORE the product-existence check, so a re-run cannot leave a
    # dangling ingredient reference. Guarded on absence so it is idempotent.
    minted = []
    for k, rec in NEW_KEYS.items():
        if k in ingredients:
            continue
        # never mint a case/space variant of an existing key
        norm = "".join(ch for ch in k.lower() if ch.isalnum())
        for existing in ingredients:
            if "".join(ch for ch in existing.lower() if ch.isalnum()) == norm:
                raise SystemExit(f"key {k!r} normalises onto existing key {existing!r}")
        ingredients[k] = rec
        minted.append(k)

    def src_for(rec, route_note):
        cas_txt = "; ".join(f"{n} {c} ({f})" for n, c, f in rec["cas"])
        s = (f"{route_note} The served item's own name reads \"{rec['served']}\". "
             f"Substances with CAS: {cas_txt}.")
        if rec["frag"]:
            s += (" Fragrance disclosed at component level as served, recorded in this prose only and NOT as "
                  "ingredient keys, per the standing fragrance discipline while the "
                  "fragrance-components-as-ingredient-keys ruling is open. Components: "
                  + "; ".join(rec["frag"]) + ".")
        else:
            s += " No fragrance is disclosed and none is listed."
        return s

    ROUTES = {
        "https://www.vestacyinfo.com/product.php?productLineId=2255":
            "Vestacy (Essential Home, formerly Reckitt's divested household brands) product ingredient "
            "disclosure for Air Wick, published under the California Cleaning Product Right to Know Act "
            "(SB-258), https://www.vestacyinfo.com/product.php?productLineId=2255 (HTTP 200), read "
            "2026-10-16. Served HTML carries the complete 'Intentionally Added' list with a CAS per line, "
            "and a separate fragrance-component section. No date of disclosure is stated on the served page.",
        "https://www.vestacyinfo.com/product.php?productLineId=2547":
            "Vestacy product ingredient disclosure for Air Wick, California SB-258, "
            "https://www.vestacyinfo.com/product.php?productLineId=2547 (HTTP 200), read 2026-10-16. Served "
            "HTML carries the complete 'Intentionally Added' list with a CAS per line and a separate "
            "fragrance-component section. No date of disclosure is stated on the served page.",
        "https://www.vestacyinfo.com/product.php?productLineId=2538":
            "Vestacy product ingredient disclosure for Air Wick, California SB-258, "
            "https://www.vestacyinfo.com/product.php?productLineId=2538 (HTTP 200), read 2026-10-16. Served "
            "HTML carries the complete 'Intentionally Added' list with a CAS per line and a separate "
            "fragrance-component section. No date of disclosure is stated on the served page.",
        "https://www.vestacyinfo.com/product.php?productLineId=3398":
            "Vestacy product ingredient disclosure for Air Wick, California SB-258, "
            "https://www.vestacyinfo.com/product.php?productLineId=3398 (HTTP 200), read 2026-10-16. Served "
            "HTML carries the complete 'Intentionally Added' list with a CAS per line and a separate "
            "fragrance-component section. No date of disclosure is stated on the served page.",
        "https://www.vestacyinfo.com/product.php?productLineId=3399":
            "Vestacy product ingredient disclosure for Air Wick, California SB-258, "
            "https://www.vestacyinfo.com/product.php?productLineId=3399 (HTTP 200), read 2026-10-16. Served "
            "HTML carries the complete 'Intentionally Added' list with a CAS per line and a separate "
            "fragrance-component section. No date of disclosure is stated on the served page.",
        ("https://whatsinsidescjohnson.com/en-us/brands/glade/sprays/odor-fighting-soft-mist-air-freshener/"
         "lavender-vanilla"):
            "SC Johnson's own ingredient-communication page for Glade, published under the California "
            "Cleaning Product Right to Know Act, "
            "https://whatsinsidescjohnson.com/en-us/brands/glade/sprays/odor-fighting-soft-mist-air-"
            "freshener/lavender-vanilla (HTTP 429 to curl from this sandbox, read in full by the fetch tool "
            "-- the recorded 'the answer can be a different TOOL' case; not a dead citation), read "
            "2026-10-16. The served page carries the complete intentionally-added list with a stated "
            "function per line, and the fragrance block at component level with SC Johnson's own "
            "skin-allergen markers. No date of disclosure is stated on the served page.",
        ("https://whatsinsidescjohnson.com/en-us/brands/glade/sprays/odor-fighting-soft-mist-air-freshener/"
         "clean-linen-air-freshener-spray"):
            "SC Johnson's own ingredient-communication page for Glade, published under the California "
            "Cleaning Product Right to Know Act, "
            "https://whatsinsidescjohnson.com/en-us/brands/glade/sprays/odor-fighting-soft-mist-air-"
            "freshener/clean-linen-air-freshener-spray (HTTP 429 to curl from this sandbox, read in full by "
            "the fetch tool; not a dead citation), read 2026-10-16. The served page carries the complete "
            "intentionally-added list with a stated function per line, and the fragrance block at component "
            "level with SC Johnson's own skin-allergen markers. No date of disclosure is stated on the "
            "served page.",
        ("https://www.churchdwight.com/ingredient-disclosure/commercial-professional/"
         "42000025-ah-deodorizing-air-freshener.aspx"):
            "Church & Dwight product ingredient disclosure form, California SB-258, "
            "https://www.churchdwight.com/ingredient-disclosure/commercial-professional/"
            "42000025-ah-deodorizing-air-freshener.aspx (HTTP 200), read 2026-10-16. The form's own PRODUCT "
            "NAME line reads \"Arm & Hammer\u2122 Deodorizing Air Freshener with Baking Soda\". Served page "
            "carries the complete 'Intentionally Added Ingredients' table and a separate fragrance-component "
            "table.",
    }

    added = []
    for rec in PRODUCTS:
        if rec["name"] in have:
            continue
        tier_note = (AW_TIER_NOTE if rec["brand"] == "Air Wick"
                     else GL_TIER_NOTE if rec["brand"] == "Glade"
                     else CD_TIER_NOTE)
        tier_src = (VESTACY_BRANDS if rec["brand"] == "Air Wick"
                    else SIMPORTER if rec["brand"] == "Glade"
                    else CANDY)
        p = {
            "name": rec["name"], "brand": rec["brand"], "cat": rec["cat"], "safe": None,
            "ings": rec["ings"], "heritage": False,
            "source": src_for(rec, ROUTES[rec["url"]]),
            "source_url": rec["url"],
            "note": rec["note"],
            "owner": brand_to_owner[rec["brand"]],
            "owner_ev": owners["owners"][brand_to_owner[rec["brand"]]]["ev"],
            "owner_src": owners["owners"][brand_to_owner[rec["brand"]]]["src"],
            "tier": "mass", "tier_ev": "reported", "tier_src": tier_src, "tier_note": tier_note,
            "substitutes": rec["substitutes"],
            "no_substitute_known": False, "no_substitute_note": None,
            "exposure": rec["exposure"], "exposure_ev": "extrapolated",
            "exposure_src": rec["exposure_src"], "exposure_basis": rec["exposure_basis"],
            "conc": None, "conc_src": None, "conc_ev": "untested",
            "grade_as_sold": None, "grade_as_sold_src": None,
            "strength_disclosure": "full", "disclosure_note": None,
            "added": TODAY, "updated": TODAY,
        }
        products.append(p)
        added.append(rec["name"])

    if not added and not minted:
        print("no change: nothing to add, nothing to mint (idempotent re-run)")
        return

    if added:
        changelog.insert(0, {
            "date": TODAY,
            "text": (f"Spectrum harvest station 2 (Dolman {TODAY}): {len(added)} air-care products added by "
                     f"exposure ({'; '.join(added)})"
                     + (f"; {len(minted)} new ungraded ingredient keys minted ({', '.join(minted)})"
                        if minted else "")
                     + ". Source: manufacturer-published California SB-258 disclosures (Vestacy for Air Wick, "
                       "SC Johnson for Glade, Church & Dwight for Arm & Hammer)."),
        })

    dump("products.json", products, 1)
    dump("ingredients.json", ingredients, 1)
    dump("owners.json", owners, 1)
    dump("changelog.json", changelog, 2)
    print(f"added {len(added)} products: {added}")
    print(f"minted {len(minted)} ingredient keys: {minted}")


if __name__ == "__main__":
    main()
