---
name: safe-set audit
description: QC finding — the "Certified safe" set on the live site includes 11 Sifter-graded products, 7 of them explicit grade F. Root cause is a schema conflation in the `safe` field. Evidence, impact, and three fix options with a recommendation.
author_agent_id: agent-2a6f39b6-8992-4026-8214-3f489dcc9f61
author_agent_name: Letinia
author_job: live-site QC sweep (commissioned by Sandra 2026-09-24)
authored_at: 2026-09-24
---

# Safe-Set Audit — "Certified safe" includes grade-F products

**Consumer:** Dolman (data lane owner), Linnea (verification lane), The Watchtower (blind-spot lane), Chris (sign-off)
**Trigger:** before the next `build.py` rebuild or any curated add that sets `safe`; before citing the "75 certified safe" figure anywhere (marketing, client kits)
**Effect:** the hero stat and the "✓ Certified safe only" filter currently misrepresent bleach- and quat-based products as certified safe to live-site users; the fix chosen here changes both

## The finding

`counts.md` and the live site's hero stat publish **75 "Certified safe"** products
(`build.py` line 105: `n_safe = sum(1 for p in products if p.get("safe"))`).
But the `safe` field is being used as a *general grade-annotation slot*, not a
safety certification. Of the 75 truthy values in `data/products.json` (182
products, read 2026-09-24):

| Kind of value | Count | Examples |
|---|---:|---|
| Real certifications (EWG Verified / EPA Safer Choice / MADE SAFE / Green Seal / USDA) | 64 | Method, Seventh Gen, Mrs. Meyer's |
| **Sifter grade D annotations** | 4 | Bar Keepers Friend (organ D: silica H373, oxalic acid) |
| **Sifter grade F annotations** | 7 | see below |
| `safe: false` (bool, correctly excluded) | 1 | Dawn Ultra |

The seven grade-F products currently inside the "Certified safe" set:

1. WinCo Foods All Purpose Cleaner with Bleach — derm F / env F (sodium hypochlorite H314/H400)
2. PowerHouse All Purpose Cleaner with Bleach — derm F / env F (sodium hypochlorite)
3. Great Value Lemon Scent All Purpose Cleaner — derm F / env F (quaternary ammonium actives)
4. up&up Lemon All-Purpose Disinfecting Cleaner — derm F / env F (quat actives H302/H314/H400)
5. Kirkland Signature Ultra Shine Plant-Based Dish Soap — env F (limonene H400)
6. 20 Mule Team Borax (BMVC) — repro F (sodium tetraborate H360FD, EU CLP Repr. 1B)
7. Organic Essential Oils Kit (BMVC) — env F (lemon oil H400)

## User-facing impact (verified on the live site, 2026-09-24)

- Hero stat: **"75 Certified safe"** (template line 399 renders `META.safe`).
- The **"✓ Certified safe only"** filter (template line 469: `list.filter(p=>p.safe)`)
  returns these 7 grade-F products. A user filtering for certified-safe products
  is shown bleach and quat disinfectants.
- Each carries a "✓" badge (line 508: `p.safe` → `<span class="bdg safe">✓ …`)
  — a green checkmark on "Sifter grade F — sodium hypochlorite H314 severe
  skin burns" is the single most misleading element on the site.

## Root cause

Schema conflation, not a data error in any one lane: The Sifter's grading lane
writes *grade annotations* into `safe` (they are honest, sourced, and
well-evidenced — the strings themselves are good work), while `build.py`,
`update_counts.py` (line 30), and the template all treat **any truthy `safe`
value** as a certification. Same class as the fleet's "measuring a narrower
object than you claim" lesson: the number is fine; the noun is wrong.

## Fix options

1. **Split the field (recommended):** move Sifter grade annotations to a new
   field (e.g. `grade_note`), keep `safe` for certifications only. Hero/filter
   become true (64 certified). Grade badges still render — off a new
   `p.grade_note` branch. Cost: one migration over 11 records + template edit.
2. **Smarten the predicate:** keep one field, but `build.py`/template count and
   filter only values matching a certification allowlist (EWG/EPA/MADE
   SAFE/Green Seal/USDA/Sifter grade A-B). Cheaper, but the conflation stays
   for the next lane that writes to `safe`.
3. **Prefix convention:** treat any value starting "Sifter grade D/F" as
   not-safe. Fragile — string-matching semantics is how FLAG-001's silent no-op
   happened.

Per the review gate this is consequential structural work on a live client
surface: **Dolman + Linnea review, Chris signs off.** I have not touched the
data or the code.

## Verification steps (reproducible)

```
python3 - <<'PY'
import json
p = json.load(open('data/products.json'))
truthy = [x for x in p if x.get('safe')]
sifter  = [x for x in truthy if isinstance(x['safe'], str) and 'Sifter grade' in x['safe']]
f = [x for x in sifter if 'grade F' in x['safe']]
print(len(truthy), len(sifter), len(f))  # -> 75 11 7
PY
```
Live site checked 2026-09-24 ~18:25Z: hero shows the safe count; filter returns
the 7 above; grade-F badge renders with a ✓.

## Adjacent observations (same sweep, minor)

- `counts.md` "Graded (safe set) 75 / Ungraded 107" inherits the same noun
  problem — "ungraded" includes products that ARE graded (by Sifter) but not
  certified.
- One product (`Dawn Ultra`) holds `safe: false` as a bool while all others are
  strings or null — a third type in one field. Harmless today (falsy), but it
  will bite a future `isinstance(str)` check.
- The Watchtower's 2026-09-22 log calls clean-chem "healthy" — it verified
  counts vs data (correct) but not set membership. Not a criticism of that
  lane; it's the gap between count-QC and content-QC, which is exactly what
  this audit covers.

*Authored by an AI agent. agent_id is the identity; the display name is for humans only.*
