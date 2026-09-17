#!/usr/bin/env python3
"""Pull GHS classification from PubChem PUG view (approved source, docs/source-policy.md).
Usage: python3 tools/ghs_lookup.py "Name 1" "Name 2" ...
Prints JSON: {name: {cid, title, signal, pictograms, h_statements}}
"""
import json, sys, time, urllib.parse, urllib.request

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "clean-chem-intel/1.0 (BMVC)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def walk(sections):
    for s in sections:
        yield s
        yield from walk(s.get("Section", []))

def parse_ghs(cid, title):
    d = fetch(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON?heading=Safety+and+Hazards")
    for sec in walk(d["Record"]["Section"]):
        if sec.get("TOCHeading") != "GHS Classification":
            continue
        rec = {"cid": cid, "title": d["Record"].get("RecordTitle", title), "signal": None, "pictograms": [], "h_statements": []}
        for info in sec.get("Information", []):
            name = info.get("Name", "")
            vals = info.get("Value", {}).get("StringWithMarkup", [])
            for v in vals:
                txt = (v.get("String") or "").strip()
                marks = [m.get("Extra") for m in v.get("Markup", []) if m.get("Extra")]
                if name == "Signal" and txt:
                    rec["signal"] = txt
                elif name == "Pictogram(s)":
                    rec["pictograms"] += [m for m in marks if m]
                elif name == "GHS Hazard Statements" and txt:
                    rec["h_statements"].append(txt.split("[")[0].strip())
        return rec
    return {"cid": cid, "title": title, "signal": None, "pictograms": [], "h_statements": [], "note": "no GHS section"}

def main():
    out = {}
    for name in sys.argv[1:]:
        q = urllib.parse.quote(name)
        try:
            cids = fetch(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{q}/cids/JSON")
            cid = cids["IdentifierList"]["CID"][0]
            out[name] = parse_ghs(cid, name)
        except Exception as e:
            out[name] = {"error": str(e)[:120]}
        time.sleep(0.35)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
