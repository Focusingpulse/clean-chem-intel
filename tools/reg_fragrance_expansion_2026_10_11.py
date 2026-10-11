#!/usr/bin/env python3
"""Regulatory watch (2026-10-11): the EU fragrance-allergen list expanded.

The registry's "Fragrance" entry records the 2005 rule -- mandatory labelling of
26 fragrance allergens. That is still true, but it is no longer the whole rule.
Commission Regulation (EU) 2023/1545 (in force 16 August 2023) amended the
Cosmetics Regulation (EC) No 1223/2009 to expand the mandatory on-pack
disclosure list from 24/26 substances to more than 80, at labelling thresholds
of 0.001% in leave-on products and 0.01% in rinse-off products; prehaptens and
prohaptens that oxidise or bioactivate into known contact allergens are treated
as allergens too. New products must comply from 31 July 2026; products already
on the market before that date may remain until 31 July 2028.

Why it matters for this corpus. Five of the products in the database disclose
named fragrance components (eugenol, isoeugenol, methyl salicylate, citral,
limonene, citronellol ...), and the Zep Grout Cleaner & Brightener record added
today discloses five by name. The US has no equivalent: fragrance is a trade
secret under US law and no allergen labelling is required. So the same bottle
carries a longer disclosure in the EU than in the US, and the gap widens on
31 July 2026.

This script APPENDS a second EU entry to the existing "Fragrance" key rather
than replacing the 2005 entry -- both rules are in force simultaneously.

Source read 2026-10-11:
  https://eur-lex.europa.eu/eli/reg/2023/1545/oj/eng
  https://www.hpra.ie/regulation/cosmetics/labelling-and-claims/cosmetic-products-labelling/labelling-of-cosmetic-fragrance-allergens
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-11"

NEW_ENTRY = {
    "region": "eu",
    "status": "restricted",
    "since": "2023",
    "rule": ("EU Cosmetics Reg. (EU) 2023/1545 (in force 16 August 2023) "
             "expanded the mandatory on-pack fragrance-allergen disclosure "
             "list from 24/26 substances to more than 80, at thresholds of "
             "0.001% in leave-on and 0.01% in rinse-off products; prehaptens "
             "and prohaptens that oxidise or bioactivate into known contact "
             "allergens are treated as allergens. New products must comply "
             "from 31 July 2026; products on the market before that date may "
             "remain until 31 July 2028."),
    "reason": ("SCCS identified additional fragrance allergens with a "
               "potential risk to human health; the 2005 list of 26 was "
               "incomplete. US law still treats fragrance as a trade secret "
               "with no allergen labelling, so the same product carries a "
               "longer disclosure in the EU than in the US."),
    "confidence": "High",
    "src": "https://eur-lex.europa.eu/eli/reg/2023/1545/oj/eng",
}


def main():
    path = os.path.join(DATA, "reg.json")
    reg = json.load(open(path, encoding="utf-8"))
    entries = reg["entries"]
    frag = entries.setdefault("Fragrance", [])

    # Idempotent: skip if the expansion entry is already present.
    for e in frag:
        if e.get("since") == "2023" and "2023/1545" in (e.get("rule") or ""):
            print("expansion entry already present; no change")
            return

    frag.append(NEW_ENTRY)
    if "--dry-run" in sys.argv:
        print("DRY RUN: would append the 2023/1545 expansion entry to 'Fragrance'")
        return
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=1, ensure_ascii=False)
    print(f"appended EU 2023/1545 expansion entry to 'Fragrance' "
          f"({len(frag)} region entries now)")

    # Changelog note.
    cl_path = os.path.join(DATA, "changelog.json")
    changelog = json.load(open(cl_path, encoding="utf-8"))
    changelog.insert(0, {
        "date": TODAY,
        "text": ("Regulatory watch: the registry's 'Fragrance' entry recorded "
                 "only the 2005 rule (26 mandatory-labelled fragrance "
                 "allergens). Added the EU's 2023/1545 expansion -- the list "
                 "grew past 80 substances at 0.001% leave-on / 0.01% rinse-off "
                 "thresholds, with new products required to comply from "
                 "31 July 2026 and existing stock until 31 July 2028. Both "
                 "rules are now recorded; the US still requires no fragrance "
                 "allergen labelling at all. Relevant to the five products in "
                 "the corpus that disclose named fragrance components, "
                 "including the Zep Grout Cleaner & Brightener record added "
                 "this run."),
    })
    with open(cl_path, "w", encoding="utf-8") as fh:
        json.dump(changelog, fh, indent=2, ensure_ascii=False)
    print("changelog updated")


if __name__ == "__main__":
    main()
