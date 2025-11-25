import requests
import tempfile
import os
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader


def is_pdf_url(url: str) -> bool:
    """Check if URL likely points to a PDF file."""
    return url.lower().endswith(".pdf") or "pdf" in url.lower()


def download_html(url: str, timeout: int = 15) -> str:
    """Download HTML document from any URL and extract text."""
    try:
        response = requests.get(url, timeout=timeout, headers={
            "User-Agent": "Mozilla/5.0"
        })
        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n")
        return text

    except Exception as e:
        print(f"[HTML Download Error] {e} for URL: {url}")
        return ""


def download_pdf(url: str, timeout: int = 20) -> str:
    """Download PDF, save temp, extract text, delete temp."""
    try:
        response = requests.get(url, timeout=timeout, headers={
            "User-Agent": "Mozilla/5.0"
        })

        if response.status_code != 200:
            return ""

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(response.content)
            temp_path = tmp.name

        # Extract PDF text
        text = extract_text_from_pdf(temp_path)

        # Cleanup
        os.remove(temp_path)

        return text

    except Exception as e:
        print(f"[PDF Download Error] {e} for URL: {url}")
        return ""


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a local PDF file."""
    try:
        reader = PdfReader(pdf_path)
        pages = []

        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except:
                continue

        return "\n".join(pages)

    except Exception as e:
        print(f"[PDF Extract Error] {e} for PDF: {pdf_path}")
        return ""


def extract_text(url: str) -> str:
    """
    Master function:
    1) Check PDF or HTML
    2) Download
    3) Return cleaned text
    """
    print(f"[Downloader] Fetching: {url}")

    if is_pdf_url(url):
        print("[Downloader] Detected PDF")
        text = download_pdf(url)
    else:
        print("[Downloader] Trying HTML")
