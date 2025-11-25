import psycopg2
import psycopg2.extras
from config import POSTGRES_CONFIG


def get_connection():
    """Create a PostgreSQL connection using global config."""
    return psycopg2.connect(
        host=POSTGRES_CONFIG["host"],
        port=POSTGRES_CONFIG["port"],
        dbname=POSTGRES_CONFIG["dbname"],
        user=POSTGRES_CONFIG["user"],
        password=POSTGRES_CONFIG["password"],
    )


def fetch_pending_records(limit=50):
    """
    Fetch records that need to be processed.
    You can later add a status column like is_processed=false.
    """
    query = f"""
        SELECT 
            id,
            url,
            citation_text,
            pubmed_id,
            doi,
            created_date,
            data_source,
            citation_source,
            hash_id,
            reviewer_id,
            review_status,
            review_assigned_date
        FROM umbizo_citations
        WHERE review_status = 'not_reviewed'
        LIMIT {limit};
    """

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(query)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def update_record(record_id, fields: dict):
    """
    Update a single record.
    Input example:
    fields = {
        "is_relevant": True,
        "relevance_score": 0.87,
        "tier": "Tier 1",
        "is_fda_approved": True,
        ...
    }
    """
    if not fields:
        return

    set_clause = ", ".join([f"{key} = %s" for key in fields.keys()])
    values = list(fields.values())

    query = f"""
        UPDATE umbizo_citations
        SET {set_clause}
        WHERE id = %s;
    """

    values.append(record_id)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(query, values)
    conn.commit()

    cur.close()
    conn.close()


def mark_error(record_id, error_message: str):
    """
    If any module fails, log error into the database.
    You can add an extra column: last_error
    """
    query = """
        UPDATE umbizo_citations
        SET last_error = %s,
            review_status = 'error'
        WHERE id = %s;
    """

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, [error_message[:500], record_id])
    conn.commit()

    cur.close()
    conn.close()
