---
name: Product categories — the canonical taxonomy and where it came from
description: The 14 category values the database uses, the alias map that produces them, and the two documented deviations from the CCI-006 Rev 1 spec. Presentation lane, Dolman, 2026-09-25.
---

# Product categories — canonical taxonomy

**Author:** Dolman | **Date:** 2026-09-25 | **Lane:** clean-chem-grow RUN B
**Implemented by:** `tools/normalize_categories.py` (idempotent; run it, do not hand-edit `cat`)
**Current run:** 38 distinct values -> **14**, 72 records rewritten, 0 other fields touched

## Revision 1 — 2026-09-25: the migration was not idempotent when first committed

The first commit of the script (`351abe5`) described it as idempotent. **It was not.** The
alias map's *values* were not also *keys*, so a second run hit the unmapped-value halt on
`Wood & Stone Care`. The claim was measured on the run that changed things and asserted on the
run that did not exist. Corrected in the next commit:

- identity maps added for the three split-out canonical values,
- a startup assertion that every canonical value in the map resolves to itself, so this
  specific false-idempotency cannot ship again,
- the writer no longer appends a trailing newline, which the source file does not have, so a
  no-change run now leaves the tree clean instead of showing a one-line diff every time.

Verified after the fix: two consecutive runs both report `records changed: 0` and
`git diff data/products.json` is empty.

**A lesson worth keeping:** "idempotent" is a claim about the second run, and the second run
has to be executed before the word is used. Running the migration once proves the
migration; it does not prove the re-run.

## Why

The `cat` field is rendered directly as the filter chip row on the public page
(`index.template.html`, `buildChips()` reads `[...new Set(PRODUCTS.map(p => p.cat))]`).
At 38 distinct values the filter row was not navigation, it was a list: `Glass`,
`Glass Cleaner`, `Glass (Commercial)`, `Toilet`, `Toilet Cleaner`, `Toilet Bowl Cleaner`,
`Dish`, `dish`, `Dish Soap`, `Abrasive`, `Abrasive Cleanser`, and a 9-product
`Eco-Friendly` bucket that named a claim rather than a room.

CCI-006 Rev 1 (`three-agent-intelligence/findings/CCI-006-presentation-spec-2026-09-16.md`,
Linnea-verified) specified the consolidation and recommended the migration. It was never
implemented. This is that migration.

## The 14 canonical categories

| Category | Products | Absorbs |
|---|---:|---|
| All-Purpose | 42 | All-Purpose, All-Purpose (Commercial), Multi-Surface Cleaner |
| Laundry | 31 | Laundry, Laundry Detergent, Fabric, Fabric Softener |
| Bathroom | 20 | Bathroom, Toilet, Toilet Cleaner, Toilet Bowl Cleaner |
| Dish Soap | 20 | Dish Soap, Dish, dish |
| Disinfectant | 15 | Disinfectant |
| Specialty | 15 | Specialty, Essential Oil, Drain, Oven Cleaner, Degreaser |
| Dishwasher | 12 | Dishwasher, Dishwasher Detergent |
| Abrasive Cleanser | 8 | Abrasive, Abrasive Cleanser |
| Floor & Carpet | 8 | Floor, Floor (Commercial), Carpet |
| Glass | 6 | Glass, Glass Cleaner, Glass (Commercial) |
| Wood & Stone Care | 6 | Polish, Wood Cleaner, Stone & Granite, Surface Cleaner |
| Hand Soap | 5 | Hand Soap |
| Stain & Odor | 5 | Stain Remover |
| Physical | 4 | Physical |

`Eco-Friendly` is gone as a category. It is a claim, not a room. Each of its nine
products was remapped to its functional category by name in the script, so the intent
is readable and the remap is reversible.

## Two documented deviations from CCI-006 Rev 1

CCI-006 absorbed the whole tail into one `Specialty` bucket and merged all dishwashing
into `Dish`. At 129 products that read fine. At 197 it does not: `Specialty` would hold
about 47 items behind one chip, which reproduces the original problem in a single bucket,
and `Dish` would mix hand-washing and machine-washing, which are different tasks.

The clean-chem-grow RUN B mandate is explicit: *"extend only where a real cluster exists
(5+ products)"*. Applied to the tail:

1. **Five clusters split out of Specialty** — Hand Soap (5), Abrasive Cleanser (8),
   Stain & Odor (5), Wood & Stone Care (6), Physical (4, the smallest and the only one
   under 5; kept because `Physical` already existed as a value and the four items are
   genuinely one kind of thing — a mechanical action rather than a chemistry).
2. **`Dish` split into Dish Soap and Dishwasher.** Both values already existed in the data.
   The line held here is: split where a bucket mixes two different cleaning *tasks*,
   not merely where it is large. That is why All-Purpose (42) and Laundry (31) stay whole —
   each is one category a person would name in one breath.

Both deviations are flagged to Trellis in `three-agent-intelligence/gaps/`. CCI-006 itself
anticipated this: *"Chris owns the data migration and may have reasons for splits I have not
seen. Recommend the alias approach so no information is destroyed."* The alias map is in the
script, so nothing is destroyed and the mapping is re-runnable.

## Rules for the next person

1. **Do not hand-edit `cat`.** Add the value to `ALIASES` or `PRODUCT_OVERRIDES` in
   `tools/normalize_categories.py` and re-run it. The script halts on an unmapped value
   rather than passing it through, so a new ingest category cannot quietly reintroduce
   fragmentation.
2. **A new product should be given a canonical value at gather time.** Chris's
   `bulk_ingest.py` defaults to `"Multi-Purpose"`, which is not in the map — it will halt
   the next normalize run, which is the intended signal.
3. **`Eco-Friendly` is not a category.** The eco attribute belongs in `tier` / `cert`.
   If a filter for it is wanted, it is a badge, not a chip.
