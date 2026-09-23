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
    "ingredient_self_conflict": {"class": "B", "opened": "2026-09-23", "deadline": "2026-09-30",
                "detail": "ingredient headline grade contradicts its own dimension grades"},
    "case_duplicate_grades": {"class": "B", "opened": "2026-09-23", "deadline": "2026-09-30",
                "detail": "the same chemical stored under two keys with different grades"},
    # NOTE: this lane is a SCREEN, not a verdict. Absence of a supporting code
    # is evidence of possible drift, not proof of it. Some grades come from a
    # mechanism the g field cannot express (respirable silica for a resp grade,
    # a separate toxicology finding for an organ grade on a carcinogen record).
    # Those are legitimate and need a documented basis rather than an H-code.
    # Linnea's merge rule requires re-deriving from the codified source per
    # substance, which is research, not a mechanical fix. Do not auto-drop.
    "dimension_without_hcode": {"class": "B", "opened": "2026-09-23", "deadline": "2026-09-30",
                "detail": "SCREEN: a dimension grade that no H-code in its own g supports. "
                          "Review, do not auto-drop."},
    "strength_not_disclosed": {"class": "A", "opened": "2026-09-23",
                "detail": "products whose source states no concentration, so no as-sold grade is derivable"},
}

# Which GHS hazard codes can support which rubric dimension. A dimension grade
# that no code in the record's own g supports is drift, not a grading. Linnea,
# two-level-grade-rule review 2026-09-23. "work" is excluded deliberately: it is
# the rubric's PPE band, not a GHS code, and has no code to trace to.
DIMENSION_HCODES = {
    "derm":  ("H314", "H315", "H316", "H317", "H318"),
    "organ": ("H370", "H371", "H372", "H373"),
    "repro": ("H360", "H361", "H362", "H360D", "H360F", "H360FD"),
    "canc":  ("H350", "H351"),
    # H373 (STOT RE 2) is listed under resp as well as organ on purpose: its
    # canonical statement is "May cause damage to organs through prolonged or
    # repeated exposure", and when the named organ is the lung it IS the
    # respiratory code. Respirable crystalline silica is the textbook STOT RE
    # lung case. Linnea, dimension-traceability-rubric-2026-09-23.
    "resp":  ("H334", "H335", "H336", "H373"),
    "endo":  ("H361", "H360", "H360F", "H360FD"),
    "env":   ("H400", "H410", "H411", "H412", "H413"),
}


def _read_state():
    """Read the lane state tolerantly.

    Linnea hit this during her replay and read it as a test artifact. It is a
    real latent fault: a zero-byte or truncated state file is a valid thing to
    find on disk (interrupted write, disk pressure) and it crashed the guard
    with JSONDecodeError. Lane history is disposable; failing the build over it
    is not. A corrupted file is treated as an empty one and rebuilt.
    """
    if not LANE_STATE.exists():
        return {}
    try:
        return json.loads(LANE_STATE.read_text(encoding="utf-8") or "{}")
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return {}


def track_lane(name, count, today=None):
    """Record a lane's count, its delta, and enforce its deadline.

    A warning stops being read when it stops changing, not when it gets old,
    so the delta is printed. The deadline, not the age, is what escalates.

    Closure is recorded explicitly. Linnea, lane-closure-edge-ff68505: the
    original version only recorded non-zero counts, so a closed lane kept its
    last count and, on reopening with the same number, resumed its unchanged
    counter. The delta exists to prevent alarm fatigue, and reporting a
    regression as continuity is precisely the warning that gets ignored.
    """
    from datetime import date
    if today is None:
        today = date.today().isoformat()

    state = _read_state()
    prev = state.get(name, {})
    lane = {
        "count": prev.get("count"),
        "unchanged": prev.get("unchanged", 0),
        "opened": prev.get("opened", today),
        "closed": prev.get("closed"),
        "ever_closed": prev.get("ever_closed", False),
        "reopened": prev.get("reopened"),
    }

    # --- closure: record it rather than leaving the last non-zero count ---
    if count == 0:
        lane.update(count=0, unchanged=0, closed=lane["closed"] or today,
                    ever_closed=True, reopened=None)
        state[name] = lane
        LANE_STATE.write_text(json.dumps(state, indent=1, sort_keys=True), encoding="utf-8")
        return 0

    # --- reopening: never report continuity across a closure ---
    if lane["closed"]:
        lane.update(unchanged=0, opened=today, closed=None, reopened=today)

    was = lane["count"]
    lane["unchanged"] = lane["unchanged"] + 1 if was == count else 0
    lane["count"] = count
    state[name] = lane
    LANE_STATE.write_text(json.dumps(state, indent=1, sort_keys=True), encoding="utf-8")

    # --- delta wording: three distinct states, never conflated ---
    if lane["reopened"] == today and lane["unchanged"] == 0:
        delta = "REOPENED this build, was closed"
    elif lane["unchanged"]:
        delta = f"unchanged {lane['unchanged']} builds"
    else:
        delta = "changed this build"

    meta = LANE_REGISTRY.get(name, {})
    msg = f"{name}: {count} ({delta})"
    if name not in LANE_REGISTRY:
        warnings.append(msg + " -- no registry entry. A lane without a deadline is the "
                             "'persists indefinitely' state the policy exists to kill.")
    elif meta.get("class") == "B" and today > meta.get("deadline", "9999"):
        # The rationale has to distinguish the two ways a lane can be late.
        why = ("closed once and has regressed" if lane["ever_closed"]
               else "was supposed to close and did not")
        failures.append(
            f"{msg} -- Class B lane past its {meta['deadline']} deadline, and it {why}. "
            f"A gap that {why} is a process failure, and it halts rather than waiting "
            f"to be noticed.")
    else:
        suffix = f", deadline {meta['deadline']}" if meta.get("class") == "B" else ""
        warnings.append(msg + suffix)
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
    if ev == "reported" and not claim.get("src"):
        failures.append(f"{where}: marked reported with no named source")
    # extrapolated must say what was searched for DIRECT data. A false basis is
    # worse than a shrug: it renders as a finding with a fake reason.
    # The Pennyroyal.children failure, caught mechanically.
    if ev == "extrapolated":
        basis = (claim.get("basis") or "").strip()
        if len(basis) < 40:
            failures.append(f"{where}: extrapolated with no stated basis")
        elif not any(w in basis.lower() for w in ("search", "located", "not measured",
                                                  "not itself", "no direct", "extrapolat")):
            failures.append(
                f"{where}: extrapolated without saying what was searched for direct data")
    # An untested claim must say what was searched and why it is flagged,
    # otherwise it becomes a resting place rather than a finding.
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
        track_lane("tier_src", len(no_tier_src))
        n += len(products)

    # --- ingredients.json: records that contradict themselves ---
    # Same shape as R1/R2/R4: a record saying two things and passing every
    # check because nothing compares the two fields. A "Not Classified"
    # headline sitting on an F dimension means the page shows whichever renders
    # first. Found while checking Chris's vinegar commit, Sep 23.
    ings = load("ingredients.json")
    if isinstance(ings, dict):
        self_conflict = []
        for name, rec in ings.items():
            if not isinstance(rec, dict):
                continue
            g = rec.get("g") or ""
            dims = rec.get("gr") or {}
            if g in ("Not Classified", "", None) and any(
                    v in ("D", "F") for v in dims.values()):
                self_conflict.append(name)
        track_lane("ingredient_self_conflict", len(self_conflict))

        # The same chemical under two keys with different grades: products
        # reference whichever the ingest lane wrote, so the answer changes by
        # spelling. Propylene Glycol carries {organ D, repro B}; propylene
        # glycol carries {organ D}.
        by_lower = {}
        for name, rec in ings.items():
            if not isinstance(rec, dict):
                continue
            by_lower.setdefault(name.strip().lower(), []).append((name, rec.get("gr") or {}))
        dupes = {k: v for k, v in by_lower.items() if len(v) > 1}
        conflicting = [k for k, v in dupes.items() if len({str(x[1]) for x in v}) > 1]
        track_lane("case_duplicate_grades", len(conflicting))

        # A dimension grade no code in the record's own g supports is drift.
        # Products read the capitalised keys, so drift there is live drift.
        unsupported = []
        for name, rec in ings.items():
            if not isinstance(rec, dict):
                continue
            g = rec.get("g") or ""
            for dim, grade in (rec.get("gr") or {}).items():
                if dim == "work":          # rubric PPE band, not a GHS code
                    continue
                codes = DIMENSION_HCODES.get(dim)
                if not codes:
                    continue
                # An extrapolated record has no H-code by definition. But the
                # exemption is PER DIMENSION, not per record: an extrapolation
                # justifies the dimension its class analogy supports and nothing
                # else. The generic Enzymes key is g=Extrapolated with resp D
                # AND repro B; the enzyme-protein analogy supports respiratory
                # sensitisation and says nothing about reproductive toxicity, so
                # repro B is drift riding an exemption it did not earn.
                # Linnea caught this hole in my first version.
                if g == "Extrapolated":
                    if dim in (rec.get("documented_mechanism") or {}):
                        continue
                    mech = rec.get("extrapolation_supports") or []
                    if dim in mech:
                        continue
                if grade not in ("D", "F"):
                    continue
                if any(c in g for c in codes):
                    continue
                # Documented mechanism is a third state, not a defect: real and
                # sourced, but GHS cannot encode it. Acceptable only when the
                # basis is written INTO the record and names a source. A basis
                # living in decisions.md is not a trace a page reader can audit.
                dm = (rec.get("documented_mechanism") or {}).get(dim)
                if dm and dm.get("src") and dm.get("mechanism") and dm.get("quote"):
                    continue
                if dm and not dm.get("quote"):
                    # mechanism + src is not enough. The dioxane failure carried
                    # BOTH and was still invented. What it could not have carried
                    # is the passage: a real justification is a quotation, and a
                    # recollection is what got fabricated.
                    unsupported.append(
                        f"{name}.{dim}={grade} [documented_mechanism has no quotable passage]")
                unsupported.append(f"{name}.{dim}={grade}")
        track_lane("dimension_without_hcode", len(unsupported))

        n += len(self_conflict)

    # --- reg.json: 40 regulatory claims, none carrying a source ---
    reg = load("reg.json")
    if isinstance(reg, dict):
        entries = reg.get("entries", {})
        unsourced = []
        for chem, lst in entries.items():
            for e in (lst if isinstance(lst, list) else []):
                if isinstance(e, dict) and not e.get("src"):
                    unsourced.append(f"{chem}: {str(e.get('rule'))[:40]}")
        track_lane("reg_src", len(unsourced))
        n += len(unsourced)

    return n


CLAIM_CONFLICT_FIELDS = ("manufacturer_claim", "manufacturer_src",
                         "toxicology_finding", "toxicology_src")


def validate_claim_conflicts():
    """A claim conflict is a claim-bearing surface too.

    Linnea, SPX spectrum build verdict, R1 (2026-09-23): the new dollar-store
    and drugstore entries carried the hazard side and no manufacturer side, so a
    safety claim stood unopposed in the record. docs/certainty.md rule 5 says
    both sides get recorded and the page shows the tension.

    The shape is enforced here so the next automated writer cannot add a
    half-block: every block must carry a level, a resolving block source, both
    sides, and a resolving source for each side. Whether a product HAS a
    manufacturer safety claim is not something a validator can know, so that
    half is a warning that names the severe-grade products still unreviewed
    rather than a halt.
    """
    products = load("products.json")
    if products is None:
        return 0, []
    n = 0
    for p in products:
        cf = p.get("claim_conflict")
        if cf is None:
            continue
        n += 1
        where = f"claim_conflict[{p.get('name','?')}]"
        if not isinstance(cf, dict):
            failures.append(f"{where}: not an object")
            continue
        ev = cf.get("ev")
        if ev not in LEVELS:
            failures.append(f"{where}: invalid or missing evidence level {ev!r}")
        for field in CLAIM_CONFLICT_FIELDS:
            if not (cf.get(field) or "").strip():
                failures.append(f"{where}: missing {field}")
        for field in ("src", "manufacturer_src", "toxicology_src"):
            val = (cf.get(field) or "").strip()
            if val and not val.startswith("http"):
                failures.append(f"{where}: {field} is not a resolvable URL")

    # Every severe-grade product should carry either a recorded manufacturer
    # claim or a written note that none was located. Warning, not a halt: some
    # manufacturers simply do not make a safety claim, and inventing one to
    # satisfy a check is the failure mode this whole file exists to prevent.
    #
    # "None located" is a claim-bearing surface of its own (claim_review): it
    # asserts that a search was done and names the page it was done against, so
    # it is validated with the same strictness as a conflict block. An absence
    # recorded with no source is indistinguishable from an absence never looked
    # for, and the warning would then read as reviewed in both cases.
    unreviewed = []
    for p in products:
        safe = p.get("safe")
        is_severe = isinstance(safe, str) and "grade" in safe and (
            "grade D" in safe or "grade F" in safe)
        if is_severe and not (p.get("claim_conflict") or p.get("claim_review")):
            unreviewed.append(p.get("name"))
    return n, unreviewed


CLAIM_REVIEW_FIELDS = ("result", "note")


def validate_claim_reviews():
    """A written 'no claim located' is a claim too, so it gets a shape.

    Added 2026-09-23 with the first claim_review blocks. The point of the field
    is to close the severe-grade warning honestly for products whose maker makes
    no safety claim, without letting "we looked and found nothing" be asserted
    for free. A review with no result, no note, or no named page is exactly that
    free assertion, so it halts the build.
    """
    products = load("products.json")
    if products is None:
        return 0
    n = 0
    for p in products:
        cr = p.get("claim_review")
        if cr is None:
            continue
        n += 1
        where = f"claim_review[{p.get('name','?')}]"
        if not isinstance(cr, dict):
            failures.append(f"{where}: not an object")
            continue
        ev = cr.get("ev")
        if ev not in LEVELS:
            failures.append(f"{where}: invalid or missing evidence level {ev!r}")
        for field in CLAIM_REVIEW_FIELDS:
            if not (cr.get(field) or "").strip():
                failures.append(f"{where}: missing {field}")
        src = (cr.get("src") or "").strip()
        if not src.startswith("http"):
            failures.append(f"{where}: src is not a resolvable URL")
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


def validate_exposure():
    """Exposure is a claim. It gets the same treatment as any other.

    Added with the spectrum build (Trellis, Sep 22 2026: order by exposure, not
    price tier). The ordering rule is only meaningful if the exposure number is
    a sourced estimate rather than a number shaped like one, so the guard fails
    the build when:

      - a non-null exposure carries no valid evidence level
      - a non-null exposure carries no source
      - an extrapolated exposure does not say what was searched for direct data
        (the check_claim rule, applied to a new dimension)

    An exposure of null with ev=untested is a legitimate and honest outcome; it
    is a research gap, not a violation.
    """
    products = load("products.json")
    if products is None:
        return 0
    n = 0
    for p in products:
        name = p.get("name", "?")
        ev = p.get("exposure_ev")
        val = p.get("exposure")
        if ev is None:
            failures.append(f"exposure[{name}]: claim has no evidence level")
        elif ev not in LEVELS:
            failures.append(f"exposure[{name}]: invalid evidence level {ev!r}")
        if val is not None:
            if ev == "untested":
                failures.append(
                    f"exposure[{name}]: carries a value {val!r} but is marked untested")
            if not p.get("exposure_src"):
                failures.append(
                    f"exposure[{name}]: carries a value {val!r} with no exposure_src")
        if ev == "extrapolated":
            basis = (p.get("exposure_basis") or "").strip()
            if len(basis) < 40:
                failures.append(f"exposure[{name}]: extrapolated with no stated basis")
            elif not any(w in basis.lower() for w in ("search", "located", "not measured",
                                                      "no direct", "none exists",
                                                      "extrapolat")):
                failures.append(
                    f"exposure[{name}]: extrapolated without saying what was searched "
                    f"for direct data")
        n += 1
    return n


def main():
    apply = "--apply" in sys.argv
    # Apply FIRST when asked. Running it after validation means the drift check
    # reads the stale committed file and fails on data it is about to fix.
    matched, total = apply_owners(dry=not apply) if apply else (0, 0)
    n_oil = validate_oils()
    n_own = validate_owners()
    n_surf = validate_surfaces()
    n_exp = validate_exposure()
    n_severe = check_substitutes()
    n_cf, cf_unreviewed = validate_claim_conflicts()
    n_cr = validate_claim_reviews()
    if cf_unreviewed:
        warnings.append(
            f"severe-grade product with no manufacturer claim on file ({len(cf_unreviewed)} of "
            f"{n_severe}): " + ", ".join(cf_unreviewed)
            + " -- record the manufacturer's claim, or record that none was located")
    if not apply:
        matched, total = apply_owners(dry=True)

    print(f"certainty: {n_oil} oil claims checked")
    print(f"ownership: {matched} of {total} products carry an ownership record")
    print(f"ownership entries: {n_own} owner records validated")
    print(f"exposure: {n_exp} exposure claims checked")
    print(f"claim conflicts: {n_cf} product records carry both sides of a claim")
    print(f"claim reviews: {n_cr} product records state that no manufacturer claim was located")
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
