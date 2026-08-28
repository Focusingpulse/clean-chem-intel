#!/usr/bin/env python3
"""Enrichment pass: upgrade data/products.json + data/ingredients.json with
the nuance layer — reproductive impact grades, health-endpoint impact tags,
heritage (passed-down) flags, and 'once safe, now flagged' reclassified notes.

Re-runnable: applies missing ingredients + smooths duplicates, idempotent-ish.
Evidence-aware: grades are worst-case dimensions; 'ev' labels confidence.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent
DATA = REPO / "data"

products = json.loads((DATA / "products.json").read_text(encoding="utf-8"))
ings = json.loads((DATA / "ingredients.json").read_text(encoding="utf-8"))

# ------------------------------------------------------------------
# 1) The 20 ingredients missing from the INGS dict (transparency gap)
# ------------------------------------------------------------------
MISSING = {
  "Ethanolamine": {"g": "H312,H332,H319", "s": "Corrosive amine. Occupational asthma documented in cleaners (meta-analyses).", "ev": "Medium", "gr": {"derm": "C", "resp": "D", "work": "C"}, "impacts": ["resp", "derm"]},
  "Surfactant": {"g": None, "s": "Undisclosed surfactant blend — cannot assess specific hazards.", "ev": "Low", "gr": {}, "impacts": [], "note": "Undisclosed blend; generic placeholder used when the true surfactant is unknown."},
  "Caprylyl/Capryl Glucoside": {"g": None, "s": "Plant-derived glucoside surfactant, biodegradable, mild.", "ev": "Low", "gr": {"derm": "B"}, "impacts": ["derm"]},
  "Dimethicone": {"g": None, "s": "Silicone polymer. Low hazard, persistent in environment.", "ev": "Medium", "gr": {"derm": "A"}, "impacts": ["aqua"], "note": "Not acutely toxic but poorly biodegradable; accumulates."},
  "Butane": {"g": "H220,H280", "s": "Extremely flammable propellant gas. Simple asphyxiant in confined spaces.", "ev": "High", "gr": {"work": "C"}, "impacts": []},
  "Alkyldimethylamine Oxide": {"g": "H315,H318", "s": "Amine oxide surfactant. Skin/eye irritant.", "ev": "Medium", "gr": {"derm": "D"}, "impacts": ["derm"]},
  "Hydrogen Peroxide": {"g": "H314,H318,H412", "s": "Corrosive oxidizer. Severe eye damage, aquatic toxicity.", "ev": "High", "gr": {"derm": "F", "env": "C", "work": "D"}, "impacts": ["aqua", "derm"]},
  "Hydroxypropyl Cyclodextrin": {"g": None, "s": "Modified starch ring that traps odor molecules. Low hazard.", "ev": "Medium", "gr": {"derm": "A"}, "impacts": []},
  "Alcohol": {"g": "H225,H319", "s": "Generic alcohol (usually ethanol or isopropanol). Flammable, eye irritant.", "ev": "Low", "gr": {"derm": "B", "work": "C"}, "impacts": []},
  "Octyl/Decyl Glucoside": {"g": None, "s": "Plant-derived glucoside surfactant, biodegradable, mild.", "ev": "Low", "gr": {"derm": "B"}, "impacts": []},
  "Propane": {"g": "H220,H280", "s": "Extremely flammable propellant gas. Simple asphyxiant in confined spaces.", "ev": "High", "gr": {"work": "C"}, "impacts": []},
  "Propylene Glycol Butyl Ether": {"g": "H302,H315,H319", "s": "Glycol ether solvent. Repro/developmental concern (glycol ether class, EPA/Prop 65 flagged 2-butoxyethanol cousin).", "ev": "Medium", "gr": {"derm": "D", "repro": "C", "work": "C"}, "impacts": ["repro", "derm"], "reclassified": ["Glycol ethers were promoted as 'safe' replacements for banned solvents (1970s–90s); regulation & Prop 65 listings later flagged reproductive/developmental harm in the class."]},
  "Gluconic Acid": {"g": None, "s": "Mild chelating acid. Low hazard.", "ev": "Medium", "gr": {"derm": "B"}, "impacts": []},
  "Sodium Dodecylbenzenesulfonate": {"g": "H302,H315,H318,H412", "s": "Anionic surfactant (linear alkylbenzene sulfonate). Skin/eye irritant, aquatic toxicity.", "ev": "Medium", "gr": {"derm": "D", "env": "C"}, "impacts": ["derm", "aqua"]},
  "Alcohol Ethoxylates": {"g": "H315,H319,H412", "s": "Ethoxylated surfactant family. Skin/eye irritant; 1,4-dioxane contaminant trace concern from ethoxylation.", "ev": "Medium", "gr": {"derm": "C", "env": "C"}, "impacts": ["derm", "aqua"], "reclassified": ["Ethoxylated surfactants (SLES, alcohol ethoxylates) can carry trace 1,4-dioxane — a byproduct EPA flagged as a probable human carcinogen (IARC 2B). Not an added ingredient; a process contaminant."]},
  "Didecyldimonium Chloride": {"g": "H302,H314,H400", "s": "Quaternary ammonium (DDAC). Corrosive, aquatic toxicity, respiratory sensitizer in occupational use.", "ev": "Medium", "gr": {"derm": "F", "resp": "C", "env": "F", "work": "D"}, "impacts": ["resp", "derm", "aqua", "allerg"], "reclassified": ["Quats (quaternary ammonium disinfectants) surged in use mid-20th c. as 'safe' germ killers; occupational studies later linked them to asthma & allergic sensitization."]},
  "Isoparaffin": {"g": "H226,H304", "s": "Petroleum-derived solvent blend. Flammable, aspiration hazard.", "ev": "Medium", "gr": {"resp": "C", "work": "B"}, "impacts": ["resp"]},
  "Phenoxyisopropanol": {"g": "H315,H319", "s": "Glycol ether-like solvent. Skin/eye irritant; glycol ether class repro flags.", "ev": "Low", "gr": {"derm": "C", "repro": "C"}, "impacts": ["repro", "derm"]},
  "Isobutane": {"g": "H220,H280", "s": "Extremely flammable propellant gas. Simple asphyxiant in confined spaces.", "ev": "High", "gr": {"work": "C"}, "impacts": []},
  "Sodium Silicate": {"g": "H314,H335", "s": "Alkaline silicate. Corrosive; dust respiratory irritant.", "ev": "Medium", "gr": {"derm": "D", "resp": "C", "work": "C"}, "impacts": ["resp", "derm"]},
}

# ------------------------------------------------------------------
# 2) Enrich existing ingredients with reproductive grades + impacts
#    (evidence-honest: only where documented, ev labeled accordingly)
# ------------------------------------------------------------------
# fields added: repro grade (gr.repro), impacts[], reclassified[] (once-safe-now-flagged)
ING_EXTRA = {
  "Water": {"impacts": []},
  "Spring Water": {"impacts": []},
  "Isopropanol": {"gr": {"repro": "B"}, "impacts": ["resp", "derm"]},
  "Isopropyl Alcohol": {"gr": {"repro": "B"}, "impacts": ["resp", "derm"]},
  "Ethanol": {"gr": {"repro": "D", "canc": "B"}, "impacts": ["repro"], "reclassified": ["Ethanol was long marketed as a harmless 'natural' solvent; high-exposure studies documented fetal harm (FAS), and occupational exposure is now treated more cautiously."]},
  "Sodium Hypochlorite": {"gr": {"resp": "C"}, "impacts": ["resp", "derm", "aqua"], "reclassified": ["Bleach was the unquestioned household standard for a century; occupational cohorts (cleaning workers, nurses) later linked routine bleach exposure to asthma & COPD risk."]},
  "Sodium Hydroxide": {"gr": {"repro": "B"}, "impacts": ["derm"]},
  "Hydrochloric Acid": {"gr": {"repro": "B"}, "impacts": ["resp", "derm"]},
  "Quaternary Ammonium": {"gr": {"resp": "C", "repro": "C"}, "impacts": ["resp", "derm", "aqua", "allerg"], "reclassified": ["Quats surged as 'safe' germ killers; occupational studies linked them to asthma & allergic sensitization; EPA registration review ongoing."]},
  "Benzalkonium Chloride": {"gr": {"resp": "C", "repro": "C"}, "impacts": ["resp", "derm", "aqua", "allerg"], "reclassified": ["Benzalkonium chloride was a go-to 'mild' disinfectant; animal repro studies + occupational asthma reports led to stricter limits & allergy labeling."]},
  "Sodium Lauryl Sulfate": {"gr": {"repro": "C"}, "impacts": ["derm", "repro"], "reclassified": ["SLS was once marketed as 'safe enough to brush your teeth with'; stripping studies & 1,4-dioxane contamination concerns (from ethoxylation variants) later tempered that."]},
  "Sodium Laureth Sulfate": {"gr": {"repro": "C"}, "impacts": ["derm", "repro"], "reclassified": ["SLES replaced SLS as 'gentler'; ethoxylation introduces trace 1,4-dioxane (IARC 2B probable carcinogen) — a contaminant, not an ingredient."]},
  "Limonene": {"gr": {"repro": "B"}, "impacts": ["resp", "derm", "aqua", "allerg"], "reclassified": ["Citrus limonene was sold as the 'natural' scent; on air exposure it oxidizes into potent sensitizers (limonene hydroperoxides) — now a known contact-allergen source."]},
  "Lauramine Oxide": {"impacts": ["derm"]},
  "Fragrance": {"gr": {"repro": "C", "endo": "D", "canc": "C"}, "impacts": ["allerg", "repro", "endo"], "reclassified": ["'Fragrance' was historically treated as one harmless scent note; undisclosed blends routinely contain phthalates & synthetic musks — endocrine/repro flags (Prop 65 phthalates) and contact allergens."], "note": "Undisclosed blend. Hazards assigned from documented fragrance-carrier chemistry (phthalates, musks), not the specific formula."},
  "Citric Acid": {"impacts": ["derm"]},
  "Oxalic Acid": {"gr": {"repro": "C"}, "impacts": ["derm", "repro"]},
  "Glycolic Acid": {"impacts": ["derm"]},
  "Lactic Acid": {"impacts": []},
  "Sodium Carbonate": {"impacts": ["derm"]},
  "Sodium Bicarbonate": {"impacts": []},
  "Sodium Percarbonate": {"impacts": ["derm", "aqua"]},
  "Calcium Carbonate": {"impacts": []},
  "Feldspar": {"impacts": []},
  "Limestone": {"impacts": []},
  "Castile Soap": {"impacts": []},
  "Tea Tree Oil": {"gr": {"repro": "C"}, "impacts": ["allerg", "resp", "derm"], "reclassified": ["Tea tree oil rode the 'natural = safe' wave; it is a documented contact sensitizer (oxidized forms) and has rare prepubertal gynecomastia case reports (weak endocrine signal)."]},
  "Lavender Oil": {"gr": {"repro": "C", "endo": "C"}, "impacts": ["allerg", "endo"], "reclassified": ["Lavender oil, once 'calming & innocent', has case reports linking topical use to prepubertal gynecomastia (weak, possible endocrine activity); a registered contact allergen."]},
  "Lemon Oil": {"impacts": ["allerg", "derm", "aqua"]},
  "Peppermint Oil": {"impacts": ["allerg", "resp", "derm"]},
  "Eucalyptus Oil": {"impacts": ["allerg", "resp", "derm"]},
  "Decyl Glucoside": {"impacts": []},
  "Lauryl Glucoside": {"impacts": []},
  "Sodium Coco-Sulfate": {"impacts": ["derm"]},
  "Cocamidopropyl Betaine": {"impacts": ["allerg", "derm"], "reclassified": ["CAPB replaced harsher surfactants as 'gentle'; became a common contact allergen (amide impurities) — now on many allergen patch panels."]},
  "Methylisothiazolinone": {"gr": {"resp": "C", "repro": "C", "canc": "B"}, "impacts": ["allerg", "derm", "resp"], "reclassified": ["MIT was the 'safe' preservative replacing parabens; became 2013 'Allergen of the Year' — epidemic of allergic contact dermatitis, now restricted in leave-on products (EU)."]},
  "Benzisothiazolinone": {"gr": {"resp": "C", "repro": "C"}, "impacts": ["allerg", "derm", "aqua"], "reclassified": ["BIT, a cousin of MIT, followed the same arc: marketed safe, became a recognized sensitizer with occupational dermatitis reports."]},
  "Phenoxyethanol": {"gr": {"repro": "C"}, "impacts": ["derm"], "reclassified": ["Phenoxyethanol replaced parabens as 'clean' preservative; repro/developmental flags in animal studies led to EU restrictions in cosmetics (2012)."]},
  "Propylene Glycol": {"gr": {"repro": "B"}, "impacts": ["derm"], "note": "Low acute hazard; mild skin irritant at high concentration."},
  "Butyloxyethanol": {"gr": {"repro": "D", "resp": "C", "work": "C"}, "impacts": ["repro", "resp", "derm"], "reclassified": ["2-Butoxyethanol (EGBE) was once in every window & all-purpose cleaner as a 'safe' solvent; CA Prop 65 lists it for reproductive/developmental harm; EPA risk reviews followed."]},
  "Ammonium Hydroxide": {"gr": {"resp": "C", "repro": "C"}, "impacts": ["resp", "derm"], "reclassified": ["Ammonia was grandma's go-to; strong respiratory irritant, and mixing with bleach produces chloramine gas — a documented household emergency."]},
  "Alcohol Ethoxylate": {"gr": {"repro": "C"}, "impacts": ["derm", "aqua", "repro"], "reclassified": ["Ethoxylated surfactants can carry trace 1,4-dioxane (IARC 2B probable carcinogen) from manufacturing — process contaminant, not on the label."]},
  "Enzymes": {"gr": {"resp": "D", "repro": "B"}, "impacts": ["resp", "allerg"], "reclassified": ["Enzymes were added to laundry products as 'natural' boosters; they are potent respiratory sensitizers — industry adopted encapsulation after occupational asthma outbreaks (1970s)."], "note": "Encapsulated in modern products to reduce aerosolization."},
  "Trichloroisocyanuric Acid": {"impacts": ["derm", "aqua"]},
  "Tetrasodium Glutamate Diacetate": {"impacts": []},
  "Norwex Cloth": {"impacts": []},
  "Pumice Stone": {"impacts": []},
  "Sodium Carbonate Peroxide": {"impacts": ["derm"]},
  "Sodium Citrate": {"impacts": []},
  "Sodium Phytate": {"impacts": []},
  "Myristyl Glucoside": {"impacts": []},
  "Caprylyl Glucoside": {"impacts": []},
  "Coco-Glucoside": {"impacts": []},
  "Potassium Oleate": {"impacts": ["derm"]},
  "Potassium Citrate": {"impacts": []},
  "Glycerin": {"impacts": []},
  "Saponified Coconut Oil": {"impacts": []},
  "Saponified Olive Oil": {"impacts": []},
  "Organic Hemp Oil": {"impacts": []},
  "Organic Peppermint Oil": {"impacts": ["allerg"]},
  "Organic Lavender Oil": {"impacts": ["allerg"]},
  "Rosemary Extract": {"impacts": []},
  "Aloe Vera": {"impacts": []},
  "Botanical surfactant": {"impacts": []},
  "Plant-based surfactants": {"impacts": []},
  "Essential Oils": {"impacts": ["allerg"], "note": "Varies widely by oil; sensitization is the common thread."},
  "Citrus essential oils": {"impacts": ["allerg", "derm"]},
  "Cedar essential oil": {"impacts": ["allerg"]},
  "Pine essential oil": {"impacts": ["allerg", "resp"]},
  "Lavender essential oil": {"impacts": ["allerg", "endo"]},
  "Geranium Oil": {"impacts": ["allerg"]},
  "Oatmeal extract": {"impacts": []},
  "Vitamin E": {"impacts": []},
  "Potassium Hydroxide": {"impacts": ["derm"], "note": "Corrosive in pure form; neutralized in finished products."},
  "Lauric Acid": {"impacts": []},
  "Sodium Chloride": {"impacts": []},
  "Alkaline Silicate": {"impacts": ["derm"]},
  "Alumina": {"impacts": []},
  "Brassica Campestris Seed Oil": {"impacts": []},
  "Helianthus Annuus Seed Oil": {"impacts": []},
  "Potassium Carbonate": {"impacts": ["derm"]},
  "Triethyl Citrate": {"impacts": []},
  "Dipterocarpus Wood Oil": {"impacts": ["allerg"]},
  "Citral": {"impacts": ["allerg", "derm"]},
  "Mandarin Oil": {"impacts": ["allerg"]},
  "Ginger Extract": {"impacts": []},
  "Mint Oil": {"impacts": ["allerg"]},
  "Basil Oil": {"impacts": ["allerg"]},
  "Denatured Alcohol": {"gr": {"repro": "D"}, "impacts": ["repro", "derm"], "reclassified": ["Denatured alcohol is ethanol + bitterants; inherits ethanol's high-exposure repro flags. Often the hidden volatile in 'natural' spray cleaners."]},
  "Citrus Aurantium Peel Oil": {"impacts": ["allerg"]},
}

# ------------------------------------------------------------------
# 3) Heritage layer: passed-down products from grandma's cupboard
# ------------------------------------------------------------------
HERITAGE = {
  "Windex Original": {"year": 1933, "note": "Blue glass cleaner since the 1930s — most families' first window spray. Formula evolved (DBC solvent era → 2-butoxyethanol → modern)."},
  "Clorox Bleach": {"year": 1913, "note": "The original household disinfectant, in cupboards for 100+ years. Effective but carries respiratory + repro flags on routine indoor use."},
  "Lysol All-Purpose": {"year": 1889, "note": "Sold since the 1889 flu era as 'household disinfectant'. Early formulas even contained cresol; generations of sickness-cleaning trust."},
  "Lysol Disinfectant Spray": {"year": 1950, "note": "The aerosol that 'kills 99.9% of germs' — a 1950s icon passed down as the default sick-day spray."},
  "Lysol Toilet Bowl": {"year": 1930, "note": "The acid-based toilet cleaner many inherited without reading the label."},
  "Pine-Sol": {"year": 1929, "note": "Pine-oil cleaner from 1929 — that 'clean pine smell' is a generational memory (and a sensitizer source)."},
  "Formula 409": {"year": 1964, "note": "'The 409' — 1960s all-purpose spray burned into muscle memory for kitchen counters."},
  "Mr. Clean": {"year": 1958, "note": "The bald genie's cleaner, a 1950s staple that defined what 'clean' smelled like."},
  "Fabuloso": {"year": 1980, "note": "Colgate's brightly colored multi-surface cleaner — a 1980s–90s kitchen fixture, passed down by scent loyalty."},
  "Simple Green": {"year": 1975, "note": "The 1970s 'environmentally friendly' pioneer — one of the first green-label cleaners in ordinary homes."},
  "Dawn Ultra": {"year": 1973, "note": "Dawn (1973) — the dish soap that doubles as wildlife-cleanup icon; generations trust it on their greasiest pots."},
  "Palmolive": {"year": 1898, "note": "A brand since 1898 — 'Palmolive' dish liquid is literally a great-grandparent's soap."},
  "Tide": {"year": 1946, "note": "The 1946 laundry breakthrough that became the default 'family detergent' for 80 years."},
  "Ajax Powder": {"year": 1947, "note": "The 1940s scouring powder with the knight — gritty, cheap, and grandma's cabinet standby."},
  "Comet Bathroom": {"year": 1956, "note": "Comet cleanser (1956) — chlorinated scouring powder era, tub rings beware."},
  "Bar Keepers Friend": {"year": 1882, "note": "A stainless-steel polish from 1882 with a cult following that skipped generations entirely via word of mouth."},
  "Bon Ami": {"year": 1886, "note": "'Hasn't scratched yet' since 1886 — the feldspar-based powder that outlived every competitor."},
  "Drano Max Gel": {"year": 1923, "note": "Drano (1923) — the caustic drain unclogger every household inherited, lye and all."},
  "Scrubbing Bubbles": {"year": 1972, "note": "The 1970s bathroom spray that foamed 'up and at 'em' — a shower-scrub icon."},
  "Pledge": {"year": 1958, "note": "Lemon-oil furniture polish (1958) — the 'clean lemon smell' of living rooms for three generations."},
  "Soft Scrub": {"year": 1968, "note": "The 1968 gentle abrasive that replaced powders — 'liquid Comet', passed along as the safe scrubbing option."},
  "Febreze": {"year": 1998, "note": "Younger than the rest, but already inherited: the 'spray the couch' reflex is now a household ritual."},
  "Swiffer WetJet": {"year": 1999, "note": "P&G's mop reinvention — the modern 'clean floor' default already being handed down."},
  "Tilex Mold & Mildew": {"year": 1980, "note": "The bleach-based mold spray that bathrooms across two generations have reached for without gloves."},
}

# ------------------------------------------------------------------
# 4) apply
# ------------------------------------------------------------------
for name, data in MISSING.items():
    ings.setdefault(name, {}).update(data)

for name, extra in ING_EXTRA.items():
    if name not in ings:
        continue
    for k, v in extra.items():
        if k == "gr":
            ings[name].setdefault("gr", {}).update(v)
        elif k == "impacts":
            ings[name]["impacts"] = sorted(set(ings[name].get("impacts", []) + v))
        elif k == "reclassified":
            ings[name]["reclassified"] = v
        elif k == "note":
            ings[name]["note"] = v

# normalize any missing imp fields to [] and gr to {}
for v in ings.values():
    v.setdefault("impacts", [])
    v.setdefault("gr", {})
    v.setdefault("note", None)

# heritage on products
for p in products:
    if p["name"] in HERITAGE:
        h = HERITAGE[p["name"]]
        p["heritage"] = True
        p["heritage_year"] = h["year"]
        p["heritage_note"] = h["note"]
    else:
        p["heritage"] = False

# dates (seed: v1 data existed Aug 18; keep stable, cron will add 'added' for new ones)
for p in products:
    p.setdefault("added", "2026-08-18")
    p.setdefault("updated", "2026-08-18")

(DATA / "ingredients.json").write_text(json.dumps(ings, indent=1, ensure_ascii=False), encoding="utf-8")
(DATA / "products.json").write_text(json.dumps(products, indent=1, ensure_ascii=False), encoding="utf-8")

print(f"ingredients now: {len(ings)}  | products: {len(products)}")
rec = sum(1 for v in ings.values() if v.get("reclassified"))
her = sum(1 for p in products if p.get("heritage"))
print(f"reclassified ingredients: {rec} | heritage products: {her}")
# verify no product references a missing ingredient
all_names = set()
for p in products:
    all_names.update(p["ings"])
missing = sorted(n for n in all_names if n not in ings)
print("still-missing ingredient refs:", missing or "NONE")