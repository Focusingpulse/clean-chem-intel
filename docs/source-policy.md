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
