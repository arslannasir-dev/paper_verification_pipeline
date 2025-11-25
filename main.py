import traceback
from db.postgres import fetch_pending_records, update_record, mark_error
from modules.downloader import extract_text
from modules.text_cleaner import clean_text
from modules.drug_extractor import extract_drug_names
from modules.fda_checker import check_all_drugs
from modules.peer_review_checker import is_peer_reviewed
from modules.relevance_checker import check_relevance
from modules.tier_classifier import tier_details


def process_record(row):
    record_id = row["id"]
    url        = row["url"]
    title_or_text = row["citation_text"]
    doi        = row["doi"]

    print("\n====================================")
    print(f"📄 Processing Record ID: {record_id}")
    print("====================================")

    try:
        # ----------------------------------------------------------
        # STEP 1: Download full paper (PDF/HTML)
        # ----------------------------------------------------------
        print("➡️  Step 1: Downloading paper...")
        raw_text = extract_text(url)

        if not raw_text or len(raw_text) < 200:
            raise Exception("Unable to fetch sufficient text from URL.")

        # ----------------------------------------------------------
        # STEP 2: Clean text
        # ----------------------------------------------------------
        print("➡️  Step 2: Cleaning text...")
        cleaned_text = clean_text(raw_text)

        # ----------------------------------------------------------
        # STEP 3: Extract drugs
        # ----------------------------------------------------------
        print("➡️  Step 3: Extracting drug names...")
        drug_list = extract_drug_names(cleaned_text)

        # ----------------------------------------------------------
        # STEP 4: FDA Check
        # ----------------------------------------------------------
        print("➡️  Step 4: Checking FDA approval...")
        fda_result = check_all_drugs(drug_list)
        is_fda = fda_result["is_fda_approved"]
        approved_drugs = fda_result["approved_drugs"]

        # ----------------------------------------------------------
        # STEP 5: Peer Review Check
        # ----------------------------------------------------------
        print("➡️  Step 5: Checking peer review status...")
        peer_result = is_peer_reviewed(title=row["citation_text"], doi=doi)
        is_peer = peer_result["is_peer_reviewed"]

        # ----------------------------------------------------------
        # STEP 6: Relevance Check
        # ----------------------------------------------------------
        print("➡️  Step 6: Checking relevance to keyword...")
        keyword = row["citation_source"] or row["data_source"] or ""
        rel_result = check_relevance(keyword, cleaned_text)

        is_relevant = rel_result["is_relevant"]
        relevance_score = rel_result["relevance_score"]

        # ----------------------------------------------------------
        # STEP 7: Tier Assignment
        # ----------------------------------------------------------
        print("➡️  Step 7: Assigning tier...")
        tier_info = tier_details(is_fda, is_peer)
        final_tier = tier_info["tier"]

        # ----------------------------------------------------------
        # STEP 8: Update DB
        # ----------------------------------------------------------
        print("➡️  Step 8: Updating database...")

        update_record(record_id, {
            "is_relevant": is_relevant,
            "relevance_score": relevance_score,
            "detected_drugs": ", ".join(drug_list) if drug_list else None,
            "is_fda_approved": is_fda,
            "approved_drugs": ", ".join(approved_drugs) if approved_drugs else None,
            "is_peer_reviewed": is_peer,
            "tier": final_tier,
            "review_status": "completed",
        })

        print(f"✅ Completed Record ID: {record_id} → Tier: {final_tier}")

    except Exception as e:
        print(f"❌ ERROR processing record {record_id}: {e}")
        mark_error(record_id, str(e))
        traceback.print_exc()


def run_pipeline(batch_size=10):
    print("\n====================================")
    print("🚀 STARTING AUTOMATED PAPER PIPELINE")
    print("====================================")

    rows = fetch_pending_records(limit=batch_size)

    if not rows:
        print("No unreviewed records found.")
        return

    for row in rows:
        process_record(row)

    print("\n🎉 Pipeline Execution Completed\n")


if __name__ == "__main__":
    run_pipeline(batch_size=10)
