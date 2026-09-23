---
description: How exposure is estimated, why the database is ordered by it, and what an exposure claim's evidence level means. Read with docs/certainty.md.
---

# Exposure

The database is ordered by **exposure**, not by price tier. Trellis's call,
Sep 22 2026. Price tier is a filing cabinet; exposure is the signal. A product
used in two million homes matters more than a product used in two thousand,
regardless of which shelf either sits on.

The tiers are then named after the breakpoints that appear in the data, not
chosen in advance. If the dollar-store generics and the mass-market staples
cluster at the top, that is a finding, not an assumption.

## What `exposure` means

`exposure` is an estimate of the **share of US households that buy or use the
product**, as a whole number percentage. It is an order-of-magnitude estimate,
not a measurement, and it is never more precise than one significant figure.

A number is not an exposure estimate unless it has a source. Every product
carries all three fields:

- `exposure` — the estimate, or `null`
- `exposure_ev` — the evidence level from `docs/certainty.md`
- `exposure_src` — the URL the estimate traces to, or `null`

Products whose estimate is derived rather than measured also carry
`exposure_basis`, which must state **what was searched for direct data** and why
the derivation was used instead. This is the same rule `check_claim` enforces on
oils: an extrapolated claim that does not say what was searched is a finding
with a fake reason.

## How an estimate is produced

There is no published per-product household penetration figure for cleaning
products in the US. Category penetration exists, and brand shares exist, and
product-level sales data exists on individual retail channels. An exposure
estimate is built from those three, in that order of reliability.

1. **Category penetration.** What share of households use the category at all.
   Example: laundry care exceeds 95% of roughly 131 million US households;
   liquid dish soap is owned by over 95% of households.
2. **Brand share of the category.** Example: Procter & Gamble held 59% of US
   laundry care retail value in 2025 (Euromonitor).
3. **Product share within the brand.** Rarely published. Where it is missing,
   the estimate stops at the brand and is marked as such.

Channel data (Amazon brand concentration, unit velocity) is used only as a
cross-check or a proxy, and the basis always says so. Amazon concentration is
not national share, and an estimate built from it is marked `extrapolated`.

## What each evidence level means for an exposure claim

- **`reported`** — a named source states a product-level or brand-level figure
  we can quote. Amazon rating counts and monthly unit velocity qualify, with the
  channel named. Example: Clorox Disinfecting Wipes at roughly 100,000 units
  per month and 117,900 Amazon ratings (April 2026).
- **`extrapolated`** — no direct figure exists for the product. The estimate is
  derived from category penetration and brand share. The basis states both the
  derivation and what was searched for a direct figure.
- **`untested`** — we looked and found no usable signal. This is a gap in our
  research, not a statement about the product. It is the honest outcome for most
  of the catalog today, and it is recorded rather than filled with a guess.
- **`unknown`** — never used at this dimension. Nothing here withholds identity;
  a missing exposure figure is our gap, not a party's choice.

## The rule this file exists to enforce

An estimate with no source is not an estimate. It is a number shaped like one,
and it would render with the same authority as a measured figure. The certainty
guard refuses to build when an exposure claim carries no valid level, when a
non-null estimate carries no source, or when an extrapolated estimate does not
say what was searched. Same principle as the voice rule and the claim levels:
enforcement in the build, not in memory.
