#!/usr/bin/env python3
"""CCI-012 Lane 3 (reg.json watchlist half) — add a source to every watchlist entry
and correct the rule text where a primary source contradicts it.

Before this run, none of the nine `reg.json` -> `watchlist` entries carried a `src`,
and the validator only checks `entries` (never `watchlist`), so the whole block was
unvalidated. Four entries also carried claims that a primary source contradicts:

  * Triclosan        "EU banned in cosmetics / since 2010"  -> Reg. (EU) 358/2014
                     RESTRICTS triclosan (0.3% in listed product types, 0.2% in
                     mouthwash) and applies from 2014, not 2010.
  * Titanium Dioxide "EU classified Carcinogen 1B by inhalation (2020)" -> the
                     classification was Carc. 2 and was ANNULLED by the General
                     Court in 2022, the annulment upheld by the Court of Justice on
                     1 Aug 2025 (OJ C/2025/6670). No harmonised classification applies.
  * Talc             "EU tightens asbestos-in-talc limits / since 2016" -> the EU
                     action is a proposed classification of talc itself as Carc. 1B
                     (ECHA RAC recommendation, opinion published July 2025), not an
                     asbestos limit. Entry renamed from "Talc (asbestos-contaminated)".
  * 1,4-Dioxane      "CA requires disclosure above 1 ppm" -> California requires
                     online listing at 10 ppm or more (HSC 108954.5), and SB 258
                     covers cleaning products, not personal care.

Idempotent: re-running produces a byte-identical file.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REG = REPO / "data" / "reg.json"

# name-as-found -> corrected record. `src` is added to every entry; other keys are
# only set where a source contradicts the existing value.
FIXES = {
    "Triclosan": {
        "status": "restricted",
        "since": "2014",
        "rule": ("EU restricts triclosan in cosmetics to 0.3% in listed product types and "
                 "0.2% in mouthwash (Reg. 358/2014) \u2014 a restriction, not a general ban. "
                 "US: FDA banned OTC consumer antiseptic washes in 2016, but it remains in "
                 "some consumer products."),
        "src": "https://eur-lex.europa.eu/eli/reg/2014/358/oj/eng",
    },
    "Nonylphenol Ethoxylates": {
        "rule": ("EU restricts nonylphenol and NPEs at 0.1% or more in domestic and industrial "
                 "cleaning, textiles, cosmetics and other uses (Directive 2003/53/EC, applied "
                 "from 17 January 2005). US: EPA's 2010 action plan pursued a voluntary "
                 "industrial-laundry phase-out and proposed TSCA rules; no consumer cleaning ban."),
        "src": "https://eur-lex.europa.eu/eli/dir/2003/53/oj/eng",
    },
    "Phosphates (detergents)": {
        "rule": ("EU banned phosphates in consumer laundry detergent from 30 June 2013 and in "
                 "consumer dishwasher detergent from 1 January 2017 (Reg. 259/2012). "
                 "US: no federal ban; a few state-level limits."),
        "src": "https://eur-lex.europa.eu/eli/reg/2012/259/oj",
    },
    "Parabens (propyl/butyl)": {
        "rule": ("EU prohibits propylparaben and butylparaben in leave-on products for the nappy "
                 "area of children under 3 (Reg. 1004/2014, Annex V entry 12a; applied from "
                 "16 April 2015), and caps them at 0.14% as acid elsewhere. US: allowed without "
                 "that age restriction."),
        "src": "https://eur-lex.europa.eu/eli/reg/2014/1004/oj",
    },
    "Formaldehyde": {
        "src": "https://echa.europa.eu/cosmetics-prohibited-substances",
    },
    "Titanium Dioxide (powder)": {
        "status": "restricted",
        "since": "2022",
        "rule": ("The 2020 EU classification of titanium dioxide powder as a carcinogen by "
                 "inhalation was annulled by the EU General Court (23 November 2022) and the "
                 "annulment was upheld by the Court of Justice on 1 August 2025, so no harmonised "
                 "classification applies. Separately, the EU banned TiO2 (E171) as a food additive "
                 "from 7 August 2022. US: allowed in food and cosmetics."),
        "reason": ("Inhalation carcinogenicity was the basis for the (now annulled) EU "
                   "classification; the E171 food-additive ban rested on genotoxicity concerns."),
        "src": "https://eur-lex.europa.eu/eli/C/2025/6670/oj/eng",
    },
    "Microplastics (intentionally added)": {
        "rule": ("EU banned intentionally added microplastics (Reg. 2023/2055), applying from "
                 "17 October 2023 with transitional periods running to 2035 for uses such as "
                 "rinse-off cosmetics. US: state-level only."),
        "src": ("https://single-market-economy.ec.europa.eu/sectors/chemicals/reach/restrictions/"
                "commission-regulation-eu-20232055-restriction-microplastics-intentionally-added-products_en"),
    },
    "Talc (asbestos-contaminated)": {
        "name": "Talc",
        "status": "review",
        "since": "2025",
        "rule": ("ECHA's Risk Assessment Committee has recommended classifying talc as a "
                 "Category 1B carcinogen and as STOT RE 1 by inhalation. The recommendation is "
                 "not yet adopted; the Commission is facing parliamentary questions over the "
                 "evidence. US: FDA testing programme, no ban."),
        "reason": "Proposed carcinogenicity by inhalation; talc-based cleaning powders affected.",
        "src": "https://www.europarl.europa.eu/doceo/document/E-10-2025-004190_EN.html",
    },
    "1,4-Dioxane": {
        "since": "2023",
        "rule": ("EU: 1,4-dioxane is on the REACH Restrictions Roadmap for potential restriction; "
                 "nothing is adopted. US: New York caps it in household cleansing and personal care "
                 "products at 2 ppm from 31 December 2022 and 1 ppm from 31 December 2023 "
                 "(ECL 35-0105); California requires cleaning-product makers to list it online at "
                 "10 ppm or more (HSC 108954.5)."),
        "src": ("https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?article=&"
                "chapter=13.&division=104.&lawCode=HSC&part=3.&title="),
    },
}


# a renamed entry must resolve on the second run too, or the script is not idempotent
ALIASES = {v["name"]: k for k, v in FIXES.items() if v.get("name")}


def lookup(name: str):
    if name in FIXES:
        return FIXES[name]
    return FIXES.get(ALIASES.get(name, ""))


def main() -> int:
    data = json.loads(REG.read_text(encoding="utf-8"))
    watch = data["watchlist"]

    seen = set()
    for entry in watch:
        name = entry["name"]
        seen.add(name)
        fix = lookup(name)
        if fix is None:
            raise SystemExit(f"halt: no fix authored for watchlist entry {name!r}")
        entry.update(fix)

    missing = set(FIXES) - {ALIASES.get(n, n) for n in seen} - seen
    if missing:
        raise SystemExit(f"halt: fix authored for absent entry {sorted(missing)}")

    # an absence with no named source is indistinguishable from an absence nobody looked for
    unsourced = [e["name"] for e in watch if not e.get("src")]
    if unsourced:
        raise SystemExit(f"halt: watchlist entries still carry no src: {unsourced}")

    REG.write_text(
        json.dumps(data, indent=1, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"watchlist: {len(watch)} entries updated, {len(watch)} carry src")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
