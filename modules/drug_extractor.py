import spacy

# Load SciSpaCy model only once (heavy)
try:
    nlp = spacy.load("en_ner_bc5cdr_md")
except Exception:
    nlp = None
    print("⚠️ SciSpaCy model not found. Install: en_ner_bc5cdr_md")


COMMON_STOPWORDS = {
    "treatment", "drug", "study", "dose", "control", "group", "model", 
    "effect", "response", "clinical", "therapy", "cell", "cells", "inhibitor"
}


def clean_entity(ent: str) -> str:
    """Normalize chemical/drug entity names."""
    ent = ent.strip()
    ent = ent.replace("\n", " ")
    ent = ent.replace("  ", " ")
    return ent


def extract_drug_names(text: str):
    """
    Extract chemical/drug/biologic names from scientific text using SciSpaCy.
    Returns list of unique drug names.
    """
    if not text or nlp is None:
        return []

    doc = nlp(text)

    drugs = []
    for ent in doc.ents:
        if ent.label_ == "CHEMICAL":
            name = clean_entity(ent.text)

            # Basic filtering to avoid noise
            if len(name) < 3:
                continue
            if name.lower() in COMMON_STOPWORDS:
                continue

            drugs.append(name)

    # Remove duplicates while preserving order
    unique_drugs = list(dict.fromkeys(drugs))

    return unique_drugs
