"""
Passport Router — retrieve, confirm, delete, merged view, edit validation
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from models import PassportOut, PassportConfirm, PassportSchema, RiskCheckOut
from database import get_db
from datetime import datetime
import google.generativeai as genai
import json
from config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)

router = APIRouter(prefix="/passport", tags=["passport"])


def _get_user(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header.")
    token = authorization.split(" ", 1)[1]
    db = get_db()
    res = db.auth.get_user(token)
    if not res.user:
        raise HTTPException(401, "Invalid token.")
    return res.user


def _verify_ownership(db, document_id: str, user_id: str):
    doc = db.table("documents").select("id").eq("id", document_id).eq("user_id", user_id).single().execute()
    if not doc.data:
        raise HTTPException(404, "Document not found.")


@router.get("/merged")
async def get_merged_passport(authorization: Optional[str] = Header(None)):
    """Merge all confirmed passports for a user into one unified view."""
    user = _get_user(authorization)
    db = get_db()

    docs = db.table("documents").select("id").eq("user_id", user.id).execute()
    if not docs.data:
        raise HTTPException(404, "No documents found.")

    doc_ids = [d["id"] for d in docs.data]
    passports = db.table("health_passports").select("structured_json").in_("document_id", doc_ids).execute()

    if not passports.data:
        raise HTTPException(404, "No passports found.")

    merged = {
        "conditions": [], "medications": [], "allergies": [],
        "tests": [], "follow_up": [], "red_flags": [], "summary_plain_english": ""
    }

    for p in passports.data:
        sj = p["structured_json"]
        for key in ["conditions", "medications", "allergies", "tests", "follow_up", "red_flags"]:
            items = sj.get(key) or []
            for item in items:
                if item and item not in merged[key]:
                    merged[key].append(item)
        if sj.get("summary_plain_english"):
            merged["summary_plain_english"] = sj["summary_plain_english"]

    return merged


@router.get("/{document_id}/risk", response_model=RiskCheckOut)
async def get_risk_check(document_id: str, authorization: Optional[str] = Header(None)):
    user = _get_user(authorization)
    db = get_db()
    _verify_ownership(db, document_id, user.id)

    row = db.table("risk_checks").select("*").eq("document_id", document_id).single().execute()
    if not row.data:
        raise HTTPException(404, "Risk check not yet available.")

    return RiskCheckOut(**row.data)


@router.get("/{document_id}", response_model=PassportOut)
async def get_passport(document_id: str, authorization: Optional[str] = Header(None)):
    user = _get_user(authorization)
    db = get_db()
    _verify_ownership(db, document_id, user.id)

    row = db.table("health_passports").select("*").eq("document_id", document_id).single().execute()
    if not row.data:
        raise HTTPException(404, "Passport not yet generated.")

    return _row_to_passport(row.data)


@router.post("/confirm", response_model=PassportOut)
async def confirm_passport(payload: PassportConfirm, authorization: Optional[str] = Header(None)):
    user = _get_user(authorization)
    db = get_db()
    _verify_ownership(db, payload.document_id, user.id)

    row = db.table("health_passports").select("*").eq("document_id", payload.document_id).single().execute()
    if not row.data:
        raise HTTPException(404, "Passport not found.")

    update_data = {"patient_confirmed": payload.confirmed}

    # If user edited fields, merge them in
    if payload.edited_fields:
        update_data["structured_json"] = payload.edited_fields.model_dump()

    updated = db.table("health_passports").update(update_data).eq("document_id", payload.document_id).execute()
    return _row_to_passport(updated.data[0])


@router.delete("/{document_id}")
async def delete_passport(document_id: str, authorization: Optional[str] = Header(None)):
    user = _get_user(authorization)
    db = get_db()
    _verify_ownership(db, document_id, user.id)

    # Delete passport, document_texts, document (cascades via FK)
    db.table("health_passports").delete().eq("document_id", document_id).execute()
    db.table("document_texts").delete().eq("document_id", document_id).execute()
    db.table("documents").delete().eq("id", document_id).execute()

    return {"message": "Document and passport deleted."}


def _row_to_passport(row: dict) -> PassportOut:
    return PassportOut(
        id=row["id"],
        document_id=row["document_id"],
        structured_json=PassportSchema(**row["structured_json"]),
        patient_confirmed=row["patient_confirmed"],
        generated_at=row["generated_at"],
    )


# ── Edit validation ───────────────────────────────────────────────────────────

_VALIDATE_PROMPT = """
You are a medical document validator.
A patient has edited their health passport. The original OCR text is provided below.
Determine if the edited fields are reasonably supported by or consistent with the original document.
Minor additions or clarifications are acceptable. Completely unrelated information is not.

Original document text:
{ocr_text}

Edited passport fields:
{edited_fields}

Respond with ONLY valid JSON:
{{"valid": true, "reason": "brief reason"}}
or
{{"valid": false, "reason": "brief reason"}}
"""


@router.post("/{document_id}/validate-edit")
async def validate_edit(
    document_id: str,
    payload: dict,
    authorization: Optional[str] = Header(None),
):
    user = _get_user(authorization)
    db = get_db()
    _verify_ownership(db, document_id, user.id)

    # Get original OCR text
    text_row = db.table("document_texts").select("ocr_text").eq("document_id", document_id).single().execute()
    if not text_row.data:
        raise HTTPException(404, "Document text not found.")

    ocr_text = text_row.data.get("ocr_text", "")
    edited_fields = payload.get("edited_fields", {})

    model = genai.GenerativeModel(GEMINI_MODEL)
    prompt = _VALIDATE_PROMPT.format(
        ocr_text=ocr_text,
        edited_fields=json.dumps(edited_fields, ensure_ascii=False, indent=2)
    )
    response = model.generate_content(prompt)
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)
    return result
