"""
Health Passport Service (Gemini)
---------------------------------
Converts translated English text into a structured Health Passport JSON.
"""

import json
import google.generativeai as genai
from models import PassportSchema
from config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)

_PASSPORT_PROMPT = """
You are a medical document summariser helping refugee patients.
Given the following English medical text, extract and return ONLY a JSON object
with these exact fields. Write ALL text values in {language}.

{{
  "document_type": "<discharge_summary | prescription | referral | test_result | other>",
  "document_date": "<YYYY-MM-DD or null>",
  "conditions": ["list of diagnosed conditions"],
  "medications": ["name dose frequency"],
  "allergies": ["substance and reaction"],
  "tests": ["test name and result"],
  "follow_up": ["follow-up instructions"],
  "red_flags": ["urgent warnings the patient must know"],
  "summary_plain_english": "2-3 sentence summary in {language}"
}}

Medical text:
{text}

Return ONLY valid JSON. No explanation, no markdown.
"""


def generate_passport(english_text: str, user_lang: str = "en") -> PassportSchema:
    """
    Call Gemini to generate structured passport from English translation.
    Output language is controlled by user_lang (DeepL/ISO code).
    Returns PassportSchema.
    """
    # Map language codes to readable names for the prompt
    lang_names = {
        "zh": "Simplified Chinese", "en": "English", "es": "Spanish",
        "pl": "Polish", "ro": "Romanian", "ar": "Arabic", "fr": "French",
        "fa": "Persian", "uk": "Ukrainian", "ru": "Russian", "tr": "Turkish",
    }
    language = lang_names.get(user_lang.lower(), "English")

    model = genai.GenerativeModel(GEMINI_MODEL)
    prompt = _PASSPORT_PROMPT.format(text=english_text, language=language)
    response = model.generate_content(prompt)
    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)
    return PassportSchema(**data)
