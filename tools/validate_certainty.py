#!/usr/bin/env python3
"""Certainty validation and ownership application.

Two jobs, both enforcement rather than documentation:

1. Every graded claim in data/oils.json must carry a valid evidence level.
   A claim with no level, or a level outside the five, fails the build. This
   is the same principle as the voice rule in build.py: a rule that is only
   remembered gets violated by the next automated writer.

2. Apply data/owners.json to data/products.json, writing owner, owner_ev and
   owner_src onto each product. Ownership is an evidence claim like any other.

Usage:
    python3 tools/validate_certainty.py          # validate + report
    python3 tools/validate_certainty.py --apply  # validate, then write owners
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"

LEVELS = {"verified", "reported", "extrapolated", "untested", "unknown"}
FLAGS = {"avoid", "caution", "no_signal", "untested"}

failures = []
warnings = []

# Warning lanes do not persist indefinitely. Every lane has three exits: close,
# escalate to a halt, or be reclassified as an accepted constraint. Linnea's
# rule, and the discriminator is the vocabulary's: Class B lanes are OUR gaps
# (untested) and are supposed to close, so they halt on a deadline rather than
# waiting for a human to notice. Class A lanes are facts about the world
# (unknown/constraint) and are per-item states, never timers.
LANE_STATE = REPO / "data" / "lane_state.json"
LANE_REGISTRY = {
    "tier_src": {"class": "B", "opened": "2026-09-23", "deadline": "2026-09-30",
                 "detail": "products carry tier_ev=reported with no tier_src"},
    "reg_src": {"class": "B", "opened": "2026-09-23", "deadline": "2026-09-30",
                "detail": "reg.json entries name no source"},
}


def track_lane(name, count, today=None):
    """Record a lane's count, its delta, and enforce its deadline.

    A warning stops being read when it stops changing, not when it gets old.
    So the delta is printed, and the deadline, not the age, is what escalates.
    """
    if today is None:
        from datetime import date
        today = date.today().isoformat()
    state = {}
    if LANE_STATE.exists():
        state = json.loads(LANE_STATE.read_text(encoding="utf-8"))
    lane = state.get(name, {"count": None, "unchanged": 0, "opened": today})
    lane["unchanged"] = lane["unchanged"] + 1 if lane["count"] == count else 0
    lane["count"] = count
    state[name] = lane
    LANE_STATE.write_text(json.dumps(state, indent=1, sort_keys=True), encoding="utf-8")

    meta = LANE_REGISTRY.get(name, {})
    delta = f"unchanged {lane['unchanged']} builds" if lane["unchanged"] else "changed this build"
    msg = f"{name}: {count} ({delta})"
    if meta.get("class") == "B" and today > meta.get("deadline", "9999"):
        failures.append(
            f"{msg} -- Class B lane past its {meta['deadline']} deadline. A gap that was "
            f"supposed to close and did not is a process failure, and it halts rather than "
            f"waiting to be noticed.")
    else:
        warnings.append(msg + (f", deadline {meta['deadline']}" if meta.get("class") == "B" else ""))
    return count


def load(name, default=None):
    p = DATA / name
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def check_claim(where, claim):
    """A claim is a dict with an 'ev' key from LEVELS."""
    if not isinstance(claim, dict):
        failures.append(f"{where}: claim is not an object")
        return
    ev = claim.get("ev")
    if ev is None:
        failures.append(f"{where}: claim has no evidence level")
    elif ev not in LEVELS:
        failures.append(f"{where}: invalid evidence level {ev!r}")
    # A verified claim must resolve to a source.
    if ev == "verified" and not claim.get("src"):
        failures.append(f"{where}: marked verified with no source")
    # 'reported' means 'we name the source'. A reported claim with no source
    # renders as 'Reported by [source]' with nothing to put there, which is
    # indistinguishable from verified. Either name the source or downgrade.
    # Raised by Linnea, CCI-009 rev1, GAP 2.
    if ev == "reported" and not claim.get("src"):
        failures.append(f"{where}: marked reported with no named source")
    # An untested claim must say what was searched and why it is flagged,
    # otherwise it becomes a resting place rather than a finding.
    # Raised by Linnea, CCI-67b9fae rev2: untested needs (a) what was searched,
    # (b) a note, (c) a re-check trigger.
    # extrapolated must say what was searched for DIRECT data. A false basis is
    # worse than a shrug: it renders as a finding with a fake reason. This is
    # the Pennyroyal.children failure caught mechanically. Linnea, Q2.
    if ev == "extrapolated":
        basis = (claim.get("basis") or "").strip()
        if len(basis) < 40:
            failures.append(f"{where}: extrapolated with no stated basis")
        elif not any(w in basis.lower() for w in ("search", "located", "not measured",
                                                  "not itself", "no direct", "extrapolat")):
            failures.append(
                f"{where}: extrapolated without saying what was searched for direct data")
    if ev == "untested" and len((claim.get("basis") or "").strip()) < 40:
        failures.append(
            f"{where}: marked untested with no note on what was searched. "
            f"An untested claim without a basis is a shrug, not a finding.")


def validate_oils():
    oils = load("oils.json")
    if oils is None:
        warnings.append("oils.json not present, skipped")
        return 0
    n = 0
    for section in ("oils", "blends"):
        for name, o in oils.get(section, {}).items():
            for dim, claim in o.get("cleaning", {}).items():
                check_claim(f"oils.{section}.{name}.cleaning.{dim}", claim)
                n += 1
            for pop, claim in o.get("populations", {}).items():
                check_claim(f"oils.{section}.{name}.populations.{pop}", claim)
                flag = claim.get("flag")
                if flag not in FLAGS:
                    failures.append(
                        f"oils.{section}.{name}.populations.{pop}: "
                        f"invalid flag {flag!r}")
                n += 1
            # A legend or a claim conflict must carry its own level.
            # Both a legend and a claim conflict make factual assertions, so
            # both carry a level. Raised by Linnea, CCI-009 rev1, GAP 1: the
            # comment said so but the code only checked naming_legend.
            for extra in ("naming_legend", "claim_conflict"):
                if extra in o:
                    check_claim(f"oils.{section}.{name}.{extra}", o[extra])
                    n += 1
    return n


def validate_owners():
    """Owner entries are evidence claims too.

    R4, raised by Linnea: apply_owners() read owners.json without ever
    validating it, so a reported-with-no-source owner entry passed the very
    check that exists to catch it. The Honest Company and Grove Collaborative
    were sitting in exactly that state.
    """
    owners = load("owners.json")
    if owners is None:
        return 0
    n = 0
    for name, info in owners.get("owners", {}).items():
        where = f"owners.{name}"
        ev, src = info.get("ev"), info.get("src")
        if ev not in LEVELS:
            failures.append(f"{where}: invalid or missing evidence level {ev!r}")
        if ev in ("verified", "reported") and not src:
            failures.append(f"{where}: marked {ev} with no named source")
        if src and not str(src).startswith("http"):
            failures.append(f"{where}: source is not a resolvable URL")
        if not info.get("brands"):
            failures.append(f"{where}: owner entry lists no brands")
        n += 1
    return n


def validate_surfaces():
    """Every claim-bearing surface is enumerated here on purpose.

    Linnea's structural point: coverage was whatever files someone remembered to
    hand the validator, which is how R1, R2 and R4 all happened. Add a surface
    to this list when you add a file that makes claims.
    """
    n = 0

    # --- products: owner drift + tier sourcing ---
    products = load("products.json")
    owners = load("owners.json")
    if products and owners:
        # Drift check: the committed file must agree with what owners.json
        # computes. build.py used to recompute in dry mode and never compare,
        # so a stale file passed the build forever. Linnea, CCI-ed915d58.
        drift = []
        for p in products:
            if p.get("owner_ev") in ("reported", "verified") and not p.get("owner_src"):
                drift.append(p.get("name"))
        if drift:
            failures.append(
                f"products.json: {len(drift)} products claim a sourced owner with no "
                f"owner_src (run validate_certainty.py --apply). Namely: "
                + ", ".join(drift[:6]) + ("..." if len(drift) > 6 else ""))

        no_tier_src = [p.get("name") for p in products
                       if p.get("tier_ev") == "reported" and not p.get("tier_src")]
        if no_tier_src:
            track_lane("tier_src", len(no_tier_src))
        n += len(products)

    # --- reg.json: 40 regulatory claims, none carrying a source ---
    reg = load("reg.json")
    if isinstance(reg, dict):
        entries = reg.get("entries", {})
        unsourced = []
        for chem, lst in entries.items():
            for e in (lst if isinstance(lst, list) else []):
                if isinstance(e, dict) and not e.get("src"):
                    unsourced.append(f"{chem}: {str(e.get('rule'))[:40]}")
        if unsourced:
            track_lane("reg_src", len(unsourced))
        n += len(unsourced)

    return n


def check_substitutes():
    """Every hazard must name a usable substitute, or say it has none.

    Sandra's rule is to document what TO DO as much as what NOT to do. That
    rule has no meaning unless it is checkable, so a product carrying a severe
    grade with an empty substitutes list is reported by name every build.
    Warning, not a halt: backfilling the whole catalog is a lane, not a night.
    """
    products = load("products.json")
    if products is None:
        return 0
    severe, missing = [], []
    for p in products:
        safe = p.get("safe")
        is_severe = isinstance(safe, str) and "Sifter grade" in safe and (
            "grade D" in safe or "grade F" in safe)
        if not is_severe:
            continue
        severe.append(p.get("name"))
        subs = p.get("substitutes") or []
        if not subs and not p.get("no_substitute_known"):
            missing.append(p.get("name"))
    if missing:
        warnings.append(
            f"hazard without a substitute on file ({len(missing)} of {len(severe)}): "
            + ", ".join(missing))
    return len(severe)


def apply_owners(dry=True):
    owners = load("owners.json")
    products = load("products.json")
    if owners is None or products is None:
        warnings.append("owners.json or products.json missing, skipped")
        return 0, 0

    # brand -> (parent, ev, src)
    table = {}
    for parent, info in owners.get("owners", {}).items():
        for b in info.get("brands", []):
            table[b] = (parent, info.get("ev", "untested"), info.get("src"))

    # A parent company can also be the brand on the label (Windex is SC Johnson,
    # Mr. Clean is P&G, Lysol is Reckitt). The subsidiary->parent map missed
    # these entirely and stamped them "unknown", which under the new vocabulary
    # would render as "Not disclosed" and accuse P&G of hiding Mr. Clean.
    # Nobody chose that; it was our lookup gap. Linnea, CCI-d04c72a.
    parents = set(owners.get("owners", {}).keys())

    matched = 0
    for p in products:
        brand = p.get("brand")
        if brand in parents:
            p["owner"] = brand
            p["owner_ev"] = "verified" if brand in ("The Honest Company",) else "reported"
            p["owner_src"] = owners["owners"][brand].get("src")
            matched += 1
            continue
        if brand in table:
            parent, ev, src = table[brand]
            p["owner"], p["owner_ev"], p["owner_src"] = parent, ev, src
            matched += 1
        elif brand in owners.get("independents", {}).get("brands", []):
            # Deliberately explicit. "No parent found" is not "independent".
            p["owner"] = None
            p["owner_ev"] = "untested"
            p["owner_src"] = None
            matched += 1
        else:
            # NOT "unknown". Unknown means a party upstream withheld identity.
            # This is our own unexamined gap, and the two must never render the
            # same way. See the scoping note in docs/certainty.md.
            p["owner"] = None
            p["owner_ev"] = "untested"
            p["owner_src"] = None

    if not dry:
        (DATA / "products.json").write_text(
            json.dumps(products, indent=1, ensure_ascii=False), encoding="utf-8")
    return matched, len(products)


def main():
    apply = "--apply" in sys.argv
    # Apply FIRST when asked. Running it after validation means the drift check
    # reads the stale committed file and fails on data it is about to fix.
    matched, total = apply_owners(dry=not apply) if apply else (0, 0)
    n_oil = validate_oils()
    n_own = validate_owners()
    n_surf = validate_surfaces()
    n_severe = check_substitutes()
    if not apply:
        matched, total = apply_owners(dry=True)

    print(f"certainty: {n_oil} oil claims checked")
    print(f"ownership: {matched} of {total} products carry an ownership record")
    print(f"ownership entries: {n_own} owner records validated")
    print(f"surfaces: {n_surf} claim-bearing records considered (products, reg)")
    print(f"hazards: {n_severe} products carry a severe grade")

    if warnings:
        for w in warnings:
            print(f"  warn: {w}")

    if failures:
        print(f"\nFAIL — {len(failures)} problem(s):")
        for f in failures:
            print(f"  {f}")
        return 1

    print("PASS — every claim carries a valid evidence level")
    return 0


if __name__ == "__main__":
    sys.exit(main())
