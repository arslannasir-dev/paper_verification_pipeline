from sentence_transformers import SentenceTransformer, util
import torch

# Load FREE MiniLM model (very fast and accurate)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


def chunk_text(text: str, chunk_size: int = 2000):
    """
    Breaks the paper text into manageable chunks for embedding.
    This avoids memory issues with large PDFs.
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def compute_similarity(query_emb, text_emb):
    """Cosine similarity."""
    return util.cos_sim(query_emb, text_emb).item()


def check_relevance(keyword: str, paper_text: str, threshold: float = 0.25):
    """
    Main function:
    1. Embed keyword/query
    2. Embed chunks of paper text
    3. Compute cosine similarity for each chunk
    4. Return maximum score (best match)
    """
    if not keyword or not paper_text:
        return {
            "is_relevant": False,
            "relevance_score": 0.0,
            "best_chunk": None
        }

    # Embed keyword
    query_emb = model.encode(keyword, convert_to_tensor=True)

    # Split paper text into chunks
    chunks = chunk_text(paper_text)

    best_score = 0
    best_chunk = None

    for chunk in chunks:
        text_emb = model.encode(chunk, convert_to_tensor=True)
        score = compute_similarity(query_emb, text_emb)

        if score > best_score:
            best_score = score
            best_chunk = chunk

    is_relevant = best_score >= threshold

    return {
        "is_relevant": is_relevant,
        "relevance_score": float(best_score),
        "best_chunk": best_chunk[:300] if best_chunk else None  # optional preview
    }
