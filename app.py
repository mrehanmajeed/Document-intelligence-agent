import os
import json
import streamlit as st
import concurrent.futures

from services.risk_engine import (
    calculate_confidence,
    fraud_risk_score,
    explain_anomalies,
    risk_label
)
from services.pdf_reader import extract_text
from services.gemini_extractor import extract_fields
from services.anomaly_detector import detect_anomalies
from services.excel_exporter import export_batch_to_excel_bytes

# Page Config
st.set_page_config(
    page_title="Document Intelligence Agent",
    page_icon="📄",
    layout="wide"
)

# Title
st.title("📄 Document Intelligence Agent")
st.markdown("Automated extractions and risk assessments for Contracts, Invoices, and Reports. All files are processed in-memory and discarded after the session.")

def process_single_document(file_bytes, file_name):
    # Process a single file pipeline using purely in-memory buffers
    try:
        text = extract_text(file_bytes)
        if not text.strip():
            return {"file_name": file_name, "error": "No text found. May be empty or unreadable.", "success": False}
        
        data = extract_fields(text)
        anomalies = detect_anomalies(data)
        
        confidence = calculate_confidence(data, anomalies)
        fraud_score = fraud_risk_score(data, anomalies)
        explanations = explain_anomalies(data, anomalies)
        label = risk_label(fraud_score)
        
        return {
            "file_name": file_name,
            "success": True,
            "data": data,
            "anomalies": anomalies,
            "confidence": confidence,
            "fraud_score": fraud_score,
            "explanations": explanations,
            "label": label
        }
    except Exception as e:
        return {"file_name": file_name, "error": str(e), "success": False}

# UI Toggle for mode
mode = st.radio("Processing Mode", ["Single File", "Batch Processing (Up to 10 files)"], horizontal=True)
is_batch = "Batch" in mode

uploaded_files = st.file_uploader(
    "Upload PDF Document(s)", 
    type=["pdf"], 
    accept_multiple_files=is_batch
)

if uploaded_files:
    # Ensure it's a list for unified handling
    files_to_process = uploaded_files if isinstance(uploaded_files, list) else [uploaded_files]
    
    if len(files_to_process) > 10:
        st.warning("You uploaded more than 10 files. Processing only the first 10 to respect rate limits.")
        files_to_process = files_to_process[:10]

    if st.button("Process Documents", type="primary"):
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Load all files into memory
        in_memory_files = []
        for uf in files_to_process:
            file_bytes = uf.read()
            in_memory_files.append((file_bytes, uf.name))

        # Parallel processing using ThreadPoolExecutor
        status_text.text(f"Processing {len(in_memory_files)} files...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_doc = {executor.submit(process_single_document, f_bytes, name): name for f_bytes, name in in_memory_files}
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_doc):
                res = future.result()
                results.append(res)
                completed += 1
                progress_bar.progress(completed / len(in_memory_files))
                status_text.text(f"Processed {completed}/{len(in_memory_files)} files.")

        status_text.success("Processing Complete!")
        
        valid_results = []
        
        # Display Results
        for res in results:
            with st.expander(f"📄 {res['file_name']}", expanded=True):
                if not res.get("success"):
                    st.error(f"Failed to process: {res.get('error')}")
                    continue
                
                valid_results.append(res)
                
                data = res["data"]
                label = res["label"]
                conf = res["confidence"]
                f_score = res["fraud_score"]
                
                # Metric Colors based on Risk
                risk_color = "red" if "HIGH" in label or "CRITICAL" in label else "orange" if "MEDIUM" in label else "green"
                
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Document Type", data.get("document_type", "N/A"))
                col2.metric("Sender", data.get("sender", "N/A"))
                col3.metric("Receiver", data.get("receiver", "N/A"))
                col4.metric("Amount", data.get("amount") or data.get("contract_value") or "N/A")
                col5.markdown(f"**Risk Profile**<br/><span style='color:{risk_color}; font-weight:bold;'>{label} ({f_score}/100)</span>", unsafe_allow_html=True)
                
                # Simple toggle for detailed info
                if res.get("anomalies"):
                    st.warning("⚠ Anomalies Detected: " + " | ".join(res["anomalies"]))
                    
        # Export logic exclusively for this session in memory
        if valid_results:
            excel_bytes = export_batch_to_excel_bytes(valid_results)
            if excel_bytes:
                st.download_button(
                    label="⬇ Download Combined Excel Report",
                    data=excel_bytes,
                    file_name="risk_assessment_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
