#!/usr/bin/env python3
"""Clean Chem Intel site builder — the living-system core.

Reads data/*.json, merges into a template, writes index.html with a
generated-at stamp. The cron workflow: edit data -> run build.py -> push.
Nothing in the site is hand-edited HTML anymore.

Usage:
    python3 build.py
"""
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent
DATA = REPO / "data"
TPL = REPO / "index.template.html"
OUT = REPO / "index.html"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))



# ---------- voice enforcement ----------
# BMVC voice rules apply to every rendered string, including data notes,
# blurbs, reclassification text, and changelog entries. The rules cannot live
# in the template only: the data lanes write prose too, so enforcement happens
# here, on the final HTML, on every build. Nothing can silently regress.
EM_DASH = "\u2014"

def voice_normalize(html):
    """Strip em dashes and enforce the CTA rule on rendered output.

    Comma before a lowercase continuation (label or fragment),
    period before an uppercase one (new sentence).
    """
    import re
    before = html.count(EM_DASH)
    html = html.replace(">\u2014<", ">n/a<")
    # Numeric ranges first, before the general rule:
    # "pH 6 — 8" must become "pH 6 to 8", never "pH 6, 8".
    # Caught by Linnea (CCI-009) as the failure mode most likely to bite.
    html = re.sub(r"(\d)\s*" + EM_DASH + r"\s*(\d)", r"\1 to \2", html)
    # Tight compounds with no surrounding space are hyphenated words,
    # not sentence breaks: "water—soluble" -> "water-soluble".
    # KNOWN FALSE POSITIVE, documented so garbled output is recognisable:
    # a no-space parenthetical collapses, because this rule runs before the
    # case heuristic: "the dog—a beagle—barked" -> "the dog-a beagle-barked".
    # It never fires on current data (none of the 151 em dashes are tight;
    # the data's parentheticals are all spaced). Flagged by Linnea, CCI-009 rev1.
    # If it ever does fire, the fix is to require the preceding token to be a
    # single word rather than narrowing the character class.
    html = re.sub(r"(\w)" + EM_DASH + r"(\w)", r"\1-\2", html)
    def repl(m):
        after = m.group(1)
        sep = ". " if after.isupper() else ", "
        return sep + after
    html = re.sub(r"\s*" + EM_DASH + r"\s*([A-Za-z0-9])", repl, html)
    # FALLBACK, and the rule above cannot cover every case: it requires an
    # alphanumeric to follow the dash, so a dash before a quote, bracket or any
    # other character falls through. The old bare replace here then left the
    # original surrounding spaces untouched and emitted " ,  " (space, comma,
    # two spaces) straight into the rendered page. Four of those were live on
    # the site 2026-10-08, two from this path and two baked into the template.
    # Consume the surrounding whitespace so the separator is always ", ".
    html = re.sub(r"\s*" + EM_DASH + r"\s*", ", ", html)
    html = html.replace("Get a Free Quote", "Get a Quote")
    html = html.replace("Free Quote", "Get a Quote")
    after = html.count(EM_DASH)
    return html, before, after


def certainty_guard():
    """Refuse to build if any claim carries an invalid or missing evidence level.

    Same principle as the voice rule: enforcement in the build, not in memory.
    The certainty vocabulary only means something if a violation stops the build.
    """
    import subprocess
    r = subprocess.run(
        [sys.executable, str(REPO / "tools" / "validate_certainty.py"), "--apply"],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout or r.stderr)
        raise SystemExit(
            "build halted: certainty validation failed. Fix the claims, "
            "do not silence the check.")
    for line in (r.stdout or "").splitlines():
        if line.startswith(("certainty:", "ownership:", "exposure:", "surfaces:", "hazards:")):
            print("  " + line)
        elif line.strip().startswith("warn:"):
            # Warnings are lanes, not failures. Printed so they stay visible.
            print("  " + line.strip())


def main():
    certainty_guard()
    products = load("products.json")
    ings = load("ingredients.json")
    changelog = load("changelog.json")
    reg = load("reg.json")

    # Last-updated = newest changelog date (stable across day rebuilds)
    last_updated = max(e["date"] for e in changelog) if changelog else date.today().isoformat()

    # Live stats for the hero
    n_reclassified = sum(1 for v in ings.values() if v.get("reclassified"))
    n_heritage = sum(1 for p in products if p.get("heritage"))
    n_safe = sum(1 for p in products if p.get("safe"))

    # Regulatory scoreboard
    entries = reg.get("entries", {})
    n_restricted_anywhere = len(entries)
    # count by status per region (US explicit entries)
    by_region = {}
    us_flags = []
    for ing, lst in entries.items():
        for e in lst:
            r = e["region"]
            by_region.setdefault(r, {"banned": 0, "restricted": 0, "review": 0, "flagged": 0, "allowed": 0})
            st = e.get("status", "restricted")
            by_region[r][st] = by_region[r].get(st, 0) + 1
            if r == "us" and st in ("flagged", "restricted", "banned"):
                us_flags.append({"ing": ing, "status": st, "since": e.get("since"), "rule": e.get("rule", "")})
    scoreboard = {
        "n_restricted_anywhere": n_restricted_anywhere,
        "watchlist": len(reg.get("watchlist", [])),
        "by_region": by_region,
        "us_flags": us_flags,
        "us_flags_count": len(us_flags),
    }

    meta = {
        "products": len(products),
        "ingredients": len(ings),
        "reclassified": n_reclassified,
        "heritage": n_heritage,
        "safe": n_safe,
        "restricted_anywhere": n_restricted_anywhere,
        "last_updated": last_updated,
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "tagline": "A living database of cleaning products — graded ingredient by ingredient, updated regularly.",
    }

    # ---- machine-readable layer (added 2026-10-05) ----
    # The tool is the citable surface for this asset, so it carries its own
    # structured data rather than leaving that to the BMVC page that embeds it.
    # Counts are read from the same lists the page renders from, so the schema
    # cannot drift from the page it describes. Entity ids match the live BMVC
    # homepage nodes (#business) exactly; never mint a second business node.
    TOOL_URL = "https://focusingpulse.github.io/clean-chem-intel/"
    BMVC_BUSINESS = "https://bellasmountainvacationcleaning.com/#business"
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebApplication",
                "@id": TOOL_URL + "#app",
                "name": "Clean Chem Intel",
                "url": TOOL_URL,
                "applicationCategory": "ReferenceApplication",
                "operatingSystem": "Any",
                "isAccessibleForFree": True,
                "inLanguage": "en-US",
                "description": (
                    "A living database of %d cleaning products and %d ingredient "
                    "profiles, graded ingredient by ingredient and searchable by "
                    "health impact." % (len(products), len(ings))
                ),
                "dateModified": last_updated,
                "publisher": {"@id": BMVC_BUSINESS},
            },
            {
                "@type": "Dataset",
                "@id": TOOL_URL + "#dataset",
                "name": "Clean Chem Intel cleaning product database",
                "description": (
                    "Cleaning products with ingredient-level health-impact grading "
                    "and regulatory status by region."
                ),
                "isPartOf": {"@id": TOOL_URL + "#app"},
                "creator": {"@id": BMVC_BUSINESS},
                "inLanguage": "en-US",
                "dateModified": last_updated,
                # Each dimension is a qualitative grade the page assigns per
                # ingredient, not a scalar with a population value, so it carries
                # a description and NOT a made-up "value".
                "variableMeasured": [
                    {"@type": "PropertyValue", "name": "Respiratory impact",
                     "description": "Graded from the ingredient's published respiratory-sensitization and inhalation hazard data."},
                    {"@type": "PropertyValue", "name": "Reproductive impact",
                     "description": "Graded from the ingredient's published reproductive and developmental toxicity data."},
                    {"@type": "PropertyValue", "name": "Endocrine impact",
                     "description": "Graded from the ingredient's published endocrine-disruption data."},
                    {"@type": "PropertyValue", "name": "Skin impact",
                     "description": "Graded from the ingredient's published dermal-irritation and sensitization data."},
                    {"@type": "PropertyValue", "name": "Aquatic impact",
                     "description": "Graded from the ingredient's published aquatic-toxicity data."},
                    {"@type": "PropertyValue", "name": "Cancer impact",
                     "description": "Graded from the ingredient's published carcinogenicity classifications."},
                    {"@type": "PropertyValue", "name": "Allergen impact",
                     "description": "Graded from the ingredient's published allergen and sensitization data."},
                ],
            },
        ],
    }

    tpl = TPL.read_text(encoding="utf-8")

    def inject(token, obj):
        return html.replace(token, json.dumps(obj, ensure_ascii=False))

    html = tpl
    html = inject("__PRODUCTS__", products)
    html = inject("__INGS__", ings)
    html = inject("__CHANGELOG__", changelog)
    html = inject("__META__", meta)
    html = inject("__SCHEMA__", schema)
    html = inject("__REG__", reg)
    html = inject("__SCOREBOARD__", scoreboard)

    html, _em_before, _em_after = voice_normalize(html)
    if _em_before:
        print(f"  voice: normalized {_em_before} em dash(es) out of rendered output")

    OUT.write_text(html, encoding="utf-8")

    print(f"built {OUT.name}: {len(products)} products, {len(ings)} ingredients")
    print(f"  last_updated={last_updated} | reclassified={n_reclassified} | heritage={n_heritage} | safe={n_safe} | restricted-elsewhere={n_restricted_anywhere}")
    print(f"  size: {OUT.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()