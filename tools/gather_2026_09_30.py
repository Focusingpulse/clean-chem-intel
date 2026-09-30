#!/usr/bin/env python3
"""Daily gather (2026-09-30, 10:00Z maintenance lane): four high-volume US
products that were missing from the database, plus the ingredient records they
need.

Sources read on 2026-09-30:

  - Liquid-Plumr Pro-Strength Clog Destroyer Gel with PipeGuard — the Clorox
    SmartLabel ingredient disclosure for UPC 044600002217 (updated 2026-03-25).
    https://smartlabel.labelinsight.com/product/6096885/ingredients
  - Softsoap Antibacterial Liquid Hand Soap Pump, Gentle Clean, Sparkling Pear —
    the Colgate-Palmolive SmartLabel disclosure for UPC 35000985408 (updated
    2024-05-29).
    https://www.colgatepalmolive.com/en-us/smartlabel/35000985408
  - Dial Complete Foaming Antibacterial Hand Wash, Spring Water — the FDA
    DailyMed OTC drug label (SPL) for NDC 54340-249, labeler The Dial
    Corporation, a Henkel company. An OTC drug label is the manufacturer's own
    regulatory filing and names the active at its declared strength, which is
    the same structure as an EPA-listed SDS.
    https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=0a70d7e2-d29f-27cc-e054-00144ff8d46c
  - Air Wick Scented Oil, Ocean Spray — the Reckitt SmartLabel ingredient
    disclosure (UPC 0-62338-02326-7), published under the California Cleaning
    Product Right to Know Act at component level.
    https://www.rbnainfo.com/smart-label.php?productLineId=3404

Why these four: the largest verifiable gaps left in the corpus by category are
drain care, antibacterial hand soap and plug-in air care. Each of the four
publishes a full intentionally-added list, which is the entry ticket; a product
whose formula is withheld does not enter.

Canonical-key mappings (no new keys minted) are recorded per product in
`disclosure_note`:
  - "FD&C Blue No. 1" -> Blue 1 (PubChem CID 19700 returns title "FD&C Blue No. 1")
  - "d-Limonene" -> Limonene
  - "Fragrance/Parfum" -> Fragrance
  - "Eucalyptus oil" kept as the DB's existing key

Grading follows the house rule (docs/source-policy.md, docs/scoring-rubric.md):
only H-codes at >=40% ECHA C&L notifier consensus drive a dimension grade, read
from PubChem PUG View. UVCB / polymer / botanical substances with no discrete
PubChem CID are recorded "Extrapolated" with an explicit sourcing note, never
graded. Every returned PubChem title was checked against the intended substance
before the record was accepted; where the title is a systematic name or a trade
synonym for the intended material, that is stated in the note.

Nothing here is product-graded. Product grading is the Sifter lane; a blank
as-sold grade is the honest state, and substitutes[] is left empty for the same
reason (the substitute rule binds on a D/F grade, and none of these carries one
yet).

Run: python3 tools/gather_2026_09_30.py
Then: python3 build.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
TODAY = "2026-09-30"

PLUMR = "https://smartlabel.labelinsight.com/product/6096885/ingredients"
SOFTSOAP = "https://www.colgatepalmolive.com/en-us/smartlabel/35000985408"
DIAL = ("https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm"
        "?setid=0a70d7e2-d29f-27cc-e054-00144ff8d46c")
AIRWICK = "https://www.rbnainfo.com/smart-label.php?productLineId=3404"

BASE_BASIS = ("searched for a published per-product US household penetration figure; none "
              "exists in the open literature, so the estimate is derived from category "
              "penetration times the brand's share of its channel. Rounded to one "
              "significant figure. ")


# ---------------------------------------------------------------- ingredients
NEW_INGS = {
    # ---- Liquid-Plumr
    "Cetyl Betaine": {
        "g": "H319,H317,H315,H302",
        "s": "Betaine surfactant. Causes skin irritation and serious eye irritation.",
        "ev": "Medium",
        "gr": {"derm": "C"},
        "impacts": ["derm"],
        "note": "Graded from PubChem GHS (CID 93554, returned title "
                "'n-(carboxymethyl)-n,n-dimethyl-1-hexadecanaminium hydroxide, inner salt' - "
                "the systematic name for the C16 alkylbetaine the disclosure calls 'Cetyl "
                "betaine', CAS 693-33-4). H315 74.2% -> derm C; H319 78.8% (eye irritation, "
                "subsumed). H317 13.6% (skin sensitization) and H302 16.7% fall below the house "
                ">=40% consensus bar and are noted, not graded. Disclosed by the Clorox "
                "SmartLabel for Liquid-Plumr Pro-Strength Clog Destroyer Gel with PipeGuard.",
    },
    # ---- Dial
    "Benzethonium Chloride": {
        "g": "H410,H400,H318,H314,H302,H301",
        "s": "Quaternary ammonium antibacterial. Toxic if swallowed; causes severe skin burns "
             "and eye damage; very toxic to aquatic life.",
        "ev": "High",
        "gr": {"derm": "F", "env": "F", "work": "D"},
        "impacts": ["derm", "aqua"],
        "note": "Graded from PubChem GHS (CID 8478, returned title 'Benzethonium Chloride' - "
                "matches; CAS 121-54-0). H314 95.2% -> derm F; H400 94.4% -> env F; H301 81% -> "
                "work D; H318 47.5% and H410 84% are subsumed by the stronger codes. H302 17.5% "
                "falls below the house bar. The declared active (0.20%) in Dial Complete Foaming "
                "Antibacterial Hand Wash, per the DailyMed SPL for NDC 54340-249.",
    },
    "Hydroxypropyl Methylcellulose": {
        "g": "Extrapolated",
        "s": "Cellulose-derived polymer (hypromellose). Polymer; no discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "Cellulose-derived polymer (hypromellose). PubChem PUG REST returns no CID for "
                "the name (404); it is a polymer family, not a discrete substance. Recorded "
                "extrapolated by polymer class rather than invented. Disclosed by the DailyMed "
                "SPL for Dial Complete Foaming Antibacterial Hand Wash (NDC 54340-249).",
    },
    "Chlorhexidine Digluconate": {
        "g": "H410,H400,H334,H318,H317,H302",
        "s": "Antiseptic biguanide. Causes serious eye damage; very toxic to aquatic life.",
        "ev": "High",
        "gr": {"derm": "D", "env": "F"},
        "impacts": ["derm", "aqua"],
        "note": "Graded from PubChem GHS (CID 9552081, returned title 'Chlorhexidine Gluconate' "
                "- the digluconate salt the SPL names, CAS 18472-51-0). H318 68.5% -> derm D; "
                "H400 87.6% -> env F; H410 87.3% subsumed. H317 (skin sensitization) and H334 "
                "(respiratory sensitization) appear in PubChem's aggregated view without notifier "
                "percentages and are noted, not graded. Disclosed by the DailyMed SPL for Dial "
                "Complete Foaming Antibacterial Hand Wash (NDC 54340-249).",
    },
    "Zinc Sulfate": {
        "g": "H410,H400,H372,H371,H361,H318,H302",
        "s": "Harmful if swallowed; causes serious eye damage; very toxic to aquatic life.",
        "ev": "High",
        "gr": {"derm": "D", "env": "F", "work": "D"},
        "impacts": ["derm", "aqua"],
        "note": "Graded from PubChem GHS (CID 24424, returned title 'Zinc Sulfate' - matches; "
                "CAS 7733-02-0). H318 99.8% -> derm D; H400 96.6% -> env F; H302 94.2% -> work D; "
                "H410 94.2% subsumed. H361 (suspected reproductive toxicity), H371 and H372 "
                "(organ damage) appear in PubChem's aggregated view without notifier percentages "
                "and are noted, not graded. Disclosed by the DailyMed SPL for Dial Complete "
                "Foaming Antibacterial Hand Wash (NDC 54340-249).",
    },
    "PEG-9": {
        "g": "H335,H319,H315",
        "s": "Polyethylene glycol (PEG-9). Causes skin and serious eye irritation; may cause "
             "respiratory irritation.",
        "ev": "Medium",
        "gr": {"derm": "C", "resp": "C"},
        "impacts": ["derm", "resp"],
        "note": "Graded from PubChem GHS (CID 4867, returned title 'Nonaethylene glycol' - the "
                "discrete nine-unit oligomer the disclosure calls 'PEG-9'; the polymer family is "
                "CAS 25322-68-3). H319 100% and H315 66.7% -> derm C; H335 66.7% -> resp C. "
                "Disclosed by the DailyMed SPL for Dial Complete Foaming Antibacterial Hand Wash "
                "(NDC 54340-249).",
    },
    "Sunflowerseedamidopropyl Ethyldimonium Ethosulfate": {
        "g": "Extrapolated",
        "s": "Quaternary ammonium conditioning surfactant (sunflower-derived). No discrete "
             "PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "Quaternary ammonium conditioning surfactant. PubChem PUG REST returns no CID for "
                "the name (404); it is a trade-named surfactant, not a discrete substance with a "
                "PubChem record. Recorded extrapolated by surfactant class rather than invented; "
                "the DB's sibling quaternary ammonium entries (benzalkonium chloride, "
                "benzethonium chloride) carry derm F / env F grades, which is a class signal, not "
                "a grade for this substance. Disclosed by the DailyMed SPL for Dial Complete "
                "Foaming Antibacterial Hand Wash (NDC 54340-249).",
    },
    # ---- Air Wick Scented Oil, Ocean Spray (fragrance components)
    "Benzyl Acetate": {
        "g": "H412,H401,H373,H372,H370,H336,H319,H315,H303,H227",
        "s": "Fragrance ester. Harmful to aquatic life with long lasting effects.",
        "ev": "Medium",
        "gr": {"env": "C"},
        "impacts": ["aqua"],
        "note": "Graded from PubChem GHS (CID 8785, returned title 'Benzyl acetate' - matches; "
                "CAS 140-11-4). H412 62.6% -> env C. H227, H303, H315, H319, H336, H370, H372, "
                "H373 and H401 appear in PubChem's aggregated view without notifier percentages "
                "and are noted, not graded. Disclosed as a fragrance component by the Reckitt "
                "SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
    "Jasmacyclene": {
        "g": "H412,H226",
        "s": "Fragrance ester (verdyl acetate). Harmful to aquatic life with long lasting "
             "effects.",
        "ev": "Medium",
        "gr": {"env": "C"},
        "impacts": ["aqua"],
        "note": "Graded from PubChem GHS (CID 110655, returned title 'Verdyl acetate' - the "
                "systematic name for the fragrance material the disclosure calls 'Jasmacyclene'; "
                "CAS 2500-83-6). H412 47.7% -> env C; H226 24.5% is a physical hazard, below the "
                "house bar and not a graded dimension. Disclosed as a fragrance component by the "
                "Reckitt SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
    "2-tert-Butylcyclohexyl Acetate": {
        "g": "H411,H410,H400,H373,H351,H336",
        "s": "Fragrance ester. Toxic to aquatic life with long lasting effects.",
        "ev": "High",
        "gr": {"env": "D"},
        "impacts": ["aqua"],
        "note": "Graded from PubChem GHS (CID 62334, returned title '2-tert-Butylcyclohexyl "
                "acetate' - matches; CAS 88-41-5). H411 96.9% -> env D. H336, H351 (suspected "
                "carcinogen), H373, H400 and H410 appear in PubChem's aggregated view without "
                "notifier percentages and are noted, not graded. Disclosed as a fragrance "
                "component by the Reckitt SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
    "Tripropylene Glycol Methyl Ether": {
        "g": "Not Classified",
        "s": "Glycol ether solvent (PPG-3 methyl ether). No GHS hazard criteria met by the "
             "notifier majority.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem GHS (CID 25054, returned title '1-Propanol, "
                "2-(2-(2-methoxypropoxy)propoxy)-' - the systematic name for the glycol ether the "
                "disclosure calls 'Tripropylene Glycol Methyl Ether (PPG-3 Methyl Ether)'; CAS "
                "25498-49-1). H319 and H336 appear in the aggregated view without notifier "
                "percentages; no code reaches the house >=40% consensus bar, so no dimension "
                "grade is justified. Disclosed as a fragrance component by the Reckitt SmartLabel "
                "for Air Wick Scented Oil, Ocean Spray.",
    },
    "Allyl Hexanoate": {
        "g": "H412,H411,H410,H400,H331,H319,H315,H311,H301,H227",
        "s": "Fragrance ester. Toxic if swallowed or in contact with skin; toxic if inhaled; "
             "very toxic to aquatic life.",
        "ev": "High",
        "gr": {"work": "D", "resp": "D", "env": "F"},
        "impacts": ["resp", "aqua"],
        "note": "Graded from PubChem GHS (CID 31266, returned title 'Allyl caproate' - the "
                "synonym for the ester the disclosure calls 'Allyl hexanoate'; CAS 123-68-2). "
                "H311 97.2% and H301 94.9% -> work D; H331 76.4% -> resp D; H400 80.2% -> env F; "
                "H412 78.8% subsumed. H315 13.3%, H319 10.3%, H410 11.8% and H411 14% fall below "
                "the house >=40% consensus bar and are noted, not graded. Disclosed as a "
                "fragrance component by the Reckitt SmartLabel for Air Wick Scented Oil, Ocean "
                "Spray.",
    },
    "beta-Pinene": {
        "g": "H335,H331,H317,H315,H304,H226",
        "s": "Terpene. May be fatal if swallowed and enters airways; skin irritant and "
             "sensitizer.",
        "ev": "High",
        "gr": {"derm": "D"},
        "impacts": ["derm", "allerg"],
        "note": "Graded from PubChem GHS (CID 14896, returned title 'Beta-Pinene' - matches; CAS "
                "127-91-3). H317 97.5% -> derm D (sensitizer, tagged allerg); H315 81.9% -> derm "
                "C (subsumed). H226 99.7% and H304 99.7% are physical/aspiration hazards and are "
                "not graded dimensions; H400 26.1% and H410 30.2% fall below the house bar. H331 "
                "and H335 appear without notifier percentages and are noted, not graded. "
                "Disclosed as a fragrance component by the Reckitt SmartLabel for Air Wick "
                "Scented Oil, Ocean Spray.",
    },
    "Eucalyptol": {
        "g": "H317,H226",
        "s": "Terpene oxide (1,8-cineole). May cause an allergic skin reaction.",
        "ev": "High",
        "gr": {"derm": "D"},
        "impacts": ["derm", "allerg"],
        "note": "Graded from PubChem GHS (CID 2758, returned title '1,8-Cineole' - the systematic "
                "name for the terpene oxide the disclosure calls 'Eucalyptol'; CAS 470-82-6). "
                "H317 84.2% -> derm D (sensitizer, tagged allerg); H226 98.7% is a physical "
                "hazard and is not a graded dimension. Disclosed as a fragrance component by the "
                "Reckitt SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
    "gamma-Undecalactone": {
        "g": "Not Classified",
        "s": "Lactone fragrance (peach). No GHS hazard criteria met by the notifier majority.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem GHS (CID 7714, returned title 'Gamma-undecalactone' - matches; CAS "
                "104-67-6). H411 10.3% and H412 19.3% fall below the house >=40% consensus bar; "
                "H401 appears without a notifier percentage. No dimension grade is justified. "
                "Disclosed as a fragrance component by the Reckitt SmartLabel for Air Wick "
                "Scented Oil, Ocean Spray.",
    },
    "Hexenyl Acetate": {
        "g": "Not Classified",
        "s": "Fragrance ester (cis-3-hexenyl acetate). No GHS health or environmental hazard "
             "criteria met by the notifier majority.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem GHS (CID 5363388, returned title 'cis-3-HEXENYL ACETATE' - matches the "
                "fragrance material the disclosure calls 'Hexenyl Acetate'; CAS 3681-71-8). The "
                "only code at >=40% consensus is H226 (flammability, 99.4%), a physical hazard "
                "that is not a graded dimension; no health or environmental grade is justified. "
                "Disclosed as a fragrance component by the Reckitt SmartLabel for Air Wick "
                "Scented Oil, Ocean Spray.",
    },
    "Hydroxycitronellol": {
        "g": "Not Classified",
        "s": "Fragrance alcohol. No GHS hazard criteria met by the notifier majority.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem GHS (CID 249494, returned title '3,7-Dimethyl-1,7-octanediol' - the "
                "systematic name for the fragrance alcohol the disclosure calls "
                "'Hydroxycitronellol', CAS 107-74-4; distinct from the aldehyde "
                "hydroxycitronellal, CAS 107-75-5). 1520 of 1669 reporting companies (91.1%) "
                "report not meeting hazard criteria; no code reaches the house bar. Disclosed as "
                "a fragrance component by the Reckitt SmartLabel for Air Wick Scented Oil, Ocean "
                "Spray.",
    },
    "Longifolene": {
        "g": "H410,H400,H317,H304",
        "s": "Sesquiterpene. May be fatal if swallowed and enters airways; skin sensitizer; very "
             "toxic to aquatic life.",
        "ev": "High",
        "gr": {"derm": "D", "env": "F"},
        "impacts": ["derm", "allerg", "aqua"],
        "note": "Graded from PubChem GHS (CID 1796220, returned title 'Longifolene' - matches; "
                "CAS 475-20-7). H317 95.8% -> derm D (sensitizer, tagged allerg); H400 99.8% -> "
                "env F; H410 98% subsumed. H304 95.8% is an aspiration hazard and is not a graded "
                "dimension. Disclosed as a fragrance component by the Reckitt SmartLabel for Air "
                "Wick Scented Oil, Ocean Spray.",
    },
    "Methyldihydrojasmonate": {
        "g": "Not Classified",
        "s": "Fragrance ester (methyl dihydrojasmonate / Hedione). No GHS hazard criteria met by "
             "the notifier majority.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem GHS (CID 102861, returned title 'Hedione' - the trade name for methyl "
                "dihydrojasmonate, the material the disclosure calls 'Methyldihydrojasmonate'; "
                "CAS 24851-98-7). 1818 of 1820 reporting companies (99.9%) report not meeting "
                "hazard criteria; H301, H311, H314, H318 and H330 appear in the aggregated view "
                "without notifier percentages and are noted, not graded. Disclosed as a fragrance "
                "component by the Reckitt SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
    "Phenethyl Alcohol": {
        "g": "H371,H361,H336,H319,H318,H311,H302",
        "s": "Fragrance alcohol. Harmful if swallowed; causes serious eye irritation.",
        "ev": "High",
        "gr": {"work": "D", "derm": "C"},
        "impacts": ["derm"],
        "note": "Graded from PubChem GHS (CID 6054, returned title '2-Phenylethanol' - the "
                "systematic name for the fragrance alcohol the disclosure calls 'Phenethyl "
                "Alcohol'; CAS 60-12-8). H319 94.5% -> derm C; H302 81.5% -> work D. H311, H336, "
                "H361, H371 and H318 appear in PubChem's aggregated view without notifier "
                "percentages and are noted, not graded. Disclosed as a fragrance component by the "
                "Reckitt SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
    "Decanal": {
        "g": "H412,H335,H319,H315,H227",
        "s": "Aldehyde fragrance. Causes serious eye irritation; harmful to aquatic life with "
             "long lasting effects.",
        "ev": "High",
        "gr": {"derm": "C", "env": "C"},
        "impacts": ["derm", "aqua"],
        "note": "Graded from PubChem GHS (CID 8175, returned title 'Decanal' - matches; CAS "
                "112-31-2). H319 91.2% -> derm C; H412 92.1% -> env C. H315 21.9% falls below the "
                "house bar; H227 and H335 appear without notifier percentages and are noted, not "
                "graded. Disclosed as a fragrance component by the Reckitt SmartLabel for Air "
                "Wick Scented Oil, Ocean Spray.",
    },
    "Octanal": {
        "g": "H411,H401,H319,H315,H226",
        "s": "Aldehyde fragrance. Causes skin and serious eye irritation; toxic to aquatic life "
             "with long lasting effects.",
        "ev": "High",
        "gr": {"derm": "C", "env": "D"},
        "impacts": ["derm", "aqua"],
        "note": "Graded from PubChem GHS (CID 454, returned title 'Octanal' - matches; CAS "
                "124-13-0). H315 97.4% and H319 97.3% -> derm C; H411 77.1% -> env D. H226 93.3% "
                "is a physical hazard and is not a graded dimension; H412 19.8% falls below the "
                "house bar; H401 appears without a notifier percentage and is noted, not graded. "
                "Disclosed as a fragrance component by the Reckitt SmartLabel for Air Wick "
                "Scented Oil, Ocean Spray.",
    },
    "Terpineol": {
        "g": "H335,H319,H315,H227",
        "s": "Terpene alcohol. Causes skin and serious eye irritation.",
        "ev": "High",
        "gr": {"derm": "C"},
        "impacts": ["derm"],
        "note": "Graded from PubChem GHS (CID 17100, returned title 'Alpha-Terpineol' - the "
                "isomer the disclosure calls 'Terpineol'; the mixed terpineol is CAS 8000-41-7 "
                "and the CID is alpha-terpineol, CAS 98-55-5). H315 98.9% and H319 81.8% -> derm "
                "C. H227 and H335 appear without notifier percentages and are noted, not graded. "
                "Disclosed as a fragrance component by the Reckitt SmartLabel for Air Wick "
                "Scented Oil, Ocean Spray.",
    },
    "Isopropyl Myristate": {
        "g": "Not Classified",
        "s": "Emollient ester. No GHS hazard criteria met by the notifier majority.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem GHS (CID 8042, returned title 'Isopropyl Myristate' - matches; CAS "
                "110-27-0). The only code, H315 (skin irritation), is reported at 15.6%, below "
                "the house >=40% consensus bar; no dimension grade is justified. Disclosed as a "
                "fragrance component by the Reckitt SmartLabel for Air Wick Scented Oil, Ocean "
                "Spray.",
    },
    "(E)-1-(2,6,6-Trimethyl-2-Cyclohexen-1-Yl)-2-Buten-1-One": {
        "g": "H411,H317,H302",
        "s": "Fragrance ketone (damascone-type). Harmful if swallowed; skin sensitizer; toxic to "
             "aquatic life with long lasting effects.",
        "ev": "High",
        "gr": {"work": "D", "derm": "D", "env": "D"},
        "impacts": ["derm", "allerg", "aqua"],
        "note": "Graded from PubChem GHS (CID 5366077, returned title "
                "'(E)-1-(2,6,6-trimethylcyclohex-2-en-1-yl)but-2-en-1-one' - matches; CAS "
                "24720-09-0). H317 99.8% -> derm D (sensitizer, tagged allerg); H302 99.7% -> "
                "work D; H411 81.4% -> env D. Disclosed as a fragrance component by the Reckitt "
                "SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
    "2,4-Dimethyl-3-Cyclohexene Carboxaldehyde": {
        "g": "H412,H411,H319,H317,H315",
        "s": "Aldehyde fragrance. Causes skin irritation; skin sensitizer; toxic to aquatic life "
             "with long lasting effects.",
        "ev": "High",
        "gr": {"derm": "D", "env": "D"},
        "impacts": ["derm", "allerg", "aqua"],
        "note": "Graded from PubChem GHS (CID 93375, returned title "
                "'2,4-Dimethyl-3-cyclohexene carboxaldehyde' - matches; CAS 68039-49-6). H317 "
                "99.7% -> derm D (sensitizer, tagged allerg); H315 99.8% and H319 43.3% -> derm C "
                "(subsumed); H411 62.7% -> env D. H412 37% falls below the house bar. Disclosed "
                "as a fragrance component by the Reckitt SmartLabel for Air Wick Scented Oil, "
                "Ocean Spray.",
    },
    "2,6-Dimethyl-5-Heptenal": {
        "g": "Not Classified",
        "s": "Aldehyde fragrance (melon). No GHS health or environmental hazard criteria met by "
             "the notifier majority.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem GHS (CID 61016, returned title '(+/-)-2,6-Dimethyl-5-heptenal' - "
                "matches; CAS 106-72-9). H226 86.6% is a physical hazard and is not a graded "
                "dimension; H317 11.2% falls below the house >=40% consensus bar. No dimension "
                "grade is justified. Disclosed as a fragrance component by the Reckitt SmartLabel "
                "for Air Wick Scented Oil, Ocean Spray.",
    },
    "2,6-Octadienal, 3,7-Dimethyl-, Reaction Products With Et Alc.": {
        "g": "Extrapolated",
        "s": "Reaction product of citral with ethanol. UVCB reaction mixture; no discrete "
             "PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "Reaction product of citral (3,7-dimethyl-2,6-octadienal) with ethanol - a UVCB "
                "reaction mixture, not a discrete substance. PubChem PUG REST returns no CID for "
                "the name (404). Recorded extrapolated rather than invented; the parent citral is "
                "graded derm C / env C in this database. Disclosed as a fragrance component by "
                "the Reckitt SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
    "2-Methylundecanal": {
        "g": "H412,H410,H400,H319,H317,H315",
        "s": "Aldehyde fragrance. Causes skin irritation; skin sensitizer; very toxic to aquatic "
             "life.",
        "ev": "High",
        "gr": {"derm": "D", "env": "F"},
        "impacts": ["derm", "allerg", "aqua"],
        "note": "Graded from PubChem GHS (CID 61031, returned title '2-Methylundecanal' - "
                "matches; CAS 110-41-8). H317 85.7% -> derm D (sensitizer, tagged allerg); H315 "
                ">99.9% -> derm C (subsumed); H400 84.1% -> env F; H410 80% subsumed. H319 11.2% "
                "and H412 14.3% fall below the house bar. Disclosed as a fragrance component by "
                "the Reckitt SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
    "3,4,4a,5,8,8a-Hexahydro-3',6-dimethylspiro[1,4-methanonaphtalene-2(1H),2'-oxirane]": {
        "g": "Not Classified",
        "s": "Fragrance (spiro-epoxide). No GHS hazard criteria met by the notifier majority.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem GHS (CID 94521, returned title "
                "'3,4,4a,5,8,8a-hexahydro-3',6-dimethylspiro[1,4-methanonaphthalene-2(1H),2'-"
                "oxirane]' - matches; CAS 41723-98-2). The only code, H411 (aquatic toxicity), is "
                "reported at 12.7%, below the house >=40% consensus bar; no dimension grade is "
                "justified. Disclosed as a fragrance component by the Reckitt SmartLabel for Air "
                "Wick Scented Oil, Ocean Spray.",
    },
    "3-Hexenol": {
        "g": "H319,H226",
        "s": "Fragrance alcohol (leaf alcohol). Causes serious eye irritation.",
        "ev": "High",
        "gr": {"derm": "C"},
        "impacts": ["derm"],
        "note": "Graded from PubChem GHS (CID 5281167, returned title '3-Hexenol' - matches; CAS "
                "928-96-1). H319 83.6% -> derm C; H226 99.2% is a physical hazard and is not a "
                "graded dimension. Disclosed as a fragrance component by the Reckitt SmartLabel "
                "for Air Wick Scented Oil, Ocean Spray.",
    },
    "6,6-Dimethoxy-2,5,5-trimethylhex-2-ene": {
        "g": "H412,H319,H315",
        "s": "Fragrance acetal. Causes skin and serious eye irritation; harmful to aquatic life "
             "with long lasting effects.",
        "ev": "High",
        "gr": {"derm": "C", "env": "C"},
        "impacts": ["derm", "aqua"],
        "note": "Graded from PubChem GHS (CID 106766, returned title "
                "'6,6-Dimethoxy-2,5,5-trimethylhex-2-ene' - matches; CAS 67674-46-8). H315 100% "
                "and H319 91.1% -> derm C; H412 >99.9% -> env C. Disclosed as a fragrance "
                "component by the Reckitt SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
    "Allyl (Cyclohexyloxy)Acetate": {
        "g": "H412,H410,H315,H302",
        "s": "Fragrance ester. Harmful if swallowed; causes skin irritation; harmful to aquatic "
             "life with long lasting effects.",
        "ev": "High",
        "gr": {"work": "D", "derm": "C", "env": "C"},
        "impacts": ["derm", "aqua"],
        "note": "Graded from PubChem GHS (CID 111727, returned title 'Allyl "
                "cyclohexyloxyacetate' - matches; CAS 68901-15-5). H302 99.8% -> work D; H315 "
                "88.7% -> derm C; H412 88.7% -> env C. H410 11.1% falls below the house bar. "
                "Disclosed as a fragrance component by the Reckitt SmartLabel for Air Wick "
                "Scented Oil, Ocean Spray.",
    },
    "cis-3-Hexenyl Methyl Carbonate": {
        "g": "Not Classified",
        "s": "Fragrance carbonate. No GHS hazard criteria met by the notifier majority.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem GHS (CID 5365699, returned title 'Hex-3-en-1-yl methyl carbonate, "
                "(3Z)-' - matches; CAS 67633-96-9). 1548 of 1679 reporting companies (92.2%) "
                "report not meeting hazard criteria; no code reaches the house bar. Disclosed as "
                "a fragrance component by the Reckitt SmartLabel for Air Wick Scented Oil, Ocean "
                "Spray.",
    },
    "Citrus Limon (Lemon) Peel Oil": {
        "g": "Extrapolated",
        "s": "Cold-pressed lemon peel oil. Botanical UVCB; no discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "Cold-pressed lemon peel oil - a botanical UVCB, not a discrete substance. "
                "PubChem PUG REST returns no CID for the name (404). Recorded extrapolated rather "
                "than invented; its principal constituent d-limonene is graded derm D / env F in "
                "this database, and the oil carries the EU fragrance-allergen labeling "
                "requirement. Disclosed as a fragrance component by the Reckitt SmartLabel for "
                "Air Wick Scented Oil, Ocean Spray.",
    },
    "Ethyl 2-Methylpentanoate": {
        "g": "Not Classified",
        "s": "Fragrance ester. No GHS health or environmental hazard criteria met by the "
             "notifier majority.",
        "ev": "Medium",
        "gr": {},
        "impacts": [],
        "note": "PubChem GHS (CID 62902, returned title 'Ethyl 2-methylpentanoate' - matches; CAS "
                "39255-32-8). The only code at >=40% consensus is H226 (>99.9%, flammability), a "
                "physical hazard that is not a graded dimension; no health or environmental grade "
                "is justified. Disclosed as a fragrance component by the Reckitt SmartLabel for "
                "Air Wick Scented Oil, Ocean Spray.",
    },
    "Floral Pyranol": {
        "g": "H319",
        "s": "Fragrance (floral pyranol). Causes serious eye irritation.",
        "ev": "High",
        "gr": {"derm": "C"},
        "impacts": ["derm"],
        "note": "Graded from PubChem GHS (CID 3017432, returned title "
                "'Tetrahydro-4-methyl-2-(2-methylpropyl)-2H-pyran' - the systematic name for the "
                "fragrance material the disclosure calls 'Floral Pyranol'; CAS 63500-71-0). H319 "
                ">99.9% -> derm C. Disclosed as a fragrance component by the Reckitt SmartLabel "
                "for Air Wick Scented Oil, Ocean Spray.",
    },
    "Isobutenyl Methyltetrahydropyran": {
        "g": "H361,H319,H315",
        "s": "Fragrance (rose oxide). Causes skin and serious eye irritation; suspected "
             "reproductive toxicity.",
        "ev": "High",
        "gr": {"derm": "C", "repro": "C"},
        "impacts": ["derm", "repro"],
        "note": "Graded from PubChem GHS (CID 27866, returned title 'Rose oxide' - the fragrance "
                "material the disclosure calls 'Isobutenyl Methyltetrahydropyran'; CAS "
                "16409-43-1). H315 95.1% and H319 92.7% -> derm C; H361 87.5% -> repro C "
                "(suspected reproductive toxicity). Disclosed as a fragrance component by the "
                "Reckitt SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
    "Isopropylphenylbutanal": {
        "g": "H411,H315",
        "s": "Fragrance aldehyde (Florhydral). Toxic to aquatic life with long lasting effects.",
        "ev": "High",
        "gr": {"env": "D"},
        "impacts": ["aqua"],
        "note": "Graded from PubChem GHS (CID 86209, returned title 'Florhydral' - the trade name "
                "for the fragrance aldehyde the disclosure calls 'Isopropylphenylbutanal'; CAS "
                "125109-85-5). H411 100% -> env D; H315 32.5% falls below the house >=40% "
                "consensus bar and is noted, not graded. Disclosed as a fragrance component by "
                "the Reckitt SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
    "Methyl Benzodioxepinone": {
        "g": "H302",
        "s": "Fragrance (Calone-type). Harmful if swallowed.",
        "ev": "High",
        "gr": {"work": "D"},
        "impacts": [],
        "note": "Graded from PubChem GHS (CID 120101, returned title 'Methyl "
                "benzodioxepinone' - matches; CAS 28940-11-6). H302 94.9% -> work D. Disclosed as "
                "a fragrance component by the Reckitt SmartLabel for Air Wick Scented Oil, Ocean "
                "Spray.",
    },
    "Nona-2-Trans-6-Cis-Dienal": {
        "g": "H317,H315",
        "s": "Aldehyde fragrance (violet leaf). Causes skin irritation; skin sensitizer.",
        "ev": "High",
        "gr": {"derm": "D"},
        "impacts": ["derm", "allerg"],
        "note": "Graded from PubChem GHS (CID 643731, returned title 'trans-2,cis-6-Nonadienal' - "
                "matches; CAS 557-48-2). H317 92.7% -> derm D (sensitizer, tagged allerg); H315 "
                "90.5% -> derm C (subsumed). Disclosed as a fragrance component by the Reckitt "
                "SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
    "Nympheal": {
        "g": "H411,H332,H317,H315",
        "s": "Fragrance aldehyde (Nympheal). Causes skin irritation; skin sensitizer; harmful if "
             "inhaled; toxic to aquatic life with long lasting effects.",
        "ev": "High",
        "gr": {"derm": "D", "resp": "C", "env": "D"},
        "impacts": ["derm", "allerg", "resp", "aqua"],
        "note": "Graded from PubChem GHS (CID 17877030, returned title "
                "'3-(4-Isobutyl-2-methylphenyl)propanal' - the systematic name for the fragrance "
                "material the disclosure calls 'Nympheal'; CAS 1637294-12-2). H317 100% -> derm D "
                "(sensitizer, tagged allerg); H315 100% -> derm C (subsumed); H332 96.6% -> resp "
                "C; H411 100% -> env D. Disclosed as a fragrance component by the Reckitt "
                "SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
    "Orange Oil, Sweet, Terpenes": {
        "g": "Extrapolated",
        "s": "Terpene fraction of sweet orange oil. Botanical UVCB; no discrete PubChem CID.",
        "ev": "Extrapolated",
        "gr": {},
        "impacts": [],
        "note": "Terpene fraction of sweet orange oil - a botanical UVCB, not a discrete "
                "substance. PubChem PUG REST returns no CID for the name (404). Recorded "
                "extrapolated rather than invented; its principal constituent d-limonene is "
                "graded derm D / env F in this database. Disclosed as a fragrance component by "
                "the Reckitt SmartLabel for Air Wick Scented Oil, Ocean Spray.",
    },
}


# ------------------------------------------------------------------ products
def prod(name, brand, cat, ings, tier, tier_ev, tier_src, exposure, exposure_ev,
         exposure_src, exposure_basis, subs=None, no_sub=None, tier_note=None,
         heritage=None, owner=None, owner_ev="untested", owner_src=None,
         disclosure_note=None, source=None, source_url=None):
    p = {
        "name": name,
        "brand": brand,
        "cat": cat,
        "safe": None,
        "ings": ings,
        "added": TODAY,
        "updated": TODAY,
        "owner": owner,
        "owner_ev": owner_ev,
        "owner_src": owner_src,
        "tier": tier,
        "tier_ev": tier_ev,
        "tier_src": tier_src,
        "substitutes": subs or [],
        "exposure": exposure,
        "exposure_ev": exposure_ev,
        "exposure_src": exposure_src,
        "conc": None,
        "conc_src": None,
        "conc_ev": "untested",
        "grade_as_sold": None,
        "grade_as_sold_src": None,
        "strength_disclosure": "not_reviewed",
        "exposure_basis": exposure_basis,
    }
    if source:
        p["source"] = source
    if source_url:
        p["source_url"] = source_url
    if tier_note:
        p["tier_note"] = tier_note
    if no_sub:
        p["no_substitute_known"] = no_sub
    if heritage:
        p["heritage"] = True
        p["heritage_year"] = heritage[0]
        p["heritage_note"] = heritage[1]
    if disclosure_note:
        p["disclosure_note"] = disclosure_note
    return p


PRODUCTS = [
    prod("Liquid-Plumr Pro-Strength Clog Destroyer Gel with PipeGuard", "Liquid-Plumr",
         "Specialty",
         ["Water", "Sodium Hypochlorite", "Sodium Chloride", "Sodium Hydroxide",
          "Cetyl Betaine", "Sodium Xylene Sulfonate", "Sodium Orthosilicate",
          "Sodium Carbonate"],
         "mass", "reported", PLUMR,
         5, "extrapolated", PLUMR,
         BASE_BASIS + "Liquid-Plumr is the leading US drain-care brand; the gel Clog "
                      "Destroyer is its flagship SKU. No per-product penetration figure "
                      "exists, so the estimate stops at the brand's share of the drain-care "
                      "category rather than a measured product share.",
         owner="The Clorox Company", owner_ev="reported", owner_src=PLUMR,
         disclosure_note="The Clorox SmartLabel for UPC 044600002217 (updated 2026-03-25) is "
                         "the manufacturer's own current disclosure and names every "
                         "intentionally-added component; no canonical-key remapping was "
                         "needed. The companion foaming SKU (UPC 044600002149) carries the "
                         "same base plus hydrogen peroxide, sulfuric acid and a confidential "
                         "stabilizer package, so the gel and the foam are not the same formula.",
         source="Clorox SmartLabel ingredient disclosure",
         source_url=PLUMR,
         tier_note="A mainstream drain cleaner sold at mass retail. The label carries a "
                   "bleach-and-lye formula: sodium hypochlorite (the bleach) plus sodium "
                   "hydroxide (lye) plus sodium orthosilicate, which is why the product "
                   "carries corrosive warnings and a 'do not mix with other drain cleaners' "
                   "instruction. The disclosure is unusually complete for the category."),

    prod("Softsoap Antibacterial Liquid Hand Soap Pump, Gentle Clean, Sparkling Pear",
         "Softsoap", "Hand Soap",
         ["Water", "Benzalkonium Chloride", "Cetrimonium Chloride", "Glycerin",
          "Lauramidopropylamine Oxide", "Cocamide MEA", "Citric Acid", "Sodium Benzoate",
          "Fragrance", "PEG-120 Methyl Glucose Dioleate", "Sodium Chloride",
          "Tetrasodium EDTA", "Blue 1", "Yellow 5"],
         "mass", "reported", SOFTSOAP,
         8, "extrapolated", SOFTSOAP,
         BASE_BASIS + "Softsoap is the leading US liquid hand-soap brand; the antibacterial "
                      "pump is its highest-volume line. No per-product penetration figure "
                      "exists, so the estimate stops at the brand's share of the hand-soap "
                      "category rather than a measured product share.",
         owner="Colgate-Palmolive", owner_ev="reported", owner_src=SOFTSOAP,
         disclosure_note="Source spelling mapped to canonical key: 'FD&C Blue No. 1' -> Blue 1 "
                         "(PubChem CID 19700 returns title 'FD&C Blue No. 1'). The "
                         "Colgate-Palmolive SmartLabel for UPC 35000985408 (updated "
                         "2024-05-29) is the manufacturer's own current disclosure and "
                         "separates the active from the inactive ingredients.",
         source="Colgate-Palmolive SmartLabel ingredient disclosure",
         source_url=SOFTSOAP,
         tier_note="A mass-market antibacterial hand soap. The active is benzalkonium "
                   "chloride, a quaternary ammonium compound; the base is a betaine/amine-oxide "
                   "surfactant blend with a fragrance that is not broken out by component. "
                   "Entered ungraded: product grading is the Sifter lane."),

    prod("Dial Complete Foaming Antibacterial Hand Wash, Spring Water", "Dial", "Hand Soap",
         ["Water", "Benzethonium Chloride", "Glycerin", "Lauramine Oxide", "Fragrance",
          "Sunflowerseedamidopropyl Ethyldimonium Ethosulfate", "PEG-9",
          "Cocamidopropyl Betaine", "Hydroxypropyl Methylcellulose", "DMDM Hydantoin",
          "Chlorhexidine Digluconate", "Citric Acid", "Zinc Sulfate", "Tetrasodium EDTA",
          "Blue 1", "Red 33"],
         "mass", "reported", DIAL,
         8, "extrapolated", DIAL,
         BASE_BASIS + "Dial is a leading US antibacterial hand-soap brand; Complete is its "
                      "flagship foaming line. No per-product penetration figure exists, so "
                      "the estimate stops at the brand's share of the hand-soap category "
                      "rather than a measured product share.",
         owner="Henkel", owner_ev="reported", owner_src=DIAL,
         disclosure_note="The FDA DailyMed OTC drug label (SPL) for NDC 54340-249 is the "
                         "labeler's own regulatory filing and names the active "
                         "(benzethonium chloride 0.20%) at its declared strength, plus the "
                         "full inactive list. This is the same structure as an EPA-listed "
                         "SDS: a government host serving a manufacturer document. The label "
                         "names The Dial Corporation, a Henkel company, as labeler of record.",
         source="FDA DailyMed OTC drug label (SPL), NDC 54340-249",
         source_url=DIAL,
         tier_note="A mass-market foaming antibacterial hand soap. The active is "
                   "benzethonium chloride, a quaternary ammonium compound; the inactive list "
                   "also names chlorhexidine digluconate (an antiseptic) and DMDM hydantoin "
                   "(a formaldehyde-releasing preservative). Two antimicrobial actives plus a "
                   "preservative is a heavier antimicrobial load than the Softsoap sibling."),

    prod("Air Wick Scented Oil, Ocean Spray", "Air Wick", "Specialty",
         ["Fragrance", "Isopropylideneglycerol", "Dipropylene Glycol", "Benzyl Acetate",
          "Jasmacyclene", "4-tert-Butylcyclohexyl Acetate", "2-tert-Butylcyclohexyl Acetate",
          "Tripropylene Glycol Methyl Ether", "Water", "Terpineol", "Dihydromyrcenol",
          "Allyl Hexanoate", "Orange Oil, Sweet, Terpenes", "Limonene", "Isopropyl Myristate",
          "(E)-1-(2,6,6-Trimethyl-2-Cyclohexen-1-Yl)-2-Buten-1-One",
          "2,4-Dimethyl-3-Cyclohexene Carboxaldehyde", "2,6-Dimethyl-5-Heptenal",
          "2,6-Octadienal, 3,7-Dimethyl-, Reaction Products With Et Alc.", "2-Methylundecanal",
          "3,4,4a,5,8,8a-Hexahydro-3',6-dimethylspiro[1,4-methanonaphtalene-2(1H),2'-oxirane]",
          "3-Hexenol", "6,6-Dimethoxy-2,5,5-trimethylhex-2-ene", "Allyl (Cyclohexyloxy)Acetate",
          "beta-Pinene", "cis-3-Hexenyl Methyl Carbonate", "Citral",
          "Citrus Limon (Lemon) Peel Oil", "Decanal", "Denatonium Benzoate",
          "Ethyl 2-Methylpentanoate", "Eucalyptol", "Eucalyptus Oil", "Floral Pyranol",
          "gamma-Undecalactone", "Hexenyl Acetate", "Hexyl Acetate", "Hydroxycitronellol",
          "Isobutenyl Methyltetrahydropyran", "Isopropylphenylbutanal", "Linalool",
          "Longifolene", "Methyl Benzodioxepinone", "Methyldihydrojasmonate",
          "Nona-2-Trans-6-Cis-Dienal", "Nympheal", "Octanal", "Phenethyl Alcohol"],
         "mass", "reported", AIRWICK,
         8, "extrapolated", AIRWICK,
         BASE_BASIS + "Air Wick is one of the two leading US air-care brands (the sibling "
                      "Glade PlugIns record carries an extrapolated exposure of 9); the "
                      "plug-in scented-oil refill is the brand's highest-volume format. No "
                      "per-product penetration figure exists, so the estimate stops at the "
                      "brand's share of the plug-in air-freshener category rather than a "
                      "measured product share.",
         owner="Reckitt", owner_ev="reported", owner_src=AIRWICK,
         disclosure_note="Source spellings mapped to canonical keys: 'Fragrance/Parfum' -> "
                         "Fragrance; 'd-Limonene' -> Limonene; 'Eucalyptus oil' kept as the "
                         "DB's existing key. The Reckitt SmartLabel (UPC 0-62338-02326-7) is "
                         "the manufacturer's own disclosure, published under the California "
                         "Cleaning Product Right to Know Act, and resolves the fragrance into "
                         "named components instead of a single 'fragrance' line. The page "
                         "flags which components sit on a California designated list and "
                         "which are EU fragrance allergens.",
         source="Reckitt SmartLabel ingredient disclosure (California Cleaning Product Right "
                "to Know Act)",
         source_url=AIRWICK,
         tier_note="A plug-in scented-oil air freshener. This is the disclosure that most of "
                   "the category does not make: an air freshener is normally a single line "
                   "reading 'fragrance', which is an unidentifiable blend. Reckitt publishes "
                   "the blend at component level, so it resolves into named substances "
                   "instead of staying a blank. The formula is a fragrance oil in a glycol "
                   "solvent base with a bittering agent (denatonium benzoate). Entered "
                   "ungraded: product grading is the Sifter lane."),
]


def main():
    prods = json.loads((DATA / "products.json").read_text(encoding="utf-8"))
    ings = json.loads((DATA / "ingredients.json").read_text(encoding="utf-8"))

    existing = {p.get("name") for p in prods}
    added_ings = []
    for name, rec in NEW_INGS.items():
        if name not in ings:
            ings[name] = rec
            added_ings.append(name)

    added_prods = []
    for p in PRODUCTS:
        if p["name"] in existing:
            continue
        prods.append(p)
        added_prods.append(p["name"])

    (DATA / "products.json").write_text(
        json.dumps(prods, indent=1, ensure_ascii=False), encoding="utf-8")
    (DATA / "ingredients.json").write_text(
        json.dumps(ings, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"products added: {len(added_prods)} -> {len(prods)} total")
    for n in added_prods:
        print("  +", n)
    print(f"ingredients added: {len(added_ings)} -> {len(ings)} total")
    for n in added_ings:
        print("  +", n)


if __name__ == "__main__":
    main()
