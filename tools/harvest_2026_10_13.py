#!/usr/bin/env python3
"""Night-shift station 2 harvest, 2026-10-13 (Dolman).

Shelf: mainstream bathroom / shower disinfectant cleaners and mold-mildew
specialists that were absent from the corpus, ordered by exposure.

Sources, all read this fire from the served document:
  * Reckitt brand ingredient site, product.php?productLineId=<id>
    (Lysol). Served HTML carries the full "View by Weight %" panel with CAS.
  * P&G keyless SmartLabel API getproductdetails?gtin=<gtin>&locale=en-US
    (Mr. Clean).
  * S.C. Johnson whatsinsidescjohnson.com product page (Scrubbing Bubbles).
  * Wet & Forget's own SDS/ingredients page, wetandforget.com (full tables).

Idempotent: a second run adds nothing and writes no changelog entry.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
TODAY = "2026-10-13"

# --------------------------------------------------------------------------
# label form -> existing registry key (same substance, different spelling)
# --------------------------------------------------------------------------
ALIASES = {
    "water": "Water",
    "fragrance": "Fragrance",
    "fragrance/parfum": "Fragrance",
    "c10-16 alkyldimethylamine oxide": "Alkyldimethylamine Oxide",
    "c9-11 pareth": "Alcohols, C9-11, ethoxylated",
    "carboxymethyl inulin": "Sodium Carboxymethyl Inulin",
    "sodium c10-16 alkylbenzenesulfonate": "Sodium (C10-16) Alkylbenzenesulfonate",
    "polyoxyalkylene substituted chromophore (yellow)": "Polyoxyalkylene Substituted Chromophore",
    "didecyl dimethyl ammonium chloride": "Didecyldimethylammonium Chloride",
    "dioctyl dimethyl ammonium chloride": "Dioctyldimethylammonium Chloride",
    "capryl glucoside": "Octyl/Decyl Glucoside",
    "tetrasodium ethylenediamine tetraacetate": "Tetrasodium EDTA",
    "alkyl (50%c14, 40%c12, 10%c16) dimethyl benzyl ammonium chloride":
        "Alkyl (50% C14, 40% C12, 10% C16) Dimethyl Benzyl Ammonium Chloride",
    "undeceth-5 (c10-16 alketh)": "Undeceth-5",
}

# new ingredient keys minted this fire, all ungraded (honest state)
NEW_KEYS = {
    "Sodium Molybdate Dihydrate": {
        "s": "Sodium Molybdate Dihydrate (CAS 7631-95-0). Named on a Reckitt (Lysol) California SB-258 ingredient disclosure, read 2026-10-13.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Added by the 2026-10-13 night-shift harvest from a manufacturer's California Cleaning Product Right to Know Act disclosure. No PubChem or ECHA grade has been resolved for this entry yet, so g is null rather than a guess. It enters ungraded, which is the honest state until the grading lane reaches it.",
    },
    "Alcohols, C10, Ethoxylated": {
        "s": "Alcohols, C10, Ethoxylated (CAS 160875-66-1). Named on a Reckitt (Lysol) California SB-258 ingredient disclosure, read 2026-10-13.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Added by the 2026-10-13 night-shift harvest. Kept separate from the C9-11 and C10-16 ethoxylate keys already in the registry because the disclosed CAS is C10-specific; the registry stores no CAS per ingredient, so the chain length is carried in the key name.",
    },
    "C6-10 Alcohols Ethoxylated Propoxylated": {
        "s": "C6-10 Alcohols Ethoxylated Propoxylated (CAS 68987-81-5). Named on a Reckitt (Lysol) California SB-258 ingredient disclosure, read 2026-10-13.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Added by the 2026-10-13 night-shift harvest from a manufacturer's California Cleaning Product Right to Know Act disclosure. Not yet graded against GHS.",
    },
    "PVP/MA Copolymer": {
        "s": "PVP/MA Copolymer (CAS 30581-59-0). Named on a Reckitt (Lysol) California SB-258 ingredient disclosure, read 2026-10-13.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Added by the 2026-10-13 night-shift harvest from a manufacturer's California Cleaning Product Right to Know Act disclosure. Not yet graded against GHS.",
    },
    "Polyoxyethylene Tallow Ethylmonium Ethosulfate": {
        "s": "Polyoxyethylene Tallow Ethylmonium Ethosulfate. Named on Wet & Forget's own SDS/ingredients page (California Cleaning Product Right to Know Act), read 2026-10-13.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Added by the 2026-10-13 night-shift harvest from the manufacturer's own published ingredient table. Not yet graded against GHS.",
    },
    "Trisodium NTA": {
        "s": "Trisodium NTA. Named on Wet & Forget's own SDS/ingredients page (California Cleaning Product Right to Know Act), read 2026-10-13.",
        "ev": "Low", "g": None, "gr": {}, "impacts": [],
        "note": "Added by the 2026-10-13 night-shift harvest from the manufacturer's own published ingredient table. Not yet graded against GHS. The manufacturer's table lists it as a technically unavoidable byproduct not intentionally added, so it is recorded as disclosed rather than as an intentional ingredient.",
    },
}

# --------------------------------------------------------------------------
# owner record added this fire
# --------------------------------------------------------------------------
NEW_OWNER = {
    "Wet & Forget USA Ltd.": {
        "type": "private",
        "detail": "US arm of the New Zealand Wet & Forget brand. PO Box 5805, Elgin, IL 60121 (from the manufacturer's own SDS/ingredients page). The company is named on the EPA-accepted label for its registered outdoor product.",
        "ev": "verified",
        "src": "https://www3.epa.gov/pesticides/chem_search/ppls/084115-00001-20120823.pdf",
        "brands": ["Wet & Forget"],
    },
}

SURF = "https://www.indexbox.io/store/united-states-household-surface-cleaners-market-analysis-forecast-size-trends-and-insights/"

PRODUCTS = [
    {
        "name": "Mr. Clean Liquid Multi-Purpose Cleaner with Febreze, Meadows & Rain, 128 fl oz",
        "brand": "Mr. Clean",
        "cat": "All-Purpose",
        "ings": [
            "Water", "Alkyldimethylamine Oxide", "Alcohols, C9-11, ethoxylated",
            "Sodium Carboxymethyl Inulin", "Sodium (C10-16) Alkylbenzenesulfonate",
            "Sodium Carbonate", "Sodium Citrate", "Benzisothiazolinone", "Fragrance",
            "Polyoxyalkylene Substituted Chromophore (Cyan)",
            "Polyoxyalkylene Substituted Chromophore",
        ],
        "source": (
            "Procter & Gamble SmartLabel product data, keyless API, GTIN 00037000231240, locale en-US, read 2026-10-13, HTTP 200. "
            "Fields.ingredientList, each entry with CAS and function: Water 7732-18-5; C10-16 alkyldimethylamine oxide 70592-80-2 "
            "(cleaning agent); C9-11 Pareth 68439-46-3 (cleaning agent); Carboxymethyl Inulin 430439-54-6 (chelator); "
            "Sodium C10-16 Alkylbenzenesulfonate 68081-81-2 (cleaning agent); Sodium Carbonate 497-19-8 (pH adjuster); "
            "Sodium Citrate 68-04-2 (pH adjuster); Benzisothiazolinone 2634-33-5 (preservative); Fragrances (see below); "
            "Polyoxyalkylene Substituted Chromophore (Cyan) and (Yellow) (colorants). "
            "Mapping note: the filing's 'C9-11 Pareth' carries CAS 68439-46-3, the same substance the registry already holds as "
            "'Alcohols, C9-11, ethoxylated', so the record uses that key; 'Carboxymethyl Inulin' (CAS 430439-54-6, the sodium salt) "
            "maps to the registry's 'Sodium Carboxymethyl Inulin'; the two chromophore colourants map to the registry's Cyan key and "
            "its generic chromophore key. Fragrance components disclosed at or above 100 ppm are recorded in the source prose only, "
            "per the standing discipline while the fragrance-components ruling is open."
        ),
        "source_url": "https://az-na-smartlabel-prod-functionapp-api.pgcloud.com/api/getproductdetails?gtin=00037000231240&locale=en-US",
        "note": (
            "The mainstream national-brand multi-purpose concentrate, entered so the corpus carries a P&G all-purpose formula "
            "alongside the value and natural shelves. Every line carries a CAS and a function in the manufacturer's own filing. "
            "Entered ungraded: product grading is the Sifter lane."
        ),
        "owner": "Procter & Gamble",
        "tier": "mass",
        "tier_src": "https://us.pg.com/brands/",
        "tier_note": "National P&G brand sold through grocery, mass and club channels; market-position vocabulary, evidenced by P&G's own brand page.",
        "substitutes": [
            {
                "name": "Seventh Generation All-Purpose Cleaner, Free & Clear",
                "tier": "natural",
                "note": "Same job, no added fragrance. Avoids the fragrance class entirely, which is the substitute for a household avoiding scent rather than for a hazard in the base formula.",
            },
            {
                "name": "Great Value Lemon Scent All Purpose Cleaner",
                "tier": "grocery",
                "note": "Lower price in the same aisle and the same cleaning chemistry family (surfactant plus pH adjuster). Swaps the fragrance load for a value-tier one; the base formula is comparable.",
            },
        ],
        "exposure": 6,
        "exposure_basis": (
            "Derived, not measured. Searched for a product-level or brand-level US household figure for the Mr. Clean multi-purpose "
            "liquid (the P&G brand page, the SmartLabel record, and a general web search) and found none. IndexBox's US Household "
            "Surface Cleaners page states approximately 95% of US households use at least one surface cleaner product per month, with "
            "all-purpose cleaners the largest segment at an estimated 30 to 35% of value. Mr. Clean is a leading all-purpose brand, so "
            "the estimate is category penetration times the all-purpose share times a large brand share, rounded to one significant figure."
        ),
    },
    {
        "name": "Lysol Power Foamer Bathroom Cleaner",
        "brand": "Lysol",
        "cat": "Bathroom",
        "ings": [
            "Water", "Didecyldimethylammonium Chloride", "Octyl Decyl Dimethyl Ammonium Chloride",
            "Dioctyldimethylammonium Chloride", "Tetrasodium EDTA", "Diethylene Glycol Monobutyl Ether",
            "Undeceth-5", "Sodium Lauroyl Sarcosinate", "Sodium Molybdate Dihydrate",
            "Ammonium Hydroxide", "Dipropylene Glycol", "Isobutane", "Fragrance",
        ],
        "source": (
            "Reckitt brand ingredient disclosure, https://www.rbnainfo.com/product.php?productLineId=3579 "
            "(LYSOL Power Foamer Bathroom Cleaner), read 2026-10-13, HTTP 200. Served page carries the full 'View by Weight %' panel. "
            "Ingredients with CAS: Octyl Decyl Dimethyl Ammonium Chloride 32426-11-2 (antimicrobial active); "
            "Didecyl Dimethyl Ammonium Chloride 7173-51-5 (antimicrobial active); Dioctyl Dimethyl Ammonium Chloride 5538-94-3 "
            "(antimicrobial active); Tetrasodium EDTA 64-02-8 (chelator); Diethylene Glycol Monobutyl Ether 112-34-5 (solvent); "
            "Undeceth-5 34398-01-1 (surfactant); Sodium Lauroyl Sarcosinate 137-16-6 (surfactant); Sodium molybdate dihydrate 7631-95-0 "
            "(corrosion inhibitor); Ammonium Hydroxide 1336-21-6 (pH adjuster); Dipropylene Glycol 25265-71-8 (solvent/fragrance component); "
            "Isobutane 75-28-5 (aerosol propellant); Water 7732-18-5; Fragrance/Parfum. "
            "Mapping note: 'Didecyl Dimethyl Ammonium Chloride' and 'Dioctyl Dimethyl Ammonium Chloride' map to the registry's existing "
            "'Didecyldimethylammonium Chloride' and 'Dioctyldimethylammonium Chloride' keys, same substances, spelling only. "
            "Fragrance components disclosed at or above 100 ppm (Eugenol 97-53-0, Isoeugenol 97-54-1, Isobornyl Acetate 125-12-2) are "
            "recorded in this prose only, not as ingredient keys, per the standing discipline."
        ),
        "source_url": "https://www.rbnainfo.com/product.php?productLineId=3579",
        "note": (
            "Aerosol bathroom disinfectant foam built on the standard triple-quaternary active system (three alkyl dimethyl ammonium "
            "chlorides) with an isobutane propellant. Recorded because the quat trio is the mainstream disinfecting chemistry and the "
            "corpus should carry it with a real filing behind it. Entered ungraded: product grading is the Sifter lane."
        ),
        "owner": "Reckitt",
        "tier": "mass",
        "tier_src": "https://www.reckitt.com/our-brands/",
        "tier_note": "Lysol is a Reckitt Powerbrand sold through grocery, mass, drug and dollar channels; evidenced by Reckitt's own brand page.",
        "substitutes": [
            {
                "name": "up&up Bathroom Disinfecting Cleaner, Unscented",
                "tier": "grocery",
                "note": "Lower price, same aisle, same disinfecting job. Avoids the fragrance class and the aerosol propellant, which is the substitute for a household that wants the bathroom disinfected without a scent or a spray cloud.",
            },
            {
                "name": "Method Daily Granite Cleaner, Apple Orchard",
                "tier": "mass",
                "note": "Same price band for a bathroom-adjacent surface. Avoids the quaternary ammonium actives and the aerosol; a surfactant-and-acid cleaner rather than a registered disinfectant, so it cleans without making a kill claim.",
            },
        ],
        "exposure": 4,
        "exposure_basis": (
            "Derived, not measured. Searched for a product-level or brand-level US household figure for the Lysol Power Foamer bathroom "
            "line (the Reckitt brand site, the disclosure page, and a general web search) and found none. IndexBox's US Household Surface "
            "Cleaners page states approximately 95% of US households use at least one surface cleaner product per month and puts specialised "
            "cleaners (bathroom, kitchen, glass, floor) at 30 to 35% of value with bathroom the largest sub-segment; Lysol is the category's "
            "leading disinfectant brand, so the estimate is category penetration times the bathroom share times a large brand share, rounded "
            "to one significant figure."
        ),
    },
    {
        "name": "Lysol Bathroom Foamer Cleaner, Brand New Day Mango & Hibiscus",
        "brand": "Lysol",
        "cat": "Bathroom",
        "ings": [
            "Water", "Citric Acid", "Dipropylene Glycol Butyl Ether", "Sodium Methyl 2-Sulfolaurate",
            "C6-10 Alcohols Ethoxylated Propoxylated", "Lauramine Oxide", "PVP/MA Copolymer", "Fragrance",
        ],
        "source": (
            "Reckitt brand ingredient disclosure, https://www.rbnainfo.com/product.php?productLineId=3366 "
            "(LYSOL Bathroom Foamer Cleaner - Brand New Day - Mango & Hibiscus), read 2026-10-13, HTTP 200. "
            "Ingredients with CAS: Citric Acid 77-92-9 (antimicrobial active); Dipropylene Glycol Butyl Ether 29911-28-2 (solvent); "
            "Sodium Methyl 2-Sulfolaurate 149458-07-1 (surfactant); C6-10 Alcohols Ethoxylated Propoxylated 68987-81-5 (surfactant); "
            "Lauramine Oxide 1643-20-5 (surfactant); PVP/MA Copolymer 30581-59-0 (antiredeposition polymer); Water 7732-18-5; "
            "Fragrance/Parfum. Fragrance components disclosed at or above 100 ppm (Alpha-Hexylcinnamaldehyde 101-86-0, "
            "Butylphenyl Methylpropional 80-54-6, Delta-3-Carene 13466-78-9, Dihydromyrcenol 18479-58-8, Dipropylene Glycol 25265-71-8, "
            "Eugenol 97-53-0, Isoeugenol 97-54-1, Tricyclodecenyl Acetate 5413-60-5, Trimethylhexyl Acetate 58430-94-7) are recorded in "
            "this prose only, not as ingredient keys, per the standing discipline."
        ),
        "source_url": "https://www.rbnainfo.com/product.php?productLineId=3366",
        "note": (
            "A citric-acid bathroom foamer, so the reader can compare an acid-active disinfectant against the quat and hypochlorite systems "
            "already in the corpus. Every line carries a CAS in the manufacturer's own filing. Entered ungraded: product grading is the "
            "Sifter lane."
        ),
        "owner": "Reckitt",
        "tier": "mass",
        "tier_src": "https://www.reckitt.com/our-brands/",
        "tier_note": "Lysol is a Reckitt Powerbrand sold through grocery, mass, drug and dollar channels; evidenced by Reckitt's own brand page.",
        "substitutes": [
            {
                "name": "up&up Bathroom Disinfecting Cleaner, Unscented",
                "tier": "grocery",
                "note": "Lower price, same aisle, same bathroom job. Avoids the fragrance class, which is what the nine disclosed fragrance components in this formula are.",
            },
        ],
        "exposure": 2,
        "exposure_basis": (
            "Derived, not measured. Searched for a product-level US household figure for the Lysol Brand New Day bathroom foamer line "
            "(the Reckitt brand site, the disclosure page, and a general web search) and found none. IndexBox's US Household Surface Cleaners "
            "page puts specialised cleaners at 30 to 35% of category value with bathroom the largest sub-segment; this is one scent variant of "
            "one brand's bathroom foamer, so the estimate is category penetration times the bathroom share times a small brand-and-variant "
            "share, rounded to one significant figure."
        ),
    },
    {
        "name": "Lysol Hydrogen Peroxide Bathroom Cleaner, Cool Spring Breeze",
        "brand": "Lysol",
        "cat": "Bathroom",
        "ings": [
            "Water", "Hydrogen Peroxide", "Dipropylene Glycol Butyl Ether", "Sodium Methyl 2-Sulfolaurate",
            "Alcohols, C10, Ethoxylated", "Octyl/Decyl Glucoside", "Lauryl Glucoside", "Citric Acid",
            "Tetrasodium Iminodisuccinate", "Dipropylene Glycol", "Fragrance",
        ],
        "source": (
            "Reckitt brand ingredient disclosure, https://www.rbnainfo.com/product.php?productLineId=3089 "
            "(LYSOL Hydrogen Peroxide Bathroom Cleaner - Cool Spring Breeze), read 2026-10-13, HTTP 200. "
            "Ingredients with CAS: Hydrogen Peroxide 7722-84-1 (antimicrobial active); Dipropylene Glycol Butyl Ether 29911-28-2 (solvent); "
            "Sodium Methyl 2-Sulfolaurate 149458-07-1 (surfactant); C10 Ethoxylated Alcohol 160875-66-1 (surfactant); "
            "Capryl Glucoside 68515-73-1 (surfactant); Lauryl Glucoside 110615-47-9 (surfactant); Citric Acid 77-92-9 (pH adjuster); "
            "Tetrasodium Iminodisuccinate 144538-83-0 (chelator); Dipropylene Glycol 25265-71-8 (solvent/fragrance component); "
            "Water 7732-18-5; Fragrance/Parfum. "
            "Mapping note: 'Capryl Glucoside' is disclosed at CAS 68515-73-1, which is the octyl/decyl glucoside the registry already holds "
            "under 'Octyl/Decyl Glucoside', so that key is used rather than minting a third glucoside twin. 'C10 Ethoxylated Alcohol' carries a "
            "C10-specific CAS and is minted as 'Alcohols, C10, Ethoxylated' rather than mapped to the C10-16 key. Fragrance components "
            "disclosed at or above 100 ppm (1,1-Dimethyl-2-Phenylethyl Acetate 151-05-3, 2-Methylundecanal 110-41-8, Camphor 76-22-2, "
            "Dihydromyrcenol 18479-58-8, Dipropylene Glycol 25265-71-8, Eucalyptol 470-82-6, Eucalyptus oil 8000-48-4, Eugenol 97-53-0, "
            "Isoamyl Salicylate 87-20-7, Isobornyl Acetate 125-12-2, Isoeugenol 97-54-1, Tetramethyl Acetyloctahydronaphthalenes 54464-57-2) "
            "are recorded in this prose only, not as ingredient keys, per the standing discipline."
        ),
        "source_url": "https://www.rbnainfo.com/product.php?productLineId=3089",
        "note": (
            "A peroxide-based bathroom cleaner with a sugar-surfactant system (glucosides) rather than a quaternary ammonium active, which "
            "makes it the useful third leg of the bathroom-disinfectant comparison in this fire. Entered ungraded: product grading is the "
            "Sifter lane."
        ),
        "owner": "Reckitt",
        "tier": "mass",
        "tier_src": "https://www.reckitt.com/our-brands/",
        "tier_note": "Lysol is a Reckitt Powerbrand sold through grocery, mass, drug and dollar channels; evidenced by Reckitt's own brand page.",
        "substitutes": [
            {
                "name": "up&up Bathroom Disinfecting Cleaner, Unscented",
                "tier": "grocery",
                "note": "Lower price, same aisle. Avoids the fragrance class, which is what the twelve disclosed fragrance components in this formula are; the peroxide active is the same family.",
            },
        ],
        "exposure": 3,
        "exposure_basis": (
            "Derived, not measured. Searched for a product-level US household figure for the Lysol hydrogen-peroxide bathroom cleaner "
            "(the Reckitt brand site, the disclosure page, and a general web search) and found none. IndexBox's US Household Surface Cleaners "
            "page puts specialised cleaners at 30 to 35% of category value with bathroom the largest sub-segment; this is one scent variant of "
            "one brand's peroxide bathroom line, so the estimate is category penetration times the bathroom share times a modest brand-and-variant "
            "share, rounded to one significant figure."
        ),
    },
    {
        "name": "Wet & Forget Shower Cleaner, Vanilla Scent",
        "brand": "Wet & Forget",
        "cat": "Bathroom",
        "ings": [
            "Water", "Tetrasodium EDTA", "Sodium Carbonate",
            "Polyoxyethylene Tallow Ethylmonium Ethosulfate", "C12-15 Alcohols Ethoxylated",
            "Lauramine Oxide", "Myristamine Oxide", "Trisodium NTA", "Magnesium Nitrate",
            "Methylchloroisothiazolinone", "Methylisothiazolinone", "Citric Acid", "Sodium Hydroxide",
            "Fragrance",
        ],
        "source": (
            "Wet & Forget's own SDS/ingredients page, https://www.wetandforget.com/wet-and-forget-sds.html "
            "(section 'Wet & Forget Shower - Vanilla Scent', item numbers 801064, 801128, 801064-F), read 2026-10-13, HTTP 200. "
            "The page publishes a per-product ingredient table with CAS and function under the California Cleaning Product Right to Know Act. "
            "Ingredients: Water 7732-18-5 (solvent); Tetrasodium EDTA 64-02-8 (chelating agent); Sodium Carbonate (buffering agent); "
            "Polyoxyethylene Tallow Ethylmonium Ethosulfate (surfactant); C12-15 Alcohols Ethoxylated (surfactant); Lauramine Oxide (surfactant); "
            "Myristamine Oxide (surfactant); Trisodium NTA (listed by the manufacturer as a technically unavoidable byproduct not intentionally "
            "added); Magnesium Nitrate (processing aid); Methylchloroisothiazolinone (preservative); Methylisothiazolinone (preservative); "
            "Citric Acid (pH adjuster); Sodium Hydroxide (listed by the manufacturer as a technically unavoidable byproduct not intentionally "
            "added); Fragrance. The manufacturer withholds the CAS for several lines while disclosing the identity; that is a CAS withholding, "
            "not an ingredient withholding, so the list is complete at the identity level."
        ),
        "source_url": "https://www.wetandforget.com/wet-and-forget-sds.html",
        "note": (
            "The shower cleaner from a brand whose whole pitch is 'spray it and forget it', entered because shower cleaning is a near-universal "
            "household task and the corpus had no dedicated shower cleaner from this brand family. The manufacturer publishes the full identity "
            "list while withholding CAS on several lines, and the two preservatives are the isothiazolinone pair the registry already carries "
            "with full grades. Entered ungraded: product grading is the Sifter lane."
        ),
        "owner": "Wet & Forget USA Ltd.",
        "tier": "mass",
        "tier_src": "https://www.wetandforget.com/",
        "tier_note": "National brand sold through home centers, hardware, grocery and online retail. The cited page evidences brand ownership rather than the shelf; disclosed.",
        "substitutes": [
            {
                "name": "Method Daily Shower Cleaner",
                "tier": "natural",
                "note": "Same job, no isothiazolinone preservative pair and no quaternary surfactant. The substitute is specifically for the methylchloroisothiazolinone and methylisothiazolinone lines, both of which the registry grades as strong skin sensitizers.",
            },
            {
                "name": "ECOS Shower Kleener",
                "tier": "natural",
                "note": "Same price band for a daily shower spray. Avoids the isothiazolinone preservative pair; check the ECOS entry for its own preservative before choosing it if the concern is preservatives generally rather than this pair.",
            },
        ],
        "exposure": 2,
        "exposure_basis": (
            "Derived, not measured. Searched for a product-level or brand-level US household figure for the Wet & Forget shower line "
            "(the brand site, the SDS page, and a general web search) and found none. IndexBox's US Household Surface Cleaners page puts "
            "specialised cleaners at 30 to 35% of category value with bathroom the largest sub-segment; Wet & Forget is a smaller brand than "
            "the category leaders, so the estimate is category penetration times the bathroom share times a small brand share, rounded to one "
            "significant figure."
        ),
    },
    {
        "name": "Wet & Forget Indoor Mold+Mildew Disinfectant Cleaner",
        "brand": "Wet & Forget",
        "cat": "Disinfectant",
        "ings": [
            "Octyl Decyl Dimethyl Ammonium Chloride", "Dioctyldimethylammonium Chloride",
            "Didecyldimethylammonium Chloride",
            "Alkyl (50% C14, 40% C12, 10% C16) Dimethyl Benzyl Ammonium Chloride",
            "Tetrasodium EDTA", "Sodium Metasilicate Pentahydrate",
        ],
        "source": (
            "Wet & Forget's own SDS/ingredients page, https://www.wetandforget.com/wet-and-forget-sds.html "
            "(section 'Indoor Mold+Mildew Disinfectant Cleaner', item numbers 802064, 802128, E802064, E802128), read 2026-10-13, HTTP 200. "
            "The page publishes a per-product ingredient table with CAS and function. Ingredients: Octyl decyl dimethyl ammonium chloride "
            "32426-11-2 (active); Dioctyl dimethyl ammonium chloride 5538-94-3 (active); Didecyl dimethyl ammonium chloride 7173-51-5 (active); "
            "Alkyl (50% C14, 40% C12, 10% C16) dimethyl benzyl ammonium chloride 68424-85-1 (active); Tetrasodium ethylenediamine tetraacetate "
            "64-02-8 (chelating agent); Sodium metasilicate pentahydrate 10213-79-3 (detergent builder). "
            "Mapping note: the filing's 'Tetrasodium ethylenediamine tetraacetate' is the same substance as the registry's 'Tetrasodium EDTA' key "
            "(same CAS), so that key is used. The manufacturer's table names the four quaternary actives by chain distribution; the C12-16 "
            "benzyl quat matches the registry's existing chain-distribution key."
        ),
        "source_url": "https://www.wetandforget.com/wet-and-forget-sds.html",
        "note": (
            "An indoor mold and mildew disinfectant built on a four-quaternary active system, which is the broadest quat blend in the corpus. "
            "Entered because mold and mildew removal is a high-frequency household task and the corpus carried no Wet & Forget indoor product. "
            "Entered ungraded: product grading is the Sifter lane."
        ),
        "owner": "Wet & Forget USA Ltd.",
        "tier": "mass",
        "tier_src": "https://www.wetandforget.com/",
        "tier_note": "National brand sold through home centers, hardware, grocery and online retail. The cited page evidences brand ownership rather than the shelf; disclosed.",
        "substitutes": [
            {
                "name": "Seventh Generation Disinfecting Multi-Surface Cleaner, Lemongrass Citrus",
                "tier": "natural",
                "note": "Same price band for an indoor disinfectant. Avoids the quaternary ammonium active system, which is the substitute for a household that wants the mold and mildew job done without a quat active.",
            },
            {
                "name": "up&up Mold and Mildew Stain Remover",
                "tier": "grocery",
                "note": "Lower price in the same aisle for the mold and mildew job. Check the up&up entry for its own active before choosing it; the point of the substitute is price and availability, not a different chemistry.",
            },
        ],
        "exposure": 2,
        "exposure_basis": (
            "Derived, not measured. Searched for a product-level or brand-level US household figure for the Wet & Forget indoor mold and mildew "
            "cleaner (the brand site, the SDS page, and a general web search) and found none. IndexBox's US Household Surface Cleaners page states "
            "approximately 95% of US households use at least one surface cleaner product per month and puts disinfectants and sanitizers at 25 to "
            "30% of category value; Wet & Forget is a smaller brand than the category leaders, so the estimate is category penetration times the "
            "disinfectant share times a small brand share, rounded to one significant figure."
        ),
    },
    {
        "name": "Scrubbing Bubbles Mega Shower Foamer Trigger",
        "brand": "Scrubbing Bubbles",
        "cat": "Bathroom",
        "ings": ["Water", "Lactic Acid", "Lauryl Glucoside", "Fragrance"],
        "source": (
            "S.C. Johnson's own ingredient disclosure page, "
            "https://whatsinsidescjohnson.com/en-us/brands/scrubbingbubbles/shower-tub/mega-shower-foamer-trigger, read 2026-10-13, HTTP 200, "
            "published under the California ingredient disclosure requirements. The page lists Water (liquid base), Fragrance, and two cleaning "
            "agents, Lactic acid and Lauryl Glucoside. Fragrance components disclosed by the manufacturer (linalool, 3,7-dimethyloctan-3-ol, "
            "3a,4,5,6,7,7a-hexahydro-4,7-methanoinden-6-yl acetate, 2,6-dimethyl-7-octen-2-ol, hexyl salicylate, benzyl salicylate, "
            "methyldihydrojasmonate, dipropylene glycol, terpenes and terpenoids sweet orange oil, terpineol, alpha-isomethyl ionone, "
            "butylphenyl methylpropional, citral, citronellol, geraniol, isoeugenol, limonene) are recorded in this prose only, not as ingredient "
            "keys, per the standing discipline. The manufacturer marks several of them on its own skin-allergen list. Note: this host returns "
            "HTTP 429 to a plain fetch; the page was read in full through the fetch tool, which is the same not-machine-readable class as "
            "whirlpoolcorp.com and the eur-lex host."
        ),
        "source_url": "https://whatsinsidescjohnson.com/en-us/brands/scrubbingbubbles/shower-tub/mega-shower-foamer-trigger",
        "note": (
            "The trigger version of the mainstream shower foamer, entered so the corpus carries the SC Johnson shower chemistry with a real "
            "disclosure behind it rather than only the bare brand record. The formula is short and fully named: a lactic-acid cleaner with a "
            "glucoside surfactant. Entered ungraded: product grading is the Sifter lane."
        ),
        "owner": "SC Johnson",
        "tier": "mass",
        "tier_src": "https://www.scjohnson.com/en/our-brands",
        "tier_note": "National SC Johnson brand sold through grocery, mass and dollar channels. The SC Johnson owner record's own source is the Method/Ecover acquisition release, which does not name Scrubbing Bubbles; that src-precision defect is already filed and is disclosed here rather than hidden.",
        "substitutes": [
            {
                "name": "Method Daily Shower Cleaner",
                "tier": "natural",
                "note": "Same job at a similar price. Avoids the fragrance load and its disclosed allergens; the lactic-acid and glucoside cleaning chemistry is comparable.",
            },
        ],
        "exposure": 4,
        "exposure_basis": (
            "Derived, not measured. Searched for a product-level or brand-level US household figure for the Scrubbing Bubbles Mega Shower Foamer "
            "(the SC Johnson brand page, the disclosure page, and a general web search) and found none. IndexBox's US Household Surface Cleaners "
            "page states approximately 95% of US households use at least one surface cleaner product per month and puts specialised cleaners "
            "(bathroom, kitchen, glass, floor) at 30 to 35% of value with bathroom the largest sub-segment; Scrubbing Bubbles is a leading bathroom "
            "brand, so the estimate is category penetration times the bathroom share times a large brand share, rounded to one significant figure."
        ),
    },
    {
        "name": "Scrubbing Bubbles Mega Shower Foamer Aerosol",
        "brand": "Scrubbing Bubbles",
        "cat": "Bathroom",
        "ings": [
            "Water", "Quaternary Ammonium Compounds", "Tetrasodium Iminodisuccinate", "Isobutane",
            "Ethoxylated Alcohol", "Sodium Hydroxide", "Fragrance",
        ],
        "source": (
            "S.C. Johnson's own ingredient disclosure page, "
            "https://whatsinsidescjohnson.com/en-us/brands/scrubbingbubbles/shower-tub/mega-shower-foamer-aerosol, read 2026-10-13, HTTP 200, "
            "published under the California ingredient disclosure requirements. The page lists an Active Ingredient (Quaternary Ammonium "
            "Compounds) and other ingredients: Water (purified), Tetrasodium Iminodisuccinate (chelator), Isobutane (propellant), Ethoxylated "
            "Alcohol (emulsifier), Fragrance, Sodium Hydroxide (pH adjuster). Fragrance components disclosed by the manufacturer (dipropylene "
            "glycol, 2,6-dimethyl-7-octen-2-ol, hexamethylindanopyran, methyldihydrojasmonate, hexyl cinnamal, tetramethyl "
            "acetyloctahydronaphthalenes, methyl ionones, citrus aurantium dulcis (orange) peel oil, tricyclo(5.2.1.02,6)dec-4-en-8-yl acetate, "
            "butylphenyl methylpropional) are recorded in this prose only, not as ingredient keys, per the standing discipline. The manufacturer "
            "marks several of them on its own skin-allergen list. Note: this host returns HTTP 429 to a plain fetch; the page was read in full "
            "through the fetch tool."
        ),
        "source_url": "https://whatsinsidescjohnson.com/en-us/brands/scrubbingbubbles/shower-tub/mega-shower-foamer-aerosol",
        "note": (
            "The aerosol version of the same shower foamer, entered alongside the trigger so the pair reads as the two pack forms of one product "
            "line. The disclosure names the active only at class level ('Quaternary Ammonium Compounds'), which is the manufacturer's own level of "
            "detail here, so the record keeps the class key rather than inventing a chain distribution. Entered ungraded: product grading is the "
            "Sifter lane."
        ),
        "owner": "SC Johnson",
        "tier": "mass",
        "tier_src": "https://www.scjohnson.com/en/our-brands",
        "tier_note": "National SC Johnson brand sold through grocery, mass and dollar channels. The SC Johnson owner record's own source is the Method/Ecover acquisition release, which does not name Scrubbing Bubbles; that src-precision defect is already filed and is disclosed here rather than hidden.",
        "substitutes": [
            {
                "name": "Method Daily Shower Cleaner",
                "tier": "natural",
                "note": "Same job at a similar price. Avoids the fragrance load and its disclosed allergens and avoids the aerosol propellant, which is the substitute for a household avoiding a spray cloud.",
            },
        ],
        "exposure": 4,
        "exposure_basis": (
            "Derived, not measured. Searched for a product-level or brand-level US household figure for the Scrubbing Bubbles Mega Shower Foamer "
            "(the SC Johnson brand page, the disclosure page, and a general web search) and found none. IndexBox's US Household Surface Cleaners "
            "page states approximately 95% of US households use at least one surface cleaner product per month and puts specialised cleaners "
            "(bathroom, kitchen, glass, floor) at 30 to 35% of value with bathroom the largest sub-segment; Scrubbing Bubbles is a leading bathroom "
            "brand, so the estimate is category penetration times the bathroom share times a large brand share, rounded to one significant figure."
        ),
    },
]

CHANGELOG_TEXT = (
    "8 bathroom and shower disinfectant cleaners added (Mr. Clean Multi-Purpose with Febreze; Lysol Power Foamer Bathroom Cleaner; "
    "Lysol Bathroom Foamer Cleaner Mango & Hibiscus; Lysol Hydrogen Peroxide Bathroom Cleaner; Wet & Forget Shower Cleaner; "
    "Wet & Forget Indoor Mold+Mildew Disinfectant Cleaner; Scrubbing Bubbles Mega Shower Foamer Trigger and Aerosol). "
    "6 new ingredient keys minted ungraded, 1 new owner record (Wet & Forget USA Ltd.), substitutes and exposure evidence on every record."
)


def load(name):
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, obj, indent, trailing_newline):
    text = json.dumps(obj, ensure_ascii=False, indent=indent)
    if trailing_newline:
        text += "\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def resolve(ings, ingredients, label):
    """Map a served label term to a registry key; mint if genuinely new."""
    low = label.strip().lower()
    if low in ALIASES:
        return ALIASES[low], None
    for key in ingredients:
        if key.lower() == low:
            return key, None
    # canonical capitalisation for a minted key
    canon = " ".join(w if w.isupper() or re.match(r"^[A-Z]?\d", w) else w.capitalize()
                     for w in label.split())
    if canon not in ingredients:
        ingredients[canon] = NEW_KEYS[canon]
        return canon, canon
    return canon, None


def main():
    products = load("products.json")
    ingredients = load("ingredients.json")
    owners = load("owners.json")

    existing_names = {p["name"] for p in products}
    added, minted = [], []

    # owner record
    if "Wet & Forget USA Ltd." not in owners["owners"]:
        owners["owners"]["Wet & Forget USA Ltd."] = NEW_OWNER["Wet & Forget USA Ltd."]

    for spec in PRODUCTS:
        if spec["name"] in existing_names:
            continue
        rec = {
            "name": spec["name"],
            "brand": spec["brand"],
            "cat": spec["cat"],
            "safe": None,
            "ings": [],
            "heritage": False,
            "source": spec["source"],
            "source_url": spec["source_url"],
            "note": spec["note"],
            "owner": spec["owner"],
            "tier": spec["tier"],
            "tier_ev": "reported",
            "tier_src": spec["tier_src"],
            "tier_note": spec["tier_note"],
            "substitutes": spec["substitutes"],
            "no_substitute_known": None,
            "no_substitute_note": None,
            "exposure": spec["exposure"],
            "exposure_ev": "extrapolated",
            "exposure_src": SURF,
            "exposure_basis": spec["exposure_basis"],
            "conc": None,
            "conc_src": None,
            "conc_ev": "untested",
            "grade_as_sold": None,
            "grade_as_sold_src": None,
            "strength_disclosure": "full",
            "disclosure_note": None,
            "added": TODAY,
            "owner_ev": "verified",
            "owner_src": owners["owners"][spec["owner"]]["src"],
            "updated": TODAY,
        }
        for label in spec["ings"]:
            key, new = resolve(ingredients, ingredients, label)
            rec["ings"].append(key)
            if new:
                minted.append(new)
        products.append(rec)
        added.append(spec["name"])

    # assert every referenced ingredient key resolves
    missing = sorted({k for p in products for k in p["ings"] if k not in ingredients})
    if missing:
        raise SystemExit("dangling ingredient references: %s" % missing)

    if added:
        cl = load("changelog.json")
        cl.insert(0, {"date": TODAY, "text": CHANGELOG_TEXT})
        write_json(DATA / "changelog.json", cl, 2, False)

    write_json(DATA / "products.json", products, 1, False)
    write_json(DATA / "ingredients.json", ingredients, 1, True)
    write_json(DATA / "owners.json", owners, 1, False)

    print("added %d products; minted %d keys: %s" % (len(added), len(minted), minted))
    for n in added:
        print("  +", n)


if __name__ == "__main__":
    main()
