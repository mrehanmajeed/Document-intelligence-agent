from datetime import datetime


def parse_amount(value):
    """
    Normalizes and converts amount safely.
    """
    if value is None:
        return None

    try:
        cleaned = str(value)
        cleaned = cleaned.replace("$", "").replace(",", "").strip()

        if cleaned == "":
            return None

        return float(cleaned)

    except:
        return None


def detect_anomalies(data):

    anomalies = []

    # -------------------------
    # 1. AMOUNT / CONTRACT VALUE CHECK
    # -------------------------

    raw_amount = (
        data.get("amount")
        or data.get("contract_value")
        or ""
    )

    amount = parse_amount(raw_amount)

    if amount is None:
        anomalies.append("Amount could not be validated")
    else:
        if amount < 0:
            anomalies.append("Negative amount detected")

        if amount > 100000:
            anomalies.append("Unusually high amount")

    # -------------------------
    # 2. DATE VALIDATION
    # -------------------------

    date = data.get("date", "")

    try:
        # safer parsing for ISO format only
        parsed_date = datetime.strptime(date, "%Y-%m-%d")

        if parsed_date > datetime.now():
            anomalies.append("Future date detected")

    except:
        anomalies.append("Invalid date format")

    # -------------------------
    # 3. COMPANY VALIDATION (INDEPENDENT BLOCK)
    # -------------------------

    sender_valid = data.get("sender_valid", True)
    receiver_valid = data.get("receiver_valid", True)

    sender_reason = data.get("validation_reason", "")
    receiver_reason = data.get("validation_reason", "")

    if not sender_valid:
        if sender_reason:
            anomalies.append(f"Sender invalid: {sender_reason}")
        else:
            anomalies.append("Suspicious sender company")

    if not receiver_valid:
        if receiver_reason:
            anomalies.append(f"Receiver invalid: {receiver_reason}")
        else:
            anomalies.append("Suspicious receiver company")

    # -------------------------
    # 4. MISSING CORE FIELDS CHECK
    # -------------------------

    if not data.get("sender"):
        anomalies.append("Missing sender company")

    if not data.get("receiver"):
        anomalies.append("Missing receiver company")

    if not data.get("document_type"):
        anomalies.append("Document type not detected")

    return anomalies