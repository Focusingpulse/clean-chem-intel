# Data Source Policy

## Principles

1. **Only use data we have a legal right to use.** No scraping databases whose terms prohibit it.
2. **Prefer open government sources.** NIH, EPA, and similar agencies provide free, API-accessible data with no usage restrictions.
3. **Cite everything.** Every data point in the system should trace back to a specific source and record.
4. **Be transparent about gaps.** If we don't have data for an ingredient, say so — don't guess silently.

## Approved sources

### PubChem (NIH)
- **URL**: https://pubchem.ncbi.nlm.nih.gov/
- **API**: PUG REST (https://pubchem.ncbi.nlm.nih.gov/rest/docs)
- **What we use**: Chemical names, CAS numbers, GHS classifications, bioassay data, safety summaries
- **Access**: Free, no API key required
- **Terms**: Public domain data, no usage restrictions

### EPA CompTox Chemicals Dashboard
- **URL**: https://comptox.epa.gov/dashboard/
- **API**: Available with key request
- **What we use**: High-throughput screening (ToxCast), exposure predictions, hazard flags
- **Access**: Free, API key may be requested
- **Terms**: Public domain data

### ACI Cleaning Chemistry Catalog (C3)
- **URL**: https://www.cleaninginstitute.org/
- **What we use**: Cleaning-specific ingredient risk assessments, human and environmental safety data
- **Access**: Free web database
- **Terms**: Public information, cite source

### CPDat (EPA)
- **URL**: https://www.epa.gov/chemical-research/chemical-and-product-database-cpdat
- **What we use**: Chemical-to-product linkages (which chemicals appear in which product categories)
- **Access**: Free download + API
- **Terms**: Public domain data

### DailyMed (NLM)
- **URL**: https://dailymed.nlm.nih.gov/
- **What we use**: Ingredient lists from FDA OTC drug labels. This is the only route to a full
  active + inactive ingredient list for several classes of cleaning-adjacent product, including
  store-brand antibacterial hand soaps, where the manufacturer publishes nothing on its own site.
- **Why it counts as a primary source**: the label is the manufacturer's own regulatory filing,
  and it names the labeler of record. It is a government host serving a manufacturer document,
  which is the same structure as an EPA-listed SDS.
- **Access**: Free, no API key. `drugInfo.cfm?setid=...` and `getFile.cfm?setid=...&type=pdf`.
- **Added**: 2026-09-25, Dolman (spectrum build station 2).

### FDA UNII Search Service
- **URL**: https://precision.fda.gov/uniisearch/srs/unii/
- **What we use**: Substance identity, specifically colour-index and trade-name synonyms, so a
  label term like "Violet 10" can be resolved to a chemical with a PubChem CID before grading.
  Without this step the grade would rest on a guessed identity.
- **Terms**: Public domain (FDA).
- **Added**: 2026-09-25, Dolman.

### Manufacturer SB-258 disclosure pages (California Cleaning Product Right to Know)
- **What we use**: Intentionally-added ingredient lists with CAS numbers, published by the
  manufacturer on its own site because California requires it. Whole Foods Market and Sprouts
  Farmers Market both publish per-product declarations this way.
- **Why it counts as a primary source**: it is the manufacturer's own published specification,
  which `docs/certainty.md` already accepts at the `verified` level. The law is what makes it
  exist, not what makes it trustworthy.
- **Note**: this is the only route that has produced full ingredient lists for private-label
  grocery cleaners so far. Treat a private label with no such page as a disclosure gap.
- **Added**: 2026-09-25, Dolman.

### Retailer-hosted and brand-hosted SB-258 indices (named, working)

Single served pages that carry a per-product SB-258 declaration for a whole brand
family. Each is the manufacturer's (or the retailer's, for its own house brand)
own publication of the filing, so they sit at the `verified` level in
`docs/certainty.md`. Read the served HTML; none needs JavaScript.

| Index | What it covers | Added |
|---|---|---|
| `kikcorp.com/ingredients/` | 176 PDF filings across KIK Consumer Products' house brands (Comet, Spic and Span, Top Job, The Works, Greased Lightning, A-1, Arctic White, SMART, Value Star, Pure Bright, Hi-lex, Austin's) | 2026-09-29 |
| `vestacyinfo.com/brand.php?brandId=<n>` then `product.php?productLineId=<id>` | Essential Home (Advent International, formerly Reckitt's divested brands): Air Wick, Calgon, Glass Plus, Lime-A-Way, Old English, Resolve, Spray 'n Wash, Woolite, Mop & Glo, Brasso, d-CON, Rid-X, Easy-Off, Botanical Origin, Silvo | 2026-10-07 |
| `summitbrands.com/ingredients/` | 44 product tables across Summit Brands (Glisten, Iron OUT, Lime OUT, Dryel, Zout, White Brite, Drain OUT, Whirl OUT, Filter Mate, Plink, EarthStone, SeptoBac, Woolite Dry Care). Each row is Ingredient Name, CAS, Functionality, SB-258 fragrance-allergen list number. | 2026-10-09 |

Retailer-hosted routes that are machine-readable and have produced records:
Walmart CDN (`i5.walmartimages.com/dfw/.../*.pdf`, Great Value), Sam's Club CDN
(`scene7.samsclub.com/is/content/samsclub/<upc>_pdf`, Member's Mark), Target
product pages (`environmental_segmentation.ingredient_chemical_disclosure_url`
naming a document on `digitalcontent.target.com`, up&up), CVS house brands on the
Spanish-locale host (`es.cvs.com/shop/ingredients/<slug>-prodid-<id>`, field
`vendorIngredientsParagraph`; the prodid alone resolves), and the CVS SB-258 PDFs
under `cvs.com/bizcontent/ca-cleaning-disclosure/` (the directory 404s by design;
the per-product PDFs are live and search-indexed).

**Known walls, do not log as broken links**: `walmart.com` product pages,
`homedepot.com`, `kroger.com` (and Ralphs, King Soopers, Smith's), `lowes.com`,
`amazon.com` product pages, `ewg.org`, `ndclist.com`. A 403/429/500 or a
"Robot or human?" body is a bot wall, not a dead citation.

- **Added**: 2026-10-09, Dolman (clean-chem-grow RUN A).

## Sources we do NOT use

### EWG Skin Deep Database
- **Why not**: EWG's Terms of Service explicitly prohibit deriving machine-readable datasets from their database without written permission. They reserve the right to pursue legal action including fee-shifting provisions. They also use Cloudflare protection.
- **What we take from them**: Nothing — not data, not scores, not ratings. We may reference their published methodology (A-F grading approach) as inspiration for how to present our own transparent scoring, but we derive zero data from EWG.
- **Decision date**: August 16, 2026

## Adding new sources

Any new data source must be vetted against this policy before integration:
1. Confirm the source's terms of service permit our intended use
2. Verify API access is available and sustainable (no fragile scraping)
3. Document what data we pull and how we cite it
4. Add to this file with a new entry
