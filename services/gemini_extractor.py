import json
import google.generativeai as genai

from config import GEMINI_API_KEY
from utils.prompts import EXTRACTION_PROMPT

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def extract_fields(document_text):

    prompt = f"""
    {EXTRACTION_PROMPT}

    DOCUMENT:

    {document_text[:15000]}
    """

    response = model.generate_content(prompt)

    cleaned = (
        response.text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    # Print raw JSON to the backend console for developer debugging
    print(f"\n--- [BACKEND DEBUG] Extracted JSON Response ---\n{cleaned}\n-----------------------------------------------\n")

    return json.loads(cleaned)