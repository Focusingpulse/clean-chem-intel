"""
PubChem API client — fetches chemical data by name or CAS number.

Uses the PUG REST API (no key required).
Docs: https://pubchem.ncbi.nlm.nih.gov/rest/docs
"""
import json
import urllib.request
import urllib.error
from typing import Optional


PUG_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"


def fetch_by_name(name: str) -> Optional[dict]:
    """
    Fetch compound data from PubChem by chemical name.
    Returns a dict with CID, GHS classifications, and synonyms, or None if not found.
    """
    url = f"{PUG_BASE}/compound/name/{urllib.parse.quote(name)}/property/Title,CAS,GHSClassification/JSON"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
        properties = data.get("PropertyTable", {}).get("Properties", [])
        if properties:
            return properties[0]
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        pass
    return None


def fetch_by_cid(cid: int) -> Optional[dict]:
    """
    Fetch compound data from PubChem by CID (PubChem Compound ID).
    """
    url = f"{PUG_BASE}/compound/cid/{cid}/property/Title,CAS,GHSClassification/JSON"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
        properties = data.get("PropertyTable", {}).get("Properties", [])
        if properties:
            return properties[0]
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        pass
    return None


def fetch_safety_summary(cid: int) -> Optional[dict]:
    """
    Fetch safety summary data from PubChem for a given CID.
    Includes GHS hazard statements, precautionary statements, etc.
    """
    url = f"{PUG_BASE}/p_view/annotations/aid/1/JSON?cid={cid}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
        return data
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        pass
    return None
