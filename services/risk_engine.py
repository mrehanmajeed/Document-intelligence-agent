def calculate_confidence(data, anomalies):

    score = 100

    for f in ["sender", "receiver", "date"]:
        if not data.get(f):
            score -= 15

    if not data.get("amount") and not data.get("contract_value"):
        score -= 20

    score -= len(anomalies) * 5

    return max(0, min(100, score))


def fraud_risk_score(data, anomalies):

    score = 0

    score += len(anomalies) * 15

    raw_amount = data.get("amount") or data.get("contract_value")

    if raw_amount is not None:
        try:
            # Safer parsing for amounts that might include characters like 'USD'
            import re
            cleaned_amount = re.sub(r'[^\d.]', '', str(raw_amount))
            if cleaned_amount:
                value = float(cleaned_amount)

                if value > 100000:
                    score += 20
                if value > 500000: # Note: This will add a cumulative 50 for > 500k
                    score += 30
            else:
                score += 25
        except:
            score += 25
    else:
        score += 25

    if data.get("sender_valid") is False:
        score += 20

    if data.get("receiver_valid") is False:
        score += 20

    for f in ["sender", "receiver", "date"]:
        if not data.get(f) or str(data.get(f)).strip() == "":
            score += 15

    return max(0, min(100, int(score)))


def explain_anomalies(data, anomalies):

    explanations = []

    for a in anomalies:

        a_lower = a.lower()

        if "amount" in a_lower:
            explanations.append(
                "Financial inconsistency detected in monetary values."
            )

        elif "date" in a_lower:
            explanations.append(
                "Date format is invalid or inconsistent with expected standards."
            )

        elif "sender" in a_lower or "receiver" in a_lower:
            explanations.append(
                "Company identity could not be verified or appears suspicious."
            )

        else:
            explanations.append(
                "Document anomaly detected requiring manual review."
            )

    return explanations


def risk_label(score):

    if score < 30:
        return "LOW RISK"
    elif score < 60:
        return "MEDIUM RISK"
    elif score < 80:
        return "HIGH RISK"
    else:
        return "CRITICAL RISK"