"""
AI NHS Navigator Service
------------------------
Mode A: General NHS navigation questions answered from knowledge base.
Mode B: NHS letter / document explanation.

Uses Gemini for generation, with static knowledge base for grounding.
Refuses clinical diagnosis / treatment advice.
"""

import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL
from services.knowledge_base import NHS_KNOWLEDGE_BASE, DISCLAIMER

genai.configure(api_key=GEMINI_API_KEY)

# Topics that should be refused (clinical advice)
REFUSED_PATTERNS = [
    "diagnos", "cancer", "do i have", "am i sick", "stop taking", "stop medication",
    "change my dose", "should i take", "what treatment", "cure", "surgery",
]

_NAVIGATOR_PROMPT = """
You are ORBIS NHS Navigator — a helpful assistant for immigrants and refugees in England.
Your role is strictly limited to helping users:
- Understand NHS services and how to access them
- Know their healthcare rights
- Prepare for appointments
- Understand NHS letters and documents
- Know when to use GP, NHS 111, or A&E

You must NOT provide clinical diagnoses, treatment recommendations, or medication advice.
If asked about diagnosis or treatment, respond: "I'm not able to advise on medical diagnoses or treatments. Please speak to your GP or call NHS 111."

Relevant NHS guidance for this question:
{context}

User's question (may be in any language): {question}

Instructions:
1. Answer in the SAME language as the user's question.
2. Be clear, warm, and simple — the user may have limited English.
3. Structure your answer as:
   - Direct answer (2–4 sentences)
   - What to do next (bullet points if helpful)
   - Where to get more help (with contact or link if available)
4. End with a brief disclaimer about seeking professional advice if relevant.
5. Keep the total response under 250 words.
"""

_LETTER_PROMPT = """
You are ORBIS NHS Letter Explainer — you help immigrants and refugees understand NHS letters and documents.

The user has shared the following NHS document text:
{document_text}

User's question or request: {question}

Instructions:
1. Identify what type of document this is (appointment letter, test result, referral, prescription, etc.).
2. Explain it in simple, clear language in the SAME language as the user's question.
3. Extract and highlight:
   - Date, time, and location of any appointment
   - What the user needs to bring or prepare
   - Any action required before the appointment
   - Any important deadlines
4. Use plain language — avoid medical jargon.
5. End with: "If anything is unclear, call the number on the letter or ask your GP."
6. Keep the total response under 300 words.
"""


def _retrieve_context(question: str) -> str:
    """Simple keyword-based retrieval from knowledge base."""
    q_lower = question.lower()
    matched = []
    for entry in NHS_KNOWLEDGE_BASE:
        score = sum(1 for kw in entry["keywords"] if kw in q_lower)
        if score > 0:
            matched.append((score, entry["content"]))
    matched.sort(key=lambda x: x[0], reverse=True)
    # Return top 2 matches
    top = [c for _, c in matched[:2]]
    if not top:
        # Fallback: return general rights + GP info
        top = [NHS_KNOWLEDGE_BASE[0]["content"], NHS_KNOWLEDGE_BASE[6]["content"]]
    return "\n\n---\n\n".join(top)


def _is_refused(question: str) -> bool:
    q_lower = question.lower()
    return any(p in q_lower for p in REFUSED_PATTERNS)


def answer_navigation_question(question: str) -> dict:
    """Mode A: Answer a general NHS navigation question."""
    if _is_refused(question):
        return {
            "answer": (
                "I'm not able to advise on medical diagnoses or treatments. "
                "Please speak to your GP or call NHS 111 (free, 24/7, interpreters available)."
            ),
            "mode": "refused",
            "disclaimer": DISCLAIMER,
        }

    context = _retrieve_context(question)
    model = genai.GenerativeModel(GEMINI_MODEL)
    prompt = _NAVIGATOR_PROMPT.format(context=context, question=question)
    response = model.generate_content(prompt)

    return {
        "answer": response.text.strip(),
        "mode": "navigator",
        "disclaimer": DISCLAIMER,
    }


def explain_letter(document_text: str, question: str = "") -> dict:
    """Mode B: Explain an NHS letter or document."""
    if not question:
        question = "Please explain this document to me in simple language."

    model = genai.GenerativeModel(GEMINI_MODEL)
    prompt = _LETTER_PROMPT.format(
        document_text=document_text[:3000],  # cap to avoid token overflow
        question=question,
    )
    response = model.generate_content(prompt)

    return {
        "answer": response.text.strip(),
        "mode": "letter_explainer",
        "disclaimer": DISCLAIMER,
    }
