"""
AI Risk Check Service (Gemini)
------------------------------
Two-stage validation of translated medical text.

Stage 1: Faithful translation check
Stage 2: Cross-check original vs translation for medical safety issues
"""

import json
import google.generativeai as genai
from models import RiskCheckResult
from config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)

_CHECK_PROMPT = """
You are a medical translation safety reviewer.
Compare the original text and the English translation below.
Identify any of the following issues:
- Missing or changed medication names
- Dosage discrepancies
- Missing dates
- Missing allergy information
- Ambiguous or changed diagnoses

Original text:
{original}

English translation:
{translation}

Respond with ONLY a valid JSON object in this exact format:
{{
  "risk_score": "low",
  "issues": [],
  "requires_review": false
}}

risk_score must be one of: "low", "medium", "high"
requires_review must be true if risk_score is "medium" or "high"
issues is a list of strings describing each problem found.
"""


def check_translation_risk(
    original_text: str,
    english_translation: str,
) -> RiskCheckResult:
    """
    Run Gemini-based risk check comparing original and translation.
    Returns RiskCheckResult.
    """
    model = genai.GenerativeModel(GEMINI_MODEL)

    prompt = _CHECK_PROMPT.format(
        original=original_text,
        translation=english_translation,
    )

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Strip markdown code fences if Gemini wraps in ```json ... ```
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)
    return RiskCheckResult(**data)
