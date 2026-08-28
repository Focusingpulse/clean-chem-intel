#!/usr/bin/env python3
"""One-time extractor: pull PRODUCTS + INGS out of the current index.html
into structured JSON so the site can become data-driven (build.py merges
data + template -> index.html). Safe, mechanical, no judgments."""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent
INDEX = REPO / "index.html"
DATA = REPO / "data"
DATA.mkdir(exist_ok=True)

html = INDEX.read_text(encoding="utf-8")

# ---- PRODUCTS ----
m = re.search(r"const PRODUCTS = \[(.*?)\n\];", html, re.S)
assert m, "PRODUCTS array not found"
arr = m.group(1)
products = []
for line in arr.splitlines():
    line = line.strip()
    if not line.startswith("{"):
        continue  # skip comment lines
    name = re.search(r'name:"([^"]*)"', line)
    brand = re.search(r'brand:"([^"]*)"', line)
    cat = re.search(r'cat:"([^"]*)"', line)
    safe = re.search(r'safe:"([^"]*)"', line)
    ings_m = re.search(r'ings:\[(.*?)\]', line)
    ings = []
    if ings_m:
        ings = re.findall(r'"([^"]*)"', ings_m.group(1))
    products.append({
        "name": name.group(1) if name else "?",
        "brand": brand.group(1) if brand else "",
        "cat": cat.group(1) if cat else "Other",
        "safe": safe.group(1) if safe else None,
        "ings": ings,
    })

print(f"extracted {len(products)} products")

# Recover the 'safe' flag which may be on the preceding line in some entries
# (some safe products had safe: on the same line; fine). Also handle multi-line.

# ---- INGS ----
m2 = re.search(r"const INGS = \{(.*?)\n\};", html, re.S)
assert m2, "INGS dict not found"
body = m2.group(1)
ings = {}
# entries: "Name":{g:"...",s:"...",ev:"...",gr:{derm:"B",...}},
for em in re.finditer(r'"([^"]+)":\{g:"?([^",}]*)"?,s:"((?:[^"\\]|\\.)*)",ev:"([^"]*)",?(gr:\{(?:[^}]*)\})?\}', body):
    name, g, s, ev, gr_raw = em.groups()
    gr = {}
    if gr_raw:
        for dim, val in re.findall(r'([a-z]+):"([A-F])"', gr_raw):
            gr[dim] = val
    ings[name] = {"g": g or None, "s": s, "ev": ev, "gr": gr}

print(f"extracted {len(ings)} ingredients")

# Handle the few entries with no ev/gr (simplified lines like "Water":{g:null,s:"...",ev:"High"} )
for em in re.finditer(r'"([^"]+)":\{g:(null|"[^"]*"),s:"((?:[^"\\]|\\.)*)",ev:"([^"]*)"(?:,(gr:\{[^}]*\}))?\}', body):
    name, g, s, ev, gr_raw = em.groups()
    if name in ings:
        continue
    gr = {}
    if gr_raw:
        for dim, val in re.findall(r'([a-z]+):"([A-F])"', gr_raw):
            gr[dim] = val
    ings[name] = {"g": None if g == "null" else g.strip('"'), "s": s, "ev": ev, "gr": gr}

print(f"total ingredients: {len(ings)}")

(DATA / "products.json").write_text(json.dumps(products, indent=1), encoding="utf-8")
(DATA / "ingredients.json").write_text(json.dumps(ings, indent=1), encoding="utf-8")
print("wrote data/products.json + data/ingredients.json")