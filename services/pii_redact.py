"""
PII Redaction Service
---------------------
Redacts obvious personally identifiable information before sending
text to external AI/translation services.

Redacted fields:
- NHS numbers (3-3-4 digit format)
- UK phone numbers
- Dates of birth patterns
- Full name patterns (Title + Name)
- UK postcodes
- Email addresses

Clinical content (conditions, medications, allergies) is preserved.
"""

import re

# NHS number: 3-3-4 digits e.g. 123 456 7890 or 1234567890
_NHS_NUMBER = re.compile(r'\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b')

# UK phone numbers
_PHONE = re.compile(r'\b(\+44\s?|0)[\d\s\-\(\)]{9,13}\b')

# Dates: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY, Month DD YYYY, DD Month YYYY
_DATE = re.compile(
    r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b'
    r'|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b'
    r'|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b',
    re.IGNORECASE
)

# Name patterns: Title + capitalised words
_NAME = re.compile(
    r'\b(?:Mr|Mrs|Ms|Miss|Dr|Prof|Sir)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b'
)

# UK postcodes
_POSTCODE = re.compile(
    r'\b[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}\b',
    re.IGNORECASE
)

# Email addresses
_EMAIL = re.compile(r'\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b', re.IGNORECASE)

# Street addresses (number + street name)
_ADDRESS = re.compile(r'\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Close|Cl|Way|Place|Pl)\b', re.IGNORECASE)


def redact_pii(text: str) -> tuple[str, list[str]]:
    """
    Redact PII from text. Returns (redacted_text, list_of_redaction_types).
    Clinical content is preserved.
    """
    redacted = []
    result = text

    if _NHS_NUMBER.search(result):
        result = _NHS_NUMBER.sub('[NHS-NUMBER]', result)
        redacted.append('nhs_number')

    if _PHONE.search(result):
        result = _PHONE.sub('[PHONE]', result)
        redacted.append('phone')

    if _DATE.search(result):
        result = _DATE.sub('[DATE]', result)
        redacted.append('date')

    if _NAME.search(result):
        result = _NAME.sub('[NAME]', result)
        redacted.append('name')

    if _POSTCODE.search(result):
        result = _POSTCODE.sub('[POSTCODE]', result)
        redacted.append('postcode')

    if _EMAIL.search(result):
        result = _EMAIL.sub('[EMAIL]', result)
        redacted.append('email')

    if _ADDRESS.search(result):
        result = _ADDRESS.sub('[ADDRESS]', result)
        redacted.append('address')

    return result, redacted
