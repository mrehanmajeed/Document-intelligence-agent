import pandas as pd
from pathlib import Path
import io

OUTPUT_FILE = "output/results.xlsx"

def export_to_excel(data, anomalies=None):
    if anomalies is None:
        anomalies = []
        
    row = {
        **data,
        "anomalies": ", ".join(anomalies)
    }

    file_exists = Path(OUTPUT_FILE).exists()

    if file_exists:
        df = pd.read_excel(OUTPUT_FILE)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_excel(OUTPUT_FILE, index=False)

def export_batch_to_excel_bytes(results_list):
    rows = []
    for item in results_list:
        data = item.get("data", {})
        anomalies = item.get("anomalies", [])
        fraud_risk_score = item.get("fraud_score", 0)
        confidence_score = item.get("confidence", 0)
        risk_label = item.get("label", "")
        
        row = {
            "file_name": item.get("file_name", ""),
            "document_type": data.get("document_type", ""),
            "sender": data.get("sender", ""),
            "receiver": data.get("receiver", ""),
            "amount": data.get("amount") or data.get("contract_value", ""),
            "fraud_risk_score": fraud_risk_score,
            "confidence_score": confidence_score,
            "risk_label": risk_label,
            "anomalies": ", ".join(anomalies)
        }
        rows.append(row)

    if not rows:
        return None
        
    df = pd.DataFrame(rows)
    
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    return excel_buffer.getvalue()