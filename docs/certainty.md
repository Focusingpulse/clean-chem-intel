# Certainty Vocabulary

Every claim in this database carries one of five evidence levels. The level is
never optional and is never implied. A claim without a level does not ship.

The reason: most product databases treat a missing flag as a clean bill of
health. A blank space reads as "safe." That is the single most common way a
transparency tool misleads the person reading it. **Absence of evidence is not
evidence of absence**, and this vocabulary exists so the difference is visible
on the page rather than buried in a footnote.

## Two axes, not one ladder

These five levels are **not** a single scale from bad to good. They are two
different kinds of gap, and conflating them is the most common mistake.

**Axis 1 — what science knows.** We have evidence, or we do not.
`verified` · `reported` · `extrapolated` · `untested`

**Axis 2 — what the label tells you.** We know what the substance is, or we
do not. `unknown`

A substance can be well studied and still not disclosed. A substance can be
fully disclosed and never studied. Those are different failures with different
causes and different remedies, and they must never render the same way.

## The levels

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
- We name the source. This is a report of a claim, not a confirmation of a fact.
- A `reported` claim with no named source is not `reported`. It is `untested`.
- **Renders as:** "Reported by [source]".

### `extrapolated`
No direct data on this substance. A **known component or close chemical
relative** has the documented effect, so we infer it likely applies here.
- The basis of the inference is always stated, including **what was searched
  for direct data**. The build fails if it is not.
- **Extrapolated is not available for a population claim when direct data for
  that population has been reported.** The corollary of "population claims get
  their own level." A false basis is worse than a shrug, because it renders as
  a finding with a fake reason.
- Never rendered as a fact.
- **Renders as:** "Extrapolated — [basis]".

### `untested`
No evidence found in either direction. We looked and did not find.
- This is a **finding**, not a blank.
- A gap in what anyone knows. Nobody has done the study. That is a limit of
  human knowledge, not a decision anyone made about you.
- **Never renders as safe, and never renders as empty.**
- **Renders as:** "Not studied".

### `unknown` — the most serious state on this page

The substance is **not identified**. We cannot look it up because we do not
know what it is. Undisclosed fragrance blends, proprietary mixtures, "surfactant".

**This is not the mildest finding. It is the worst one, and it must render that
way.** The reasons:

1. **A bad grade is actionable. Unknown is not.** If an ingredient is graded F,
   you can decide what to do about it. You can substitute the product. You can
   ventilate. You can wear gloves. Unknown gives you nothing to act on. It
   removes your ability to choose, which is worse than giving you bad news.
2. **It could be anything.** That is not a figure of speech. An undisclosed
   blend is a container with no label on it. There is no such thing as a small
   unknown.
3. **Somebody chose this.** `untested` is a limit of what anyone knows. `unknown`
   is a limit somebody imposed. In the United States, a fragrance blend can hold
   dozens of chemicals behind one word, legally, and the label does not have to
   say which. That is a decision made upstream of you, and the database should
   say so plainly rather than shrugging.

The fear here is proportionate and it should not be talked down. The point is
not to frighten anyone. The point is that a person standing in a store has a
right to know that the honest answer is "they did not tell us," and that this
is different from "nobody has checked yet."

- **Renders as:** "Not disclosed" — never "unknown", never blank, never a
  neutral grey. Visually and in wording it must read as more serious than a
  failing grade, because it is.
- Never soften it into "we don't have information on this." The subject of the
  sentence is the manufacturer, not us.

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
7. **`unknown` is never softened.** It is the only level that describes a
   choice rather than a gap, and it renders as the most serious of the five.
