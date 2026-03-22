"""
Documents Router — upload, process, retrieve
"""

import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Header
from pathlib import Path
from typing import Optional
from models import DocumentOut, DocumentTextOut, DocumentStatus, ReprocessResponse
from services.ocr import extract_text
from services.translation import detect_language, translate_to_english, translate_to_language
from services.ai_check import check_translation_risk
from services.passport import generate_passport
from services.pii_redact import redact_pii
from database import get_db, get_authed_db
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, SUPABASE_BUCKET
import logging

router = APIRouter(prefix="/documents", tags=["documents"])
MAX_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Safe logger — never log document content
logger = logging.getLogger("documents")
logger.setLevel(logging.INFO)


def _get_user(authorization: Optional[str]) -> dict:
    """Extract user from Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header.")
    token = authorization.split(" ", 1)[1]
    db = get_db()
    res = db.auth.get_user(token)
    if not res.user:
        raise HTTPException(401, "Invalid token.")
    return res.user


# ── Upload ────────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
):
    user = _get_user(authorization)
    _validate_file(file.filename)

    file_bytes = await file.read()
    if len(file_bytes) > MAX_BYTES:
        raise HTTPException(400, f"File exceeds {MAX_FILE_SIZE_MB}MB limit.")

    token = authorization.split(" ", 1)[1]
    db = get_db()
    authed_db = get_authed_db(token)
    doc_id = str(uuid.uuid4())
    ext = Path(file.filename).suffix.lower()
    safe_filename = f"{doc_id}{ext}"
    file_path = f"{user.id}/{doc_id}/{safe_filename}"

    # Save to Supabase Storage using authed client
    authed_db.storage.from_(SUPABASE_BUCKET).upload(file_path, file_bytes)

    # Get user preferred language
    user_row = db.table("users").select("preferred_language").eq("id", user.id).execute()
    user_lang = user_row.data[0].get("preferred_language", "en") if user_row.data else "en"

    # Insert document row
    row = db.table("documents").insert({
        "id": doc_id,
        "user_id": user.id,
        "file_path": file_path,
        "status": DocumentStatus.upload,
    }).execute()

    # Kick off background processing
    background_tasks.add_task(_process_document, doc_id, file_bytes, file.filename, user_lang)

    data = row.data[0]
    return DocumentOut(**data)


# ── Retrieve ──────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[DocumentOut])
async def list_documents(authorization: Optional[str] = Header(None)):
    user = _get_user(authorization)
    db = get_db()
    rows = db.table("documents").select("*").eq("user_id", user.id).execute()
    return [DocumentOut(**r) for r in rows.data]


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(document_id: str, authorization: Optional[str] = Header(None)):
    user = _get_user(authorization)
    db = get_db()
    row = db.table("documents").select("*").eq("id", document_id).eq("user_id", user.id).single().execute()
    if not row.data:
        raise HTTPException(404, "Document not found.")
    return DocumentOut(**row.data)


@router.get("/{document_id}/text", response_model=DocumentTextOut)
async def get_document_text(document_id: str, authorization: Optional[str] = Header(None)):
    user = _get_user(authorization)
    db = get_db()
    # Verify ownership
    doc = db.table("documents").select("id").eq("id", document_id).eq("user_id", user.id).single().execute()
    if not doc.data:
        raise HTTPException(404, "Document not found.")
    row = db.table("document_texts").select("*").eq("document_id", document_id).single().execute()
    if not row.data:
        raise HTTPException(404, "Text not yet available.")
    return DocumentTextOut(document_id=document_id, **row.data)


# ── Background processing pipeline ───────────────────────────────────────────

async def _process_document(doc_id: str, file_bytes: bytes, filename: str, user_lang: str):
    db = get_db()

    def set_status(status: str):
        db.table("documents").update({"status": status}).eq("id", doc_id).execute()

    try:
        # Step 1: OCR
        ocr_text = extract_text(file_bytes, filename)
        set_status(DocumentStatus.ocr_complete)

        # Step 2: Language detection
        source_lang, confidence = detect_language(ocr_text)
        if confidence < 0.7:
            source_lang = None  # Let DeepL auto-detect
        else:
            db.table("documents").update({"source_language": source_lang}).eq("id", doc_id).execute()

        # Step 3: PII redaction before sending to external services
        redacted_text, redacted_fields = redact_pii(ocr_text)
        logger.info("PII redaction complete for doc_id=%s, fields=%s", doc_id, redacted_fields)

        # Step 4: Translate to English (using redacted text)
        english_text = translate_to_english(redacted_text, source_lang=source_lang)

        # Step 5: Translate to user language
        user_lang_text = translate_to_language(english_text, target_lang=user_lang)

        # Save translations (store original ocr_text in DB, redacted used for APIs)
        db.table("document_texts").upsert({
            "document_id": doc_id,
            "ocr_text": ocr_text,
            "english_translation": english_text,
            "user_language_translation": user_lang_text,
        }).execute()
        set_status(DocumentStatus.translation_complete)

        # Step 6: AI risk check (on redacted text)
        risk = check_translation_risk(redacted_text, english_text)
        db.table("risk_checks").upsert({
            "document_id": doc_id,
            "risk_score": risk.risk_score,
            "issues": risk.issues,
            "requires_review": risk.requires_review,
        }).execute()
        if risk.requires_review:
            set_status(DocumentStatus.needs_user_review)

        # Step 7: Generate passport (on redacted text)
        passport = generate_passport(redacted_text, user_lang=user_lang)
        db.table("health_passports").upsert({
            "document_id": doc_id,
            "structured_json": passport.model_dump(),
            "patient_confirmed": False,
        }).execute()
        # Preserve needs_user_review if risk check flagged it
        if not risk.requires_review:
            set_status(DocumentStatus.passport_generated)

    except Exception:
        logger.error("Processing failed for doc_id=%s", doc_id)
        db.table("documents").update({
            "status": DocumentStatus.failed,
            "error_message": "Processing failed. Please try again.",
        }).eq("id", doc_id).execute()
        raise


# ── Reprocess ─────────────────────────────────────────────────────────────────

@router.post("/{document_id}/reprocess", response_model=ReprocessResponse)
async def reprocess_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None),
):
    user = _get_user(authorization)
    db = get_db()

    # Verify ownership and get file info
    row = db.table("documents").select("*").eq("id", document_id).eq("user_id", user.id).single().execute()
    if not row.data:
        raise HTTPException(404, "Document not found.")

    file_path = row.data["file_path"]
    filename = file_path.split("/")[-1]

    # Re-download file from Supabase Storage
    file_bytes = db.storage.from_(SUPABASE_BUCKET).download(file_path)

    # Clear old results
    db.table("risk_checks").delete().eq("document_id", document_id).execute()
    db.table("health_passports").delete().eq("document_id", document_id).execute()
    db.table("document_texts").delete().eq("document_id", document_id).execute()

    # Reset status
    db.table("documents").update({
        "status": DocumentStatus.upload,
        "error_message": None,
    }).eq("id", document_id).execute()

    # Get user preferred language
    user_row = db.table("users").select("preferred_language").eq("id", user.id).execute()
    user_lang = user_row.data[0].get("preferred_language", "en") if user_row.data else "en"

    background_tasks.add_task(_process_document, document_id, file_bytes, filename, user_lang)

    return ReprocessResponse(document_id=document_id, message="Reprocessing started.")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _validate_file(filename: str):
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}. Allowed: {ALLOWED_EXTENSIONS}")
