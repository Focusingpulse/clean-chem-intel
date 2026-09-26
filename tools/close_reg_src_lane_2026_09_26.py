#!/usr/bin/env python3
"""Close the `reg_src` Class B lane (deadline 2026-09-30, build halts 2026-10-01).

Lane: data/reg.json carries 40 regulatory claims with no resolving source.
This assigns each entry the URL of the authoritative instrument its own `rule`
text names. Nothing else changes: no rule text, no status, no confidence.

Two rules followed:
  * The source is the instrument named in the entry's `rule`, not a search page.
  * Where the entry states a US *absence* ("no federal restriction"), the source
    is the federal page whose scope is exactly that question (FDA prohibited/
    restricted list, FDA allergens, EPA action), so the absence is auditable
    rather than asserted. `src_note` says so on those entries.

Every index is asserted against (chem, region, status) so a data change fails
loudly instead of mis-assigning a source.

Run: python3 tools/close_reg_src_lane_2026_09_26.py
Then: python3 tools/validate_certainty.py --apply && python3 build.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REG = REPO / "data" / "reg.json"

# ---- authoritative instruments -------------------------------------------------
COSM = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009R1223"
CLP = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32008R1272"
REACH = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32006R1907"
BPR = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012R0528"
DEC_2026_599 = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32026D0599"
R_2021_1902 = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32021R1902"
R_2023_1490 = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R1490"
HC_HOTLIST = ("https://www.canada.ca/en/health-canada/services/consumer-product-safety/"
              "cosmetics/cosmetic-ingredient-hotlist-prohibited-restricted-ingredients.html")
PROP65 = "https://oehha.ca.gov/proposition-65/proposition-65-list"
SB258 = ("https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml"
         "?lawCode=HSC&division=104.&title=&part=3.&chapter=13.&article=")
NY_DEC = ("https://dec.ny.gov/environmental-protection/pollution-prevention/"
          "household-personal-cosmetic-dioxane-limits")
JP_MHLW = ("https://www.mhlw.go.jp/file/06-Seisakujouhou-11120000-Iyakushokuhinkyoku/"
           "0000032704.pdf")
FDA_ALLERGENS = "https://www.fda.gov/cosmetics/cosmetic-ingredients/allergens-cosmetics"
FDA_PROHIB = ("https://www.fda.gov/cosmetics/cosmetics-laws-regulations/"
              "prohibited-restricted-ingredients-cosmetics")
EPA_NPE = ("https://www.epa.gov/assessing-and-managing-chemicals-under-tsca/"
           "risk-management-nonylphenol-and-nonylphenol-ethoxylates")
EPA_BORIC = ("https://www3.epa.gov/pesticides/chem_search/reg_actions/reregistration/"
             "red_PC-011001_16-Feb-94.pdf")

# (index, expected chem, expected region, expected status, src, src_note)
MAP = [
    (1, "Methylisothiazolinone", "eu", "restricted", COSM, ""),
    (2, "Methylisothiazolinone", "ca", "restricted", HC_HOTLIST, ""),
    (3, "Benzisothiazolinone", "eu", "restricted", COSM, ""),
    (4, "Quaternary Ammonium", "eu", "review", BPR, ""),
    (5, "Didecyldimonium Chloride", "eu", "review", BPR, ""),
    (6, "Benzalkonium Chloride", "eu", "restricted", COSM, ""),
    (7, "Butyloxyethanol", "eu", "restricted", CLP, ""),
    (8, "Butyloxyethanol", "us", "flagged", PROP65, ""),
    (9, "Fragrance", "eu", "restricted", COSM, ""),
    (10, "Limonene", "eu", "restricted", COSM, ""),
    (11, "Essential Oils", "eu", "restricted", COSM, ""),
    (12, "Citral", "eu", "restricted", COSM, ""),
    (13, "Sodium Laureth Sulfate", "eu", "restricted", COSM, ""),
    (14, "Alcohol Ethoxylates", "eu", "restricted", CLP, ""),
    (15, "Alcohol Ethoxylate", "eu", "restricted", CLP, ""),
    (16, "Phenoxyethanol", "eu", "restricted", COSM, ""),
    (17, "Phenoxyethanol", "jp", "restricted", JP_MHLW,
     "Japan MHLW Standards for Cosmetics, App. 3: phenoxyethanol capped at 1.0% "
     "across all cosmetic types. English provisional translation (PDF)."),
    (18, "Hydrogen Peroxide", "eu", "restricted", COSM, ""),
    (19, "Sodium Tetraborate", "eu", "restricted", CLP, ""),
    (20, "Sodium Tetraborate", "us", "allowed", EPA_BORIC,
     "The claim is an absence: EPA's Reregistration Eligibility Decision covers boric "
     "acid and its sodium salts as registered pesticide actives, i.e. EPA regulates "
     "them rather than banning consumer sale."),
    (21, "Trichloroisocyanuric Acid", "eu", "restricted", CLP, ""),
    (22, "Ethanolamine", "eu", "restricted", COSM, ""),
    (23, "DMDM Hydantoin", "eu", "restricted", COSM, ""),
    (24, "DMDM Hydantoin", "us", "allowed", FDA_ALLERGENS,
     "Absence claim. FDA lists DMDM hydantoin among cosmetic preservatives without a "
     "federal concentration cap or formaldehyde-releaser labelling rule."),
    (25, "Formaldehyde releaser (paraformaldehyde + 2-hydroxypropylamine 1:1)", "eu",
     "banned", DEC_2026_599, ""),
    (26, "Formaldehyde", "eu", "restricted", REACH,
     "REACH Annex XVII Entry 77 (formaldehyde emission limits in articles)."),
    (27, "1,4-Dioxane", "us", "restricted", NY_DEC,
     "New York ECL Art. 35/37 limits; DEC implements as 6 NYCRR Subpart 352-1."),
    (28, "1,4-Dioxane", "eu", "restricted", REACH,
     "REACH Restrictions Roadmap lists further 1,4-dioxane uses for potential "
     "Annex XVII restriction; not yet adopted."),
    (29, "Methylchloroisothiazolinone", "eu", "banned", COSM, ""),
    (30, "Methylchloroisothiazolinone", "eu", "restricted", CLP, ""),
    (31, "Methylchloroisothiazolinone", "us", "allowed", FDA_ALLERGENS,
     "Absence claim. FDA lists CMIT among cosmetic preservatives with no US federal "
     "ppm cap for household cleaners."),
    (32, "Butylphenyl Methylpropional", "eu", "banned", R_2021_1902,
     "Commission Regulation (EU) 2021/1902 added BMHCA (Lilial) to Cosmetics Reg. "
     "Annex II after CMR 1B classification by Delegated Reg. (EU) 2020/1182."),
    (33, "Butylphenyl Methylpropional", "us", "allowed", FDA_PROHIB,
     "Absence claim. FDA's own list of prohibited/restricted cosmetic ingredients "
     "does not include BMHCA or any fragrance allergen."),
    (34, "Benzophenone", "eu", "banned", R_2023_1490,
     "Commission Regulation (EU) 2023/1490 added benzophenone to Cosmetics Reg. "
     "Annex II (Entry 1703)."),
    (35, "Benzophenone", "us", "flagged", SB258,
     "California Cleaning Product Right to Know Act (SB-258), HSC Ch. 13 "
     "ss 108950-108960 and its designated lists."),
    (36, "Sodium Metaborate", "eu", "restricted", CLP, ""),
    (37, "Nonoxynol", "eu", "restricted", REACH,
     "REACH Annex XVII Entry 46 (nonylphenol and NPEs)."),
    (38, "Nonoxynol", "us", "allowed", EPA_NPE,
     "Absence claim plus EPA's actual action: SNUR for industrial uses only, no "
     "household-cleaning restriction."),
    (39, "Citronellol", "eu", "restricted", COSM, ""),
    (40, "Citronellol", "us", "allowed", FDA_PROHIB,
     "Absence claim. No US requirement to name individual fragrance allergens on "
     "cleaning-product labels."),
]


def main():
    reg = json.loads(REG.read_text())
    flat = []
    for chem, lst in reg["entries"].items():
        for e in lst:
            flat.append((chem, e))
    assert len(flat) == 40, f"expected 40 reg entries, found {len(flat)}"

    changed = 0
    for idx, chem, region, status, src, note in MAP:
        got_chem, e = flat[idx - 1]
        assert got_chem == chem, f"row {idx}: expected {chem!r}, got {got_chem!r}"
        assert e.get("region") == region, f"row {idx}: region {e.get('region')!r} != {region!r}"
        assert e.get("status") == status, f"row {idx}: status {e.get('status')!r} != {status!r}"
        if e.get("src") != src:
            e["src"] = src
            changed += 1
        if note:
            e["src_note"] = note

    # Preserve the repo's exact on-disk formatting (indent=1, ensure_ascii, no
    # trailing newline) so the diff is only the added fields.
    REG.write_text(json.dumps(reg, indent=1))
    print(f"reg_src lane: {changed} entries assigned a source, {len(MAP)} rows checked")


if __name__ == "__main__":
    main()
