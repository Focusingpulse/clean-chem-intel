# Scoring Rubric

## Overview

Each ingredient receives grades across multiple dimensions. Grades are letter-based (A-F) to avoid false precision. A numeric score that implies "73.4 out of 100" suggests a level of accuracy the underlying data rarely supports.

## Dimension details

### Disclosure quality
- **A**: Full ingredient list published, all components identified by name and CAS number
- **B**: Most ingredients identified, some vague terms (e.g., "fragrance" without breakdown)
- **C**: Partial disclosure, proprietary blends undisclosed
- **D**: Minimal disclosure, only active ingredients listed
- **F**: No ingredient information available

### Respiratory impact
- **A**: No respiratory hazard known
- **B**: Mild odor, no irritation reported
- **C**: Respiratory irritant, may cause discomfort in sensitive individuals
- **D**: Known respiratory sensitizer or asthma trigger
- **F**: Confirmed respiratory toxin, chronic exposure risk

### Dermal impact
- **A**: No skin hazard known
- **B**: Mild irritant possible with prolonged contact
- **C**: Skin irritant, may cause rash or contact dermatitis
- **D**: Known skin sensitizer, may cause allergic reaction
- **F**: Corrosive or confirmed dermal toxin

### Endocrine impact
- **A**: No endocrine activity detected in ToxCast/bioassay screening
- **B**: Weak or equivocal evidence in screening assays
- **C**: Some evidence of endocrine activity (e.g., estrogen receptor binding)
- **D**: Confirmed endocrine disruptor in multiple assays
- **F**: Strong evidence of endocrine disruption with known mechanism

### Organ toxicity
- **A**: No organ toxicity known
- **B**: Effects only at extremely high doses unlikely in normal use
- **C**: Some evidence of organ effects at occupational exposure levels
- **D**: Confirmed organ toxin, liver/kidney effects documented
- **F**: Severe organ toxicity, multiple organs affected

### Environmental impact
- **A**: Readily biodegradable, no aquatic toxicity
- **B**: Biodegradable, low aquatic toxicity
- **C**: Slow biodegradation, moderate aquatic toxicity
- **D**: Not biodegradable, or high aquatic toxicity
- **F**: Persistent bioaccumulative toxin, severe aquatic hazard

### Worker safety
- **A**: Safe for repeated occupational use with standard PPE
- **B**: Minor precautions needed (gloves recommended)
- **C**: Requires PPE (gloves + ventilation), exposure limits apply
- **D**: Requires strict exposure controls, sensitization risk with repeated use
- **F**: Hazardous for repeated use, substitute if possible

### Sensitive occupant flag
- **Yes**: Ingredient warrants special caution for children, pets, or chemically sensitive individuals
- **No**: No special concern beyond standard grades

### Evidence confidence
- **High**: Multiple peer-reviewed sources + ToxCast/bioassay data
- **Medium**: At least one regulatory classification + some assay data
- **Low**: Limited data, mostly structural/property-based assessment
- **Extrapolated**: No direct data — assessment based on interaction rules and chemical similarity only

## Overall product grade

The overall product grade is not a simple average. It is the **worst dimension grade** that is supported by **Medium or higher** evidence confidence. This prevents a product with one serious confirmed hazard from being averaged away by good grades in other dimensions.

If all dimensions are A or B with High confidence, the product grade is A.
If any dimension is D or F with High or Medium confidence, the product grade cannot exceed D.

## Interaction flags

Interaction flags are advisory, not grading inputs. They highlight combinations that may compound risk:

| Flag | Trigger | Concern |
|------|---------|---------|
| Dermal absorption risk | Penetration enhancer + sensitizer present | More of the sensitizer may reach systemic circulation |
| Indoor air quality | Volatile organic + respiratory irritant | Combined effect on airway during use |
| Environmental persistence | Non-biodegradable + aquatic toxic | Long-term ecosystem impact |
| Compounded irritation | Surfactant + known irritant | Enhanced penetration of irritant through skin/mucosa |
