---
name: EWG gap analysis — where Clean Chem Intel can be more useful than the EWG Guide
description: What the EWG Guide to Healthy Cleaning actually covers (verified against its own pages), the six gaps that are real, and a one-line build plan for each. Revision 2 (2026-10-16) adds the scale update and the finding that this tool's two relevance dimensions, turnover and mountain, carry 45 percent of its own ranking weight and render nowhere. Presentation lane, Dolman.
---

# EWG Gap Analysis

**Author:** Dolman | **Date:** 2026-09-25 | **Lane:** clean-chem-grow RUN B (presentation / EWG-killer layer)
**Repo:** Focusingpulse/clean-chem-intel | **Positioning rule:** informs and promotes BMVC's services, never competes with them. No DIY framing anywhere.

## How this was made

Two kinds of evidence, labelled per claim:

- **verified** — the page was read directly and the wording below is quoted from it.
- **reported** — the page was read through a search index rather than fetched directly, because `ewg.org` returns HTTP 403 to a plain fetch. The 403 is bot protection, not a dead page: the same URLs serve normally to a browser, and `ewg.org/cleaners/content/methodology/` was retrieved in full through the fetch tool. Nothing here is logged as broken on the strength of a 403.

One correction up front, because it changes the shape of the whole document: **the gaps I assumed going in were largely wrong.** EWG does cover professional cleaners, hard-water stain removers, mold and mildew removers, and heritage laundry brands. The real gaps are elsewhere, and they are better gaps to own.

---

## 1. What EWG actually covers

| Measure | EWG Guide to Healthy Cleaning | This database (2026-09-25) |
|---|---:|---:|
| Products | **2,109** | 197 |
| Brands | 197 | 24 owner records |
| Ingredients | **more than 1,000** | 330 |
| Product categories | 70+ types in nine groups | 14 |
| Oldest core data | assembled winter 2011-2012 | per-record `added` date |

Source: EWG's own Quick Facts, `ewg.org/cleaners/content/methodology/`.

EWG's nine groups, from its own navigation, with the product types under them. Read this before proposing a gap:

- **All Purpose Cleaners** — All Purpose, Dusting, General Purpose Cleaner, Glass Cleaner, Graffiti / Stain Remover, Mold and Mildew Remover, Air Fresheners, Disinfectant, **Professional Cleaners**
- **Living Spaces / Bathroom** — Drain Opener / Clog Remover, All Purpose Bathroom Cleaner, Tub / Tile / Sink Cleaner, **Hard Water Stain Remover**, Shower Cleaner, Toilet Cleaner, Toilet Deodorizer
- **Living Spaces / Kitchen** — All Purpose Kitchen Cleaner, Degreaser, Dish Washer Cleaner, Granite / Stone Cleaner, Oven Cleaner, Cook Top Cleaner
- **Living Spaces / Floor and Furniture** — Carpet Cleaner, Carpet Stain Remover / Protector, Floor Cleaner, Floor Wax / Polish, Wood Floor Cleaner, Fabric Cleaner, Fabric Deodorizer, Fabric Stain Remover / Protector, Leather Cleaner, Wood Cleaner / Wax / Polish
- **Household Items / Laundry** — Anti-static / Wrinkle Remover, Bleach, Fabric Softener, Laundry Additive, Laundry Detergent (cold water, with softener, delicate, general, HE), Laundry Packs / Pods / Tablets, Washing Machine Cleaner
- **Household Items / Dishwashing** — Baby Bottle Soap, Dishwasher Detergent, Dishwashing Packs / Pods / Tablets, Hand Dishwashing Detergent / Soap, Rinse Aid
- **Household Items / Other** — Electronic Cleaner, Jewelry Cleaner, Metal Cleaner, Outdoor Cleaner, Pet Stain Remover and Deodorizer, Baby and Kid Products, Toy Cleaner

**Three assumptions that this list kills:**

1. **"EWG ignores professional products."** It has a `Professional Cleaners` product type. Do not build content on the claim that EWG covers only consumer products. It does not survive contact with their own navigation.
2. **"EWG ignores hard water."** It has a `Hard Water Stain Remover` type.
3. **"EWG ignores heritage products."** It rates them. Fels-Naptha's brand page carries one product, `Fels-Naptha Heavy Duty Laundry Bar Soap`, typed `Laundry Additive`, score range **C**; and `20 Mule Team Borax Natural Laundry Booster & Multi-Purpose Household Cleaner` is rated **D** under the same brand family. Both live on Henkel's company page (`ewg.org/cleaners/business/657-HenkelKGaACorporation/`), which reports 167 products across 14 brands.

---

## 2. The six gaps that are real

### G1 — EWG's own admission: most of its entries do not have a complete ingredient list

**Evidence (verified).** From EWG's methodology page, in its own words:

> "for the majority of the products in EWG's Guide to Healthy Cleaning, there was no way to get a complete list of every ingredient"

and, on labels specifically:

> "EWG examined more than 1,000 package labels and found that the ingredient information for 48 percent listed three or fewer ingredients on the label."

**Why it is the one that matters.** A hazard rating is only as good as the ingredient list under it. EWG is rating partial lists for most of its catalogue and saying so. This database has the opposite rule at its core: a product enters only with a manufacturer disclosure, a published SDS, or an EPA listing, and a partial disclosure is recorded as a disclosure gap rather than smoothed over. That is a structural difference, and it is the single strongest honest claim available.

**Build plan.** Make ingredient completeness a visible per-record fact: a disclosure-completeness state on every product (complete list / partial, with what is missing named), so a reader can see the difference rather than being told about it. Owner: data lane; presentation surface is Chris's.

### G2 — EWG rates hazard, and says plainly that it does not account for exposure

**Evidence (verified).** EWG's own rating disclaimer:

> "The ratings indicate the relative level of concern posed by exposure to the ingredients in this product - not the product itself ... The ratings reflect potential health hazards but do not account for the level of exposure or individual susceptibility, factors which determine actual health risks, if any."

**Why it matters.** EWG's letter grades are the most-quoted number in this category and they are explicitly hazard-only. This database carries an `exposure` field on every product, with an evidence level and, where the figure is derived, the search that produced it (`docs/exposure.md`). That is a genuinely different claim, and it is checkable rather than asserted.

**Build plan.** Surface exposure next to the grade on the product card, labelled as a derivation with its basis, so "how common is this" sits beside "how hazardous is this". Owner: presentation; the field already exists.

### G3 — Currency, and two 2021 reductions in what EWG actually reviews

**Evidence (verified).** EWG's methodology states the core product data was "first amassed in the winter of 2011-2012", with store visits in summer 2012. Two specific scope reductions are dated on the same page:

> "as of March 01, 2021, EWG actively seeks pH values for only corrosive cleaning product categories and forms."
> "As of March 01, 2021, EWG automatically assigns 2 points for MSDS Disclosure."

EWG also warns on its own product pages that formulations drift: *"Manufacturers frequently change product formulations ... The formulations may have since changed."*

**Why it matters.** Reading 2 of the 20 possible disclosure points as a standing award, rather than from a document actually read, means a disclosure score can improve without anyone reviewing anything new. Meanwhile this database stamps `updated` per record and re-checks citations each build.

**Build plan.** Show "last verified" per product on the page, and state the number of records re-checked in the current build. Currency as a visible property, not a claim. Owner: presentation.

### G4 — The consumer / professional information asymmetry is EWG's own observation

**Evidence (verified).** EWG on SDSs:

> "OSHA also requires that cleaning products sold for professional use be accompanied by MSDSs ... These documents are not provided to consumers, even when they buy products identical to those used by custodial staff."

**Why it matters, and what not to claim.** EWG *does* have a Professional Cleaners product type, so this is not a coverage gap. The gap is what a homeowner can know. The same cleaner can exist on a shelf as a ready-to-use spray at consumer dilution and as a concentrate used at a professional dilution, and the consumer route does not surface the document that states the difference. This is exactly the "expertise is the product" angle, and it is grounded in EWG's own text rather than in a swipe at EWG.

**Build plan.** A "what I bring that a spray bottle can't" panel on the page: concentration, dwell time, dilution, and material compatibility, each tied to a product already in the database, with the two-level grade rule (`docs/decisions.md`) doing the honesty work. No instructions, no recipes. Owner: content lane (Dolman) + Chris's render.

### G5 — EWG is organised by product type, never by home condition

**Evidence (verified, from the navigation itself).** Each of the 70+ product types is a product type. Nothing in that structure is an axis for water chemistry, elevation, wood heat, or a dwelling sitting empty. Hard-water *products* exist, but the condition does not.

**Why it matters, and why it is ours.** The corridor is a condition set, not a product set. Three conditions recur here and none is a product-type filter:

- **Hard water.** Colorado mountain and Front Range water runs from soft to very hard depending on source and season; Denver Water describes its own supply as soft to moderately hard and notes scale forming in two to five years, and its winter water is harder than its summer water because freeze-up concentrates minerals. CSU Extension categorises 151-300 mg/L as hard. Scale and soap scum are the visible result, and they need different chemistry from a general-purpose spray.
- **Wood heat.** Ash, soot and smoke residue are a seasonal cleaning reality here. EPA's Burn Wise: three of every ten home-heating fires come from poorly maintained fireplaces and dirty chimneys, and wood smoke's PM2.5 aggravates asthma and heart and lung disease. Annual inspection by a qualified professional is the EPA recommendation, and the cleaning residue still lands indoors.
- **Dwellings that sit empty.** A vacant or seasonally used mountain home accumulates conditions that an occupied home does not: unfixed moisture, musty odour, and closed-up air. EWG's catalogue has no category for a house that has been shut for six weeks.

**Build plan.** Three original first-party pages, one per condition, each anchored on BMVC's own job record and each stating the condition in plain language before any product is named. "What a mountain home needs that a product shelf cannot know." Owner: content lane.

### G6 — Heritage and reclassification are a presentation gap, not a coverage gap

**Evidence (verified/reported).** EWG rates Fels-Naptha (C) and 20 Mule Team Borax (D) as `Laundry Additive`. It also runs its own editorial against borax: its article *"Borax: Not the green alternative it's cracked up to be"* states *"EWG does not recommend using borax to clean your home"*.

**Why it matters.** The heritage layer here is not "EWG missed these products." It is that a bar soap and a booster powder get one letter in EWG, where this database carries the `heritage` field, the `heritage_year`, the story, and the **once safe, now flagged** reclassification layer — the products a grandmother used that the modern evidence has moved on. That is a different and better presentation, and one the brand can own honestly because the family history is real.

Note the standing decision (`docs/decisions.md`): the marketing ban on vinegar and borax does **not** apply to this database. They appear as graded ingredients with a note. EWG's own position on borax is an interesting third party to cite when the page explains why.

**Build plan.** Extend the heritage section with the reclassification contrast made explicit: "what my grandmother used, and what we know now." Owner: content lane + Chris's render.

---

## 3. Honest scale check

We are not going to be bigger than EWG by mid-October, and the page should not imply otherwise.

- Products: 197 against 2,109. EWG is roughly **10.7x** larger.
- Ingredients: 330 against more than 1,000. EWG is roughly **3x** larger.
- Brands/owners: 24 records against 197 brands.

Where we can genuinely be *more useful*, on the evidence above: completeness of the ingredient list per record (G1), exposure beside hazard (G2), per-record currency (G3), the professional/consumer concentration gap (G4), and mountain conditions no national catalogue is organised around (G5). Every one of those is a depth or context claim, not a scale claim. Say depth, not size.

## 4. What I did not verify

- **How much is actually in EWG's `Professional Cleaners` type.** The type exists in the navigation; its product count was not read. G4 is therefore framed around the consumer information asymmetry, which EWG states directly, and not around a coverage count I did not measure.
- **Whether EWG rates Zote, Sal Suds, or soap nuts.** Only Fels-Naptha and 20 Mule Team Borax were confirmed by name. Do not generalise from two brands to "EWG covers heritage products" in public copy.
- **EWG's per-product page counts for the types above** (e.g. Hard Water Stain Remover). One category page was read (`All Purpose`, 779 results); the others were not counted.
- **Exposure figures for our own 197 products** are not re-derived here. They are the data lane's, and their basis wording is already on each record.

## Claims log

| # | Claim | Level | Source |
|---|---|---|---|
| 1 | EWG's Guide contains information and hazard assessments for 2,109 products, 197 brands, more than 1,000 ingredients | verified | https://www.ewg.org/cleaners/content/methodology/ |
| 2 | EWG states that for the majority of products there was no way to get a complete list of every ingredient | verified | https://www.ewg.org/cleaners/content/methodology/ |
| 3 | Of more than 1,000 package labels examined, 48 percent listed three or fewer ingredients | verified | https://www.ewg.org/cleaners/content/methodology/ |
| 4 | EWG's ratings "do not account for the level of exposure or individual susceptibility" | verified | https://www.ewg.org/cleaners/content/scoringoverview/ |
| 5 | EWG core product data first amassed winter 2011-2012, with store visits summer 2012 | verified | https://www.ewg.org/cleaners/content/methodology/ |
| 6 | As of 2021-03-01 EWG seeks pH values only for corrosive categories and forms | verified | https://www.ewg.org/cleaners/content/methodology/ |
| 7 | As of 2021-03-01 EWG automatically assigns 2 points for MSDS disclosure | verified | https://www.ewg.org/cleaners/content/methodology/ |
| 8 | EWG warns formulations may have changed since the assessment | reported | https://www.ewg.org/news-insights/news/how-ewg-scored-cleaning-products-recommended-today |
| 9 | SDSs for professional products are not provided to consumers, even when the products are identical to those used by custodial staff | verified | https://www.ewg.org/cleaners/content/methodology/ |
| 10 | EWG's product-type navigation includes Professional Cleaners, Hard Water Stain Remover, and Mold and Mildew Remover | verified | https://www.ewg.org/cleaners/business/657-HenkelKGaACorporation/ (nav) |
| 11 | EWG categorises products into 70+ types organised into nine major groups | verified | https://www.ewg.org/cleaners/content/methodology/ |
| 12 | EWG rates Fels-Naptha Heavy Duty Laundry Bar Soap (Laundry Additive, score range C) and 20 Mule Team Borax (D) | verified | https://www.ewg.org/cleaners/business/657-HenkelKGaACorporation/ |
| 13 | EWG's editorial position is that borax should not be used to clean the home | reported | https://www.ewg.org/news-insights/news/borax-not-green-alternative-its-cracked-be |
| 14 | Denver Water classifies its supply as soft to moderately hard; scale typically forms in two to five years; winter water is harder than summer | verified | https://www.denverwater.org/your-water/water-quality/water-hardness |
| 15 | USGS defines hardness as dissolved calcium and magnesium; hard water needs more soap and leaves soap scum and scale | verified | https://www.usgs.gov/water-science-school/science/hardness-water |
| 16 | CSU Extension categorises 151-300 mg/L CaCO3 as hard water, over 300 as very hard | verified | https://extension.colostate.edu/routt/resource/drinking-water-quality/ |
| 17 | EPA: three of every ten home-heating fires are caused by poorly maintained fireplaces and dirty chimneys | verified | https://www.epa.gov/burnwise/burn-wise-facts-figures-health-and-safety-tips |
| 18 | EPA: creosote forms when wood-smoke gases condense in a cooler chimney; buildup risks a chimney fire | verified | https://www.epa.gov/burnwise/frequent-questions-about-wood-burning-appliances |
| 19 | EPA: wood smoke PM2.5 can cause asthma attacks and severe bronchitis and aggravate heart and lung disease | verified | https://www.epa.gov/burnwise/burn-wise-facts-figures-health-and-safety-tips |
| 20 | EPA maintains public guidance on mold, moisture and the home | verified | https://www.epa.gov/mold/brief-guide-mold-moisture-and-your-home |
| 21 | This database holds 197 products, 330 ingredients, 24 owner records at 2026-09-25 | verified | data/ at HEAD, re-derived this run |
| 22 | A product enters this database only with a manufacturer disclosure, published SDS, or EPA listing; partial disclosure is recorded as a gap | verified | docs/source-policy.md |
| 23 | The two-level grade rule: the ingredient entry grades the pure chemical, the product entry grades the strength as sold | verified | docs/decisions.md (2026-09-22, item 4) |
| 24 | The vinegar and borax marketing ban does not apply to this database | verified | docs/decisions.md (2026-09-22), SPX-006 hard_rules |

## Uncertainty flags

1. `ewg.org` returns HTTP 403 to an unauthenticated fetch. Claims marked **verified** were read either through the fetch tool (the methodology page) or by direct page read (the Henkel company page); claims marked **reported** were read through a search index. A future check should re-confirm the reported ones.
2. EWG's Quick Facts figure (2,109 products) and a 2020 EWG article's "more than 2,500 products" disagree. The Quick Facts figure is from EWG's own current methodology page and is the one used here.
3. G6's framing depends on the `heritage` field being populated honestly. It is a presentation argument, not a data claim.
4. Every build plan above defers implementation to the owner named. None of it ships without Sandra's sign-off (`docs/decisions.md`: CCI-011 is the launch gate).

---

# Revision 2 — 2026-10-16 (clean-chem-grow RUN B)

Sections 1 to 4 are unchanged. This appends what a month of harvesting changed, and one
structural finding that outranks the rest of the document.

## 5. The scale argument moved, and it is worth re-saying

| Measure | 2026-09-25 (Rev 1) | 2026-10-16 (HEAD) | EWG |
|---|---:|---:|---:|
| Products | 197 | **436** | 2,109 |
| Ingredients | 330 | **777** | more than 1,000 |
| Categories | 14 | **15** | 70+ types in nine groups |
| Heritage records | not measured | 29 | not applicable |

The product gap is still real (EWG is roughly 4.8x larger, down from 10.7x). The
**ingredient** gap has nearly closed: 777 against "more than 1,000". That is a materially
different sentence from the one Rev 1 could write, and it is the honest one to use. Keep
saying depth, not size, but the depth claim is now close to a parity claim on ingredients.

## 6. The gap this database owns and has not switched on

This is the finding of this revision, and it is more useful than any of G1 to G6.

EWG is organised by **product type** (G5). It has no notion of the home the product is used
in, and structurally cannot: a national catalogue of 2,109 products cannot be indexed by
"hard water at 9,000 feet" or "a house that sat empty through February".

This database already computes two dimensions of exactly that kind, in
`tools/curation_score_2026_10_04.py`:

- **Turnover relevance** (`str`): how much a product matters to a short-term-rental changeover.
- **Mountain relevance** (`mountain`): hard-water and mineral scale, wood-stove soot and
  creosote, mildew in a home that sat closed, wood and stone surfaces, de-icer and road salt.

The scorer's own weights put **0.25 on turnover and 0.20 on mountain** (against sales 0.30,
hazard 0.15, ungraded 0.10). **Forty-five percent of this tool's ranking weight rests on two
axes EWG cannot have at all.**

**Neither one renders.** `index.template.html` contains no data reference to `mountain`, its
`str` score, or `turnover`; the built page's only "mountain" strings are the BMVC domain in
the schema and the CTA. The curation queue built from those weights is also stale: it was
generated 2026-10-04 over 294 products, against 436 today.

So the largest EWG-killer in this repo is not more products. It is that the differentiator is
computed, weighted, and invisible. A visitor cannot ask "what do I use on mineral scale in a
mountain rental", which is the exact question the tool is best placed to answer.

### G7 — Render the two relevance dimensions. *(highest value; no data work needed)*
Expose `mountain` and `str` as filter chips ("mountain homes", "rental turnover") and one
line on the card. The data already exists; only the template holds it back. Owner: Chris/Cairn.
This joins the standing missing-render-surface ruling as its **strongest** member, because it
is the tool's differentiator rather than an internal annotation.

### G8 — Carry the same two dimensions into the machine-readable layer.
The `@graph` block already mirrors page counts; the AI-facing claim ("organised by the home,
not just the product type") belongs there too. Owner: Chris/Cairn.

### G9 — One page per mountain condition, framed as what a trained cleaner knows. *(extends G5)*
Four conditions, each anchored on the sources already in this document's claims log:
hard-water scale (Denver Water, USGS, CSU Extension), wood-stove soot and creosote (EPA Burn
Wise), mildew in a home that sat closed (EPA moisture and mold guidance), and de-icer and road
salt. **The angle is the operator's knowledge, never a recipe the reader performs.**

The cleanest example, and it is a maintenance fact rather than a product fact: in a
wood-heated home the biggest single lever on indoor particulate is the **flue**, not the
cleaner on the shelf. Flue cleaning explained 16 percent of the variance in indoor PM2.5 in a
peer-reviewed household study, and stove age was not associated with indoor PM at all. An
ingredient database cannot say that. A person who cleans these homes for a living can.

## 7. Two fields the presentation lane was told to fill, that nothing renders

Recorded here because the RUN B mandate names them and a future fire should not re-discover it:

- **`note`**: 269 of 436 records carry one. `p.note` renders **zero** times; the modal
  interpolates only `cf.note`, `cr.note` and `heritage_note`. Adding plain-language product
  context to `note` is invisible work until the field has a surface.
- **`substitutes`**: 187 of 436 records carry one. It renders **zero** times, so a record with
  a same-price alternative looks identical to one without.

Both are the same class as G7 and are already filed as render-surface questions. Do not write
more of either until Trellis rules the surface.

## 8. What this revision did not do

- **No DIY content, by rule.** Every mountain condition above is written as an operator's
  knowledge, per the positioning rule at the top of this document.
- **No data was graded or re-graded.** This is a presentation revision.
- The **Air Care** category (13 records, split out of Specialty this fire) is a taxonomy
  change under the existing RUN B mandate; it is documented in
  `docs/presentation-categories.md` Revision 2 and flagged to Trellis.
- The scorer's `STR_CAT` and `MOUNTAIN_CAT` maps have **no `Air Care` key**, so those records
  take the caller's 4.0 default for both dimensions. That is not wrong, but if air treatment
  should weigh differently for a mountain turnover it needs an explicit entry. Flagged to Cairn.

## Claims log — Revision 2

| # | Claim | Level | Source |
|---|---|---|---|
| 25 | This database holds 436 products and 777 ingredient records at HEAD 2026-10-16 | verified | data/ at HEAD, re-derived this run |
| 26 | The curation scorer weights are sales 0.30, str 0.25, mountain 0.20, hazard 0.15, ungraded 0.10 | verified | tools/curation_score_2026_10_04.py |
| 27 | The scorer's turnover domain keys on disinfectant, bleach, sanitizing, mold, stain, toilet/tub/shower, laundry | verified | tools/curation_score_2026_10_04.py (STR_KEYWORDS) |
| 28 | The scorer's mountain domain keys on hard water, lime, calcium, rust, soot, creosote, wood stove, mold, mildew, granite, stone, wood, de-icer, road salt | verified | tools/curation_score_2026_10_04.py (MOUNTAIN_KEYWORDS) |
| 29 | `curation-queue.json` was generated 2026-10-04 over 294 products ("top 30 of 218 ungraded"), against 436 today | verified | data/curation-queue.json |
| 30 | No mountain or turnover dimension renders: the template has no data reference to either, and the built page's only "mountain" strings are the BMVC domain | verified | grep of index.template.html and index.html |
| 31 | 269 of 436 records carry `note`; `p.note` renders 0 times (only `cf.note`, `cr.note`, `heritage_note`) | verified | data/products.json + index.template.html |
| 32 | 187 of 436 records carry `substitutes`; it renders 0 times | verified | data/products.json + index.template.html |
| 33 | EPA: "The key to mold control is moisture control"; dry water-damaged areas within 24-48 hours; keep indoor humidity below 60 percent, ideally 30 to 50 percent | verified | https://www.epa.gov/mold/brief-guide-mold-moisture-and-your-home |
| 34 | EPA names woodstoves and fireplaces as combustion sources and states that benzo(a)pyrene, "which can cause cancer", attaches to small particles inhaled deep into the lung | verified | https://www.epa.gov/indoor-air-quality-iaq/sources-combustion-products |
| 35 | Flue cleaning "explained 16% of the variance" in indoor PM2.5, and stove age was not associated with indoor PM, in a peer-reviewed household study | verified | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9609584/fullTextXML |
| 36 | 13 air-care records were split from Specialty into a new `Air Care` category this fire | verified | data/products.json diff, tools/normalize_categories.py Revision 2 |

## Uncertainty flags — Revision 2

5. Claim 30 is a grep of two files, not a render test. It says the template never reads the
   field; it does not prove no other surface (for example the machine-readable layer in
   `build.py`) consumes it. G8 should be checked against that layer before it is written.
6. The 16 percent figure in claim 35 is from one study of households in a single setting. Use
   it as the direction of the finding (maintenance over product) rather than as a precise
   coefficient, and do not attach it to Sandra's own service area.
7. `Air Care` as a category name is the presentation lane's proposal under the standing RUN B
   mandate, not a ruled taxonomy value. Trellis owns that ruling; the alias map makes it
   reversible if he rules differently.
