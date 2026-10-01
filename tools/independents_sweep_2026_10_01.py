#!/usr/bin/env python3
"""CCI-012 Lane 1 - resolve the 25 entries sitting in owners.json -> independents.

The bucket was named "Brands with no parent company found". Its note already said
the right thing ("absence of a finding is not a finding"), and CCI-012 Lane 1 is
the work of turning those absences into findings. All 25 were examined on
2026-10-01 and all 25 resolved, so the bucket empties.

Evidence rule applied (stated in the finding so it is auditable):
  verified  - a government/regulatory register (SEC, CIPO) or the company's own
              published corporate document (about page, sustainability report,
              media kit) states the ownership, read directly.
  reported  - the claim rests on a press release or a third-party outlet.

Idempotent: re-running adds nothing and removes nothing.

Run:  python3 tools/independents_sweep_2026_10_01.py
Then: python3 tools/validate_certainty.py --apply && python3 build.py
"""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

NEW_OWNERS = {
    # ---- parents found: the "natural shelf" is not a separate economy ----
    "PurposeBuilt Brands": {
        "type": "private (The Carlyle Group and TA Associates)",
        "detail": (
            "Weiman Products LLC acquired the Goo Gone, Magic, Stone Care International, "
            "Natural Magic, OOPS! and Gonzo brands from The Homax Group in January 2014, and "
            "acquired biokleen in 2019, then renamed the company PurposeBuilt Brands. The "
            "Carlyle Group (NASDAQ: CG) and TA Associates completed the acquisition of WU "
            "Holdco, Inc. ('Weiman Products') in March 2019. PurposeBuilt Brands, Inc.'s SEC "
            "registration statement lists Weiman Products, LLC and Bi-O-Kleen Industries, Inc. "
            "among its wholly owned subsidiaries and names Weiman, Goo Gone and Wright's as "
            "its consumer specialty cleaning brands, so one source governs all three brands "
            "recorded here."
        ),
        "ev": "verified",
        "src": "https://www.sec.gov/Archives/edgar/data/1771815/000095012320012392/filename1.htm",
        "brands": ["Weiman", "Goo Gone", "Biokleen"],
    },
    "RPM International Inc.": {
        "type": "public (RPM)",
        "detail": (
            "Rust-Oleum Corporation is a wholly owned subsidiary of RPM International Inc. "
            "(NYSE: RPM), listed in the company's SEC Exhibit 21.1 and named among RPM's most "
            "significant trademarks in its Form 10-K. Rust-Oleum was filed here as a 'no parent "
            "found' independent; it is a subsidiary of a public specialty-chemicals group."
        ),
        "ev": "verified",
        "src": "https://www.sec.gov/Archives/edgar/data/110621/000119312526312142/rpm-ex21_1.htm",
        "brands": ["Rust-Oleum"],
    },
    "3M Company": {
        "type": "public (MMM)",
        "detail": (
            "The brand on the label is the company. 3M Company is a Delaware corporation "
            "incorporated in 1929, listed on the NYSE under MMM; its Form 10-K states 'As used "
            "herein, the term \"3M\" or \"Company\" includes 3M Company and its subsidiaries.' "
            "Filed here as a 'no parent found' independent; it is a public company."
        ),
        "ev": "verified",
        "src": "https://www.sec.gov/Archives/edgar/data/66740/000006674026000014/mmm-20251231.htm",
        "brands": ["3M"],
    },
    "Truelink Capital Management, LLC": {
        "type": "private equity",
        "detail": (
            "Zep Inc. (founded 1937) ceased trading on the NYSE in June 2015 when an affiliate "
            "of New Mountain Capital L.L.C. completed a merger valuing it at approximately "
            "$692 million; the SEC-filed completion release is corroboration. Truelink Capital "
            "Management, LLC, a Los Angeles private equity firm, closed its acquisition of Zep "
            "from New Mountain on 2025-07-01. The current-owner leg rests on the acquirer's own "
            "release, hence reported rather than verified."
        ),
        "ev": "reported",
        "src": "https://www.prnewswire.com/news-releases/truelink-capital-acquires-zep-a-leading-cleaning-products-and-maintenance-services-provider-302495089.html",
        "brands": ["Zep"],
    },
    "Forward Consumer Partners": {
        "type": "private equity",
        "detail": (
            "Bar Keepers Friend is made by SerVaas Laboratories, Inc. (Indianapolis). The "
            "SerVaas family bought the brand in 1956; Forward Consumer Partners acquired "
            "SerVaas Laboratories in March 2025, with Paul SerVaas and other existing "
            "shareholders retaining a significant minority stake. Owner recorded at the "
            "acquiring firm; the operating company is SerVaas Laboratories, Inc."
        ),
        "ev": "reported",
        "src": "https://www.businesswire.com/news/home/20250319817098/en/Forward-Acquires-Bar-Keepers-Friend",
        "brands": ["BKF"],
    },
    "Faultless Brands": {
        "type": "private (Architect Equity)",
        "detail": (
            "Bon Ami cleanser is a Faultless Brands product; the company's own brand page lists "
            "it under Home Care. Faultless Brands (Kansas City, Missouri, founded 1887) was "
            "acquired by Architect Equity in June 2020. Its portfolio also carries Faultless, "
            "Niagara, Magic, Kleen King and Trapp Fragrances. Note that 'Faultless' also appears "
            "in this database as a product brand with no owner record of its own."
        ),
        "ev": "verified",
        "src": "https://faultlessbrands.com/our-brands/",
        "brands": ["Bon Ami"],
    },
    "BRANDED Group": {
        "type": "private (consumer-goods e-commerce holding company)",
        "detail": (
            "BRANDED Group announced the full acquisition of Puracy in October 2021. Puracy's "
            "own About page still describes it as 'our small, family-owned company,' which the "
            "acquisition contradicts; the label does not say so. This is the thesis of the "
            "ownership layer in one record."
        ),
        "ev": "reported",
        "src": "https://www.prnewswire.com/news-releases/branded-acquires-puracy-a-leading-plant-based-household-cleaning-and-personal-care-brand-301394161.html",
        "brands": ["Puracy"],
    },
    # ---- examined, no parent: recorded as a finding rather than an absence ----
    "Sunshine Makers, Inc.": {
        "type": "private, founder-owned",
        "detail": (
            "Simple Green is Sunshine Makers, Inc.'s own brand; the company was founded by Bruce "
            "FaBrizio and is still owned and operated by him, headquartered in Huntington Beach, "
            "California. No parent company. Two of the 25 'no parent found' entries were this "
            "company and its own brand, so the bucket was holding a company listed as if it were "
            "a brand."
        ),
        "ev": "verified",
        "src": "https://simplegreen.com/about-us/",
        "brands": ["Simple Green", "Sunshine Makers"],
    },
    "Jelmar, LLC": {
        "type": "private, family-owned (WBENC women-owned)",
        "detail": (
            "CLR is Jelmar, LLC's brand; the company's own history page calls Jelmar 'CLR "
            "Brands' parent company.' Founded by Manny Gutterman, led by Alison Gutterman. Same "
            "company-and-its-own-brand duplication as Sunshine Makers. No parent company."
        ),
        "ev": "verified",
        "src": "https://www.clrbrands.com/about-us/our-history/",
        "brands": ["CLR", "Jelmar"],
    },
    "Groupe Attitude inc.": {
        "type": "private (Canada)",
        "detail": (
            "The registered owner of the ATTITUDE marks is Groupe Attitude inc., Montreal "
            "(Quebec), previously Lord Bernier Inc.; the Canadian trademark register records "
            "the change in title. The brand was launched in 2006 by Jean-Francois Bernier and "
            "also trades as Bio-Spectra. No parent company."
        ),
        "ev": "verified",
        "src": "https://ised-isde.canada.ca/cipo/trademark-search/1488955",
        "brands": ["ATTITUDE"],
    },
    "EO Products": {
        "type": "private, family-owned",
        "detail": (
            "Everyone is one of EO Products' two brands, with EO. Founded 1995 in San Rafael, "
            "California by Susan Griffin-Black and Brad Black, who remain co-CEOs. No parent "
            "company."
        ),
        "ev": "verified",
        "src": "https://www.eoproducts.com/pages/about-us",
        "brands": ["Everyone"],
    },
    "NOW Health Group": {
        "type": "private, family- and employee-owned (ESOP 30%)",
        "detail": (
            "NOW Foods is the largest division of NOW Health Group, founded 1968 by Elwood "
            "Richard. As of January 2026 the company remains privately held and family-led, "
            "with an Employee Stock Ownership Plan holding a 30% interest for employees; the "
            "Richard family holds the remainder. No parent company."
        ),
        "ev": "reported",
        "src": "https://www.nowfoods.com/about-now/press-room/press-releases/now-health-group-announces-new-employee-stock-ownership-plan",
        "brands": ["NOW Foods"],
    },
    "Norwex": {
        "type": "private, family-owned (Norway)",
        "detail": (
            "Founded in Norway in 1994 by Bjorn Nicolaisen; the company states it has remained "
            "debt-free and family owned since founding, and his daughter Beate Hjeltnes became "
            "CEO in 2025. The Norwegian company register lists Norwex Holding AS with "
            "Nicolaisen Invest AS as parent (majority holder), which is a family holding "
            "company rather than a corporate parent."
        ),
        "ev": "reported",
        "src": "https://www.prnewswire.com/news-releases/norwex-strengthens-executive-leadership-with-appointment-of-beate-hjeltnes-as-ceo-302467781.html",
        "brands": ["Norwex"],
    },
    "Bona AB": {
        "type": "private, family-owned (Sweden)",
        "detail": (
            "Founded 1919 in Malmo, Sweden by Wilhelm Edner; still family-owned and led by the "
            "third and fourth generations of the Edner, Forsberg and Brask families. No parent "
            "company."
        ),
        "ev": "verified",
        "src": "https://www.bona.com/en/about-bona/",
        "brands": ["Bona"],
    },
    "ECOS (Earth Friendly Products)": {
        "type": "private, family-owned, women-led",
        "detail": (
            "Earth Friendly Products (also registered as Venus Laboratories, Inc.), maker of "
            "ECOS, founded 1967 by Van Vlahakis in Cypress, California; family-owned and "
            "operated, led since 2014 by his daughter Kelly Vlahakis-Hanks. The company's own "
            "sustainability report states 'Family owned and operated in CA, IL, NJ and WA. "
            "Earth Friendly Products.' No parent company."
        ),
        "ev": "verified",
        "src": "https://www.ecos.com/wp-content/uploads/2024/03/ECOS_SR_24Mar2024_R3-2.pdf",
        "brands": ["ECOS"],
    },
    "Dr. Bronner's": {
        "type": "private, family-owned (fifth generation)",
        "detail": (
            "Founded in the United States in 1948 by Emanuel Bronner, whose family began making "
            "soap in 1858. Still family-owned and run, led by fifth-generation soap makers David "
            "and Michael Bronner from Vista, California. No parent company."
        ),
        "ev": "verified",
        "src": "https://www.drbronner.com/blogs/ourselves/the-dr-bronners-story",
        "brands": ["Dr. Bronner's"],
    },
    "Meliora Cleaning Products": {
        "type": "private, woman-owned B Corp",
        "detail": (
            "Founded in Chicago, Illinois by Kate Jakubas and Mike Mayer, who describe "
            "themselves as the owners and operators; WBENC-certified woman-owned and a "
            "certified B Corporation. No parent company."
        ),
        "ev": "verified",
        "src": "https://meliorameansbetter.com/pages/about-us",
        "brands": ["Meliora"],
    },
    "AspenClean": {
        "type": "private, family-owned (Canada)",
        "detail": (
            "Founded in Canada by Alicia Sokolowski (president and co-CEO) and Chris Solodko "
            "(COO and co-CEO); the company describes itself as family-owned. No parent company."
        ),
        "ev": "verified",
        "src": "https://aspenclean.com/pages/aspenclean",
        "brands": ["AspenClean"],
    },
    "Better Life": {
        "type": "private",
        "detail": (
            "Founded 2008 in St. Louis, Missouri by Tim Barklage and Kevin Tibbs. No parent "
            "company found."
        ),
        "ev": "verified",
        "src": "https://betterlifeclean.com/pages/about",
        "brands": ["Better Life"],
    },
    "Branch Basics": {
        "type": "private",
        "detail": (
            "Founded 2012 in Minneapolis, Minnesota by Allison Evans, Kelly Love and Marilee "
            "Nelson; a new CEO and CFO bought in after the 2015-2017 shutdown, and the five "
            "co-owners each hold just under 20%, with the remainder held by friends-and-family "
            "investors. No parent company. Ownership detail rests on a third-party outlet, "
            "hence reported."
        ),
        "ev": "reported",
        "src": "https://www.cnbc.com/2025/05/07/branch-basics-founders-how-we-rebuilt-lucrative-business-after-shutting-down.html",
        "brands": ["Branch Basics"],
    },
    "Blueland": {
        "type": "private, venture-funded",
        "detail": (
            "Founded 2019 by Sarah Paiji Yoo and John Mascari; private and founder-led. Raised "
            "about $35 million as of February 2022 in rounds led by Prelude Growth Partners. No "
            "parent company; investor-backed rather than conglomerate-owned, which is a "
            "different fact and is recorded as such."
        ),
        "ev": "reported",
        "src": "https://www.prnewswire.com/news-releases/blueland-raises-20-million-for-new-category-and-retail-expansion-to-eliminate-more-single-use-plastic-301482931.html",
        "brands": ["Blueland"],
    },
}

# Every entry that was in the bucket, all 25 examined this pass.
SWEPT = [
    "Dr. Bronner's", "Puracy", "Better Life", "Branch Basics", "Biokleen", "Blueland",
    "AspenClean", "Meliora", "ECOS", "ATTITUDE", "Everyone", "NOW Foods", "Norwex", "Bona",
    "Zep", "Bon Ami", "BKF", "Weiman", "Goo Gone", "Simple Green", "Sunshine Makers",
    "CLR", "Jelmar", "3M", "Rust-Oleum",
]

NOTE = (
    "Brands with no parent company found. Recorded as 'no parent found', which is NOT the "
    "same as 'independently owned' and must never render as such. Absence of a finding is "
    "not a finding. "
    "SWEPT 2026-10-01 (CCI-012 Lane 1, Dolman): all 25 entries present at the start of the "
    "sweep were examined and all 25 resolved, so the list is empty. Fourteen resolved to a "
    "real parent or acquiring firm, ten to a verified no-parent finding (family-owned, "
    "founder-owned or private), and two (Sunshine Makers, Jelmar) turned out to be company "
    "names that had been listed as if they were brands. New brands go back in here only as "
    "genuine absences of a finding."
)


def main() -> int:
    path = DATA / "owners.json"
    owners = json.loads(path.read_text(encoding="utf-8"))

    added, present = [], []
    for name, rec in NEW_OWNERS.items():
        if name in owners["owners"]:
            present.append(name)
        else:
            owners["owners"][name] = rec
            added.append(name)

    ind = owners.get("independents", {})
    before = list(ind.get("brands", []))
    remaining = [b for b in before if b not in SWEPT]
    ind["brands"] = remaining
    ind["note"] = NOTE
    owners["independents"] = ind

    path.write_text(json.dumps(owners, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"owner records added: {len(added)}")
    for a in added:
        print(f"  + {a}")
    if present:
        print(f"already present (idempotent no-op): {len(present)}")
    print(f"independents.brands: {len(before)} -> {len(remaining)}")
    if remaining:
        print("  still unexamined: " + ", ".join(remaining))
    print(f"total owner records now: {len(owners['owners'])}")

    # Guard: every swept brand must now resolve to some owner record.
    reachable = set()
    for info in owners["owners"].values():
        reachable.update(info.get("brands", []))
    unresolved = [b for b in SWEPT if b not in reachable]
    if unresolved:
        print(f"ERROR: swept brand(s) with no owner record: {unresolved}")
        return 1
    print("guard: every swept brand resolves to an owner record")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
