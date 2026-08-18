# Clean Chem Intel

A Product Ingredient Transparency Engine for Bella's Mountain Vacation Cleaning (BMVC).

## What it does

Enter a cleaning product's ingredient list. Get back:
- Each ingredient broken out individually
- What each ingredient does to the human body (respiratory, dermal, endocrine, organ toxicity)
- A transparent grade based on clinical research and regulatory data
- Extrapolation flags for ingredients not in any database (based on chemical properties and interaction rules)

The end goal is a public-facing tool on [bellasmountainvacationcleaning.com](https://bellasmountainvacationcleaning.com) that proves Sandra actually vets what she uses — not just marketing claims.

## Data sources

This project uses **only open, legal, API-accessible data sources**:

| Source | What it provides | Access |
|--------|-----------------|--------|
| **PubChem** (NIH) | 110M+ chemicals, toxicity, bioassays, GHS classifications | Free REST API (PUG), no key needed |
| **EPA CompTox Dashboard** | 1M+ chemicals, high-throughput screening, ToxCast, exposure data | Free API with key request |
| **ACI Cleaning Chemistry Catalog (C3)** | 1,100+ cleaning-specific ingredients with risk assessments | Free web database |
| **CPDat** (EPA) | Chemical-to-product linkage data | Free download + API |

We do **not** scrape or derive datasets from the Environmental Working Group (EWG) Skin Deep database. EWG's Terms of Service prohibit machine-readable derivation without written permission. We reference their A-F grading *methodology* as inspiration for how to present scores, but all underlying data comes from the open sources above.

## Project structure

```
clean-chem-intel/
├── README.md
├── docs/
│   ├── methodology.md
│   ├── source-policy.md
│   └── scoring-rubric.md
├── data/
│   ├── seeds/          # Manually researched starter data
│   └── raw/            # Raw API responses (gitignored)
├── src/
│   ├── core/
│   │   ├── models.py   # Data models
│   │   ├── parser.py   # Ingredient string -> matched chemicals
│   │   ├── scorer.py   # Transparent scoring engine
│   │   └── fetcher.py  # PubChem API client
│   ├── api/
│   └── cli/
│       └── main.py     # CLI entry point
└── tests/
```

## Phased build plan

- **Phase 0** (current): Methodology docs, seed data, ingredient parser
- **Phase 1**: SQLite database, 25 products entered manually, scorer
- **Phase 2**: OCR for label photos, SDS extraction, PubChem enrichment, web UI
- **Phase 3**: Public-facing tool on bellasmountainvacationcleaning.com

## Legal

This tool provides informational analysis based on publicly available scientific and regulatory data. It is not a substitute for professional medical or toxicological advice. See `docs/methodology.md` for the full disclaimer.

## License

MIT
