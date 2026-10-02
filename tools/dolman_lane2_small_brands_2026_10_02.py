#!/usr/bin/env python3
"""CCI-012 Lane 2 (Dolman, 2026-10-02): resolve the remaining untested small brands
and correct the Reckitt / Essential Home split. Idempotent."""
import json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
p = REPO / "data" / "owners.json"
o = json.loads(p.read_text())
owners = o["owners"]

def setrec(name, rec):
    owners[name] = rec

# --- A. Reckitt: Essential Home divested to Advent, completed 2025-12-31 ---------
owners["Reckitt"] = {
    "type": "public (RKT)",
    "detail": ("Trades as Reckitt Benckiser in some markets. Reckitt's own brand page "
               "(www.reckitt.com/our-brands/, read 2026-10-02) lists eleven Powerbrands: Dettol, "
               "Lysol, Harpic, Finish, Vanish, Strepsils, Nurofen, Mucinex, Gaviscon, Durex, Veet. "
               "Air Wick and Calgon were REMOVED from this record on 2026-10-02: Reckitt divested its "
               "Essential Home business (Air Wick, Calgon, Cillit Bang, Mortein and ~80 brands in all) "
               "to Advent International, L.P. - announced 2024-07-24, completed 2025-12-31, Reckitt "
               "retaining a 30% equity stake. They are now recorded under 'Essential Home (Advent "
               "International)'. OPEN FLAG: Woolite is kept on this record but Reckitt's own brand page "
               "does not list it and no primary source for its current ownership was located this fire; "
               "unverified, not corrected. The previous src for this record was the whobrands.com blog, "
               "a bot-walled secondary source flagged defective on 2026-10-01; replaced with Reckitt's "
               "own brand page."),
    "ev": "verified",
    "src": "https://www.reckitt.com/our-brands/",
    "brands": ["Lysol", "Vanish", "Woolite", "Finish", "Reckitt Benckiser"],
    "brand_sources": {
        "verified_by_reckitt_brand_page": ["Lysol", "Vanish", "Finish"],
        "unverified_kept_pending_primary": ["Woolite", "Reckitt Benckiser"],
    },
}

# --- B. Essential Home (Advent International) ------------------------------------
setrec("Essential Home (Advent International)", {
    "type": "private equity (Advent International, L.P.); Reckitt retains 30%",
    "detail": ("Reckitt Benckiser divested its Essential Home business to Advent International, L.P. - "
               "announced 2024-07-24, completed 2025-12-31. Essential Home spans roughly 80 brands "
               "including Air Wick, Calgon, Cillit Bang and Mortein, sold across about 70 countries; "
               "Reckitt retains a 30% equity stake in Advent's acquisition vehicle. Air Wick and Calgon "
               "were previously recorded under Reckitt and were moved here on 2026-10-02."),
    "ev": "verified",
    "src": ("https://www.reckitt.com/news/reckitt-to-sharpen-its-portfolio-and-simplify-organisation-"
            "for-accelerated-growth-and-value-creation/"),
    "brands": ["Air Wick", "Calgon", "Cillit Bang", "Mortein"],
})

# --- C. RPM: Mean Green and The Pink Stuff ---------------------------------------
rpm = owners["RPM International Inc."]
for b in ["Mean Green", "The Pink Stuff"]:
    if b not in rpm["brands"]:
        rpm["brands"].append(b)
rpm["brand_sources"] = {
    "verified_by_sec_exhibit_21_1": ["Rust-Oleum"],
    "reported_by_rpm_own_site": ["Mean Green"],
    "reported_by_rpm_acquisition_release": ["The Pink Stuff"],
}
rpm["detail"] = (rpm["detail"] + " Extended 2026-10-02: Mean Green (acquired from CR Brands, 2018) and "
                 "The Pink Stuff (Star Brands Group, announced 2025-04-03, completed 2025-05-01) are RPM "
                 "cleaning brands carried by the Rust-Oleum cleaners business. Known limitation unchanged: "
                 "apply_owners() stamps ONE src per record, so all brands here receive the SEC exhibit src, "
                 "which governs Rust-Oleum and not the brand names.")

# --- D. New records for the remaining small brands --------------------------------
NEW = {
 "JoySuds, LLC": dict(
   type="private", detail=("US/Canada/Latin America owner of the Joy dish brand; formed November 2019 to "
   "acquire Joy and Cream Suds from Procter & Gamble. P&G continues to sell Joy outside the Americas."),
   ev="verified", src="https://www.joysuds.com/history/", brands=["Joy"]),
 "Nakoma Products, LLC": dict(
   type="private", detail=("Bridgeview, Illinois. Bought Endust and Behold from Sara Lee in 2011. The brand's "
   "own marketing PDF distributed with the product states 'Endust is a registered trademark of Nakoma "
   "Products LLC'. Trademark-based evidence, not a corporate filing."),
   ev="reported", src="https://images.salsify.com/image/upload/s--DHgt0mbF--/nktncnpzsi8mhxkq8x2r.pdf",
   brands=["Endust"]),
 "Clean Control Corporation": dict(
   type="private, family-owned", detail=("Warner Robins, Georgia. Founded by Stephen Davison; makes OdoBan, "
   "Earth Choice, Lethal, Pets Rule and Sports Edge. Company's own founder page describes it as a "
   "locally-owned business. OPEN FLAG: a third-party aggregator (PatSnap) lists it as 'part of Walker Eden "
   "International, Inc.'; no primary source for that relationship was located and it is not recorded here."),
   ev="verified", src="https://www.cleancontrol.com/about-us/our-founder/",
   brands=["OdoBan", "Earth Choice", "Lethal", "Pets Rule", "Sports Edge"]),
 "Awesome Products, Inc.": dict(
   type="private, founder-owned", detail=("Buena Park, California. Founded 1983 by LD (Sarang) Hardas; makes "
   "LA's Totally Awesome."),
   ev="verified", src="https://www.lastotallyawesome.com/company/", brands=["LA's Totally Awesome"]),
 "Granite Gold Inc.": dict(
   type="private, family-owned", detail=("Poway, California. Founded 2002/2003 by cousins Lenny Sciarrino and "
   "Lenny Pellegrino; three generations of stone fabrication. Also carries the MicroGold and Guardsman brands."),
   ev="verified", src="https://granitegold.com/pages/about",
   brands=["Granite Gold", "MicroGold", "Guardsman"]),
 "Racine International, LLC": dict(
   type="private", detail=("Racine, Wisconsin; formerly Racine Industries, Inc. (and before that Rench "
   "Manufacturing). Maker of the HOST Dry Extraction Cleaning System. The company's own history page records "
   "the move to new ownership and the rename to Racine International, LLC."),
   ev="verified", src="https://hostdry.com/our-company/", brands=["HOST"]),
 "Plus Manufacturing, Inc.": dict(
   type="private, family-owned", detail=("Spokane, Washington, operating since 1982. Founded by Ivan Day; "
   "maker of the Soap Free Procyon line. The product SDS names Plus Manufacturing Inc as manufacturer."),
   ev="verified", src="https://soapfreeprocyon.com/about", brands=["Procyon"]),
 "Greenology Products, Inc.": dict(
   type="private", detail=("Raleigh, North Carolina. Manufacturer of record for Green Shield Organic on the "
   "EPA ChemExpo product record; the GREENSHELD ORGANIC trademark (USPTO 86377207, registered and renewed "
   "2025-06-26) is owned by Greenology Products."),
   ev="verified", src="https://comptox.epa.gov/chemexpo/product/702571/", brands=["Green Shield Organic"]),
 "Stoner, Inc.": dict(
   type="private, family-owned", detail=("Quarryville, Pennsylvania. Founded 1942 by Paul Stoner; "
   "third-generation family-owned. Maker of Invisible Glass."),
   ev="verified", src="https://stonersolutions.com/our-story", brands=["Invisible Glass"]),
 "Kirk's Natural LLC": dict(
   type="private, family-owned", detail=("Erlanger, Kentucky. Family of Natural Brands (Kirk's, The Grandpa "
   "Soap Company, South of France); purchased from Procter & Gamble in the early 2000s by Rich Oliver and run "
   "by his daughters Katherine and Molly Oliver. Kirk's own site gives the company name and address."),
   ev="verified", src="https://kirkssoap.com/pages/who-we-are", brands=["Kirk's"]),
 "American Cleaning Solutions": dict(
   type="private", detail=("Long Island City, New York. Maker of the Focus line; Focus MP 11 Multi-Purpose "
   "Cleaner has been Green Seal certified (GS-37) since 2005."),
   ev="verified", src="https://certified.greenseal.org/product/focus-mp-11-multi-purpose-cleaner-american-cleaning-solutions-focus",
   brands=["Focus"]),
 "Cot'n Wash, Inc.": dict(
   type="private, founder-owned", detail=("Philadelphia, Pennsylvania. Founder and CEO Jonathan Propper; the "
   "Dropps pod brand is made by Cot'n Wash, Inc."),
   ev="verified", src="https://www.dropps.com/pages/the-dropps-story", brands=["Dropps"]),
 "Aunt Fannie's, Inc.": dict(
   type="private, venture-backed", detail=("Portland, Oregon. Founded 2013 by Mat Franken; no parent company "
   "found. An aggregator summary claimed a Unilever acquisition in 2018; the underlying article and the "
   "company's own releases carry no such transaction and the claim is NOT recorded. Evidence level is "
   "reported rather than verified because the finding is an absence backed by a company release, not by a "
   "corporate register."),
   ev="reported",
   src="https://www.globenewswire.com/news-release/2019/02/14/1725297/0/en/Aunt-Fannie-s-Closes-5-Million-Financing-Round.html",
   brands=["Aunt Fannie's"]),
 "Delta Carbona, L.P.": dict(
   type="private, family-owned (Dr. Beckmann Group)", detail=("Fairfield / Pine Brook, New Jersey. The US "
   "sales, marketing and distribution arm for the Carbona brand; Carbona joined the Dr. Beckmann Group "
   "(formerly Delta Pronatura) in 1994."),
   ev="verified", src="https://carbona.com/about/", brands=["Carbona"]),
 "NiTEO Products, LLC": dict(
   type="private equity (Highlander Partners)", detail=("Dallas, Texas. Acquired Folexport, Inc. (Folex) from "
   "Barrett and Patty Lash on 2025-12-04. Recorded at reported: the evidence is the acquirer's own press "
   "release, not a register or a corporate filing."),
   ev="reported",
   src="https://highlander-partners.com/news-posts/niteo-products-a-portfolio-company-of-highlander-partners-acquires-folex/",
   brands=["Folex"]),
 "Consumer Product Partners, LLC": dict(
   type="private", detail=("St. Louis, Missouri; formerly Vi-Jon, LLC (One Swan Drive, Smyrna, Tennessee). "
   "Labeler of record for Swan 70% Isopropyl Alcohol on the FDA DailyMed drug listing."),
   ev="verified",
   src="https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=0bd995eb-a261-469b-8b7a-a5ff613ce48b&type=display",
   brands=["Swan"]),
 "Planet Inc.": dict(
   type="private", detail=("Maker of Planet Ultra dishwashing liquid. Company's own site is the only source "
   "located; no parent company found. Recorded at reported because the finding rests on the maker's own "
   "self-description and no independent register was checked."),
   ev="reported", src="http://www.planetinc.com/planet.htm", brands=["Planet"]),
 "Pure Natural Cleaners": dict(
   type="private", detail=("Maker of Pure Natural Laundry Detergent (Free & Clear), MADE SAFE certified. "
   "OPEN FLAG: two similarly named firms exist - 'Pure Natural Cleaners' (soap-berry detergent, "
   "purenaturalcleaners.com) and 'PURE Natural Laundry Detergent' (Blaine Burgan, Indianapolis). The MADE "
   "SAFE certificate names Pure Natural Cleaners for the Free & Clear detergent, which is the product in this "
   "database, but the two were not disambiguated to a corporate register."),
   ev="reported", src="https://madesafe.org/products/pure-natural-cleaners-laundry-detergent-free-clear",
   brands=["Pure Natural"]),
 "U.S. Pumice Company": dict(
   type="private", detail=("Maker of the Pumie pumice stick (uspumice.com). OPEN FLAG: Summit Brands now "
   "markets a 'Pumie Toilet Bowl Ring Remover' and the relationship between the two (acquisition, licence or "
   "distribution) was not resolved this fire, so the brand is recorded under its manufacturer of record and "
   "the Summit Brands link is left open."),
   ev="reported", src="https://www.uspumice.com/", brands=["Pumie"]),
}
for name, rec in NEW.items():
    owners[name] = rec

p.write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n")
print("owner records now:", len(owners))
