from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    upload = "upload"
    ocr_complete = "ocr_complete"
    translation_complete = "translation_complete"
    passport_generated = "passport_generated"
    needs_user_review = "needs_user_review"
    failed = "failed"


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    preferred_language: str = "en"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    preferred_language: str
    role: str = "patient"


# ── Documents ─────────────────────────────────────────────────────────────────

class DocumentOut(BaseModel):
    id: str
    user_id: str
    file_path: str
    source_language: Optional[str]
    status: DocumentStatus
    error_message: Optional[str] = None
    uploaded_at: datetime


class DocumentTextOut(BaseModel):
    document_id: str
    ocr_text: Optional[str]
    english_translation: Optional[str]
    user_language_translation: Optional[str]


# ── Health Passport ───────────────────────────────────────────────────────────

class PassportSchema(BaseModel):
    document_type: Optional[str]
    document_date: Optional[str]
    conditions: List[str] = []
    medications: List[str] = []
    allergies: List[str] = []
    tests: List[str] = []
    follow_up: List[str] = []
    red_flags: List[str] = []
    summary_plain_english: Optional[str]


class PassportOut(BaseModel):
    id: str
    document_id: str
    structured_json: PassportSchema
    patient_confirmed: bool
    generated_at: datetime


class PassportConfirm(BaseModel):
    document_id: str
    confirmed: bool
    edited_fields: Optional[PassportSchema] = None


# ── AI Check ──────────────────────────────────────────────────────────────────

class RiskCheckResult(BaseModel):
    risk_score: str          # "low" | "medium" | "high"
    issues: List[str] = []
    requires_review: bool


class RiskCheckOut(BaseModel):
    id: str
    document_id: str
    risk_score: str
    issues: List[str]
    requires_review: bool
    checked_at: datetime


class ReprocessResponse(BaseModel):
    document_id: str
    message: str
