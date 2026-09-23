#!/usr/bin/env python3
"""Record the manufacturer side on the five severe-grade products that had none.

Linnea's SPX spectrum build verdict (R1) and the build warning that followed it
both named the same thing: six products carry a severe grade, one (LA's bleach)
carries a claim conflict, and the other five carry nothing on the manufacturer
side. The warning has said since fa5267e: "record the manufacturer's claim, or
record that none was located."

Two states are recorded here, and they are different states:

  claim_conflict  the manufacturer makes a safety claim. Both sides are
                  recorded, quoted, with a resolving source for each.
  claim_review    the manufacturer makes no safety claim that could be located.
                  The absence is recorded as a fact, with the page reviewed and
                  what was found there instead. The absence is not a finding
                  about the product and must not be softened into one.

Run:  python3 tools/apply_claim_reviews.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PRODUCTS = REPO / "data" / "products.json"

# ---------------------------------------------------------------- claim_conflict
CONFLICTS = {
    "Bar Keepers Friend": {
        "ev": "reported",
        "src": "https://barkeepersfriend.com/blogs/bar-keepers-blog/best-way-to-clean-shower-rust",
        "manufacturer_claim": (
            "The manufacturer's own care guide states: \"Bar Keepers Friend is "
            "non-toxic, but to avoid skin irritation, put on rubber gloves before "
            "wiping the area with a wet sponge or cloth.\" A second company post "
            "describes the cleanser as a cleaner's alternative to harsh chemicals: "
            "\"Soap scum and hard water deposits make shower doors look cloudy. You "
            "can use harsh chemicals to remove that film, but you might also damage "
            "your shower door in the process. Bar Keepers Friend Cleanser is a "
            "smarter alternative, it's non-toxic and safe for most surfaces.\""
        ),
        "manufacturer_src": "https://barkeepersfriend.com/blogs/bar-keepers-blog/best-way-to-clean-shower-rust",
        "toxicology_finding": (
            "The disclosed ingredient set includes feldspar, graded D on the organ "
            "and respiratory dimensions (GHS H373: may cause damage to organs "
            "through prolonged or repeated exposure; the respirable crystalline "
            "silica concern; High evidence), and oxalic acid, graded D on the "
            "dermal and organ dimensions (H302, H312: harmful if swallowed or in "
            "contact with skin; High evidence). Both carry their own evidence "
            "levels in ingredients.json."
        ),
        "toxicology_src": "https://pubchem.ncbi.nlm.nih.gov/compound/3080680",
        "note": (
            "Recorded as a tension, not as a verdict. \"Non-toxic\" is a safety "
            "assertion about a formula whose own hazard record carries organ and "
            "dermal effects, and the same page advises gloves, which is the "
            "manufacturer naming a dermal route in its own instructions. Both pages "
            "were reached by direct fetch of the manufacturer's site."
        ),
    },
    "Cascade": {
        "ev": "reported",
        "src": "https://directionsforme.org/product/54693",
        "manufacturer_claim": (
            "The manufacturer's own pack copy for the Cascade Free & Clear line "
            "reads: \"No phosphates. No chlorine bleach. Safe for septic tanks.\" "
            "and \"Cascade believes in the safety and quality of our products. Visit "
            "Cascadeclean.com to learn more about what goes into our products and "
            "why we make those choices.\""
        ),
        "manufacturer_src": "https://directionsforme.org/product/54693",
        "toxicology_finding": (
            "The brand's disclosed ingredient set across its dishwasher line "
            "includes sodium percarbonate, graded D on the dermal dimension (GHS "
            "H272, H302, H318: oxidizer, harmful if swallowed, causes serious eye "
            "damage; High evidence), and sodium silicate, graded D on dermal (H314, "
            "H335: causes severe skin burns and eye damage, may cause respiratory "
            "irritation; Medium evidence). P&G's own SmartLabel disclosure for "
            "Cascade Complete ActionPacs lists both substances."
        ),
        "toxicology_src": "https://smartlabel.pg.com/00037000982081.html",
        "note": (
            "Recorded as a tension, not as a verdict. \"No phosphates\" and \"safe "
            "for septic tanks\" are environmental and plumbing claims, not "
            "toxicological findings about the people using the product; the same "
            "pack carries \"Caution: Irritant. Harmful if swallowed or put in "
            "mouth.\" Our entry is brand-level, so the claim quoted is the brand's "
            "own line copy rather than one SKU's. The pack wording was reached "
            "through a label mirror, not by fetching the physical pack."
        ),
    },
    "Finish": {
        "ev": "reported",
        "src": "https://www.finishdishwashing.com/products/detergents/quantum-detergent/84/",
        "manufacturer_claim": (
            "The manufacturer's product page for its leading detergent states: "
            "\"FINISH QUANTUM\u00ae is safe for septic systems.\" The same page's "
            "benefit list reads \"Care & protect For your glasses, dishes & "
            "machines,\" and its FAQ describes the tablets as containing \"safe "
            "bleaches\": \"They also include enzymes (to break down starchy foods "
            "and protein), builders (to tackle hard water) and safe bleaches.\""
        ),
        "manufacturer_src": "https://www.finishdishwashing.com/products/detergents/quantum-detergent/84/",
        "toxicology_finding": (
            "The brand's disclosed ingredient set across its dishwasher line "
            "includes sodium percarbonate, graded D on the dermal dimension (GHS "
            "H272, H302, H318; High evidence), and sodium silicate, graded D on "
            "dermal (H314, H335; Medium evidence). Reckitt's own SmartLabel for the "
            "Finish dishwasher cleaner line carries \"CAUTION: MAY IRRITATE EYES\" "
            "and a poison-control first-aid instruction."
        ),
        "toxicology_src": "https://www.rbnainfo.com/smart-label.php?productLineId=2294",
        "note": (
            "Recorded as a tension, not as a verdict. \"Safe for septic systems\" "
            "is a plumbing and environmental claim, and \"safe bleaches\" is a "
            "reassurance attached to an oxidizer whose own GHS classification "
            "includes serious eye damage. Our entry is brand-level, so the claim is "
            "quoted from the brand's leading detergent SKU page rather than a "
            "SKU-matched page."
        ),
    },
    "20 Mule Team Borax (BMVC)": {
        "ev": "reported",
        "src": "https://www.20muleteamlaundry.com/safety-information.html",
        "manufacturer_claim": (
            "The manufacturer's safety page asks \"How safe is 20 MULE TEAM\u00ae "
            "Borax?\" and answers: \"20 MULE TEAM\u00ae Borax has been used safely "
            "by hundreds of people for over 127 years! While no one can say their "
            "product is 100% safe in all circumstances (even table salt can be "
            "deadly if you ingest too much), Borax is safe when used as "
            "directed.\" The same page states \"Borax is a 100% all-natural mineral "
            "that we mine, refine and package for your use,\" and the brand's home "
            "page adds \"The only ingredient in Borax is a naturally occuring "
            "mineral called sodium tetraborate. It's free of phosphates, chlorine "
            "and other chemicals.\""
        ),
        "manufacturer_src": "https://www.20muleteamlaundry.com/safety-information.html",
        "toxicology_finding": (
            "Sodium tetraborate is graded F on the reproductive dimension: "
            "EU/CLP-classified reproductive toxicant 1B (H360FD, may damage "
            "fertility or the unborn child; High evidence). The manufacturer's own "
            "SDS lists \"Suspected of damaging fertility or the unborn child\" in "
            "its hazard statements while also stating \"This product is a laundry "
            "care product. The use of this product by consumers is safe under "
            "normal and reasonable foreseen use.\""
        ),
        "toxicology_src": "https://assets.unilogcorp.com/267/ITEM/DOC/20MULETEAMBORAXtrade_DIA00201_1.pdf",
        "note": (
            "Recorded as a tension, not as a verdict. \"Safe when used as directed\" "
            "and \"all-natural\" stand opposite a 1B reproductive classification "
            "that the same company's SDS repeats on this product. \"Natural\" "
            "describes where the substance came from, not what it does, and the "
            "manufacturer's own \"no one can say their product is 100% safe\" is the "
            "claim conceding its own limit. The SDS was reached through a "
            "distributor's document mirror of the sheet naming Henkel Corporation "
            "as manufacturer, not from a Henkel-hosted URL."
        ),
    },
}

# ------------------------------------------------------------------ claim_review
REVIEWS = {
    "Organic Essential Oils Kit (BMVC)": {
        "ev": "reported",
        "src": "https://www.nowfoods.com/products/essential-oils/lemon-oil",
        "result": "no_safety_claim_located",
        "note": (
            "Reviewed 2026-09-23: this kit as sold, and the constituent brand's own "
            "product pages. No manufacturer safety claim was located. What the "
            "brand's page publishes instead is a purity claim and a caution, and "
            "they are not the same kind of statement: \"NOW\u00ae Essential Oils "
            "are analytically tested for identity, purity and adulteration to "
            "assure the highest quality\" is a quality claim, while the label "
            "caution reads \"Keep out of reach of children. Avoid contact with "
            "eyes. If pregnant or lactating, consult your healthcare practitioner "
            "before using. Do not use on skin\" and \"Natural essential oils are "
            "highly concentrated and should be used with care.\" The caution "
            "direction agrees with the hazard record rather than opposing it, which "
            "is why there is no tension to show here. The absence of a safety claim "
            "is recorded as an absence, not as reassurance about the product."
        ),
    },
}


def main():
    products = json.loads(PRODUCTS.read_text())
    by_name = {p.get("name"): p for p in products}
    written = []

    for name, block in CONFLICTS.items():
        p = by_name.get(name)
        if p is None:
            print(f"  missing product: {name}")
            continue
        p["claim_conflict"] = block
        p["updated"] = "2026-09-23"
        written.append(f"conflict: {name}")

    for name, block in REVIEWS.items():
        p = by_name.get(name)
        if p is None:
            print(f"  missing product: {name}")
            continue
        p["claim_review"] = block
        p["updated"] = "2026-09-23"
        written.append(f"review:   {name}")

    # Match the file's existing shape exactly (indent=1, no trailing newline) so
    # the diff is the five records and not a reformat of the whole catalog.
    PRODUCTS.write_text(json.dumps(products, indent=1, ensure_ascii=False))
    for line in written:
        print(line)
    print(f"{len(written)} product records updated")


if __name__ == "__main__":
    main()
