import requests
import time

OPENFDA_DRUG_LABEL = "https://api.fda.gov/drug/label.json"
OPENFDA_NDC = "https://api.fda.gov/drug/ndc.json"
OPENFDA_ORANGEBOOK = "https://api.fda.gov/drug/drugsfda.json"

HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 10


def query_openfda(endpoint: str, query: str):
    """
    Generic OpenFDA query helper.
    Returns JSON or None.
    """
    try:
        url = f"{endpoint}?search={query}&limit=1"
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

        if response.status_code == 200:
            return response.json()
        return None

    except Exception as e:
        print(f"[FDA API Error] {e}")
        return None


def check_drug_label(drug_name: str):
    """
    Search drug name in FDA Drug Label database.
    """
    query = f'openfda.generic_name:"{drug_name}"'
    return query_openfda(OPENFDA_DRUG_LABEL, query)


def check_drug_ndc(drug_name: str):
    """
    Search drug name in FDA NDC Directory.
    """
    query = f'brand_name:"{drug_name}"'
    return query_openfda(OPENFDA_NDC, query)


def check_orange_book(drug_name: str):
    """
    Search drug in the FDA Orange Book.
    """
    query = f'products.brand_name:"{drug_name}"'
    return query_openfda(OPENFDA_ORANGEBOOK, query)


def is_fda_approved(drug_name: str):
    """
    Check all 3 FDA APIs.
    If any API returns a match, consider drug FDA-approved.
    """
    # Try generic name
    label = check_drug_label(drug_name)
    if label and "results" in label:
        return True, label

    # Try NDC listing
    ndc = check_drug_ndc(drug_name)
    if ndc and "results" in ndc:
        return True, ndc

    # Try Orange Book
    ob = check_orange_book(drug_name)
    if ob and "results" in ob:
        return True, ob

    return False, None


def check_all_drugs(drug_list):
    """
    Main function:
    Input: list of drug names from spaCy
    Output:
        {
           "is_fda_approved": bool,
           "approved_drugs": [...],
           "drug_fda_details": {...}
        }
    """
    approved = []
    details = {}

    for drug in drug_list:
        print(f"[FDA Checker] Checking FDA status for: {drug}")

        ok, data = is_fda_approved(drug)

        if ok:
            approved.append(drug)
            details[drug] = data

        # Mild sleep to avoid API throttling
        time.sleep(0.5)

    return {
        "is_fda_approved": len(approved) > 0,
        "approved_drugs": approved,
        "drug_fda_details": details
    }
