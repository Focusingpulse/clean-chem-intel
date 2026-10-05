#!/usr/bin/env python3
"""Apply Linnea's R1 (required) and R2 (recommended) revisions, 2026-10-05.

Source verdict: three-agent-intelligence/verdicts/clean-chem-delta-sifter-grow-sort-2026-10-04.md
(2026-10-04 20:00Z), over the Sifter grow+sort commit c721d4f.

R1 (required, text-only) -- three note fixes, no data change:
  1. Sodium Metabisulfite note misattributes the Danger signal. It says the
     H334/H372 minority block "is ... the reason the powder carries a Danger
     signal". Wrong: the Danger signal is driven by H318 (Eye Dam. 1 at 99.5%
     consensus), which alone mandates Danger. The minority block is not the
     reason for the signal word.
  2. Benzene, C10-13 alkyl derivatives note carries the merged-in boilerplate
     "so the verified grade reaches them". That survivor is UNGRADED (g null);
     there is no verified grade to deliver. The merge is a canonicalization.
  3. Sodium (C10-16) Alkylbenzenesulfonate carries the same boilerplate twice;
     its grade is Extrapolated, not verified.

R2 (recommended) -- add the RAC context to the metabisulfite record: the EU
harmonised classification is H302 + H318 only, and the 2021 RAC opinion on the
SO2 releaser concluded respiratory sensitisation does not apply to sodium
metabisulfite (the asthma-like effects are SO2-mediated and classified as STOT
SE, not H334). The resp D is a conservative worst-credible notifier-block call
and must not be readable as the EU harmonised position.

No `g`, `ev`, `gr` or `impacts` value is touched. Idempotent: a second run
reports 0 edits.

Usage:  python3 tools/repair_2026_10_05.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
DRY = "--dry-run" in sys.argv

META_NOTE = (
    "Graded from PubChem GHS (CID 656671, sodium pyrosulfite): aggregate "
    "consensus H302 98.9%, H318 99.5%; minority notifier blocks carry H334 "
    "respiratory sensitizer, H317, H335, H372 (organ damage through prolonged "
    "exposure) and H402/H412. The Danger signal is driven by H318 (Eye Dam. 1 "
    "at 99.5% consensus) on its own; the minority H334/H372 block is not the "
    "reason for the signal word. Those minority severe codes are graded "
    "worst-credible rather than consensus-only, consistent with the "
    "Butyloxyethanol organ-D precedent; the low-severity minority codes (H317, "
    "H335) are recorded but not graded. The EU harmonised classification for "
    "sodium metabisulfite is H302 + H318 only, and the 2021 RAC opinion on the "
    "SO2 releaser concluded that respiratory sensitisation does not apply to "
    "sodium metabisulfite (the asthma-like effects are SO2-mediated and "
    "classified as STOT SE, not H334). The respiratory D here is therefore a "
    "conservative worst-credible notifier-block call and must not be read as "
    "the EU harmonised position. Releases sulfur dioxide on contact with acid. "
    "Disclosed by the Iron OUT Powder manufacturer SDS."
)

BENZENE_OLD_TAIL = ("1 product disclosed it under that spelling and now read "
                    "this key, so the verified grade reaches them.")
BENZENE_NEW_TAIL = ("1 product disclosed it under that spelling and now reads "
                    "this single record. This record is ungraded (g is null): "
                    "the merge is a canonicalization of two spellings for one "
                    "substance, not a grade delivery.")

LAS_OLD_TAIL = ("now read this key, so the verified grade reaches them.")
LAS_NEW_TAIL = ("now read this key, so the extrapolated grade reaches them.")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def dump(path, obj):
    # ingredients.json is indent=1 with no trailing newline (measured at head).
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)


def main():
    ings = load(os.path.join(DATA, "ingredients.json"))
    edits = 0

    # R1.1 + R2 -- Sodium Metabisulfite note.
    key = "Sodium Metabisulfite"
    if key not in ings:
        raise SystemExit(f"missing key {key!r}")
    if ings[key]["note"] == META_NOTE:
        print(f"{key}: already corrected (no-op)")
    else:
        ings[key]["note"] = META_NOTE
        edits += 1
        print(f"{key}: note corrected (R1.1 Danger-signal attribution + R2 RAC context)")

    # R1.2 -- Benzene, C10-13 alkyl derivatives boilerplate.
    key = "Benzene, C10-13 alkyl derivatives"
    if key not in ings:
        raise SystemExit(f"missing key {key!r}")
    note = ings[key]["note"]
    if "so the verified grade reaches them" in note:
        ings[key]["note"] = note.replace(BENZENE_OLD_TAIL, BENZENE_NEW_TAIL)
        edits += 1
        print(f"{key}: ungraded-survivor boilerplate corrected (R1.2)")
    else:
        print(f"{key}: already corrected (no-op)")

    # R1.3 -- Sodium (C10-16) Alkylbenzenesulfonate boilerplate (twice).
    key = "Sodium (C10-16) Alkylbenzenesulfonate"
    if key not in ings:
        raise SystemExit(f"missing key {key!r}")
    note = ings[key]["note"]
    n = note.count("so the verified grade reaches them")
    if n:
        ings[key]["note"] = note.replace(LAS_OLD_TAIL, LAS_NEW_TAIL)
        edits += 1
        print(f"{key}: extrapolated-grade boilerplate corrected x{n} (R1.3)")
    else:
        print(f"{key}: already corrected (no-op)")

    # Guard: no grade/evidence field may have changed shape.
    for k in ("Sodium Metabisulfite", "Benzene, C10-13 alkyl derivatives",
              "Sodium (C10-16) Alkylbenzenesulfonate"):
        if "g" not in ings[k] or "ev" not in ings[k]:
            raise SystemExit(f"{k!r} lost a required field")

    if DRY:
        print(f"\nDRY RUN: {edits} note edit(s) would be written.")
        return
    dump(os.path.join(DATA, "ingredients.json"), ings)
    print(f"\nwrote {edits} note edit(s).")


if __name__ == "__main__":
    main()
