import re
import unicodedata


def remove_non_ascii(text: str) -> str:
    """Remove non-ASCII characters but preserve letters and punctuation."""
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode("ascii", "ignore").decode("ascii", "ignore")


def remove_references_section(text: str) -> str:
    """
    Removes the references section typically starting with
    'References', 'Bibliography', or similar keywords.
    """
    patterns = [
        r"(?i)references\n.*",
        r"(?i)bibliography\n.*",
        r"(?i)works cited\n.*",
    ]
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.DOTALL)
    return text


def collapse_whitespace(text: str) -> str:
    """Normalize excessive whitespace and line breaks."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_duplicate_lines(text: str) -> str:
    """Remove repeating lines (common in PDFs with headers/footers)."""
    lines = text.split("\n")
    seen = set()
    cleaned = []
    for line in lines:
        if line.strip() not in seen:
            cleaned.append(line)
            seen.add(line.strip())
    return "\n".join(cleaned)


def clean_text(text: str, max_chars: int = 20000) -> str:
    """
    Full cleaning pipeline:
    1. Remove non-ASCII
    2. Remove references
    3. Remove duplicate lines
    4. Normalize whitespace
    5. Trim to max characters
    """
    if not text:
        return ""

    # Remove weird PDF characters
    text = remove_non_ascii(text)

    # Remove references section
    text = remove_references_section(text)

    # Remove duplicated lines
    text = remove_duplicate_lines(text)

    # Collapse whitespace
    text = collapse_whitespace(text)

    # Trim to max allowed characters
    if len(text) > max_chars:
        text = text[:max_chars]

    return text.strip()
