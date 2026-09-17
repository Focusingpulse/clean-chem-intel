#!/usr/bin/env python3
"""Grade ungraded ingredients from PubChem GHS data, batch 1 (CCI-004).
Reads ghs JSON on stdin (from tools/ghs_lookup.py), applies a conservative H-code -> grade mapping,
and prints proposed ingredient record updates as JSON. Human/Dolman review before applying.
"""
import json, sys

# Conservative H-code -> record mapping. Ties go to the worst credible hazard.
# 'g' = headline GHS H-code (worst), 's' = short hazard summary, 'gr' = dimension grades,
# 'impacts' = impact tags, 'sens' = sensitive occupant flag.
def hmap(codes):
    derm = "A"; resp = "A"; organ = "A"; env = "A"; wsens = False
    headline = None; summary = None
    for c in sorted(codes, key=lambda x: -x[0]):
        code = f"H{c[0]}"
        pct = c[1]
        if code in ("H314", "H318") and pct >= 40:
            derm = "F" if code == "H314" else max(derm, "D", key=lambda g: g)  # corrosive
        ...

def grade(codes):
    """codes: list of (hcode_int, pct). Returns record dict or None if too sparse."""
    strong = [(h, p) for h, p in codes if p >= 40]
    weak = [(h, p) for h, p in codes if p < 40]
    def worst(grades):
        order = ["A", "B", "C", "D", "F"]
        return max(grades, key=order.index)

    derm, resp, organ, env, wsafe = "A", "A", "A", "A", "B"
    sens = False
    impacts = set()
    for h, p in codes:
        code = f"H{h}"
        if code in ("H314",):
            if p >= 40: derm = worst([derm, "F"])
            elif p >= 10: derm = worst([derm, "D"])
        elif code in ("H318",):
            if p >= 40: derm = worst([derm, "D"])
            elif p >= 10: derm = worst([derm, "C"])
        elif code == "H317":
            if p >= 40: derm = worst([derm, "D"]); sens = True; impacts.add("allerg")
            else: derm = worst([derm, "C"]) if derm == "A" else derm
        elif code in ("H315",):
            if p >= 40: derm = worst([derm, "C"])
        elif code == "H335":
            if p >= 20: resp = worst([resp, "C"])
        elif code == "H334":
            resp = worst([resp, "D"]); sens = True; impacts.add("allerg")
        elif code == "H330":
            resp = worst([resp, "F"]); sens = True
        elif code == "H331" or code == "H332":
            resp = worst([resp, "D" if code == "H331" and p >= 40 else "C"])
        elif code in ("H372",):
            if p >= 40: organ = worst([organ, "D"])
        elif code in ("H373", "H371"):
            if p >= 40: organ = worst([organ, "C"])
        elif code == "H370":
            if p >= 40: organ = worst([organ, "D"])
        elif code in ("H400",):
            if p >= 40: env = worst([env, "F"])
        elif code in ("H410", "H411"):
            if p >= 40: env = worst([env, "D"])
        elif code == "H412":
            if p >= 40: env = worst([env, "C"])
    return derm, resp, organ, env, sens, impacts

def strong_codes(codes):
    """H-codes meeting >=40% notifier consensus, excluding physical-only (H2xx) for headline selection... kept for gr dims."""
    return [(h, p) for h, p in codes if p >= 40]

def main():
    data = json.load(sys.stdin)
    out = {}
    for name, rec in data.items():
        if "error" in rec or not rec.get("h_statements"):
            continue
        # parse "H314 (81%): ..." or "H314: ..."
        codes = []
        for line in rec["h_statements"]:
            line = line.strip()
            if not line.startswith("H"): continue
            h = line[1:4]
            if not h[:3].isdigit(): continue
            pct = 100
            if "(" in line.split(":")[0]:
                try: pct = float(line.split("(")[1].split("%")[0].replace(">", "").strip())
                except Exception: pct = 100
            codes.append((int(h), pct))
        if not codes:
            out[name] = {
                "g": "Not Classified",
                "s": "No GHS hazard criteria met (majority not-classified per ECHA C&L via PubChem)",
                "ev": "Medium",
                "gr": {},
                "impacts": [],
                "sens": False,
                "note": f"Graded from PubChem GHS classifications (CID {rec['cid']}) — no H-codes at >=40% consensus; treated as minimal hazard with Medium confidence.",
            }
            continue
        derm, resp, organ, env, sens, impacts = grade(codes)
        if not strong_codes(codes):
            out[name] = {
                "g": "Not Classified",
                "s": "No GHS hazard criteria met (majority not-classified per ECHA C&L via PubChem)",
                "ev": "Medium",
                "gr": {},
                "impacts": [],
                "sens": False,
                "note": f"Graded from PubChem GHS classifications (CID {rec['cid']}) — no H-codes at >=40% consensus; treated as minimal hazard with Medium confidence.",
            }
            continue
        worst_code = max(codes, key=lambda c: (c[1] >= 40, c[0] * -1))
        out[name] = {
            "g": ",".join(f"H{c[0]}" for c in sorted(strong_codes(codes), key=lambda c: -c[0])),
            "s": next((l.split(":", 1)[1].strip() for l in rec["h_statements"]
                        if l.startswith(f"H{worst_code[0]}:")), "GHS hazard"),
            "ev": "High" if worst_code[1] >= 90 else "Medium",
            "gr": {d: v for d, v in (("derm", derm), ("resp", resp), ("organ", organ), ("env", env)) if v != "A"},
            "impacts": sorted(impacts),
            "sens": sens,
            "note": f"Graded from PubChem GHS classifications (CID {rec['cid']}).",
        }
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
