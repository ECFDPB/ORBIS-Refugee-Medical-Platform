"""
Navigator Router
----------------
POST /navigator/ask       — Mode A: general NHS navigation question
POST /navigator/explain   — Mode B: explain an NHS letter (by document_id or raw text)
POST /navigator/help      — store a "need more help" request in DB
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from database import get_db
from services.navigator import answer_navigation_question, explain_letter

router = APIRouter(prefix="/navigator", tags=["navigator"])


def _get_user(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header.")
    token = authorization.split(" ", 1)[1]
    db = get_db()
    res = db.auth.get_user(token)
    if not res.user:
        raise HTTPException(401, "Invalid token.")
    return res.user


# ── Request models ─────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str

class ExplainRequest(BaseModel):
    question: Optional[str] = ""
    document_id: Optional[str] = None
    raw_text: Optional[str] = None

class HelpRequest(BaseModel):
    message: str


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/ask")
async def ask_navigator(
    body: AskRequest,
    authorization: Optional[str] = Header(None),
):
    """Mode A — answer a general NHS navigation question."""
    user = _get_user(authorization)
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    result = answer_navigation_question(body.question)
    return result


@router.post("/explain")
async def explain_document(
    body: ExplainRequest,
    authorization: Optional[str] = Header(None),
):
    """Mode B — explain an NHS letter/document."""
    user = _get_user(authorization)
    text = ""

    if body.document_id:
        db = get_db()
        row = (
            db.table("documents")
            .select("id")
            .eq("id", body.document_id)
            .eq("user_id", user.id)
            .single()
            .execute()
        )
        if not row.data:
            raise HTTPException(status_code=404, detail="Document not found.")
        # fetch text from document_texts
        txt_row = (
            db.table("document_texts")
            .select("english_translation, user_language_translation")
            .eq("document_id", body.document_id)
            .single()
            .execute()
        )
        if txt_row.data:
            text = txt_row.data.get("english_translation") or txt_row.data.get("user_language_translation") or ""
    elif body.raw_text:
        text = body.raw_text
    else:
        raise HTTPException(status_code=400, detail="Provide document_id or raw_text.")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Document has no readable text.")

    result = explain_letter(text, body.question or "")
    return result


@router.post("/help")
async def request_more_help(
    body: HelpRequest,
    authorization: Optional[str] = Header(None),
):
    """Store a 'need more help' request."""
    user = _get_user(authorization)
    db = get_db()
    db.table("help_requests").insert({
        "user_id": user.id,
        "message": body.message,
    }).execute()
    return {"status": "received", "message": "Your request has been noted. A moderator will follow up."}
