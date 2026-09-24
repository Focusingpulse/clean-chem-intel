#!/usr/bin/env python3
"""Spectrum build (station 2, 2026-09-24): exposure-ordered harvest.

Third night of the spectrum build. Ordering is by EXPOSURE, not price tier
(Sandra Sep 22, ordering set by Trellis). The four channel tiers
(dollar-store, drugstore, grocery, apothecary-bulk) are coverage targets, not
four sequential work orders, and an empty bin is not the goal.

This pass:

  1. Adds products whose ingredient lists are verified against a manufacturer
     disclosure, a published SDS, a state SB-258 private-label disclosure, or a
     retailer ingredient page. No invented grades. If the list cannot be
     verified, the product does not enter, and the absence is recorded as a
     finding in the findings file rather than as an empty product row.
  2. Fills exposure / exposure_ev / exposure_src (and exposure_basis where the
     estimate is derived). See docs/exposure.md.
  3. Assigns tier + tier_ev + tier_src where the purchase channel is defensible.
     tier_src is required on anything marked reported: a tier is a claim.
  4. Behind every D or F grade, names a usable same-price substitute and says
     in the note which hazard it avoids. Sandra's rule: document what to do.

Run: python3 tools/apply_spectrum_2026_09_24.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"

# ---------------------------------------------------------------- sources
SRC_HOUSEHOLDS = ("https://www.indexbox.io/store/united-states-laundry-home-products-"
                  "market-analysis-forecast-size-trends-and-insights/")
SRC_DISH_AMZ = "https://www.asinsight.com/market-analysis/US/dish-soap"
SRC_APC_AMZ = ("https://www.amazon.com/Best-Sellers-Health-Household-All-Purpose-"
               "Household-Cleaners/zgbs/hpc/15356141")

# --- new product sources, each read this fire ---
SRC_WINCO = ("https://cms-uploads-prd.mctimg.com/public/winco/wp-content/uploads/"
             "declarations/winco_foods_all_purpose_cleaner_with_bleach.pdf")
SRC_KIRKLAND_PB = ("https://customerservice.costco.com/euf/assets/answer_pdfs/"
                   "SDS%201677453%20-%20Kirkland%20Signature%20Ultra%20Shine%20"
                   "Plant-Based%20Dish%20Detergent.pdf")
SRC_KIRKLAND_PREM = ("https://www.msdsdigital.com/system/files/Kirkland-Signature-"
                     "Ultra-Shine-Premium-Dish-Soap-Citrus-Scent.pdf")
SRC_TARGET_LEMON = ("https://www.target.com/p/lemon-all-purpose-disinfecting-cleaner-"
                    "without-bleach-32oz-up-38-up-8482/-/A-90283206")
SRC_POWERHOUSE = "https://www.deltabrands.com/products/all-purpose-cleaner-with-bleach"
SRC_POWERHOUSE_CHANNEL = ("https://www.walgreens.com/store/c/productlist/"
                          "powerhouse-all-purpose-cleaner/N=20000912-9000150801")
SRC_PERCARB = "https://sds.chemicalstore.com/spc2010.pdf"
SRC_VINEGAR = "http://sds.staples.com/msds/24438939.pdf"
SRC_BSODA = ("https://churchdwight.com/ingredient-disclosure/household-products/"
             "40002501-arm-hammer-pure-baking-soda.aspx")
SRC_SOAPNUTS = "https://pmc.ncbi.nlm.nih.gov/articles/PMC9502486/"
SRC_SOAPNUTS_TOX = "https://hrcak.srce.hr/file/485163"

DERIVED = ("searched for a published per-product US household penetration figure; none "
           "exists in the open literature for a store-brand cleaner, so the estimate is "
           "derived from category penetration times the retailer's household reach. "
           "Rounded to one significant figure. Channel derivation, not a measured "
           "national share.")

UNSEARCHED = ("searched for a published per-product US household penetration figure or a "
              "channel sales figure covering this product; none located. The retailer "
              "listing confirms the channel and price but publishes no unit or household "
              "figure, so this is left as a research gap rather than a number shaped like "
              "an estimate.")


def prod(name, brand, cat, ings, tier, tier_src, tier_note,
         source, source_url, note, owner=None, owner_ev="untested", owner_src=None,
         substitutes=None, no_sub=False, no_sub_note=None, safe=None,
         exposure=None, exposure_ev="untested", exposure_src=None, exposure_basis=None,
         conc=None, conc_src=None, conc_ev="untested", strength_disclosure="not_reviewed"):
    return {
        "name": name, "brand": brand, "cat": cat, "safe": safe, "ings": ings,
        "heritage": False, "source": source, "source_url": source_url,
        "added": "2026-09-24", "updated": "2026-09-24", "note": note,
        "owner": owner, "owner_ev": owner_ev, "owner_src": owner_src,
        "tier": tier, "tier_ev": "reported", "tier_src": tier_src, "tier_note": tier_note,
        "substitutes": substitutes or [],
        "no_substitute_known": no_sub, "no_substitute_note": no_sub_note,
        "exposure": exposure, "exposure_ev": exposure_ev,
        "exposure_src": exposure_src, "exposure_basis": exposure_basis or UNSEARCHED,
        "conc": conc, "conc_src": conc_src, "conc_ev": conc_ev,
        "grade_as_sold": None, "grade_as_sold_src": None,
        "strength_disclosure": strength_disclosure,
    }


NEW = [
    # ------------------------------------------------------------ grocery
    prod(
        "WinCo Foods All Purpose Cleaner with Bleach", "WinCo Foods", "Disinfectant",
        ["Water", "Sodium Hypochlorite", "Sodium Hydroxide", "Lauramine Oxide", "Fragrance"],
        "grocery", SRC_WINCO,
        "WinCo Foods house brand, private label; the disclosure names WinCo as distributor "
        "and KIK International as manufacturer.",
        "WinCo Foods private-label chemical disclosure (California SB-258)",
        SRC_WINCO,
        "A rare case in this tier: a grocery private label that publishes its full "
        "intentionally-added list under California's Cleaning Product Right to Know Act. "
        "Sodium hypochlorite is the active and the disclosure still names the surfactant "
        "and the fragrance, which most bleach cleaners keep behind a trade-secret line. "
        "The bleach is the hazard; the short list is a strength, not a gap.",
        owner="WinCo Foods, LLC", owner_ev="reported", owner_src=SRC_WINCO,
        safe="Sifter grade F - worst credible dimension: derm F and env F (sodium "
             "hypochlorite, GHS H314 severe skin burns and eye damage, H400 aquatic "
             "toxicity; High evidence)",
        exposure=1, exposure_ev="extrapolated", exposure_src=SRC_HOUSEHOLDS,
        exposure_basis=DERIVED + (" WinCo is a western-US grocery chain (roughly 140 "
                                  "stores in 8 states, private and employee-owned); bleach "
                                  "all-purpose cleaner is a mainstream subsegment of "
                                  "surface care, which is 15 to 20 percent of the "
                                  "laundry-and-home category."),
        substitutes=[
            {"name": "Great Value Cleaning Vinegar All Purpose Cleaner", "tier": "grocery",
             "note": "Same price band, non-bleach, two disclosed ingredients. Avoids the "
                     "hypochlorite derm and aquatic grades entirely; weaker on mildew and "
                     "disinfection."},
            {"name": "Bon Ami cleansing powder", "tier": "grocery",
             "note": "Powder scouring alternative for sinks and tubs that avoids the bleach "
                     "load; check the feldspar silica entry if you use it on sealed stone."},
        ],
    ),
    prod(
        "Kirkland Signature Ultra Shine Plant-Based Dish Soap", "Kirkland Signature",
        "Dish",
        ["Sodium Lauryl Sulfate", "Glycerin", "Limonene"],
        "grocery", SRC_KIRKLAND_PB,
        "Costco house brand, warehouse channel; the SDS names Costco Wholesale as the "
        "supplier.",
        "Costco-published SDS (Clementine and Lemongrass scent)",
        SRC_KIRKLAND_PB,
        "The full composition is three substances. Sodium lauryl sulfate carries the "
        "cleaning load; limonene is the scent and is the severe one, graded on the aquatic "
        "and dermal dimensions. A plant-based label describes where the ingredients came "
        "from, not what they do.",
        owner="Costco Wholesale Corporation", owner_ev="reported", owner_src=SRC_KIRKLAND_PB,
        safe="Sifter grade F - worst credible dimension: env F (limonene, GHS H400 aquatic "
             "acute toxicity and H315/H317 skin hazard; High evidence)",
        exposure=2, exposure_ev="extrapolated", exposure_src=SRC_DISH_AMZ,
        exposure_basis=DERIVED + (" Liquid dish soap is owned by over 95 percent of "
                                  "households; the estimate is discounted for Costco's "
                                  "membership-household share and again for the plant-based "
                                  "niche within the Kirkland dish line."),
        substitutes=[
            {"name": "Kirkland Signature Ultra Shine Premium Dish Soap (Citrus Scent)",
             "tier": "grocery",
             "note": "Same brand, same warehouse price point. Avoids the limonene aquatic "
                     "grade; still carries sodium lauryl sulfate, so it is a scent fix "
                     "rather than a surfactant fix."},
        ],
    ),
    prod(
        "Kirkland Signature Ultra Shine Premium Dish Soap (Citrus Scent)",
        "Kirkland Signature", "Dish",
        ["Sodium Lauryl Sulfate"],
        "grocery", SRC_KIRKLAND_PREM,
        "Costco house brand, warehouse channel; the SDS names Costco Wholesale as "
        "distributor.",
        "Costco distributor SDS for the citrus-scent premium line",
        SRC_KIRKLAND_PREM,
        "One disclosed substance. The SDS records sodium lauryl sulfate at 5 to 10 percent "
        "and states no substance is hazardous at its given concentration. Sodium lauryl "
        "sulfate carries a moderate dermal grade, not a severe one, so no substitute is "
        "owed; the note is here because the near-identical sibling SKU is graded F.",
        owner="Costco Wholesale Corporation", owner_ev="reported",
        owner_src=SRC_KIRKLAND_PREM,
        exposure=2, exposure_ev="extrapolated", exposure_src=SRC_DISH_AMZ,
        exposure_basis=DERIVED + (" Same derivation as the plant-based Kirkland dish soap: "
                                  "dish-soap category penetration discounted for Costco's "
                                  "household share and for this line within the Kirkland "
                                  "dish range."),
    ),
    prod(
        "up&up Lemon All-Purpose Disinfecting Cleaner without Bleach", "up&up",
        "Disinfectant",
        ["Water", "Quaternary Ammonium", "Fragrance"],
        "grocery", SRC_TARGET_LEMON,
        "Target house brand, sold at Target (mass and grocery channel).",
        "Target product page publishing the EPA-registered active ingredients",
        SRC_TARGET_LEMON,
        "A mass-retailer house brand. The page publishes the two active quaternary ammonium "
        "blends and their chain-length splits, but the inactive fraction is not disclosed, "
        "so the fragrance and any other inerts sit behind the label. 'Without bleach' is "
        "not the same as 'without a hazard': the quat actives are the severe dimension here.",
        owner="Target Corporation", owner_ev="reported", owner_src=SRC_TARGET_LEMON,
        safe="Sifter grade F - worst credible dimension: derm F and env F (alkyl dimethyl "
             "benzyl ammonium chloride actives, GHS H302/H314/H400; High evidence)",
        exposure=1, exposure_ev="extrapolated", exposure_src=SRC_APC_AMZ,
        exposure_basis=DERIVED + (" Disinfecting sprays are a large subsegment of surface "
                                  "care, which is 15 to 20 percent of the laundry-and-home "
                                  "category; discounted for Target's household share and "
                                  "for the up&up line within the retailer's cleaner shelf."),
        substitutes=[
            {"name": "Great Value Cleaning Vinegar All Purpose Cleaner", "tier": "grocery",
             "note": "Same price band, two disclosed ingredients. Avoids the quaternary "
                     "ammonium actives and the undisclosed inactive fraction; not a "
                     "disinfectant, so it will not carry an EPA kill claim."},
        ],
    ),
    # ------------------------------------------------------------ drugstore
    prod(
        "PowerHouse All Purpose Cleaner with Bleach", "PowerHouse", "Disinfectant",
        ["Water", "Sodium Hypochlorite", "Sodium Hydroxide",
         "Compound Based on Anionic and Nonionic Surfactants", "Fragrance"],
        "drugstore", SRC_POWERHOUSE_CHANNEL,
        "Sold through the Walgreens drugstore channel as its value cleaning line; the "
        "brand itself is owned by Delta Brands, not by Walgreens.",
        "Manufacturer product page publishing the ingredient table",
        SRC_POWERHOUSE,
        "Ownership note, and it is the kind of thing a value brand hides: PowerHouse looks "
        "like a Walgreens house brand because it sits on the Walgreens value shelf at about "
        "a dollar fifty, but the manufacturer page names Delta Brands and Products LLC as "
        "the owner. The channel is Walgreens; the brand is not. The surfactant line is "
        "described as a class rather than a substance, which is itself a disclosure gap.",
        owner="Delta Brands & Products LLC", owner_ev="reported", owner_src=SRC_POWERHOUSE,
        safe="Sifter grade F - worst credible dimension: derm F and env F (sodium "
             "hypochlorite, GHS H314/H318/H400; High evidence)",
        exposure=1, exposure_ev="extrapolated", exposure_src=SRC_HOUSEHOLDS,
        exposure_basis=DERIVED + (" Drugstore value-brand cleaners reach the shoppers who "
                                  "use the pharmacy aisle for household staples; the "
                                  "estimate is derived from bleach-cleaner subsegment share "
                                  "of surface care discounted for the Walgreens value shelf."),
        substitutes=[
            {"name": "Great Value Cleaning Vinegar All Purpose Cleaner", "tier": "grocery",
             "note": "Non-bleach alternative at the same price band. Avoids the "
                     "hypochlorite and the undisclosed surfactant class; carries no "
                     "disinfectant claim."},
        ],
    ),
    # ------------------------------------------------------------ apothecary / bulk
    prod(
        "Sodium Percarbonate (bulk)", "commodity", "Specialty",
        ["Sodium Percarbonate", "Sodium Carbonate", "Sodium Silicate"],
        "apothecary-bulk", SRC_PERCARB,
        "Sold by the pound or kilo as an oxygen-bleach powder; no brand story, the product "
        "is the chemistry.",
        "Solvay FB Sodium Percarbonate SDS (composition table)",
        SRC_PERCARB,
        "The ingredient tier in its purest form: the powder is roughly 85 percent sodium "
        "carbonate peroxyhydrate with the balance sodium carbonate and a little sodium "
        "silicate as a stabiliser. This is what an oxygen-bleach product is made of before "
        "a brand puts it in a tub and doubles the price. The oxidizer classification is "
        "real, so the household-strength alternative below is a genuine downgrade in risk, "
        "not a rebrand.",
        owner="commodity", owner_ev="reported", owner_src=SRC_PERCARB,
        safe="Sifter grade D - worst credible dimension: derm D (sodium percarbonate, GHS "
             "H272 oxidizer, H302 harmful if swallowed, H318 serious eye damage; High "
             "evidence)",
        substitutes=[
            {"name": "Hydrogen Peroxide 3% (drugstore)", "tier": "drugstore",
             "note": "The same oxygen-bleaching chemistry at a pre-diluted household "
                     "strength. Avoids the solid-oxidizer fire risk and the concentrated "
                     "eye-damage grade; sold at the same dollar price band as a small "
                     "percarbonate tub."},
            {"name": "Washing soda (sodium carbonate)", "tier": "grocery",
             "note": "Buys the alkalinity without the peroxide. Avoids the oxidizer "
                     "classification entirely; as a result it lifts grease and softens "
                     "water but does not brighten or deodorise the way percarbonate does."},
        ],
    ),
    prod(
        "Distilled White Vinegar (5%)", "commodity", "Specialty",
        ["Water", "Acetic Acid"],
        "apothecary-bulk", SRC_VINEGAR,
        "Sold as a food-grade acid by the gallon and used as a cleaner; the product is the "
        "chemistry.",
        "Distilled white vinegar SDS (5 percent acidity, composition table)",
        SRC_VINEGAR,
        "Two substances and both are on the label, which makes this the most disclosed "
        "cleaner in the database. It is also the sharpest test of the two-level grading "
        "rule: the acetic acid ingredient entry is graded F as the pure acid, and this "
        "product is graded as sold. At 5 percent it is an eye and skin irritant, not a "
        "corrosive, so the product does not inherit the concentrated grade. The ingredient "
        "record is not softened to match; the two grades coexist.",
        owner="commodity", owner_ev="reported", owner_src=SRC_VINEGAR,
        conc="5% acetic acid by weight", conc_src=SRC_VINEGAR, conc_ev="verified",
        strength_disclosure="stated",
        exposure=None, exposure_ev="untested", exposure_src=None,
        exposure_basis=("searched for a published penetration figure for distilled white "
                        "vinegar as a purchased cleaning product as distinct from a food "
                        "ingredient; household availability is near-universal but no "
                        "cleaner-use figure was located, so no number is recorded."),
    ),
    prod(
        "Baking Soda (bulk)", "commodity", "Specialty",
        ["Sodium Bicarbonate"],
        "apothecary-bulk", SRC_BSODA,
        "Sold by the box and the bulk bag as a single-substance commodity; usable as a "
        "mild abrasive and deodoriser.",
        "Manufacturer ingredient disclosure (sodium bicarbonate)",
        SRC_BSODA,
        "One substance, no fragrance, no surfactant, no preservative. It is the default "
        "non-abrasive scouring substitute in this database, which is why it is entered as a "
        "product rather than only as an ingredient: a person reading a D grade on a cream "
        "cleanser needs its name and its price band. Graded no-hazard at Medium evidence; "
        "the substance record says why.",
        owner="commodity", owner_ev="reported", owner_src=SRC_BSODA,
        exposure=None, exposure_ev="untested", exposure_src=None,
        exposure_basis=("searched for a published per-product US household penetration "
                        "figure for baking soda as a cleaning product; the box is near "
                        "universal in US kitchens but the sources located describe it as a "
                        "food ingredient, so a cleaning-use figure was not recorded."),
    ),
    prod(
        "Soap Nuts (Sapindus mukorossi)", "commodity", "Laundry",
        ["Sapindus Saponins"],
        "apothecary-bulk", SRC_SOAPNUTS,
        "Sold dried by weight in refill shops and bulk aisles; the product is the fruit "
        "pericarp, and the cleaning agent is the saponin it contains.",
        "Peer-reviewed review of Sapindus mukorossi saponins (surfactant properties)",
        SRC_SOAPNUTS,
        "The refill-shop alternative people reach for because it has no label chemicals. "
        "The honest picture is mixed: the saponins are genuine surfactants, comparable to a "
        "commercial detergent on greasy and oily soil, but they are poor on protein stains "
        "(no enzymes), and one 2023 wastewater study found soapnut effluent acutely more "
        "toxic to zebrafish than commercial detergent, so it is not automatically the softer "
        "environmental choice. The substance has no harmonised hazard classification, and "
        "the record says that rather than implying safety.",
        owner="commodity", owner_ev="reported", owner_src=SRC_SOAPNUTS,
        exposure=None, exposure_ev="untested", exposure_src=None,
        exposure_basis=("searched for a published penetration figure for soap nuts as a US "
                        "laundry product; none located. The market is small and largely "
                        "unmeasured, so this is recorded as a research gap."),
    ),
]

# new ingredient records: only where the substance is genuinely not in the file
NEW_INGS = {
    "Sapindus Saponins": {
        "g": "Not Classified",
        "s": "No harmonised GHS classification located for the saponin extract",
        "ev": "Low",
        "gr": {},
        "impacts": [],
        "note": ("The triterpenoid saponins of Sapindus mukorossi are the surfactant in "
                 "soap nuts. No harmonised GHS classification exists and the toxicology is "
                 "thin, so this is recorded as no-classification with weak evidence rather "
                 "than graded: grading a substance with no harmonised classification would "
                 "be invention. What the literature does say, and it cuts both ways: the "
                 "saponins reduce water surface tension below 40 mN/m and match a "
                 "commercial detergent on greasy and oily soil, while a 2023 wastewater "
                 "study found soapnut effluent acutely more toxic to zebrafish than "
                 "commercial detergent, with saponin degradation slow enough that treatment "
                 "matters. Compare Quillaja Saponaria Bark Extract, which carries the same "
                 "grading gap."),
        "src": SRC_SOAPNUTS_TOX,
    },
}

# owner records: apply_owners() writes owner from this file on every build, so a
# brand missing here is silently stamped untested. That is what happened to the
# two 'commodity' products added on 2026-09-23.
NEW_OWNERS = {
    "Costco Wholesale Corporation": {
        "type": "public (COST)",
        "detail": "Owns and distributes the Kirkland Signature house brand, sold only on "
                  "Costco shelves.",
        "ev": "reported",
        "src": SRC_KIRKLAND_PB,
        "brands": ["Kirkland Signature"],
    },
    "Target Corporation": {
        "type": "public (TGT)",
        "detail": "Owns the up&up house brand.",
        "ev": "reported",
        "src": SRC_TARGET_LEMON,
        "brands": ["up&up"],
    },
    "WinCo Foods, LLC": {
        "type": "private, employee-owned",
        "detail": "Western-US grocery chain. Its All Purpose Cleaner with Bleach is "
                  "distributed by WinCo and manufactured by KIK International.",
        "ev": "reported",
        "src": SRC_WINCO,
        "brands": ["WinCo Foods"],
    },
    "Delta Brands & Products LLC": {
        "type": "private",
        "detail": "Owns the PowerHouse value brand. The brand is sold through the Walgreens "
                  "value shelf and other retailers; Walgreens is the channel, not the owner, "
                  "which the value presentation is designed not to make obvious.",
        "ev": "reported",
        "src": SRC_POWERHOUSE,
        "brands": ["PowerHouse"],
    },
    "Greenbrier International": {
        "type": "private",
        "detail": "Dollar Tree's product-development and import arm; the FDA labeler of "
                  "record for Assured-brand products.",
        "ev": "reported",
        "src": "https://ndclist.com/ndc/33992-3033/label",
        "brands": ["Assured"],
    },
    "Dollar General Corporation": {
        "type": "public (DG)",
        "detail": "Owns the True Living house brand.",
        "ev": "reported",
        "src": ("https://www.dollargeneral.com/p/true-living-multi-purpose-cleaner-"
                "lavender-scent-56-fl-oz/59647560446"),
        "brands": ["True Living"],
    },
    "Dollar Tree, Inc.": {
        "type": "public (DLTR)",
        "detail": "Owns Family Dollar; the Homeline house brand sits under it.",
        "ev": "reported",
        "src": ("https://sameday.familydollar.com/store/family-dollar/products/"
                "20662818-homeline-all-purpose-cleaner-lemon-scented-1-qt"),
        "brands": ["Homeline"],
    },
    "commodity": {
        "type": "n/a - no brand owner",
        "detail": "Commodity goods sold by the pound or out of a bulk bin, with no brand "
                  "owner to hold accountable. Recorded as 'commodity', which is not a "
                  "company and is not the same as an unexamined gap. Without this entry "
                  "apply_owners() silently stamped the two commodity products added on "
                  "2026-09-23 back to untested on the next build; the field was reverting.",
        "ev": "reported",
        "src": "https://pubchem.ncbi.nlm.nih.gov/",
        "brands": ["commodity"],
    },
}


def main():
    products = json.loads((DATA / "products.json").read_text(encoding="utf-8"))
    ings = json.loads((DATA / "ingredients.json").read_text(encoding="utf-8"))
    owners = json.loads((DATA / "owners.json").read_text(encoding="utf-8"))

    # ---- ingredients ----
    n_ing = 0
    for k, v in NEW_INGS.items():
        if k not in ings:
            ings[k] = v
            n_ing += 1
    (DATA / "ingredients.json").write_text(
        json.dumps(ings, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---- owners ----
    n_own = 0
    for k, v in NEW_OWNERS.items():
        if k not in owners["owners"]:
            owners["owners"][k] = v
            n_own += 1
    (DATA / "owners.json").write_text(
        json.dumps(owners, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---- products ----
    existing = {p["name"] for p in products}
    added = []
    for np_ in NEW:
        if np_["name"] in existing:
            print("  skip (already present):", np_["name"])
            continue
        products.append(np_)
        added.append(np_["name"])

    CLAIM_REVIEW = {
        "WinCo Foods All Purpose Cleaner with Bleach": {
            "ev": "reported", "src": SRC_WINCO,
            "result": "no_safety_claim_located",
            "note": ("Searched the WinCo private-label SB-258 disclosure and the WinCo "
                     "product listing for a safety assertion. WinCo publishes the full "
                     "ingredient list and a hazard caution and makes no safety or efficacy "
                     "claim; the bleach itself is the active and the caution names it. "
                     "Absence of a safety claim is not reassurance."),
        },
        "Kirkland Signature Ultra Shine Plant-Based Dish Soap": {
            "ev": "reported", "src": SRC_KIRKLAND_PB,
            "result": "no_safety_claim_located",
            "note": ("Searched the Costco-published SDS for the plant-based dish line. It "
                     "publishes hazard statements (dermal and inhalation acute toxicity, "
                     "skin sensitisation) and makes no safety or 'gentle' claim. The "
                     "plant-based marketing sits on the retail page, not in the SDS; no "
                     "safety assertion was located on the manufacturer's own document."),
        },
        "up&up Lemon All-Purpose Disinfecting Cleaner without Bleach": {
            "ev": "reported", "src": SRC_TARGET_LEMON,
            "result": "no_safety_claim_located",
            "note": ("Searched the Target product page. Target publishes the EPA-registered "
                     "actives and a kill claim (COVID-19, flu) and a 'without bleach' "
                     "framing. The kill claim is an efficacy claim, not a safety claim, and "
                     "the 'without bleach' line names an ingredient it excludes rather than "
                     "asserting the product is safe. No safety assertion was located."),
        },
        "PowerHouse All Purpose Cleaner with Bleach": {
            "ev": "reported", "src": SRC_POWERHOUSE,
            "result": "no_safety_claim_located",
            "note": ("Searched the Delta Brands product page, which is the manufacturer's "
                     "own listing. It publishes an ingredient and function table and a "
                     "sales line about bleach variants outselling standard ones. No safety "
                     "or 'non-toxic' claim was located on the manufacturer page."),
        },
        "Sodium Percarbonate (bulk)": {
            "ev": "reported", "src": SRC_PERCARB,
            "result": "no_safety_claim_located",
            "note": ("Searched the Solvay FB Sodium Percarbonate SDS, which is the "
                     "manufacturer's own document. It publishes hazard statements and "
                     "handling controls and makes no safety claim. For a commodity sold by "
                     "the pound there is no consumer-facing page that would carry one."),
        },
    }

    n_review = 0
    for p in products:
        cr = CLAIM_REVIEW.get(p["name"])
        if cr and p["name"] in added:
            p["claim_review"] = cr
            n_review += 1

    # ---- claim reviews for the new severe-grade products ----
    # The severe-grade warning names any D/F product with no manufacturer claim
    # on file. A warning that names the same products every build is alarm
    # fatigue, so each new severe product carries a written review: what was
    # searched, and the page it was searched against. An absence with no source
    # is indistinguishable from an absence nobody looked for.
    # ---- tier backfill: house brands already in the catalog that share a
    # retailer with a product added tonight, where the channel is defensible.
    TIER_BACKFILL = {}
    n_tier = 0
    for p in products:
        t = TIER_BACKFILL.get(p["name"])
        if t:
            p["tier"], p["tier_ev"], p["tier_src"], p["tier_note"] = t
            n_tier += 1

    (DATA / "products.json").write_text(
        json.dumps(products, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"ingredients added: {n_ing}")
    print(f"owner records added: {n_own}")
    print(f"claim reviews attached: {n_review}")
    print(f"tier backfilled: {n_tier}")
    print(f"products added: {len(added)}")
    for a in added:
        print("  +", a)
    print(f"catalog now {len(products)} products, {len(ings)} ingredients")


if __name__ == "__main__":
    main()
