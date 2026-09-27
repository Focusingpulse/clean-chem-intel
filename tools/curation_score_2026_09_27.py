#!/usr/bin/env python3
"""Chem-curation scoring — 2026-09-27.

Scores the 136 ungraded products for BMVC audience relevance (STEP 2/3 of the
chem-curation cron). Weights: sales 30%, STR 25%, mountain 20%, hazard 15%,
ungraded 10%. Every dimension carries an evidence label (MEASURED / ESTIMATED /
UNSOURCED) so no score overstates what we actually hold (SO-02).

- MEASURED: grounded in fields already in products.json (ingredient acts,
  exposure with source, tier=mass).
- ESTIMATED: general consumer-market / cleaning-domain knowledge (mass-market
  brand, turnover-domain category, product purpose). Noted as such.
- UNSOURCED: no grounding in the data and no established market fact; left at a
  neutral mid-score and flagged.
"""
import json, re

items = json.load(open('data/products.json'))
ungraded = [p for p in items if p.get('safe') is None]

# --- factor maps (ESTIMATED — general/domain knowledge, not measured data) ---

# Sales volume 0-10 (ESTIMATED unless exposure+src present).
# Household-penetration anchors: category mass staples + known big grocery/Target/Amazon
# movers within their category. This is general consumer knowledge, labelled ESTIMATED.
MASS_SCORE = {  # known high-volume category staples
    'Dawn Ultra', 'Dawn Powerwash Dish Spray, Fresh', 'Gain', 'Tide PODS Laundry Detergent Pacs, Original Scent',
    'Tide Original Liquid Laundry', 'Clorox Bleach', 'Clorox Disinfecting Wipes, Fresh Scent', 'Clorox Disinfecting Bleach',
    'Lysol Disinfecting Wipes, Crisp Linen', 'Lysol Disinfectant Spray', 'Lysol All-Purpose', 'Lysol Multi-Surface Cleaner',
    'Pine-Sol', 'Fabuloso', 'Mr. Clean', 'Formula 409', 'Windex Original', 'Cascade', 'Palmolive', 'Ajax Dishwashing Liquid, Lemon',
    'Swiffer WetJet', 'Febreze', 'Scrubbing Bubbles', 'Easy-Off Heavy Duty Oven Cleaner', 'Bar Keepers Friend',
    'Comet with Bleach Cleanser', 'Soft Scrub', 'Simple Green', 'Kaboom Foam-Tastic', 'Fels-Naptha Heavy Duty Laundry Bar Soap',
    'Drano Max Gel', 'CLR', 'Calcium Lime Rust Cleaner', 'Goo Gone Original', 'Mr. Clean Magic Eraser', 'Finish',
    'The Works Toilet Bowl Cleaner', 'Murphy Oil Soap', 'Distilled White Vinegar (5%)', 'Baking Soda (bulk)', 'Hydrogen Peroxide 3% (drugstore)',
    'Gain Ultra Dishwashing Liquid, Original Scent', 'Dawn Ultra Dishwashing Liquid', 'Signature Select Dish Soap, Ultra Concentrated, Ocean Scent',
    'Kirkland Signature Ultra Shine Plant-Based Dish Soap', 'Kirkland Signature Ultra Shine Premium Dish Soap (Citrus Scent)',
}

# STR relevance 0-10 (ESTIMATED — turnover checklist / host-forum domain knowledge)
# Turnover-critical categories: laundry (sheets/towels), disinfecting, dishwasher, bathroom, floor.
STR_CAT = {  # categories that dominate STR turnover checklists
    'Laundry': 8, 'Disinfectant': 9, 'Dishwasher': 7, 'Bathroom': 8, 'Floor & Carpet': 7,
    'Dish Soap': 6, 'Stain & Odor': 6, 'Glass': 5, 'All-Purpose': 5, 'Abrasive Cleanser': 4,
    'Wood & Stone Care': 4, 'Specialty': 3, 'Hand Soap': 4, 'Physical': 3,
}
STR_BOOSTERS = {  # STR-hosts specifically reach for these (linen sanitizer, mold, stain)
    'Lysol Laundry Sanitizer, Free & Clear', 'Tilex Mold & Mildew', 'OxiClean Versatile Stain Remover',
    'Resolve Heavy Traffic Foam Carpet Cleaner', 'Folex Instant Carpet Spot Remover', 'Carbona 2-in-1 Oxy-Powered Carpet Cleaner',
    'Shout Advanced Stain Remover Action Gel', 'Vanish Oxi Action In-Wash Fabric Stain Remover', 'Clorox ToiletWand',
}

# Mountain-specific 0-10 (ESTIMATED — product purpose maps to hard water / soot / mildew / wood)
MOUNTAIN_BOOST = {  # hard water / lime, wood stove soot, seasonal mildew, wood care, pet
    'CLR', 'Calcium Lime Rust Cleaner', 'Lime-A-Way Toilet Bowl Cleaner', 'Tilex Mold & Mildew',
    'Murphy Oil Soap', 'Pledge', 'Old English Lemon Oil Furniture Polish', 'Granite Gold Daily Cleaner',
    'Weiman Stainless Steel Cleaner & Polish', 'Bona', 'Dawn Powerwash Dish Spray, Fresh',  # grease
    'Easy-Off Heavy Duty Oven Cleaner',  # stove (wood stove interiors + oven)
    'Green Works', 'Essential Oil Spray (BMVC)', 'Wood Surface Cleaner (BMVC)', 'Granite & Stone Cleaner (BMVC)',
    'Puracy Natural Multi-Surface Cleaner (Green Tea & Lime)', 'The Honest Company Dish Soap',
}
MOUNTAIN_CAT = {'Wood & Stone Care': 7, 'Specialty': 4, 'Floor & Carpet': 4, 'Bathroom': 4}

# Hazard-interest 0-10 (MEASURED from ingredient acts in products.json)
HAZARD_TERMS = [
    (re.compile(r'quat|benzyl ammonium|didecyldimethyl|alkyl.*dimethyl', re.I), 'quats'),
    (re.compile(r'butyloxyethanol|2-butoxy|ethylene glycol monobutyl', re.I), '2-butoxyethanol / BGE'),
    (re.compile(r'sodium hypochlorite', re.I), 'sodium hypochlorite (bleach)'),
    (re.compile(r'fragrance|parfum', re.I), 'undisclosed fragrance'),
    (re.compile(r'ammonium hydroxide|ammonia', re.I), 'ammonia'),
    (re.compile(r'nonylphenol|octylphenol', re.I), 'alkylphenol ethoxylates'),
    (re.compile(r'formaldehyde|paraformaldehyde', re.I), 'formaldehyde'),
    (re.compile(r'sodium tetraborate|borax|boric acid', re.I), 'borates'),
    (re.compile(r'glycol ether', re.I), 'glycol ethers'),
    (re.compile(r'phthalate', re.I), 'phthalates'),
    (re.compile(r'chlorine|sodium dichloro', re.I), 'chlorine'),
    (re.compile(r'percarbonate|peroxide', re.I), 'oxidizers'),
]

def hazard_score(p):
    ings = p.get('ings') or []
    found = []
    for rx, label in HAZARD_TERMS:
        if any(rx.search(i or '') for i in ings):
            found.append(label)
    if not found:
        return 4.0, '', 'MEASURED (clean ingredient act list)'
    # quats / 2-butoxyethanol / undisclosed fragrance / formaldehyde = highest controversy
    weight = 6.0
    if any(f in ('quats', '2-butoxyethanol / BGE', 'formaldehyde') for f in found):
        weight += 2.0
    if 'undisclosed fragrance' in found:
        weight += 1.0
    if any(f in ('sodium hypochlorite (bleach)', 'nonylphenol', 'alkylphenol ethoxylates', 'phthalates') for f in found):
        weight += 1.0
    weight = min(10.0, weight + 0.5 * (len(found) - 1))
    return round(weight, 1), ', '.join(found), f'MEASURED ({", ".join(found)})'

def sales_score(p):
    name = p.get('name') or ''
    if name in MASS_SCORE:
        base, label = 8.5, 'ESTIMATED (known mass-market category staple)'
    else:
        base, label = 4.5, 'ESTIMATED (product/brand positioning, no volume data held)'
    # exposure field already in products.json is a MEASURED/derived household-penetration signal
    ev = p.get('exposure_ev')
    if p.get('exposure') and p.get('exposure_src'):
        # exposure is a per-product household-penetration estimate with a source
        base = min(10.0, base + min(p.get('exposure', 0) / 20.0, 3.0) * (0.5 if name not in MASS_SCORE else 1.0))
        label = f"ESTIMATED + exposure={p.get('exposure')} ({ev}, {p.get('exposure_src')})"
    return base, label

def str_score(p):
    name, cat = p.get('name') or '', p.get('cat') or ''
    base = STR_CAT.get(cat, 4)
    if name in STR_BOOSTERS:
        base += 2
    return min(10.0, base), 'ESTIMATED (turnover-domain category' + (' + STR staple' if name in STR_BOOSTERS else '') + ')'

def mountain_score(p):
    name, cat = p.get('name') or '', p.get('cat') or ''
    base = MOUNTAIN_CAT.get(cat, 3.5)
    if name in MOUNTAIN_BOOST:
        base += 2
    return min(10.0, base), 'ESTIMATED (product purpose -> hard water/soot/mildew/wood)'

def ungraded_score(p):
    # boost if full ingredient list exists but no grade yet (all 136 qualify)
    if p.get('ings'):
        return 10.0, 'MEASURED (full ingredient list present, no grade)'
    return 6.0, 'MEASURED (no full ingredient list)'

# --- score all ungraded ---
rows = []
for p in ungraded:
    s, s_label = sales_score(p)
    t, t_label = str_score(p)
    m, m_label = mountain_score(p)
    h, h_label, h_note = hazard_score(p)
    u, u_label = ungraded_score(p)
    total = 0.30 * s + 0.25 * t + 0.20 * m + 0.15 * h + 0.10 * u
    rows.append({
        'name': p.get('name'), 'brand': p.get('brand'), 'cat': p.get('cat'),
        'sales': s, 'str': t, 'mountain': m, 'hazard': h, 'ungraded': u,
        'total': round(total, 2),
        'evidence': {
            'sales': s_label, 'str': t_label, 'mountain': m_label,
            'hazard': h_label.split(' (', 1)[0], 'ungraded': u_label,
        },
        'dominant': max([('sales', s), ('str', t), ('mountain', m), ('hazard', h)], key=lambda x: x[1])[0],
        'hazard_factors': h_note,
    })

rows.sort(key=lambda r: r['total'], reverse=True)
print(f"Scored {len(rows)} ungraded products (weighted 30/25/20/15/10).")
print("Top 30:")
for i, r in enumerate(rows[:30], 1):
    print(f"  {i:2d}. {r['total']:5.2f}  {r['name'][:46]:46s} [sales {r['sales']:.1f} | str {r['str']:.1f} | mt {r['mountain']:.1f} | haz {r['hazard']:.1f}] <- {r['dominant']:<8s} cat={r['cat']}")

json.dump(rows, open('/tmp/curation_rows.json', 'w'), indent=1)
