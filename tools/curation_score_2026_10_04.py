#!/usr/bin/env python3
"""Chem-curation scoring + routing — 2026-10-04.

Scores the ungraded products for BMVC-audience relevance and emits the weekly
curation queue (STEP 2/3/4 of the chem-curation cron).

Weights (unchanged from 2026-09-27, so the weekly comparison stays meaningful):
    sales 30% | str 25% | mountain 20% | hazard 15% | ungraded 10%

Changes from the 2026-09-27 run:
  1. `safe` is treated as a THREE-value field. 2026-09-27 selected with
     `p.get('safe') is None`, which silently drops any product holding a
     boolean False (Dawn Ultra Dishwashing Liquid). Ungraded = falsy safe.
  2. sales is anchored on the measured `exposure` field where present, with a
     MEASURED / ESTIMATED / UNSOURCED evidence label, instead of a name list.
     The name list stays only as a fallback for products with no exposure.
  3. ungraded is scaled by disclosure completeness, not a flat 10.0. A stub
     note with one named ingredient is not the same curation target as a full
     CAS-level list.
  4. The queue carries three blocks the v1 queue lacked: `routing_exceptions`
     (research items outside the ranked set — v1's vocabulary structurally
     could not emit a research route from a set defined as "ungraded"),
     `coverage` (the whole 257-product population, so the queue is readable
     against something other than itself), and `data_flags`.

Every dimension carries an evidence label so no score overstates what we hold
(SO-02): no sales data is invented; where the data holds nothing the score is
marked UNSOURCED and left at a neutral mid-point.
"""
import json
import re
import argparse
from datetime import datetime, timezone

WEIGHTS = {"sales": 0.30, "str": 0.25, "mountain": 0.20, "hazard": 0.15, "ungraded": 0.10}
TOP_N = 30

# --- research lane (STEP 4) -------------------------------------------------
# Products whose ingredient list is deliberately incomplete: components that were
# intentionally added are not named. Read from the notes, not keyword-matched.
RESEARCH_PREFIXES = [
    "Kirkland Signature Ultra Shine Premium Dish Soap",
    "Mean Green Super Strength Cleaner",
    "Krud Kutter Original",
    "Invisible Glass (Aerosol)",
    "Granite Gold Daily Cleaner",
    "Fels-Naptha Heavy Duty Laundry Bar Soap",
    "Great Value Carpet & Upholstery Cleaner Oxy",
    "Comet Classic Shower Cleaner",
    "Comet Ultra Bathroom Spray",
    "Great Value Lemon Scent Foaming Bathroom Cleaner",
    "Goo Gone Original",
    "CVS All Purpose Cleaner + Bleach Spray",
    "Fresh Gel Toilet Cleaning Stamp",
    "Clorox 2 for Colors Stain Remover",
]
# borderline: one class-named line, or a gap narrower than a withheld component
RESEARCH_BORDERLINE = {
    "Goo Gone Original",
    "CVS All Purpose Cleaner + Bleach Spray",
    "Fresh Gel Toilet Cleaning Stamp",
    "Clorox 2 for Colors Stain Remover",
}
# Near-misses, recorded with the reason so a later run does not re-litigate them.
# A thin list is not automatically a gap: for a single-substance product (baking
# soda, citric acid, vinegar, isopropyl alcohol) a one-line list IS the whole
# formula. Research priority is a read of the note, not a count of lines.
EXCLUDED_FROM_RESEARCH = {
    "Weiman Stainless Steel Cleaner & Polish":
        "identities listed, 8 lines; concentrations withheld as trade secret - a concentration gap, not a component gap",
    "Murphy Original Oil Soap":
        "undisclosed fragrance blend only; fragrance-only withholding is a category pattern carried in the hazard factor, not a product-specific research target",
    "Folex Instant Carpet Spot Remover":
        "components named; CAS withheld on 4 of 5. The disclosure_note hit was an incidental source-spelling mapping",
}
EXCLUDED_PREFIXES = {
    "Liquid-Plumr Pro-Strength Clog Destroyer":
        "disclosure_note states the SmartLabel names every intentionally-added component - no gap",
}

# --- sales ----------------------------------------------------------------
# exposure is the one household-penetration field we actually hold. Values in
# the ungraded set run 1-30. Reported = measured; extrapolated = estimated.
EXPOSURE_STEPS = [(20, 9.5), (15, 9.0), (12, 8.0), (10, 7.0), (8, 6.0),
                  (6, 5.0), (5, 4.5), (4, 4.0), (3, 3.5), (2, 3.0), (1, 2.0)]
TIER_BREADTH = {"mass": 1.0, "grocery": 0.5, "drugstore": 0.5,
                "dollar-store": 0.0, "natural": -0.5, "apothecary-bulk": -0.5}
BRAND_ANCHORS = {  # fallback only, for products with no exposure value at all
    "Dawn", "Tide", "Gain", "Clorox", "Lysol", "Pine-Sol", "Fabuloso", "Mr. Clean",
    "Windex", "Cascade", "Palmolive", "Ajax", "Febreze", "Comet", "Soft Scrub",
    "Simple Green", "Bar Keepers Friend", "Drano", "CLR", "Swiffer", "Finish",
    "Murphy", "Scrubbing Bubbles", "Formula 409", "OxiClean", "Shout", "Resolve",
}

# --- str: turnover-checklist relevance ------------------------------------
STR_CAT = {"Disinfectant": 9.5, "Bathroom": 9.0, "Laundry": 8.5, "Floor & Carpet": 7.5,
           "Dishwasher": 7.5, "All-Purpose": 7.0, "Glass": 7.0, "Stain & Odor": 6.5,
           "Dish Soap": 6.0, "Abrasive Cleanser": 5.5, "Hand Soap": 4.5,
           "Wood & Stone Care": 4.0, "Specialty": 3.5, "Physical": 3.0}
STR_KEYWORDS = [
    (re.compile(r"sanitiz|disinfect|bleach|antibacterial", re.I), 1.0),
    (re.compile(r"mold|mildew", re.I), 1.0),
    (re.compile(r"stain\s*(remover|fighter)|spot\s*remover|oxy", re.I), 1.0),
    (re.compile(r"toilet|tub|shower|tile|grout", re.I), 0.5),
    (re.compile(r"laundry|fabric|linen", re.I), 0.5),
]

# --- mountain: hard water / soot / mildew / wood --------------------------
MOUNTAIN_CAT = {"Wood & Stone Care": 9.0, "Bathroom": 8.5, "Glass": 8.0,
                "Abrasive Cleanser": 7.5, "Dishwasher": 7.5, "Floor & Carpet": 7.0,
                "Stain & Odor": 6.5, "All-Purpose": 6.5, "Disinfectant": 6.0,
                "Laundry": 5.5, "Dish Soap": 5.5, "Specialty": 5.5,
                "Hand Soap": 4.5, "Physical": 4.0}
MOUNTAIN_KEYWORDS = [
    (re.compile(r"hard water|lime[- ]?a[- ]?way|limescale|calcium|rust|\bclr\b", re.I), 1.5),
    (re.compile(r"soot|creosote|wood stove|stove|oven|chimney", re.I), 1.0),
    (re.compile(r"mold|mildew|moss", re.I), 1.0),
    (re.compile(r"granite|stone|marble|quartz|travertine|slate", re.I), 1.0),
    (re.compile(r"wood|oak|teak|cabinet|leather", re.I), 1.0),
    (re.compile(r"de[- ]?icer|ice melt|road salt|salt stain", re.I), 1.0),
]

# --- hazard: MEASURED from the ingredient acts we hold --------------------
HAZARD_TERMS = [
    (re.compile(r"benzyl.*ammonium|didecyldimethyl|alkyl.*dimethyl.*ammonium|quaternary", re.I), "quats", 3.0),
    (re.compile(r"2-butoxyethanol|butyl.*glycol|ethylene glycol monobutyl|glycol ether", re.I), "glycol ethers", 2.5),
    (re.compile(r"sodium hypochlorite|hypochlorite", re.I), "sodium hypochlorite", 2.0),
    (re.compile(r"ammonium hydroxide|\bammonia\b", re.I), "ammonia", 2.0),
    (re.compile(r"hydrochloric acid|phosphoric acid|sulfuric acid|sulfamic acid", re.I), "strong acid", 2.5),
    (re.compile(r"sodium hydroxide|potassium hydroxide|\blye\b|caustic", re.I), "caustic alkali", 2.0),
    (re.compile(r"methylisothiazolinone|methylchloroisothiazolinone|\bMIT\b|\bCMIT\b", re.I), "isothiazolinone preservative", 2.0),
    (re.compile(r"nonylphenol|octylphenol|alkylphenol", re.I), "alkylphenol ethoxylates", 2.5),
    (re.compile(r"dmdm hydantoin|quaternium-15|diazolidinyl urea|imidazolidinyl urea|formaldehyde", re.I), "formaldehyde releaser", 1.5),
    (re.compile(r"sodium tetraborate|borax|boric acid", re.I), "borates", 2.0),
    (re.compile(r"oxalic acid", re.I), "oxalic acid", 1.5),
    (re.compile(r"phthalate", re.I), "phthalates", 1.5),
    (re.compile(r"trichloro|dichloro|chlorine bleach", re.I), "chlorinated compound", 2.0),
    (re.compile(r"fragrance|parfum|\bscent\b", re.I), "undisclosed fragrance", 1.5),
]
HAZARD_BASE = 4.0


def evidence_class(ev):
    if ev == "reported":
        return "MEASURED"
    if ev == "extrapolated":
        return "ESTIMATED"
    return "UNSOURCED"


def sales_score(p):
    exp, ev = p.get("exposure"), p.get("exposure_ev")
    tier = p.get("tier")
    if exp:
        base = next((s for cut, s in EXPOSURE_STEPS if exp >= cut), 2.0)
        base += TIER_BREADTH.get(tier, 0.0)
        cls = evidence_class(ev)
        label = f"{cls} exposure={exp} ({ev or 'no basis'}) tier={tier or 'untiered'}"
    else:
        brand = p.get("brand") or ""
        base = 6.0 if any(b.lower() in (p.get("name") or "").lower() for b in BRAND_ANCHORS) else 3.0
        cls = "ESTIMATED"
        label = f"ESTIMATED brand anchor, no exposure value held tier={tier or 'untiered'}"
    return round(max(0.0, min(10.0, base)), 2), label, cls


def cat_keyword_score(cat, cat_map, default, keywords, name, label):
    base = cat_map.get(cat, default)
    hits = [rx.pattern for rx, w in keywords if rx.search(name or "")]
    base += sum(w for rx, w in keywords if rx.search(name or ""))
    return round(max(0.0, min(10.0, base)), 2), f"ESTIMATED ({label}" + (f"; +{len(hits)} keyword hits)" if hits else ")")


def hazard_score(p):
    ings = p.get("ings") or []
    if not ings:
        return HAZARD_BASE, "UNSOURCED (no ingredient list held)", []
    found, total = [], HAZARD_BASE
    for rx, lab, w in HAZARD_TERMS:
        if any(rx.search(str(i)) for i in ings):
            found.append(lab)
            total += w
    total = min(10.0, total)
    return round(total, 2), (f"MEASURED ({', '.join(found)})" if found else "MEASURED (no flagged act in list)"), found


def ungraded_score(p):
    ings = p.get("ings") or []
    named = [i for i in ings if i and str(i).strip() and "proprietary" not in str(i).lower()]
    if len(named) >= 3:
        return 10.0, f"MEASURED ({len(named)} named components, no grade)"
    if named:
        return 6.0, f"MEASURED (only {len(named)} named component, thin list)"
    return 3.0, "MEASURED (no named components)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--products", default="data/products.json")
    ap.add_argument("--out", default="/tmp/curation-queue-2026-10-04.json")
    args = ap.parse_args()

    items = json.load(open(args.products))

    # `safe` is a THREE-value field: None (never graded), True (graded), and
    # one stray boolean False. Ungraded = falsy, so nothing is silently dropped.
    ungraded = [p for p in items if not p.get("safe")]
    graded = [p for p in items if p.get("safe")]
    bool_defects = [p["name"] for p in items if p.get("safe") is False]

    rows = []
    for p in ungraded:
        s, s_lab, s_cls = sales_score(p)
        t, t_lab = cat_keyword_score(p.get("cat"), STR_CAT, 4.0, STR_KEYWORDS, p.get("name"), "turnover-domain category")
        m, m_lab = cat_keyword_score(p.get("cat"), MOUNTAIN_CAT, 4.0, MOUNTAIN_KEYWORDS, p.get("name"), "product purpose vs hard water/soot/mildew/wood")
        h, h_lab, h_found = hazard_score(p)
        u, u_lab = ungraded_score(p)
        total = sum(WEIGHTS[k] * v for k, v in
                    (("sales", s), ("str", t), ("mountain", m), ("hazard", h), ("ungraded", u)))
        rows.append({
            "name": p.get("name"), "brand": p.get("brand"), "cat": p.get("cat"), "tier": p.get("tier"),
            "evidence_class": {"sales": s_cls,
                               "str": "ESTIMATED", "mountain": "ESTIMATED",
                               "hazard": h_lab.split(" (")[0], "ungraded": "MEASURED"},
            "factors": {"sales": s, "str": t, "mountain": m, "hazard": h, "ungraded": u},
            "score": round(total, 2),
            "dominant": max((("sales", s), ("str", t), ("mountain", m), ("hazard", h)),
                            key=lambda x: x[1])[0],
            "hazard_factors": h_found,
        })

    rows.sort(key=lambda r: (-r["score"], r["name"] or ""))
    ranked = rows[:TOP_N]
    cutoff = ranked[-1]["score"] if ranked else 0.0
    score_by_name = {r["name"]: r["score"] for r in rows}

    # STEP 4 routing. Research items are matched on the note, not the score.
    research_hits = []
    for p in ungraded:
        nm = p.get("name") or ""
        for pre in RESEARCH_PREFIXES:
            if nm.startswith(pre):
                reason = (p.get("note") or p.get("disclosure_note") or "").strip()
                if not reason:
                    withheld = [str(i) for i in (p.get("ings") or [])
                                if re.search(r"proprietary|confidential", str(i), re.I)]
                    reason = ("no note held; the ingredient list itself carries a line entered only as "
                              + "; ".join(withheld)) if withheld else "ingredient list incomplete"
                research_hits.append({
                    "name": nm, "brand": p.get("brand"), "cat": p.get("cat"),
                    "reason": reason[:260],
                    "priority": "borderline" if pre in RESEARCH_BORDERLINE else "firm",
                    "score": score_by_name.get(nm),
                })
                break

    excluded_from_research = []
    for nm, why in EXCLUDED_FROM_RESEARCH.items():
        if any((p.get("name") or "") == nm for p in ungraded):
            excluded_from_research.append({"name": nm, "reason": why})
    for pre, why in EXCLUDED_PREFIXES.items():
        for p in ungraded:
            if (p.get("name") or "").startswith(pre):
                excluded_from_research.append({"name": p.get("name"), "reason": why})
                break

    ranked_names = {r["name"] for r in ranked}
    routing_split = {"enrichment": 0, "research": 0, "verification": 0}
    for r in ranked:
        if r["name"] in {h["name"] for h in research_hits}:
            r["route"] = "research"
            routing_split["research"] += 1
        else:
            r["route"] = "enrichment"
            routing_split["enrichment"] += 1

    # verification: a manufacturer claim-vs-toxicology tension is recorded but
    # not resolved. Separate lane, NOT part of the ranked partition, and an item
    # can legitimately sit in both (ungraded AND carrying an open conflict).
    def _txt(v, *keys):
        if not isinstance(v, dict):
            return str(v or "").strip()
        for k in keys:
            if v.get(k):
                return str(v[k]).strip()
        return ""

    verification = [{"name": p.get("name"), "cat": p.get("cat"),
                     "graded": bool(p.get("safe")),
                     "manufacturer_claim": _txt(p.get("claim_conflict"), "manufacturer_claim")[:300],
                     "conflict_note": _txt(p.get("claim_conflict"), "note")[:300],
                     "src": _txt(p.get("claim_conflict"), "src")}
                    for p in items if p.get("claim_conflict")]

    routing_exceptions = [h for h in research_hits if h["name"] not in ranked_names]
    # the research lane is carried separately because the weighted score cannot
    # surface it: hazard is MEASURED from the acts we hold, so an undisclosed
    # list scores LOW on hazard and never reaches the ranked set. Research
    # priority and score priority are orthogonal, not ranked together.
    research_lane = [{**h, "in_ranked": h["name"] in ranked_names,
                      "gap_to_cutoff": (round(cutoff - h["score"], 2)
                                        if h.get("score") is not None else None)}
                     for h in research_hits]

    coverage = {
        "products_total": len(items),
        "graded": len(graded),
        "ungraded": len(ungraded),
        "ungraded_with_ingredient_list": sum(1 for p in ungraded if p.get("ings")),
        "ungraded_exposure_basis": {},
        "ungraded_by_tier": {},
        "ungraded_by_cat": {},
        "graded_by_cat": {},
    }
    for p in ungraded:
        coverage["ungraded_exposure_basis"][p.get("exposure_ev") or "none"] = \
            coverage["ungraded_exposure_basis"].get(p.get("exposure_ev") or "none", 0) + 1
        coverage["ungraded_by_tier"][p.get("tier") or "untiered"] = \
            coverage["ungraded_by_tier"].get(p.get("tier") or "untiered", 0) + 1
        coverage["ungraded_by_cat"][p.get("cat") or "uncategorised"] = \
            coverage["ungraded_by_cat"].get(p.get("cat") or "uncategorised", 0) + 1
    for p in graded:
        coverage["graded_by_cat"][p.get("cat") or "uncategorised"] = \
            coverage["graded_by_cat"].get(p.get("cat") or "uncategorised", 0) + 1

    data_flags = []
    if bool_defects:
        data_flags.append({
            "flag": "safe holds a boolean False, not None",
            "products": bool_defects,
            "impact": "a third value in a two-value field; a `safe is None` selector drops these rows silently",
        })

    coverage["claim_conflicts_open"] = len(verification)
    coverage["claim_reviews_on_record"] = sum(1 for p in items if p.get("claim_review"))
    coverage["ranked_also_carrying_open_conflict"] = sum(
        1 for r in ranked if any(v["name"] == r["name"] for v in verification))
    coverage["ranked_by_cat"] = {}
    for r in ranked:
        coverage["ranked_by_cat"][r["cat"] or "uncategorised"] = \
            coverage["ranked_by_cat"].get(r["cat"] or "uncategorised", 0) + 1
    top_cat = max(coverage["ranked_by_cat"].items(), key=lambda kv: kv[1])
    coverage["ranked_top_cat"] = {"cat": top_cat[0], "count": top_cat[1],
                                 "share_of_ranked": round(top_cat[1] / len(ranked), 2)}

    # notes carry live counts and scores; compute them here so the prose can never
    # drift from the data it sits next to (a hardcoded figure in a generated file
    # is falsified by the next run and is the part a reader trusts).
    _top2 = sorted(coverage["ranked_by_cat"].items(), key=lambda kv: -kv[1])[:2]
    _top2_s = " + ".join(f"{c} {n}" for c, n in _top2)
    _top2_tot = sum(n for _, n in _top2)
    _best_res = max((h for h in research_lane if h.get("score") is not None),
                    key=lambda h: h["score"], default=None)

    queue = {
        "schema_version": 2,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scope": f"top {len(ranked)} of {len(ungraded)} ungraded products, plus research and verification lanes",
        "weights": WEIGHTS,
        "ranked": ranked,
        "routing_split": routing_split,
        "lane_totals": {"ranked": len(ranked), "research_lane": len(research_lane),
                        "verification_lane": len(verification),
                        "ungraded_population": len(ungraded), "products_total": len(items)},
        "research_lane": research_lane,
        "excluded_from_research": excluded_from_research,
        "routing_exceptions": routing_exceptions,
        "verification_lane": verification,
        "coverage": coverage,
        "data_flags": data_flags,
        "notes": [
            "research = ingredient list deliberately incomplete, not 'unranked'. Matched on the note, not the score.",
            "enrichment = list present, grade absent. Every ungraded product qualifies, so enrichment alone is not a priority signal.",
            "verification = a manufacturer claim-vs-toxicology tension recorded but not resolved. verification_lane is a SEPARATE list, not part of routing_split: an item can be ungraded and carry an open conflict at once.",
            "routing_split partitions the ranked set only and sums to lane_totals.ranked.",
            "the research lane is carried separately because the weighted score usually cannot surface it: hazard is MEASURED from the ingredient acts we hold, so a product with an undisclosed list scores LOW on hazard. On the run that wrote this file, "
            + f"{sum(1 for h in research_lane if h['in_ranked'])} of {len(research_lane)} research items reached the ranked set"
            + (f"; the highest-scoring research item is {_best_res['score']:.2f} ({_best_res['name']}), "
               + (f"{abs(_best_res['gap_to_cutoff']):.2f} above" if _best_res['gap_to_cutoff'] < 0
                  else f"{_best_res['gap_to_cutoff']:.2f} below")
               + f" the rank-30 cutoff of {cutoff:.2f}."
               if _best_res else "; no research item was scored this run."),
            f"ranked concentration on the run that wrote this file: {_top2_s} = {_top2_tot} of {len(ranked)}, the bleach/bathroom cluster fed by the Sep 28-Oct 1 value-shelf harvest.",
            "sales is anchored on the exposure field where held; products with no exposure fall back to a brand anchor and are marked UNSOURCED or ESTIMATED.",
        ],
    }
    json.dump(queue, open(args.out, "w"), indent=1)

    print(f"products={len(items)} graded={len(graded)} ungraded={len(ungraded)} bool_defects={len(bool_defects)}")
    print(f"routing_split={routing_split}  research_matched={len(research_hits)} exceptions={len(routing_exceptions)}")
    print(f"wrote {args.out}")
    for i, r in enumerate(ranked[:TOP_N], 1):
        print(f"  {i:2d}. {r['score']:5.2f} {str(r['name'])[:44]:44s} "
              f"[{r['factors']['sales']:.1f}/{r['factors']['str']:.1f}/{r['factors']['mountain']:.1f}/{r['factors']['hazard']:.1f}] "
              f"{r['route']:<11s} {r['cat']}")


if __name__ == "__main__":
    main()
