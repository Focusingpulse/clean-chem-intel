#!/usr/bin/env python3
"""Sifter lane grow run 2026-10-11.
Adds 4 products from manufacturer disclosures (Church & Dwight SB-258, Reckitt rbnainfo,
Seventh Generation page+SDS, P&G SmartLabel), mints 15 ingredient profiles, merges 4
word-order duplicate key pairs onto graded/canonical keys. Never invents grades.
"""
import json

D = "data/"
prods = json.load(open(D + "products.json"))
ings = json.load(open(D + "ingredients.json"))

def rec(ev, g, gr, impacts, note, s, **kw):
    d = {"ev": ev, "g": g, "gr": gr, "impacts": impacts, "note": note, "s": s}
    d.update(kw)
    return dict(sorted(d.items()))

# ---------- 1. New ingredient profiles ----------
NEW = {
 "Alkyl Imino Dipropionic Acid, Monosodium Salt": rec(
   ev="Low", g=None, gr={}, impacts=[],
   note="Named on the Church & Dwight California SB-258 disclosure for OxiClean MaxForce (CAS 64972-18-5). PubChem resolves the CAS to CID 23695304, but the record carries no GHS classification section, so no consensus basis exists. Left ungraded rather than extrapolated from the amphoteric-surfactant class.",
   s="Amphoteric iminodipropionate surfactant (CAS 64972-18-5). Not yet graded against GHS."),
 "Sandalore": rec(
   ev="High", g="H411", gr={"env": "D"}, impacts=["aqua"],
   note="ECHA C&L consensus via PubChem CID 103212: H411 at 95.5% of notifiers. H319 (18.3%) sits below the 40% grading bar and is not graded. Named on the Church & Dwight SB-258 disclosure for OxiClean MaxForce (CAS 65113-99-7).",
   s="Synthetic sandalwood fragrance (CAS 65113-99-7). Toxic to aquatic life with long lasting effects."),
 "Tetrasodium Etidronate": rec(
   ev="High", g="H302,H319", gr={"derm": "C"}, impacts=["derm"],
   note="ECHA C&L consensus via PubChem CID 19629: H302 83.6%, H319 86.6%. Named on the Reckitt SB-258 disclosure for Finish Quantum Lemon (CAS 3794-83-0).",
   s="Phosphonate chelant (HEDP tetrasodium salt, CAS 3794-83-0). Eye irritant; harmful if swallowed."),
 "Polyacrylic Acid, Sodium Bisulfite Terminated": rec(
   ev="Low", g=None, gr={}, impacts=[],
   note="Named on the Reckitt SB-258 disclosure for Finish Quantum Lemon (CAS 68479-09-4). Polymer, not a discrete substance; PubChem PUG REST returns no CID for name or CAS. Unclassified by policy; not graded rather than extrapolated.",
   s="Antiredeposition polymer (CAS 68479-09-4). Not yet graded against GHS."),
 "Alcohol Polyglycolether": rec(
   ev="Low", g=None, gr={}, impacts=[],
   note="Named on the Reckitt SB-258 disclosure for Finish Quantum Lemon (CAS 501019-91-6). PubChem PUG REST returns no CID for name or CAS. Unclassified by policy; not graded rather than extrapolated.",
   s="Nonionic polyglycol ether surfactant (CAS 501019-91-6). Not yet graded against GHS."),
 "Manganese Catalyst": rec(
   ev="Low", g=None, gr={}, impacts=[],
   note="Bleach catalyst named on the Reckitt SB-258 disclosure for Finish Quantum Lemon (CAS 116633-52-4), where it is carried on the CA TACs, CA Non-Cancer Hazards and NY Air Toxics designated lists as a manganese compound. PubChem resolves the CAS to CID 138319435 but the record has no GHS classification section, so there is no consensus basis to grade. Placeholder profile; grades never guessed.",
   s="Manganese-based bleach activator catalyst (CAS 116633-52-4). Not yet graded against GHS."),
 "Polymeric Red Colorant": rec(
   ev="Low", g=None, gr={}, impacts=[],
   note="Named on the Reckitt SB-258 disclosure for Finish Quantum Lemon with CAS given only as 'Proprietary'. Undisclosed composition: placeholder profile, never graded.",
   s="Proprietary polymeric red colorant (CAS withheld by manufacturer)."),
 "Talc": rec(
   ev="Medium", g="Not Classified", gr={}, impacts=[],
   note="Non-functional constituent on the Reckitt SB-258 disclosure for Finish Quantum Lemon, recorded there as containing no asbestiform fibres (CAS 14807-96-6). ECHA C&L via PubChem CID 165411828: reported as not meeting GHS hazard criteria by 4523 of 4758 notifiers (95.1%); H370/H372 carried only by a small minority, below the grading bar. The disclosure's designated-list flag traces to IARC, which classified talc Group 2A (probably carcinogenic) in 2024 on route-specific evidence -- a non-GHS finding, recorded here rather than invented as a grade.",
   s="Magnesium silicate mineral (CAS 14807-96-6). Not GHS-classified by 95.1% of ECHA notifiers."),
 "Thymol": rec(
   ev="High", g="H302,H314,H411", gr={"derm": "F", "env": "D"}, impacts=["derm", "aqua"],
   note="ECHA C&L consensus via PubChem CID 6989: H302 >99.9%, H314 99.4%, H411 99.5%; H318 (10.5%) below the bar. derm F on the H314 corrosive consensus per the 2026-09-26 H314 precedent. This is the pure-substance grade: the Seventh Generation disinfecting cleaner that carries it discloses the active at 0.05%, recorded as conc on the product. EPA-registered antimicrobial active.",
   s="Thyme-oil phenolic antiseptic (CAS 89-83-8); the active in botanical disinfectants. Corrosive as the pure substance; toxic to aquatic life with long lasting effects."),
 "Copper Sulfate Pentahydrate": rec(
   ev="High", g="H302,H315,H319,H400,H410", gr={"derm": "C", "env": "F"}, impacts=["derm", "aqua"],
   note="The pentahydrate's own C&L notification base (PubChem CID 24463) is sparse and internally mixed; the anhydrous salt (CID 24462) carries the strong aggregate (H302 96.3%, H315 79.3%) and the same copper(II) ion in solution drives the hazard, so the grade rests on the combined consensus: derm C (H315/H319), env F (H400/H410). Seventh Generation discloses it as the bluestone water mineralizer in its disinfecting cleaner (<0.1%).",
   s="Copper(II) salt (CAS 7758-99-8). Skin and eye irritant; very toxic to aquatic life."),
 "Citronella Oil": rec(
   ev="Low", g=None, gr={}, impacts=[],
   note="Named as a fragrance component of Seventh Generation Disinfecting Multi-Surface Cleaner (Cymbopogon nardus, CAS 8000-29-1). UVCB essential oil; no discrete PubChem CID to grade against. Its named allergens (citral, geraniol) are carried on their own graded keys. Unclassified by policy.",
   s="Essential oil from Cymbopogon nardus (CAS 8000-29-1). UVCB; not yet graded against GHS."),
 "Lemongrass Oil": rec(
   ev="Low", g=None, gr={}, impacts=[],
   note="Named as a fragrance component of Seventh Generation Disinfecting Multi-Surface Cleaner (Cymbopogon schoenanthus, CAS 8007-02-1). UVCB essential oil; no discrete PubChem CID to grade against. Its named allergens (citral, geraniol) are carried on their own graded keys. Unclassified by policy.",
   s="Essential oil from Cymbopogon schoenanthus (CAS 8007-02-1). UVCB; not yet graded against GHS."),
 "PPG-26-Buteth-26": rec(
   ev="Low", g=None, gr={}, impacts=[],
   note="Named on the P&G SmartLabel disclosure for Swiffer Sweeper Wet cloths (polyoxypropylene/polyoxyethylene butyl ether, generic CAS 9038-95-3 class). Polymer family; PubChem PUG REST returns no CID for the name. Unclassified by policy.",
   s="Polymeric PPG/PEG butyl ether surfactant. Not yet graded against GHS."),
 "PEG Hydrogenated Castor Oil": rec(
   ev="Low", g=None, gr={}, impacts=[],
   note="Named on the P&G SmartLabel disclosure for Swiffer Sweeper Wet cloths with no ethoxylation number given (ethoxylated hydrogenated castor oil, CAS 61788-85-0 class). The DB already carries the specific PEG-40 Castor Oil and PEG-60 Hydrogenated Castor Oil keys; this key keeps the label's generic spelling rather than guessing a chain length. Polymer family, unclassified by policy.",
   s="Ethoxylated hydrogenated castor oil, chain length unspecified on the label. Not yet graded against GHS."),
 "Polypropylene-Polyester-Cellulose Sheet": rec(
   ev="Low", g="Not Classified", gr={}, impacts=[],
   note="Wet-wipe substrate (polypropylene/polyester/cellulose nonwoven) named first on the P&G SmartLabel disclosure for Swiffer Sweeper Wet cloths. Physical article, not a chemical; no hazard grading applicable. Polyester Sheet and Norwex Cloth precedent.",
   s="Physical article, not a chemical"),
}
for k, v in NEW.items():
    assert k not in ings, f"already exists: {k}"
    ings[k] = v

# ---------- 2. Alias notes on reused records ----------
ings["Modified Acrylic Polymer"]["note"] += " The Church & Dwight SB-258 disclosure for OxiClean MaxForce names 'modified acrylic copolymer' (CAS 52255-49-9), the same dispersing-polymer class; that product references this key rather than minting a second near-identical polymer key."
ings["Polyethylene-polypropylene glycol"]["note"] = (ings["Polyethylene-polypropylene glycol"].get("note") or "") + " Reckitt's SB-258 disclosure for Finish Quantum Lemon names 'Ethylene/Propylene Oxide Copolymer' (CAS 58205-99-5), the same EO/PO copolymer class; that product references this key rather than minting a class duplicate."

# ---------- 3. Key merges (word-order/synonym duplicates onto graded/canonical keys) ----------
MERGES = [
 ("2,6-Dimethyl-7-octen-2-ol", "Dihydromyrcenol",
  "Key merge 2026-10-11 (Sifter lane): '2,6-Dimethyl-7-octen-2-ol' (ungraded Low, 3 product refs) merged onto this key -- the two names are the same substance (CAS 18479-58-8; this record's own summary gives both names), keyed differently by different disclosures."),
 ("Alcohols, C12-15, Ethoxylated", "C12-15 Alcohols Ethoxylated",
  "Key merge 2026-10-11 (Sifter lane): 'Alcohols, C12-15, Ethoxylated' (ungraded Low, 3 product refs) merged onto this key -- same UVCB class (CAS 68131-39-5), word-order duplicate of the kind the validator comment describes."),
 ("Protease", "Protease Enzyme",
  "Key merge 2026-10-11 (Sifter lane): 'Protease' (ungraded Low, 5 product refs) merged onto this key -- same generic detergent-protease class at the same specificity; 'Subtilisin' stays separate as the CAS-specific (9014-01-1) High-evidence key."),
 ("Amylase", "Amylase Enzyme",
  "Key merge 2026-10-11 (Sifter lane): 'Amylase' (ungraded Low, 7 product refs) merged onto this key -- same generic detergent-amylase class (CAS 9000-90-2), keyed by label spelling on the 2026-09-28 gather pass."),
]
for old, new, note in MERGES:
    assert old in ings and new in ings, (old, new)
    n = 0
    for p in prods:
        if old in p["ings"]:
            p["ings"] = [new if i == old else i for i in p["ings"]]
            n += 1
    ings[new]["note"] = (ings[new].get("note") or "") + " " + note
    del ings[old]
    print(f"merged {old} -> {new} ({n} refs)")

# ---------- 4. New products ----------
TODAY = "2026-10-11"
def prod(**kw):
    base = {
     "name": None, "brand": None, "cat": None, "safe": None, "grade_note": None,
     "ings": [], "heritage": False, "added": TODAY, "updated": TODAY,
     "source": None, "source_url": None, "note": None,
     "owner": None, "owner_ev": None, "owner_src": None,
     "tier": "mass", "tier_ev": "reported", "tier_src": None,
     "substitutes": [],
     "exposure": None, "exposure_ev": "untested", "exposure_src": None,
     "conc": None, "conc_src": None, "conc_ev": "untested",
     "grade_as_sold": None, "grade_as_sold_src": None,
     "strength_disclosure": "not disclosed", "exposure_basis": None,
    }
    base.update(kw)
    return base

GAP = ("Searched for a published per-product US household-penetration figure in the open sources "
       "this database uses (IndexBox category pages, market summaries). Located no citable "
       "household-base figure; the reports that exist give channel share of category value, which "
       "is not a share of households and is not a substitute for one. Left as a research gap "
       "rather than estimated.")

NEW_PRODUCTS = [
 prod(
  name="OxiClean MaxForce Laundry Stain Remover Spray",
  brand="OxiClean", cat="Stain & Odor",
  grade_note="Sifter grade F — worst credible dimension: derm F (methylisothiazolinone H314 corrosive; High evidence). Sodium tetraborate (borax) repro F is a second independent F driver.",
  ings=["Water", "Alcohols, C10-16, Ethoxylated", "Propylene Glycol", "Sodium Tetraborate",
        "Citric Acid", "Alkyl Imino Dipropionic Acid, Monosodium Salt", "Modified Acrylic Polymer",
        "Sodium Hydroxide", "Fragrance", "Subtilisin", "Amylase Enzyme", "Mannanase Enzyme",
        "Benzisothiazolinone", "Methylisothiazolinone", "Calcium Chloride",
        "Dihydromyrcenol", "2-Methoxynaphthalene", "Butylphenyl Methylpropional", "Verdyl Acetate",
        "Sandalore", "Dipropylene Glycol", "Galaxolide", "Terpineol Acetate"],
  source=("Church & Dwight's own California SB-258 ingredient disclosure form for OxiClean MaxForce Laundry Stain Remover "
          "(material number 40500533), read 2026-10-11, listing every intentionally added ingredient with CAS and function: "
          "Water (7732-18-5), C10-16 alketh surfactant (68131-39-5 or 68002-97-1 or 68551-12-2), propylene glycol (57-55-6), "
          "sodium borate (12179-04-3, flagged EU CMR on the form), citric acid (77-92-9), alkyl imino dipropionic acid "
          "monosodium salt (64972-18-5), modified acrylic copolymer (52255-49-9), sodium hydroxide (1310-73-2), fragrances, "
          "protease (9014-01-1), amylase (9000-90-2), mannanase (37288-54-3), benzisothiazolinone (2634-33-5), "
          "methylisothiazolinone (2682-20-4) and calcium chloride (10035-04-8); plus fragrance components at >=100 ppm or on "
          "a designated list: 2,6-dimethyl-7-octen-2-ol (18479-58-8, i.e. dihydromyrcenol), 2-methoxynaphthalene (93-04-9), "
          "butylphenyl methylpropional (80-54-6), verdyl acetate (5413-60-5), sandalore (65113-99-7), dipropylene glycol "
          "(25265-71-8), hexamethylindanopyran (1222-05-5, i.e. galaxolide) and terpineol acetate (8007-35-0). "
          "Cross-checked against the manufacturer SDS: alcohol ethoxylate 10-30%, propylene glycol 1-5%, sodium tetraborate "
          "decahydrate 0.1-1%, enzymes 0.1-1% each."),
  source_url="https://churchdwight.com/ingredient-disclosure/laundry-fabric-care/40500533-oxiclean-maxforce-laundry-stain-remover.aspx",
  note=("A three-enzyme pre-treat spray (protease + amylase + mannanase, with borax, propylene glycol and calcium chloride as "
        "the enzyme-stabilizer system) behind a C10-16 alcohol ethoxylate surfactant at 10-30% -- the '5 in 1' stain-fighter "
        "positioning. Two preservatives (BIT and MI) close it out. The disclosure is unusually complete for the tier: eight "
        "fragrance components named with CAS numbers, among them butylphenyl methylpropional (Lilial), which the form itself "
        "flags as EU CMR -- it has been prohibited in EU cosmetics since 2022 but remains legal in US laundry products. "
        "Distinct from the corpus's OxiClean Versatile powder (a percarbonate soaker) and from the Shout gel. The disclosure "
        "says 'sodium borate' with CAS 12179-04-3 (the pentahydrate); the SDS names sodium tetraborate decahydrate, so the "
        "product references the graded Sodium Tetraborate (borax) key."),
  owner="Church & Dwight", owner_ev="verified", owner_src="https://churchdwight.com/our-brands/",
  tier_src="https://www.oxiclean.com/en/products/stain-fighters/oxiclean-max-force-spray",
  strength_disclosure="partial",
  exposure_basis=GAP + " A mass-channel laundry pre-treat spray."),
 prod(
  name="Finish Quantum Dishwasher Detergent Pacs, Lemon",
  brand="Finish", cat="Dishwasher",
  grade_note=("Sifter grade D — worst credible dimension: resp D (subtilisin protease enzyme H334 respiratory sensitizer; "
              "High evidence). The proprietary red colorant and the manganese bleach catalyst are undisclosed/ungraded and "
              "limit confidence; they do not drive the grade."),
  ings=["Sodium Carbonate", "Sodium Citrate", "C12-14 Alcohols Ethoxylated Propoxylated", "Sodium Percarbonate",
        "Polyethylene-polypropylene glycol", "TAED", "Polyvinyl Alcohol", "Sodium Polyacrylate",
        "Polyacrylic Acid, Sodium Bisulfite Terminated", "Alcohol Polyglycolether", "Tetrasodium Etidronate",
        "Propylene Glycol", "Fragrance", "Subtilisin", "Amylase Enzyme", "Manganese Catalyst",
        "Acid Yellow 23", "Polymeric Red Colorant", "Sodium Sulfate", "Talc"],
  source=("Reckitt's own SB-258 ingredient disclosure portal (rbnainfo.com) for FINISH Quantum Lemon (product line 3644, "
          "UPC 0-51700-99535-6, country of sale USA), read 2026-10-11, listed in descending weight percent: sodium carbonate "
          "(497-19-8), sodium citrate (68-04-2), C10-16 alcohols ethoxylated propoxylated, disclosed as C12-14 alcohols "
          "ethoxylated propoxylated (68551-13-3 or 120313-48-6 or 68439-51-0), sodium percarbonate (15630-89-4), "
          "ethylene/propylene oxide copolymer (58205-99-5), TAED bleach activator (10543-57-4), polyvinyl alcohol film "
          "(25213-24-5), sodium polyacrylate (9003-04-7), polyacrylic acid sodium bisulfite terminated (68479-09-4), "
          "alcohol polyglycolether (501019-91-6), tetrasodium etidronate (3794-83-0), propylene glycol (57-55-6), "
          "fragrance, protease enzyme (9014-01-1), amylase enzyme (9000-90-2), manganese bleach catalyst (116633-52-4), "
          "Acid Yellow 23 colorant (1934-21-0), a polymeric red colorant (CAS proprietary), and non-functional constituents "
          "sodium sulfate (7757-82-6) and talc (14807-96-6, recorded as containing no asbestiform fibres)."),
  source_url="https://www.rbnainfo.com/product.php?productLineId=3644",
  note=("The premium Finish pac, and the corpus's first entry carrying a manganese bleach catalyst (the MnTACN-class "
        "activator that makes percarbonate bleach work at lower wash temperatures) -- Reckitt discloses it by CAS with "
        "designated-list flags (CA TACs, CA Non-Cancer Hazards, NY Air Toxics, all manganese-compound listings), but no GHS "
        "consensus exists anywhere to grade it, so it sits as an honest placeholder. The formula otherwise reads like a "
        "conventional premium pac: carbonate/citrate alkalinity, percarbonate + TAED oxygen bleach, three antiredeposition "
        "polymers, HEDP chelant, two enzymes. Talc and sodium sulfate are disclosed as non-functional constituents (the "
        "talc's IARC flag is route-specific and recorded on the ingredient, not graded). Distinct product from the corpus's "
        "base 'Finish' entry and from Jet-Dry."),
  owner="Reckitt", owner_ev="reported", owner_src="https://www.reckitt.com/our-brands/",
  tier_src="https://www.finishdishwashing.com/",
  strength_disclosure="partial",
  exposure_basis=GAP + " A mass-channel dishwasher detergent pac."),
 prod(
  name="Seventh Generation Disinfecting Multi-Surface Cleaner, Lemongrass Citrus",
  brand="Seventh Generation", cat="Disinfectant",
  grade_note=("Sifter grade F — worst credible dimension: derm F (thymol H314 corrosive as the pure substance; High "
              "evidence). The active is disclosed at 0.05% (conc on record); no as-sold grade derived -- the two-trace rule "
              "(decisions 2026-09-23) requires an authority concentration-to-hazard mapping, which does not exist for thymol."),
  ings=["Thymol", "Water", "Sodium Lauryl Sulfate", "Citric Acid", "Sodium Citrate",
        "Copper Sulfate Pentahydrate", "Citronella Oil", "Lemongrass Oil", "Citral", "Geraniol"],
  source=("Seventh Generation's own product page and SDS (revision 2019-02-11) for Disinfecting Multi-Surface Cleaner, "
          "Lemongrass Citrus, read 2026-10-11: thymol antimicrobial active 0.05% (89-83-8), water (7732-18-5), sodium lauryl "
          "sulfate (68585-47-7, <1%), citric acid (77-92-9), sodium citrate (6132-04-3), copper sulfate pentahydrate "
          "(7758-99-8, <0.1%), essential-oil fragrance of cymbopogon nardus (citronella) oil and cymbopogon schoenanthus "
          "(lemongrass) oil (<0.1%), with citral and geraniol named by the manufacturer as fragrance allergens. "
          "EPA-registered disinfectant."),
  source_url="https://www.seventhgeneration.com/disinfecting-multi-surface-cleaner",
  note=("The corpus's first botanical disinfectant: the active is thymol (thyme-oil phenolic) at a stated 0.05%, one of the "
        "minimum-risk actives EPA registers for disinfection, carried in a citric-acid/SLS base with copper sulfate "
        "pentahydrate as a mineralizer. It is also the cleanest test of the two-level grading doctrine in the corpus: the "
        "thymol ingredient entry is corrosive-grade on the pure substance (H314 at 99.4% consensus), while the product as "
        "sold is 99.95% other ingredients -- the concentration is recorded (conc), but per Sandra's two-trace rule no "
        "as-sold grade is derived without an authority mapping. No quats, no bleach, no MI/BIT preservatives."),
  owner="Unilever", owner_ev="reported",
  owner_src="https://www.whobrands.com/blog/20-cleaning-product-brands-owned-by-3-companies",
  tier_src="https://www.seventhgeneration.com/",
  strength_disclosure="full",
  conc="Thymol 0.05% (antimicrobial active); all other ingredients <1% except water",
  conc_src="https://www.seventhgeneration.com/sites/default/files/2020-01/sds-fm000054-00-4-disinfecting-multi-surface-cleaner-en-2019-02-11.pdf",
  conc_ev="verified",
  exposure_basis=GAP + " A mass-channel botanical disinfectant spray."),
 prod(
  name="Swiffer Sweeper Wet Mopping Cloth Refills, Lavender",
  brand="Swiffer", cat="Floor & Carpet",
  grade_note=("Sifter grade F — worst credible dimension: derm F (methylchloroisothiazolinone/methylisothiazolinone "
              "preservative pair, H314 corrosive; High evidence)."),
  ings=["Polypropylene-Polyester-Cellulose Sheet", "Water", "Propylene Glycol Butyl Ether", "Fragrance",
        "Phenoxyisopropanol", "Dipropylene Glycol Butyl Ether", "Alkyldimethylamine Oxide", "PPG-26-Buteth-26",
        "PEG Hydrogenated Castor Oil", "Acrylic Polymer", "Methylchloroisothiazolinone", "Methylisothiazolinone"],
  source=("P&G's SmartLabel disclosure for Swiffer Sweeper Wet Mopping Cloth Refills with Febreze freshness, Lavender scent "
          "(UPC 0-30772-14227-1, information last updated 2024-07-09 by Swiffer), read 2026-10-11: polypropylene/polyester/"
          "cellulose substrate, water, propylene glycol butyl ether, fragrances, phenoxyisopropanol, dipropylene glycol "
          "butyl ether, C10-16 alkyldimethylamine oxide, PPG-26-buteth-26, PEG hydrogenated castor oil, acrylic polymer, "
          "methylchloroisothiazolinone/methylisothiazolinone."),
  source_url="https://smartlabel.pg.com/en-ca/00030772142271.html",
  note=("The refill companion to the corpus's Swiffer WetJet entry -- same product family, different delivery: a presoaked "
        "disposable cloth instead of a sprayed solution. The chemistry is a light glycol-ether/amine-oxide cleaning "
        "solution on a nonwoven substrate, preserved with the CMIT/MIT isothiazolinone pair that also drives the grade on "
        "several wipe products here. SmartLabel lists the substrate itself as the first ingredient, so it is recorded as a "
        "physical-article key (Polyester Sheet precedent). P&G discloses no CAS numbers on this entry; the generic 'PEG "
        "hydrogenated castor oil' keeps the label spelling rather than guessing a chain length."),
  owner="Procter & Gamble", owner_ev="verified", owner_src="https://us.pg.com/brands/",
  tier_src="https://swiffer.com/",
  exposure_basis=GAP + " A mass-channel presoaked mopping cloth."),
]

existing = {(p["name"].lower(), p["brand"].lower()) for p in prods}
for p in NEW_PRODUCTS:
    assert (p["name"].lower(), p["brand"].lower()) not in existing, p["name"]
    for i in p["ings"]:
        assert i in ings, f"{p['name']}: unknown ingredient {i}"
    prods.append(p)
    print("added:", p["name"])

json.dump(prods, open(D + "products.json", "w"), indent=1, ensure_ascii=False)
json.dump(ings, open(D + "ingredients.json", "w"), indent=1, ensure_ascii=False)
print(f"totals: {len(prods)} products, {len(ings)} ingredients")
