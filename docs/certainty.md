# Certainty Vocabulary

Every claim in this database carries one of five evidence levels. The level is
never optional and is never implied. A claim without a level does not ship.

The reason: most product databases treat a missing flag as a clean bill of
health. A blank space reads as "safe." That is the single most common way a
transparency tool misleads the person reading it. **Absence of evidence is not
evidence of absence**, and this vocabulary exists so the difference is visible
on the page rather than buried in a footnote.

## The five levels

### `verified`
A **primary source** states it and we read the source ourselves.
- Primary means: a government agency, a peer-reviewed study, a manufacturer's
  own published specification, or a standards body.
- The source URL is recorded and resolvable.
- An identifier (DOI, PMID, CAS, CID) has been resolved against its registry,
  not merely pattern-matched on author and year.
- **Renders as:** "Verified" with a link.

### `reported`
A **credible secondary source** states it. We did not check the primary.
- Secondary means: a professional body's summary, a veterinary or medical
  reference, a published guidance page.
- We name the source and we name what it is: this is a report of a claim, not
  a confirmation of a fact.
- **Renders as:** "Reported by [source]".

### `extrapolated`
No direct data on this substance. A **known component or close chemical
relative** has the documented effect, so we infer it likely applies here.
- The basis of the inference is always stated.
- Never rendered as a fact. Always rendered as an inference.
- **Renders as:** "Extrapolated — [basis]".

### `untested`
No evidence found in either direction. We looked and did not find.
- This is a **finding**, not a blank. It is the honest answer and it is
  published as one.
- **Never renders as safe, and never renders as empty.**
- **Renders as:** "No evidence found either way".

### `unknown`
The substance is **not identified**. We cannot look it up because we do not
know what it is.
- Undisclosed fragrance blends, proprietary mixtures, generic "surfactant".
- Different from `untested`: untested means we know what it is and found
  nothing. Unknown means we do not know what it is at all.
- **Renders as:** "Ingredient not identified".

## Rules

1. **Never upgrade a level to make a page look more complete.** A page full of
   `verified` and a page full of `untested` are both correct if both are true.
2. **Never invent a grade to fill a slot.** If the answer is `untested`, the
   answer is `untested`.
3. **Resolve identifiers, do not pattern-match them.** A wrong DOI passes an
   author-year check exactly like a fabricated paper. Resolve against Crossref
   or NCBI before recording `verified`.
4. **Do not treat a non-200 HTTP status as a broken source.** Several
   authoritative sites return 403 to machine requests while serving normally
   to a browser. Record it as "not machine-readable" and confirm another way,
   never as "dead link".
5. **A safety claim and a marketing claim are different claim types.** When a
   manufacturer asserts safety and a toxicology source documents hazard, both
   get recorded, both get their level, and the page shows the tension rather
   than resolving it in the manufacturer's favour.
6. **Population claims get their own level.** A substance can be `verified`
   hazardous to cats and `untested` for birds. One level per claim, never one
   level per substance.

## Why five and not three

Three levels (safe / unknown / unsafe) collapse two distinct failures.
"Untested" and "unknown" are not the same thing, and telling a reader that an
undisclosed blend is merely "untested" hides the real problem, which is that
nobody, including the manufacturer, has said what is in it.
