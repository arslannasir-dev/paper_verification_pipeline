1️⃣ Install Python 3.11

SciSpaCy does not support Python 3.12/3.13.

Download Python 3.11 here:

👉 https://www.python.org/downloads/release/python-3110/

Verify:

python --version

2️⃣ Set up Virtual Environment
python -m venv venv


Activate:

Windows

venv\Scripts\activate


Mac/Linux

source venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Database (PostgreSQL)

Edit config.py:

POSTGRES_CONFIG = {
  "host": "localhost",
  "port": 5433,
  "dbname": "postgres",
  "user": "postgres",
  "password": "admin"
}


Required table columns:

ALTER TABLE umbizo_citations ADD COLUMN review_status TEXT DEFAULT 'not_reviewed';
ALTER TABLE umbizo_citations ADD COLUMN is_relevant BOOLEAN;
ALTER TABLE umbizo_citations ADD COLUMN relevance_score FLOAT;
ALTER TABLE umbizo_citations ADD COLUMN detected_drugs TEXT;
ALTER TABLE umbizo_citations ADD COLUMN is_fda_approved BOOLEAN;
ALTER TABLE umbizo_citations ADD COLUMN approved_drugs TEXT;
ALTER TABLE umbizo_citations ADD COLUMN is_peer_reviewed BOOLEAN;
ALTER TABLE umbizo_citations ADD COLUMN tier TEXT;
ALTER TABLE umbizo_citations ADD COLUMN last_error TEXT;

🧪 Running the Pipeline
python main.py


This will:

Read all not_reviewed citations

Download the paper

Extract + clean text

Extract drug names

Check FDA approval

Check peer-review status

Evaluate keyword relevance

Assign Tier 1 / 2 / 3

Update the database

🧠 Tier Classification Rules

Tier 1: Drug/device mentioned is FDA-approved

Tier 2: Peer-reviewed but not FDA-approved

Tier 3: Not peer-reviewed + no FDA-approved drug

🔧 Troubleshooting
SciSpaCy model not loading?

You are using Python 3.12 or 3.13 → switch to Python 3.11.

PDF extraction errors?

Some publishers block direct download; pipeline will fallback to HTML extraction.

FDA API returns 429?

Add delay or API key in fda_checker.py.

📜 License

MIT License.

🙋 Need Help?

Open an issue or contact the maintainer.




                                  +-----------------------------+
                                  |   PostgreSQL Database       |
                                  |-----------------------------|
                                  | umbizo_citations (raw data) |
                                  +--------------+--------------+
                                                 |
                                                 v
                                  +-----------------------------+
                                  |         main.py             |
                                  |  (Orchestrator Pipeline)    |
                                  +-----------------------------+
            +------------------------+-------------+------------------------+
            |                        |             |                        |
            v                        v             v                        v
+-------------------+    +------------------+   +-------------------+   +--------------------+
| downloader.py     |    | text_cleaner.py |   | drug_extractor.py |   | relevance_checker.py|
|  (HTML/PDF fetch) | -> | (sanitize text) | ->| (NER: drugs/chem) | ->| (MiniLM embeddings) |
+-------------------+    +------------------+   +-------------------+   +--------------------+
                                                                            |
                                                                            v
                                                         +----------------------------------+
                                                         | peer_review_checker.py           |
                                                         |  (PubMed API → peer-reviewed?)   |
                                                         +----------------------------------+
                                                                            |
                                                                            v
                                                         +----------------------------------+
                                                         | fda_checker.py                   |
                                                         | (OpenFDA APIs → FDA Approval?)   |
                                                         +----------------------------------+
                                                                            |
                                                                            v
                                                         +----------------------------------+
                                                         | tier_classifier.py               |
                                                         | (Tier1/2/3 logic)                |
                                                         +----------------------------------+
                                                                            |
                                                                            v
                                              +------------------------------------------------+
                                              |   Update PostgreSQL + status + metadata        |
                                              +------------------------------------------------+
