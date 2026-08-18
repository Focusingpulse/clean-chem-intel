# Methodology

## Purpose

This document defines how Clean Chem Intel evaluates cleaning product ingredients and assigns grades. The goal is transparency: every score should be traceable to a specific data source and a clear rule.

## Scope

This tool analyzes ingredients in cleaning products (not cosmetics, not food). It focuses on:
- Human health impact (respiratory, dermal, endocrine, organ toxicity)
- Environmental impact (biodegradability, aquatic toxicity)
- Worker safety (repeated exposure considerations)
- Sensitive occupant flags (children, pets, chemically sensitive individuals)

## Data hierarchy (strongest to weakest evidence)

1. **EPA ToxCast / high-throughput screening** — empirical bioassay results (e.g., "this chemical showed activity in estrogen receptor assays"). Strongest evidence.
2. **PubChem bioassays** — peer-reviewed assay data from NIH.
3. **GHS classifications** — internationally harmonized hazard statements (H-phrases).
4. **EPA CompTox exposure data** — modeled exposure and hazard predictions.
5. **ACI C3 risk assessments** — cleaning-industry-specific safety evaluations.
6. **Structural similarity extrapolation** — if no data exists, flag based on chemical properties and interaction rules. Weakest evidence, always flagged as extrapolation.

## Scoring dimensions

Rather than a single 0-100 score, each ingredient is graded across multiple dimensions:

| Dimension | What it measures | Grade range |
|-----------|------------------|-------------|
| **Disclosure quality** | How complete and transparent is the ingredient listing? | A-F |
| **Respiratory impact** | Risk of inhalation irritation or damage | A-F |
| **Dermal impact** | Risk of skin irritation, sensitization, or absorption | A-F |
| **Endocrine impact** | Evidence of endocrine disruption activity | A-F |
| **Organ toxicity** | Evidence of liver, kidney, or other organ effects | A-F |
| **Environmental impact** | Biodegradability and aquatic toxicity | A-F |
| **Worker safety** | Repeated-use exposure risk for cleaning professionals | A-F |
| **Sensitive occupant flag** | Special concern for children, pets, or chemically sensitive individuals | Flag (Yes/No) |
| **Evidence confidence** | How strong is the underlying data for this ingredient? | High/Medium/Low/Extrapolated |

## Grade definitions

- **A**: No known hazard based on available data
- **B**: Minimal hazard, minor irritant potential
- **C**: Moderate hazard, some evidence of concern
- **D**: Significant hazard, multiple risk factors
- **F**: Strong evidence of serious health or environmental harm

## Interaction rules (extrapolation)

When an ingredient lacks direct toxicity data, we flag potential risks based on known chemical properties and how they interact:

- **Penetration enhancer + sensitizer** → elevated dermal risk
- **Volatile organic + respiratory irritant** → indoor air quality concern
- **Non-biodegradable + aquatic toxic** → environmental persistence
- **Surfactant + known irritant** → compounded dermal/respiratory risk

These are always labeled as extrapolation and never presented as confirmed findings.

## Disclaimer

This tool provides informational analysis based on publicly available scientific and regulatory data. It is not a substitute for professional medical advice, toxicological assessment, or regulatory compliance guidance. Grades reflect the best available evidence at time of analysis and may change as new data becomes available. Always consult product Safety Data Sheets (SDS) and follow manufacturer instructions.
