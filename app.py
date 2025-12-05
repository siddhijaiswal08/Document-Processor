import streamlit as st
import time
import json
import traceback
from pathlib import Path
from src.pipeline.mod_01_splitting import split_pdf_packet
from src.pipeline.mod_02_classification import classify_document_chunk
from src.pipeline.mod_03_extraction import extract_key_values
from src.pipeline.mod_04_validation import validate_packet_data

# 🌐 Streamlit Page Setup
st.set_page_config(page_title="Document Classification Agent v2",
                   page_icon="🧾", layout="wide")

st.title("🚀 Intelligent Claims Packet Processor — v2")
st.caption("Automatically splits, classifies, extracts, and validates insurance-related documents.")

# 🎛️ Sidebar Settings
st.sidebar.header("⚙️ Settings")
SIMILARITY = st.sidebar.slider("Similarity threshold (split)", 0.20, 0.95, 0.60)
CONSECUTIVE = st.sidebar.slider("Consecutive low pages to split", 1, 4, 2)
st.sidebar.markdown("---")
st.sidebar.info("🔍 Adjust thresholds for better page grouping accuracy.")

uploaded_file = st.file_uploader("📤 Upload a multi-page claims PDF", type="pdf")

if uploaded_file is not None:
    pdf_bytes = uploaded_file.getvalue()

    if st.button("▶️ Process Packet", use_container_width=True):
        try:
            t0 = time.time()

            # STEP 1: Splitting
            with st.spinner("🪓 Step 1/4: Splitting PDF into logical documents..."):
                logical_docs = split_pdf_packet(
                    pdf_bytes,
                    similarity_threshold=SIMILARITY,
                    consecutive_low_pages=CONSECUTIVE
                )
            st.success(f"✅ Found {len(logical_docs)} logical documents.")

            # STEP 2: Classification
            with st.spinner("🧩 Step 2/4: Classifying document types..."):
                classified_docs = []
                for i, doc_chunk in enumerate(logical_docs, start=1):
                    chunk_images = [page[2] for page in doc_chunk]
                    chunk_texts = [page[1] for page in doc_chunk]
                    doc_type, confidence = classify_document_chunk(chunk_images, chunk_texts)
                    start_page = doc_chunk[0][0] + 1
                    end_page = doc_chunk[-1][0] + 1
                    page_range = f"Pages {start_page}-{end_page}" if start_page != end_page else f"Page {start_page}"
                    classified_docs.append({
                        "id": i,
                        "doc_type": doc_type,
                        "confidence": confidence,
                        "page_range": page_range,
                        "chunk_data": doc_chunk
                    })
            st.success("✅ Document classification complete.")

            # STEP 3: Extraction
            with st.spinner("📄 Step 3/4: Extracting key information..."):
                extracted_data_list = []
                for doc in classified_docs:
                    chunk_images = [page[2] for page in doc["chunk_data"]]
                    chunk_texts = [page[1] for page in doc["chunk_data"]]
                    extracted_data = extract_key_values(chunk_images, doc["doc_type"], chunk_texts)
                    doc["extracted_data"] = extracted_data
                    extracted_data_list.append({
                        "number": doc["id"],
                        "type": doc["doc_type"],
                        "data": extracted_data
                    })
            st.success("✅ Key-value data extraction complete.")

            # STEP 4: Validation
            with st.spinner("🧠 Step 4/4: Running validation checks..."):
                validation_status, validation_flags = validate_packet_data(extracted_data_list)
            st.success("✅ Validation complete!")

            t1 = time.time()
            st.markdown("---")

            # 🧾 Display Results
            col1, col2 = st.columns([1.2, 1])

            # 🧮 Left: Documents + Validation
            with col1:
                st.subheader("📊 Validation Summary")
                if validation_status == "Approved":
                    st.success(f"✅ Status: {validation_status}")
                else:
                    st.error(f"⚠️ Status: {validation_status}")

                if validation_flags:
                    for flag in validation_flags:
                        st.warning(f"⚡ {flag}")
                else:
                    st.info("No validation issues found.")

                st.markdown("---")
                st.subheader("📑 Discovered Documents")

                for doc in classified_docs:
                    doc_num = doc['id']
                    doc_type = doc['doc_type']
                    conf = doc['confidence']
                    pages = doc['page_range']

                    st.markdown(
                        f"""
                        <div style='padding: 15px; border-radius: 12px; margin-bottom:10px;
                                    background-color:#f8f9fa; border-left:6px solid #4B9CD3'>
                            <h5>📘 <b>Document {doc_num}: {doc_type}</b></h5>
                            <p style='margin:2px 0;color:#666;'>📄 {pages}</p>
                            <p style='margin:2px 0;color:#888;'>🔹 Confidence: {conf*100:.1f}%</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    with st.expander(f"🧾 View Extracted Data for Document {doc_num}"):
                        st.json(doc['extracted_data'])

            # 💾 Right: JSON Export
            with col2:
                st.subheader("📦 Raw Extracted JSON (Numbered)")
                st.json(extracted_data_list)

                result_json = {
                    "total_documents": len(classified_docs),
                    "validation": {
                        "status": validation_status,
                        "flags": validation_flags
                    },
                    "documents": extracted_data_list
                }

                st.download_button(
                    "⬇️ Download Results as JSON",
                    data=json.dumps(result_json, indent=2),
                    file_name="document_results.json",
                    mime="application/json",
                    use_container_width=True
                )

                st.caption(f"⏱️ Processing time: {t1 - t0:.2f} seconds")

        except Exception as e:
            st.error("❌ Processing failed. See error trace below.")
            st.text(traceback.format_exc())
