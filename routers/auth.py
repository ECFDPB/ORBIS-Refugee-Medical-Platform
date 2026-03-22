"""
Auth Router — Supabase Auth
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from models import UserCreate, UserLogin, UserOut
from database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
async def register(payload: UserCreate):
    db = get_db()
    res = db.auth.sign_up({"email": payload.email, "password": payload.password})

    if not res.user:
        raise HTTPException(400, "Registration failed.")

    # Insert into public.users
    db.table("users").insert({
        "id": res.user.id,
        "email": payload.email,
        "preferred_language": payload.preferred_language,
        "role": "patient",
    }).execute()

    return UserOut(
        id=res.user.id,
        email=payload.email,
        preferred_language=payload.preferred_language,
    )


@router.post("/login")
async def login(payload: UserLogin):
    db = get_db()
    res = db.auth.sign_in_with_password({"email": payload.email, "password": payload.password})

    if not res.user:
        raise HTTPException(401, "Invalid credentials.")

    user_row = db.table("users").select("*").eq("id", res.user.id).execute()
    user_data = user_row.data[0] if user_row.data else {}

    return {
        "access_token": res.session.access_token,
        "token_type": "bearer",
        "user": UserOut(
            id=res.user.id,
            email=res.user.email,
            preferred_language=user_data.get("preferred_language", "en"),
        ),
    }


@router.post("/logout")
async def logout():
    db = get_db()
    db.auth.sign_out()
    return {"message": "Logged out."}


class ProfileUpdate(BaseModel):
    preferred_language: str


@router.patch("/profile", response_model=UserOut)
async def update_profile(payload: ProfileUpdate, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header.")
    token = authorization.split(" ", 1)[1]
    db = get_db()
    res = db.auth.get_user(token)
    if not res.user:
        raise HTTPException(401, "Invalid token.")

    updated = db.table("users").update({
        "preferred_language": payload.preferred_language,
    }).eq("id", res.user.id).execute()

    row = updated.data[0]
    return UserOut(id=row["id"], email=row["email"], preferred_language=row["preferred_language"])


@router.delete("/data")
async def delete_all_user_data(authorization: Optional[str] = Header(None)):
    """Delete all documents, passports, and texts for the current user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header.")
    token = authorization.split(" ", 1)[1]
    db = get_db()
    res = db.auth.get_user(token)
    if not res.user:
        raise HTTPException(401, "Invalid token.")

    user_id = res.user.id

    # Get all document ids for this user
    docs = db.table("documents").select("id").eq("user_id", user_id).execute()
    if docs.data:
        doc_ids = [d["id"] for d in docs.data]
        db.table("risk_checks").delete().in_("document_id", doc_ids).execute()
        db.table("health_passports").delete().in_("document_id", doc_ids).execute()
        db.table("document_texts").delete().in_("document_id", doc_ids).execute()
        db.table("documents").delete().eq("user_id", user_id).execute()

        # Delete files from storage
        for doc in docs.data:
            try:
                files = db.storage.from_("documents").list(f"{user_id}/{doc['id']}")
                paths = [f"{user_id}/{doc['id']}/{f['name']}" for f in (files or [])]
                if paths:
                    db.storage.from_("documents").remove(paths)
            except Exception:
                pass

    return {"message": "All user data deleted."}
