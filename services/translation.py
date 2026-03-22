"""
Translation Service
-------------------
Translates extracted OCR text using DeepL API.

Pipeline:
  1. Detect source language (via langdetect, confirmed by DeepL)
  2. Translate to English (for clinicians)
  3. Optionally translate to user's preferred language (for patient review)

DeepL language codes: https://developers.deepl.com/docs/resources/supported-languages
"""

from config import DEEPL_API_KEY
import deepl

# Singleton DeepL client
_deepl_client: deepl.DeepLClient | None = None


def _get_deepl() -> deepl.DeepLClient:
    global _deepl_client
    if _deepl_client is None:
        if not DEEPL_API_KEY:
            raise RuntimeError("DEEPL_API_KEY is not configured.")
        _deepl_client = deepl.DeepLClient(DEEPL_API_KEY)
    return _deepl_client


# ── Language detection ────────────────────────────────────────────────────────

def detect_language(text: str) -> tuple[str, float]:
    """
    Returns (language_code, confidence).
    Uses langdetect; falls back to "unknown" with 0.0 on failure.
    """
    try:
        from langdetect import detect_langs
        results = detect_langs(text)
        if results:
            top = results[0]
            return top.lang, round(top.prob, 2)
    except Exception:
        pass
    return "unknown", 0.0


# ── Main translation entry points ─────────────────────────────────────────────

def translate_to_english(text: str, source_lang: str = None) -> str:
    """Translate text to English (EN-GB) using DeepL."""
    return _deepl_translate(text, target_lang="EN-GB", source_lang=source_lang)


def translate_to_language(text: str, target_lang: str, source_lang: str = "EN") -> str:
    """
    Translate English text to user's preferred language.
    target_lang should be a DeepL language code, e.g. "ZH", "AR", "FR".
    """
    return _deepl_translate(text, target_lang=target_lang.upper(), source_lang=source_lang)


# ── DeepL implementation ──────────────────────────────────────────────────────

# Map common ISO 639-1 codes → DeepL target language codes
_LANG_CODE_MAP = {
    "zh": "ZH-HANS",   # Simplified Chinese
    "zh-cn": "ZH-HANS",
    "zh-tw": "ZH-HANT",
    "ar": "AR",
    "fr": "FR",
    "de": "DE",
    "es": "ES",
    "pt": "PT-PT",
    "ru": "RU",
    "ja": "JA",
    "ko": "KO",
    "tr": "TR",
    "fa": "FA",         # Farsi/Persian
    "uk": "UK",
    "pl": "PL",
    "it": "IT",
    "nl": "NL",
    "en": "EN-GB",
}


def _deepl_translate(text: str, target_lang: str, source_lang: str = None) -> str:
    """
    Call DeepL to translate text.
    Normalises language codes before sending.
    """
    client = _get_deepl()

    # Normalise target lang
    normalised_target = _LANG_CODE_MAP.get(target_lang.lower(), target_lang.upper())

    # Normalise source lang (DeepL accepts None for auto-detect)
    normalised_source = None
    if source_lang and source_lang != "unknown":
        normalised_source = _LANG_CODE_MAP.get(source_lang.lower(), source_lang.upper())
        # DeepL source lang uses 2-letter codes (no region suffix)
        if "-" in normalised_source:
            normalised_source = normalised_source.split("-")[0]

    result = client.translate_text(
        text,
        target_lang=normalised_target,
        source_lang=normalised_source,
    )

    # result can be a single TextResult or list; handle both
    if isinstance(result, list):
        return result[0].text
    return result.text
