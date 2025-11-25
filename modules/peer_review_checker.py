import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def search_pubmed(title: str = None, doi: str = None):
    """
    Search PubMed using either title or DOI.
    Returns PMID if found, else None.
    """
    if not title and not doi:
        return None

    try:
        if doi:
            query = doi
        else:
            query = title

        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json"
        }

        response = requests.get(ESEARCH_URL, headers=HEADERS, params=params, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        idlist = data.get("esearchresult", {}).get("idlist", [])

        if len(idlist) > 0:
            return idlist[0]

        return None

    except Exception as e:
        print(f"[PubMed Search Error] {e}")
        return None


def fetch_pubmed_metadata(pmid: str):
    """
    Fetch paper metadata from PubMed.
    Returns dict or None.
    """
    try:
        params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml"
        }

        response = requests.get(EFETCH_URL, headers=HEADERS, params=params, timeout=10)

        if response.status_code != 200:
            return None

        return response.text

    except Exception as e:
        print(f"[PubMed Fetch Error] {e}")
        return None


def extract_journal_from_xml(xml_text: str):
    """
    Simple journal name + pub date extractor from XML.
    """
    import re

    journal_match = re.search(r"<Title>(.*?)</Title>", xml_text)
    year_match = re.search(r"<PubDate>.*?<Year>(\d+)</Year>", xml_text, re.DOTALL)

    journal = journal_match.group(1) if journal_match else "Unknown"
    year = year_match.group(1) if year_match else "Unknown"

    return journal, year


def is_peer_reviewed(title: str = None, doi: str = None):
    """
    Main function:
    1. Search PubMed
    2. If found → peer-reviewed
    3. Return journal metadata
    """
    pmid = search_pubmed(title, doi)

    if not pmid:
        return {
            "is_peer_reviewed": False,
            "pmid": None,
            "journal": None,
            "pubyear": None
        }

    # fetch metadata
    xml = fetch_pubmed_metadata(pmid)
    if not xml:
        return {
            "is_peer_reviewed": False,
            "pmid": pmid,
            "journal": None,
            "pubyear": None
        }

    journal, year = extract_journal_from_xml(xml)

    return {
        "is_peer_reviewed": True,
        "pmid": pmid,
        "journal": journal,
        "pubyear": year
    }
