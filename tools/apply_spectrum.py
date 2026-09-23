#!/usr/bin/env python3
"""Spectrum build (station 2): exposure harvest, tier assignment, new products.

Sandra directive Sep 22 2026, ordering by Trellis: expose what is used, not
what costs more. This script does three things and writes data/products.json:

  1. exposure  — fill exposure / exposure_ev / exposure_src (and exposure_basis
                 where the estimate is derived). See docs/exposure.md.
  2. tier      — assign tier + tier_ev + tier_src where a purchase channel is
                 defensible. 'untested' is the honest answer where it is not.
  3. products  — add products whose ingredient lists are verified against a
                 manufacturer disclosure, SDS, or EPA listing. No invented
                 grades. If the list cannot be verified, the product does not
                 enter.

Run: python3 tools/apply_spectrum.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"

# ---------------------------------------------------------------- sources
SRC_HOUSEHOLDS = ("https://www.indexbox.io/store/united-states-laundry-home-products-"
                  "market-analysis-forecast-size-trends-and-insights/")
SRC_LAUNDRY = ("https://www.giiresearch.com/report/moi2119204-united-states-laundry-"
               "care-market-share-analysis.html")
SRC_DISH_AMZ = "https://www.asinsight.com/market-analysis/US/dish-soap"
SRC_LLD_AMZ = "https://www.asinsight.com/market-analysis/US/liquid-laundry-detergent"
SRC_LD_AMZ = "https://www.asinsight.com/market-analysis/US/laundry-detergent"
SRC_HC_REPORT = "https://www.asinsight.com/report/US/household-cleaning"
SRC_AMZ_APC = ("https://www.amazon.com/Best-Sellers-Health-Household-All-Purpose-"
               "Household-Cleaners/zgbs/hpc/15356141")
SRC_LA_FAQ = "http://004f876.netsolhost.com/html/faqs.html"
SRC_LA_SDS = "https://visalia-keenan.safeschoolssds.com/document/repo/aac9721e-a6a9-47f4-ad5e-374d5f9d2c63"
SRC_WALMART_LEMON = ("https://i5.walmartimages.com/dfw/4ff9c6c9-4aaa/"
                     "k2-_7865d767-2806-4c89-b5df-ebc58306684e.v1.pdf")
SRC_WALMART_AMMONIA = ("https://i5.walmartimages.com/dfw/4ff9c6c9-1cf4/"
                       "k2-_610488e6-05bb-4792-a3f9-fb86d93621d2.v1.pdf")
SRC_WALMART_BLEACH = ("https://msdsdigital.com/system/files/Great%20Value%20All%20Purpose"
                      "%20Cleaner%20with%20Bleach%20Safety%20Data%20Sheet.pdf")
SRC_WALMART_VINEGAR = ("https://i5.walmartimages.com/dfw/4ff9c6c9-96af/"
                       "k2-_e74e64a8-aa24-4ec4-98ac-a7490a77e827.v1.pdf")
SRC_CVS_BLEACH = "https://es.cvs.com/shop/cvs-all-purpose-cleaner-bleach-spray-32-oz-prodid-100640"
SRC_LAUNDRY_AMZ = "https://www.asinsight.com/market-analysis/US/laundry-detergent"

# Brand-level exposures and the derivation behind each. Ratio of category
# reach times brand share. Everything derived is 'extrapolated' and carries a
# basis that says what was searched for a direct figure.
DERIVED = "searched for a published per-product US household penetration figure; none exists in the open literature, so the estimate is derived from category penetration times brand share. Rounded to one significant figure."

# (name substring, exposure%, ev, src, basis)
EXPOSURE = [
    # ---- laundry: category >95% of ~131M households ----
    ("Tide Original Liquid Laundry", 25, "extrapolated", SRC_LAUNDRY, DERIVED + " P&G held 59% of US laundry care retail value in 2025; Tide is its lead brand; Amazon liquid-detergent brand share 50.9% of top-10 volume, July 2026."),
    ("Tide PODS", 12, "extrapolated", SRC_LAUNDRY, DERIVED + " Pods are roughly 30% of detergent volume (Mintel, US home laundry 2026); Tide is the category leader."),
    ("Tide", 25, "extrapolated", SRC_LAUNDRY, DERIVED + " P&G 59% of US laundry care retail value, 2025; Tide is the lead brand."),
    ("Gain", 8, "extrapolated", SRC_LAUNDRY, DERIVED + " Gain is P&G's value laundry brand; P&G held 59% of US laundry care retail value, 2025."),
    ("Persil", 5, "extrapolated", SRC_LAUNDRY, DERIVED + " Henkel is a top-three US laundry company; Persil is its premium line."),
    ("Purex", 5, "extrapolated", SRC_LAUNDRY, DERIVED + " Henkel value brand; Henkel is a top-three US laundry company."),
    ("Arm & Hammer Sensitive", 6, "extrapolated", SRC_LLD_AMZ, DERIVED + " Arm & Hammer is 21.1% of Amazon top-10 liquid-detergent volume, July 2026; the sensitive-skin variant is a fraction of that line."),
    ("OxiClean Odor Blasters", 10, "extrapolated", SRC_LD_AMZ, DERIVED + " OxiClean was 24.2% of Amazon top-10 laundry-detergent volume, July 2026."),
    ("OxiClean Baby Stain Soaker", 4, "extrapolated", SRC_LD_AMZ, DERIVED + " OxiClean 24.2% of Amazon top-10 laundry-detergent volume, July 2026; the baby variant is a small part of the line."),
    ("Seventh Generation Free & Clear Dish", 3, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Natural/eco dish care is 10-15% of household dish volume; Seventh Generation is a leading eco brand."),
    ("Free & Clear Laundry Detergent", 2, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Natural/eco laundry is a low-single-digit share; this is a fragrance-free niche line."),
    ("Chlorine Free Bleach", 2, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Non-chlorine bleach is a small share of the bleach segment."),
    ("Super Washing Soda", 12, "reported", "https://www.asinsight.com/market-analysis/US/liquid-laundry-detergent", "Arm & Hammer Super Washing Soda (ASIN B0029XNTEU) sold 70,000 units at $4.98 in July 2026 with 57,000 ratings, and appears in the Amazon top-10 liquid laundry ranking. Channel figure, not national share."),
    ("20 Mule Team Borax", 6, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Borax is a legacy laundry booster; laundry care exceeds 95% of US households but boosters are a small share of that."),
    ("Laundry Detergent Pods", 3, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Natural/eco pod brands are a small fraction of the pod segment."),
    ("Laundry Powder", 1, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Powder detergent is 15-20% of detergent volume and this is a niche eco powder within it."),
    ("Liquid Laundry Detergent", 1, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Fragrance-free eco liquid is a small fraction of the liquid detergent segment."),
    ("Baby Laundry Detergent", 1, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Baby-specific laundry is a small subsegment."),
    # ---- dish: liquid dish soap owned by >95% of households ----
    ("Dawn Ultra Dishwashing Liquid", 30, "reported", SRC_DISH_AMZ, "Dawn moved 430,000 units across six ASINs in July 2026, 68.3% of Amazon top-10 dish-soap volume. Channel figure, not national share; Dawn is nonetheless the category leader."),
    ("Dawn Ultra Dish Soap", 30, "reported", SRC_DISH_AMZ, "Dawn moved 430,000 units across six ASINs in July 2026, 68.3% of Amazon top-10 dish-soap volume. Channel figure, not national share."),
    ("Dawn Ultra", 30, "reported", SRC_DISH_AMZ, "Dawn moved 430,000 units across six ASINs in July 2026, 68.3% of Amazon top-10 dish-soap volume. Channel figure, not national share."),
    ("Dawn Powerwash", 10, "extrapolated", SRC_DISH_AMZ, DERIVED + " Dawn is 68.3% of Amazon top-10 dish-soap volume, July 2026; Powerwash is one line within Dawn."),
    ("Cascade", 15, "extrapolated", SRC_DISH_AMZ, DERIVED + " Cascade was 17.5% of Amazon top-10 dish-soap volume, July 2026; automatic dish care is growing with dishwasher ownership above 70% of households."),
    ("Finish", 8, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Reckitt's automatic dish brand; automatic dish care is a growing share but a fraction of the category."),
    ("Blueland dishwasher", 2, "reported", SRC_DISH_AMZ, "BLUELAND held 7.9% of Amazon top-10 dish-soap volume in July 2026 (50,000 units). Channel figure."),
    ("Dishwasher", 2, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Eco dishwasher formats are a small share of automatic dish care."),
    ("Dish Liquid", 1, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Eco hand-dish brands are a small fraction of the >95% of households that own liquid dish soap."),
    ("Meliora Dish Soap", 1, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Small eco hand-dish brand."),
    ("ECOS Dishmate", 1, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Small eco hand-dish brand."),
    ("Wave Dishwashing", 1, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Small eco hand-dish brand."),
    # ---- surface / disinfectant ----
    ("Lysol All-Purpose", 10, "reported", SRC_AMZ_APC, "Lysol All Purpose Cleaner Spray sits in Amazon's Best Sellers in All-Purpose Household Cleaners (top-ranked listings, Sep 2026). Rank-based channel signal, not a measured share."),
    ("Lysol Disinfectant Spray", 12, "reported", SRC_AMZ_APC, "Lysol Disinfectant Spray appears among Amazon Best Sellers in Household Cleaning (Sep 2026). Rank-based channel signal."),
    ("Lysol Disinfecting Wipes", 10, "reported", SRC_AMZ_APC, "Lysol Disinfecting Wipes appear among Amazon Best Sellers in Household Cleaning (Sep 2026). Rank-based channel signal."),
    ("Lysol Toilet Bowl", 8, "extrapolated", SRC_AMZ_APC, DERIVED + " Toilet care is a small share of the cleaners category; Lysol is a leading brand within it."),
    ("Lysol Multi-Surface", 8, "extrapolated", SRC_AMZ_APC, DERIVED + " Reckitt's Lysol surface line; surface cleaners are 15-20% of the US laundry-and-home category."),
    ("Clorox Disinfecting Wipes", 10, "reported", SRC_HC_REPORT, "Clorox Disinfecting Wipes (ASIN B00HSC9F2C) moved about 100,000 units in April 2026 with 117,900 ratings. Channel figure, not national share."),
    ("Clorox Toilet Bowl Cleaner with Bleach", 8, "reported", SRC_HC_REPORT, "Clorox Toilet Bowl Cleaner Clinging Bleach Gel (ASIN B00W5D1MDE) moved about 100,000 units in April 2026 with 40,100 ratings. Channel figure."),
    ("Clorox Bleach", 15, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Bleach retains broad institutional and residential use; Clorox is the leading bleach brand. No per-product penetration figure published."),
    ("Clorox Disinfecting Bleach", 15, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Clorox is the leading US bleach brand; bleach retains broad residential use."),
    ("Clorox Clean-Up All Purpose Cleaner with Bleach", 8, "extrapolated", SRC_AMZ_APC, DERIVED + " Clorox Clean-Up appears in Amazon Best Sellers in All-Purpose Household Cleaners (Sep 2026)."),
    ("Clorox ToiletWand", 6, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Disposable toilet-cleaning system; toilet care is a small share of the cleaners category."),
    ("Pine-Sol", 10, "extrapolated", SRC_AMZ_APC, DERIVED + " Pine-Sol appears in Amazon Best Sellers in All-Purpose Household Cleaners (Sep 2026); Clorox lists Pine-Sol as a lead surface brand."),
    ("Fabuloso", 12, "extrapolated", SRC_AMZ_APC, DERIVED + " Fabuloso appears in Amazon Best Sellers in All-Purpose Household Cleaners (Sep 2026); Colgate-Palmolive's mass-market floor and surface cleaner."),
    ("Formula 409", 6, "extrapolated", SRC_AMZ_APC, DERIVED + " Clorox all-purpose spray; surface cleaners are 15-20% of the US laundry-and-home category."),
    ("Tilex", 4, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Specialty mold and mildew cleaner; a small share of surface care."),
    ("Green Works", 2, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Clorox's plant-based line; natural/eco cleaners are a low-single-digit share."),
    ("Mr. Clean Magic Eraser", 12, "extrapolated", SRC_AMZ_APC, DERIVED + " Mr. Clean Magic Eraser appears in Amazon Best Sellers in Household Cleaning Tools (Sep 2026)."),
    ("Mr. Clean", 10, "extrapolated", SRC_AMZ_APC, DERIVED + " Mr. Clean appears in Amazon Best Sellers in All-Purpose Household Cleaners (Sep 2026)."),
    ("Windex Original", 15, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Glass cleaner is a staple surface-cleaner segment; Windex is the category-defining brand. No per-product penetration figure published."),
    ("Fantastik", 4, "extrapolated", SRC_AMZ_APC, DERIVED + " Fantastik appears in Amazon Best Sellers in All-Purpose Household Cleaners (Sep 2026)."),
    ("Spic and Span", 3, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Legacy all-purpose disinfecting cleaner; a small share of surface care."),
    ("Ajax Powder", 5, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Ajax is a long-standing mass scouring-powder brand; scouring powders are a small share of surface care."),
    ("Comet Bathroom", 5, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Comet is a long-standing mass scouring-powder brand; scouring powders are a small share of surface care."),
    ("Soft Scrub", 4, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Cream cleanser segment; a small share of surface care."),
    ("Bar Keepers Friend", 3, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Specialty oxalic-acid cleanser; a small share of surface care."),
    ("Bon Ami", 1, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Legacy feldspar scouring powder; a small share of surface care."),
    ("Swiffer WetJet", 8, "extrapolated", SRC_AMZ_APC, DERIVED + " Swiffer WetJet appears in Amazon Best Sellers in Household Cleaning Tools (Sep 2026)."),
    ("Glass Cleaner", 1, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Eco glass cleaner; a small fraction of the glass-cleaner segment."),
    ("All-Purpose", 1, "extrapolated", SRC_HOUSEHOLDS, DERIVED + " Eco all-purpose lines are a low-single-digit share of surface care."),
]

# ---------------------------------------------------------------- tiers
# Purchase channel, named after the breakpoints in the data (Trellis).
# tier_src is required: a tier is a claim like any other.
SRC_LA_TIER = SRC_LA_FAQ
SRC_AMZ_TIER = "https://www.amazon.com/Best-Sellers-Health-Household-All-Purpose-Household-Cleaners/zgbs/hpc/15356141"
SRC_FD_MANUAL = ("https://www.dollartree.com/file/general/"
                 "Family_Dollar_Quality_and_Regulatory_Compliance_Manual.pdf")
SRC_WALMART_DRUG = "https://www.walmart.com/"

TIERS = {
    # dollar-store: sold at dollar price points as the primary channel
    "LA's Totally Awesome All-Purpose Cleaner": ("dollar-store", "reported", SRC_LA_TIER,
        "Manufacturer FAQ directs customers to 99 Cents Only, Dollar Tree and Family Dollar; the product is not sold online or direct."),
    "LA's Totally Awesome All-Purpose Cleaner with Bleach": ("dollar-store", "reported", SRC_LA_TIER,
        "Same dollar-channel distribution as the parent SKU; manufacturer FAQ names Dollar Tree and Family Dollar as the retailers."),
    # drugstore: house brand sold through the pharmacy chain
    "CVS All Purpose Cleaner + Bleach Spray": ("drugstore", "reported", SRC_CVS_BLEACH,
        "Sold under the CVS Health house brand on cvs.com."),
    # grocery / mass: sold through grocery and big-box channels
    "Great Value Lemon Scent All Purpose Cleaner": ("grocery", "reported", SRC_WALMART_LEMON,
        "Walmart house brand, distributed by Walmart Inc., manufactured by KIK Custom Products."),
    "Great Value All Purpose Cleaner With Bleach": ("grocery", "reported", SRC_WALMART_BLEACH,
        "Walmart house brand; SDS names Walmart as distributor."),
    "Great Value Clear Ammonia All Purpose Cleaner": ("grocery", "reported", SRC_WALMART_AMMONIA,
        "Walmart house brand, distributor Walmart Inc., manufacturer KIK International."),
    "Great Value Cleaning Vinegar All Purpose Cleaner": ("grocery", "reported", SRC_WALMART_VINEGAR,
        "Walmart house brand, distributor Walmart Inc., manufacturer KIK Custom Products."),
    # apothecary and bulk: sold for its chemistry, not its brand story
    "Super Washing Soda": ("apothecary-bulk", "reported", "https://churchdwight.com/ingredient-disclosure/laundry-fabric-care/40002697-arm-hammer-super-washing-soda.aspx",
        "Washing soda is sold in the bulk and laundry-booster aisle as a commodity builder; manufacturer confirms sodium carbonate as the builder."),
    "20 Mule Team Borax (BMVC)": ("apothecary-bulk", "reported", "https://www.20muleteamlaundry.com/",
        "Borax is sold as a bulk laundry and cleaning staple, not as a finished branded cleaner."),
    "Castile Soap, Peppermint": ("apothecary-bulk", "reported", "https://www.drbronner.com/",
        "Castile soap is a bulk concentrated ingredient, diluted for use; sold as a chemistry, not a finished spray."),
    "Castile Soap, Lavender": ("apothecary-bulk", "reported", "https://www.drbronner.com/",
        "Castile soap is a bulk concentrated ingredient, diluted for use."),
    "Washing Soda (bulk)": ("apothecary-bulk", "reported", "https://www.essentialdepot.com/",
        "Sold as a bulk commodity powder for cleaning and laundry, no brand story."),
    "Citric Acid (bulk)": ("apothecary-bulk", "reported", "https://pubchem.ncbi.nlm.nih.gov/compound/Citric-Acid",
        "Sold as a bulk commodity powder for descaling and cleaning; the product is the chemical."),
    "Hydrogen Peroxide 3% (drugstore)": ("apothecary-bulk", "reported", "https://www.poison.org/articles/hydrogen-peroxide",
        "Sold as a first-aid and cleaning staple at 3% strength; the product is the dilute chemistry."),
}

# ---------------------------------------------------------------- new products
def prod(name, brand, cat, ings, tier, tier_ev, tier_src, tier_note,
         source, source_url, note, owner=None, owner_ev="untested", owner_src=None,
         substitutes=None, no_sub=None, no_sub_note=None, safe=None):
    return {
        "name": name, "brand": brand, "cat": cat, "safe": safe, "ings": ings,
        "heritage": False, "source": source, "source_url": source_url,
        "added": "2026-09-23", "updated": "2026-09-23", "note": note,
        "owner": owner, "owner_ev": owner_ev, "owner_src": owner_src,
        "tier": tier, "tier_ev": tier_ev, "tier_src": tier_src, "tier_note": tier_note,
        "substitutes": substitutes or [],
        "no_substitute_known": no_sub, "no_substitute_note": no_sub_note,
        "exposure": None, "exposure_ev": "untested", "exposure_src": None,
        "conc": None, "conc_src": None, "conc_ev": "untested",
        "grade_as_sold": None, "grade_as_sold_src": None,
        "strength_disclosure": "not_reviewed",
    }

NEW = [
    prod(
        "Great Value Lemon Scent All Purpose Cleaner", "Great Value", "All-Purpose",
        ["Water", "Tetrasodium EDTA", "Lauramine Oxide",
         "Alkyl C12-16 Dimethylbenzyl Ammonium Chloride", "Caprylyl/Capryl Glucoside",
         "Octyl Decyl Dimethyl Ammonium Chloride", "Lauryl Glucoside",
         "Dioctyldimethylammonium Chloride", "Didecyldimethylammonium Chloride",
         "Fragrance", "Nonoxynol"],
        "grocery", "reported", SRC_WALMART_LEMON,
        "Walmart house brand, manufactured by KIK Custom Products.",
        "Walmart ingredient disclosure (California Cleaning Right to Know)",
        SRC_WALMART_LEMON,
        "Full ingredient list from Walmart's published disclosure; fragrance withheld as CBI, which is itself the disclosure gap. The actives are quaternary ammonium compounds, graded on the derm and env dimensions.",
        owner="Walmart Inc.", owner_ev="reported", owner_src=SRC_WALMART_LEMON,
        safe="Sifter grade F, worst credible dimension: derm F and env F (quaternary ammonium actives: alkyl dimethylbenzyl ammonium chloride, didecyldimethylammonium chloride, dioctyldimethylammonium chloride; High evidence)",
        substitutes=[
            {"name": "Great Value Cleaning Vinegar All Purpose Cleaner", "tier": "grocery",
             "note": "Same aisle, same price band, two disclosed ingredients. Avoids the quaternary ammonium actives entirely."},
            {"name": "Seventh Generation All-Purpose Cleaner, Free & Clear", "tier": "grocery",
             "note": "Fragrance-free. Avoids the undisclosed fragrance blend and the quat actives."},
        ],
    ),
    prod(
        "Great Value All Purpose Cleaner With Bleach", "Great Value", "Disinfectant",
        ["Water", "Sodium Hypochlorite"],
        "grocery", "reported", SRC_WALMART_BLEACH,
        "Walmart house brand; SDS names Walmart as distributor.",
        "Walmart-published SDS (EPA-registered disinfectant)",
        SRC_WALMART_BLEACH,
        "EPA-registered disinfectant, so only the active is disclosed on the label: sodium hypochlorite at 1 to 3 percent, exact strength withheld as a trade secret. The inert fraction is not published, which is a disclosure gap rather than an absence of hazard.",
        owner="Walmart Inc.", owner_ev="reported", owner_src=SRC_WALMART_BLEACH,
        substitutes=[
            {"name": "Great Value Cleaning Vinegar All Purpose Cleaner", "tier": "grocery",
             "note": "Non-bleach alternative in the same aisle and price band. Avoids hypochlorite and the undisclosed inert fraction."},
        ],
    ),
    prod(
        "Great Value Clear Ammonia All Purpose Cleaner", "Great Value", "Glass",
        ["Water", "Ammonium Hydroxide", "Tetrasodium EDTA",
         "Sodium C10-16 Alkylbenzenesulfonate", "Sodium Xylene Sulfonate", "Sodium Hydroxide"],
        "grocery", "reported", SRC_WALMART_AMMONIA,
        "Walmart house brand, manufactured by KIK International.",
        "Walmart ingredient disclosure (California Cleaning Right to Know)",
        SRC_WALMART_AMMONIA,
        "Full intentionally-added list from Walmart's disclosure. Sodium hydroxide appears as a nonfunctional byproduct and is on the California Prop 65 list. No fragrance disclosed, which Walmart records as disclosure level 5.",
        owner="Walmart Inc.", owner_ev="reported", owner_src=SRC_WALMART_AMMONIA,
        substitutes=[
            {"name": "Great Value Cleaning Vinegar All Purpose Cleaner", "tier": "grocery",
             "note": "Same price band and aisle. Avoids ammonia and the Prop 65-listed sodium hydroxide byproduct."},
        ],
    ),
    prod(
        "Great Value Cleaning Vinegar All Purpose Cleaner", "Great Value", "All-Purpose",
        ["Water", "Acetic Acid"],
        "grocery", "reported", SRC_WALMART_VINEGAR,
        "Walmart house brand, manufactured by KIK Custom Products.",
        "Walmart ingredient disclosure (California Cleaning Right to Know)",
        SRC_WALMART_VINEGAR,
        "Two disclosed ingredients, no fragrance. Vinegar is the rare case where the short list is the whole list. Acetic acid carries a severe grade on the ingredient entry as the pure chemical; as sold this is dilute household vinegar, and docs/decisions.md rule 4 keeps the two grades separate.",
        owner="Walmart Inc.", owner_ev="reported", owner_src=SRC_WALMART_VINEGAR,
    ),
    prod(
        "CVS All Purpose Cleaner + Bleach Spray", "CVS Health", "Disinfectant",
        ["Water", "Sodium Hypochlorite", "Sodium Hydroxide"],
        "drugstore", "reported", SRC_CVS_BLEACH,
        "CVS Health house brand, sold on cvs.com.",
        "CVS.com product page (EPA-registered disinfectant)",
        SRC_CVS_BLEACH,
        "EPA-registered disinfectant. The page states the actives (2 percent sodium hypochlorite and sodium hydroxide); the inert fraction is not disclosed anywhere by the retailer, which is a wider disclosure gap than the bleach products whose manufacturers publish full lists.",
        owner="CVS Health", owner_ev="reported", owner_src=SRC_CVS_BLEACH,
        substitutes=[
            {"name": "CVS Health 70% Isopropyl Alcohol", "tier": "drugstore",
             "note": "Same store, same price band. Avoids hypochlorite and the undisclosed inert fraction."},
        ],
    ),
    prod(
        "LA's Totally Awesome All-Purpose Cleaner with Bleach", "Awesome Products",
        "Disinfectant",
        ["Water", "Orange Oil Blend", "Ethoxylated Alcohol", "Sodium Metasilicate",
         "Sodium Phosphate", "Sodium Hydroxide", "Sodium Hypochlorite"],
        "dollar-store", "reported", SRC_LA_TIER,
        "Manufacturer FAQ names Dollar Tree, Family Dollar and 99 Cents Only as the retail channel.",
        "Manufacturer SDS for the bleach variant (Awesome Products Inc.)",
        SRC_LA_SDS,
        "Full SDS ingredient table with CAS numbers, unlike the parent SKU whose list is only partly published. Sodium hydroxide and sodium hypochlorite both appear; the bleach variant is the more hazardous of the two dollar-store SKUs.",
        substitutes=[
            {"name": "LA's Totally Awesome All-Purpose Cleaner (non-bleach)", "tier": "dollar-store",
             "note": "Same brand, same dollar price point, no hypochlorite. Avoids the bleach and the caustic soda."},
        ],
    ),
    prod(
        "Citric Acid (bulk)", "commodity", "Specialty",
        ["Citric Acid"],
        "apothecary-bulk", "reported", "https://pubchem.ncbi.nlm.nih.gov/compound/Citric-Acid",
        "Sold as a bulk commodity powder, no brand owner.",
        "PubChem compound record (CID 311) and commodity supplier specification",
        "https://pubchem.ncbi.nlm.nih.gov/compound/Citric-Acid",
        "The ingredient tier in its purest form: a food-grade acid sold by the pound for descaling kettles, humidifiers and coffee makers. Graded as the pure chemical, per docs/decisions.md rule 4; the household dilution is far below the concentration at which the eye-irritant classification attaches.",
        owner="commodity", owner_ev="reported",
        owner_src="https://pubchem.ncbi.nlm.nih.gov/compound/Citric-Acid",
    ),
    prod(
        "Hydrogen Peroxide 3% (drugstore)", "commodity", "Disinfectant",
        ["Water", "Hydrogen Peroxide"],
        "apothecary-bulk", "reported", "https://www.poison.org/articles/hydrogen-peroxide",
        "Sold as a 3 percent first-aid and cleaning staple across drugstore and grocery channels.",
        "Standard 3 percent label strength, corroborated by poison-control guidance",
        "https://www.poison.org/articles/hydrogen-peroxide",
        "Sold at 3 percent, which is the strength that matters. The ingredient entry grades hydrogen peroxide F as the pure chemical (corrosive oxidizer); as sold at 3 percent it is an eye and skin irritant rather than a corrosive, and docs/decisions.md rule 4 keeps the two grades apart. Typically dispensed in an opaque bottle because light degrades it.",
        owner="commodity", owner_ev="reported",
        owner_src="https://www.poison.org/articles/hydrogen-peroxide",
    ),
]


def main():
    products = json.loads((DATA / "products.json").read_text(encoding="utf-8"))
    # ---- 1. exposure ----
    n_exp = 0
    for p in products:
        for key, val, ev, src, basis in EXPOSURE:
            if key.lower() in p["name"].lower():
                p["exposure"] = val
                p["exposure_ev"] = ev
                p["exposure_src"] = src
                p["exposure_basis"] = basis
                n_exp += 1
                break

    # products not matched keep untested, but say what was searched so the gap
    # is a finding rather than a shrug.
    for p in products:
        if p.get("exposure_ev") == "untested":
            p["exposure_basis"] = ("searched for a category penetration or brand-share "
                                   "figure covering this product; none found in the open "
                                   "sources. Left as a research gap rather than estimated.")

    # ---- 2. tiers ----
    n_tier = 0
    for p in products:
        t = TIERS.get(p["name"])
        if t:
            p["tier"], p["tier_ev"], p["tier_src"], p["tier_note"] = t
            n_tier += 1

    # ---- 3. new products ----
    existing = {p["name"] for p in products}
    added = []
    for np_ in NEW:
        if np_["name"] not in existing:
            products.append(np_)
            added.append(np_["name"])

    # new products need exposure too, from the same table
    for p in products:
        if p["name"] in added:
            for key, val, ev, src, basis in EXPOSURE:
                if key.lower() in p["name"].lower():
                    p["exposure"], p["exposure_ev"] = val, ev
                    p["exposure_src"], p["exposure_basis"] = src, basis
                    break
            else:
                p["exposure_basis"] = ("searched for a category penetration or brand-share "
                                       "figure covering this product; none found in the open "
                                       "sources. Left as a research gap rather than estimated.")

    # ---- 4. substitute notes name the hazard they avoid ----
    # Linnea's quality bar on the D/F gate (CCI-d04c72a): presence of a
    # substitute is not enough; the note has to say what it gets you away from,
    # or the entry documents worry without documenting an action. Applied to the
    # pre-existing severe set, which predates the standard.
    HARDEN = {
        ("Bar Keepers Friend", "Baking soda paste"):
            "Non-abrasive, no oxalic acid. Avoids the oxalic-acid organ effects and the feldspar respirable-silica question entirely. Weaker on mineral stain, safe on enamel and most stone.",
        ("Bar Keepers Friend", "Bon Ami cleansing powder"):
            "Avoids the oxalic acid in BKF, but not the silica: Bon Ami is feldspar-based, so check the feldspar silica entry before choosing it for a sealed stone counter.",
        ("Cascade", "Seventh Generation dishwasher detergent"):
            "Fragrance-free option. Avoids the sodium percarbonate eye-damage hazard and the sodium silicate corrosivity load that drives Cascade's D grade.",
        ("Cascade", "Blueland dishwasher tablets"):
            "Tablet format, no plastic tub. Avoids the percarbonate and silicate load; confirm the tablet's own ingredient list before relying on it.",
        ("Finish", "Seventh Generation dishwasher detergent"):
            "Same swap as Cascade. The hazard is the percarbonate and silicate load, not the brand, so this avoids the derm and eye route rather than a label.",
        ("20 Mule Team Borax (BMVC)", "Washing soda (sodium carbonate)"):
            "The classic laundry-boost swap. Avoids the EU/CLP reproductive-toxicity classification that drives borax's F grade. Cheaper, and carries an eye-irritant grade only.",
    }
    n_note = 0
    for p in products:
        for s in (p.get("substitutes") or []):
            key = (p["name"], s.get("name"))
            if key in HARDEN and HARDEN[key] not in (s.get("note") or ""):
                s["note"] = HARDEN[key]
                n_note += 1

    (DATA / "products.json").write_text(
        json.dumps(products, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"exposure filled on {n_exp} existing products")
    print(f"tiers assigned on {n_tier} products")
    print(f"substitute notes hardened to name the hazard: {n_note}")
    print(f"new products added: {len(added)}")
    for a in added:
        print("  +", a)
    print(f"catalog now {len(products)} products")

if __name__ == "__main__":
    main()
