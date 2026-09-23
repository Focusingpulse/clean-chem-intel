---
description: Sandra's sign-off decisions for the Clean Chem Intel public page. Authoritative for all agents. Decisions live here, not in conversations.
---

# Decisions

Sandra's rulings, dated. These are authoritative for every agent working on this
repo. A constraint given in a chat does not exist for the other agents until it
is written here.

---

## 2026-09-22 — Public page decisions (Sandra, sign-off)

Four questions were put to Sandra. All four answered. These unblock the page
build (Chris / Cairn's lane). They do not constitute the go-live sign-off
itself, which is CCI-011.

### 1. Page URL: `/products-we-use/`

**Decided.** Full URL: `https://bellasmountainvacationcleaning.com/products-we-use/`

Rationale: it is the phrase a homeowner would actually say out loud, it matches
the site's first-person voice, and it says what the page is. `/clean-chemistry/`
was the alternative and is not used.

Consequence: the URL is now frozen. It appears in the schema `url` field, the
sitemap entry, every internal link, and every CTA. Changing it later breaks all
of them.

### 2. Grandmother's name: NOT named in public copy

**Decided.** The "Grandma's cupboard" section stays as a section. **Martha is
not named on the public page.**

Rationale: the origin story is the most personal material in the project and a
name on a public page is permanent once indexed. Sandra's call, and reversible
only by her.

### 3. Sticky Get a Quote bar: NOT added for now

**Decided.** No sticky quote bar.

Rationale: keep the tool purely informational and see how people actually use it
before adding any conversion ask. Sandra's words: no bar for now. This is
explicitly a deferral, not a rejection, and it can be revisited once there is
usage data.

Note: this was Dolman's suggestion, not a package requirement. The page still
carries the standard "Get a Quote" CTA to `/contact-us/` after the intro
paragraph and at the page bottom. Only the sticky-on-scroll variant is dropped.

### 4. Grading basis: BOTH, at two levels

**Decided.** Two distinct grades, two distinct claims:

- **The ingredient entry grades the pure chemical**, with the concentration
  caveat attached to the entry. Glacial acetic acid is graded as glacial acetic
  acid.
- **The product entry grades the strength as sold**, computed from the
  concentration in that product's actual ingredient list.

Rationale: neither single-level answer works. Grading only by pure substance
publishes household vinegar as corrosive and graded F, which is false and
destroys trust in every other grade on the page. Grading only as-sold forces
99% acetic acid and 4% vinegar into one entry that cannot be right for both.

This is the population-claim rule applied to concentration instead of species:
**one level per claim, never one level per substance.**

Consequence: products whose ingredient list specifies a diluted strength do not
inherit the severe grade of the concentrated form. This also affects existing
entries graded on the pure-substance basis, hydrogen peroxide at household 3%
among them.

### Consequences of decision 4, as ruled (Linnea, two-level review 2026-09-23)

**The as-sold grade needs two traces, not one.** Both must be present:
- `conc` + `conc_src` — the concentration stated in **this product's own source**
- `grade_as_sold` + `grade_as_sold_src` — the concentration-to-hazard mapping from an authority
  (CLP generic concentration limits, a harmonized classification, or an SDS classifying that strength)

A concentration alone is not enough: it would let a harvester read "5% acetic acid" and still
grade it F because the substance is acetic acid.

**The ingredient entry is NOT softened.** The rule cuts both ways. Acetic acid stays F on the
ingredient entry. The softening exists only at product level. Anyone "fixing" vinegar by
downgrading the ingredient has broken the rule rather than applied it.

**A typical-range note is context, not data.** Only a stated concentration counts.

**No concentration given: `strength_disclosure = "not disclosed"`.** Not a silent blank, which
reads as benign, and not an inherited severe grade either. This is an `unknown`-class state on
the concentration dimension and carries two obligations: it owes a substitute the way an F does,
and the product still shows the substance grade **as reference, not as inheritance**, so the
reader is not nudged toward benign.

**"As sold" means the form the product presents**, not only its strength. Form and route change
hazard too: the respirable-silica concern on alumina and feldspar is a product-form question
rather than a concentration one. Noted where it matters.

**Sequencing, and the most likely way this fails:** products.json holds no concentration and no
stored product grade today, so grades derive at build time from the ingredient keys. Fields
before grades before guard, or the "both directions" rule has nothing to check and verification
is by eye across 157 products. The capitalised-key drift must be fixed in the same pass or
products keep grading off softened keys and the two-level rule renders as a lie.

---

## Standing decisions carried from elsewhere

- **Vinegar and borax**: the marketing ban does NOT apply to this database.
  Sandra confirmed the database is a chemistry reference, not marketing copy.
  Both appear as graded ingredients with a note. (2026-09-22)
- **No DIY content.** The tool informs and promotes BMVC services; it never
  teaches. No recipes, no mixing instructions, no "clean it yourself" framing.
- **Voice**: first person, no em dashes, no apostrophe in Bellas, CTA is "Get a
  Quote" and never "Free Quote". These are enforced mechanically in
  `build.py::voice_normalize`, not remembered.
- **`unknown` is the most serious state on the page.** Not the mildest.
  `untested` is a limit of what anyone knows; `unknown` is a limit somebody
  imposed. See `docs/certainty.md`.
