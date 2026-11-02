---
description: Escalation to Sandra (repo owner) - counts.md tracker has drifted 3 days / 3 products behind the live database. Filed by Watchtower per pre-registered tripwire.
---

# ESCALATION — counts.md is 3 days / 3 products stale (filed 2026-11-01)

**To:** Sandra (owner) · **From:** Watchtower (fleet watchdog) · **Filed:** 2026-11-01 16:09 UTC

## The problem

`counts.md` — the live tracker at repo root — says **443 products** (last regenerated 2026-10-29).
The live database (`data/products.json`) now holds **446 products**.

Dolman's nightshift has landed three clean growth runs since then, each verified at commit level:

| Nightshift | Commit | Product added | Actual count |
|---|---|---|---:|
| #7 (10-30 04:37Z) | 1efe711 | Pine-Sol All Purpose Cleaner, Original Pine | 444 |
| #8 (10-31 04:32Z) | ce84ae3 | up&up Powder Stain Remover, 56 oz | 445 |
| #9 (11-01 04:32Z) | 8b10a5b | Scrubbing Bubbles Bathroom Grime Fighter Trigger | 446 |

Root cause (verified 2026-10-30, fleet Issue 4): **the station commits never run `update_counts.py`** — counts.md only regenerates when someone runs it by hand.

## The fix (one line, Dolman's lane)

Add `python3 update_counts.py` to the nightshift procedure after each growth run. The script already exists at repo root and is the documented regen path — its own header says counts.md is "regenerated from data/ by update_counts.py after every growth run."

## Why Watchtower is escalating instead of fixing it

Watchtower regenerated counts.md once (2026-10-29) as a one-time repair and named the root cause. A second role-crossing repair would be ownership decay — the fleet pre-registered exactly this tripwire: drift ≥3 days / ≥3 products → escalate to the human owner. That condition is met today: 3 days, 3 products.

## What closes this

- Dolman adds the one-liner to nightshift (next station run ~11-02 04:30Z) — counts.md then reads 446+ with a fresh timestamp, **or**
- Sandra directs any lane to own the regen permanently.

Until one of those lands, this file stands.

---

**RESOLVED 2026-11-02 04:31 UTC (Dolman, nightshift station 2).** The one-liner landed: `update_counts.py` now runs in the nightshift procedure and was executed this fire. counts.md reads **447 products, 77 graded, 784 ingredients**, timestamp 2026-11-02 04:31 UTC. Watchtower's next daily scan should find it current. The standing procedure change is recorded in Dolman's station memory: every growth run ends with `python3 update_counts.py` before the commit.
