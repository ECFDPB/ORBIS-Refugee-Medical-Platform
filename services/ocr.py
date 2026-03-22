"""
OCR Service
-----------
Extracts raw text from uploaded PDF / image files.

Backend selection via config.OCR_BACKEND:
  "google"     — Google Cloud Vision API (default, configured)
  "tesseract"  — local PyMuPDF + pytesseract (no API key needed)
  "mistral"    — Mistral OCR API          [TODO]
  "azure"      — Azure Document Intelligence [TODO]
"""

import io
import os
from pathlib import Path
from config import OCR_BACKEND, GOOGLE_CREDENTIALS_PATH


# ── Public entry point ────────────────────────────────────────────────────────

def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Extract text from file bytes.
    Returns raw extracted string.
    """
    ext = Path(filename).suffix.lower()

    if OCR_BACKEND == "google":
        return _google_extract(file_bytes, ext)
    elif OCR_BACKEND == "tesseract":
        return _tesseract_extract(file_bytes, ext)
    elif OCR_BACKEND == "mistral":
        return _mistral_extract(file_bytes, filename)
    elif OCR_BACKEND == "azure":
        return _azure_extract(file_bytes, filename)
    else:
        raise ValueError(f"Unknown OCR_BACKEND: {OCR_BACKEND}")


# ── Google Cloud Vision ───────────────────────────────────────────────────────

def _google_extract(file_bytes: bytes, ext: str) -> str:
    """
    Use Google Cloud Vision text_detection for images.
    For PDFs, render each page to PNG first, then send to Vision.
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDENTIALS_PATH

    from google.cloud import vision

    client = vision.ImageAnnotatorClient()

    if ext == ".pdf":
        return _google_extract_pdf(client, file_bytes)
    else:
        return _google_extract_image(client, file_bytes)


def _google_extract_image(client, image_bytes: bytes) -> str:
    from google.cloud import vision

    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)

    if response.error.message:
        raise RuntimeError(f"Google Vision error: {response.error.message}")

    texts = response.text_annotations
    if not texts:
        return ""

    # texts[0].description is the full concatenated text
    return texts[0].description.strip()


def _google_extract_pdf(client, pdf_bytes: bytes) -> str:
    """Render each PDF page to PNG, then run Vision OCR on each page."""
    import fitz  # PyMuPDF

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_text = []

    for page in doc:
        # Try direct text extraction first (fast, works for digital PDFs)
        text = page.get_text().strip()
        if text:
            pages_text.append(text)
        else:
            # Render page as PNG and send to Google Vision
            pix = page.get_pixmap(dpi=200)
            png_bytes = pix.tobytes("png")
            pages_text.append(_google_extract_image(client, png_bytes))

    return "\n\n".join(pages_text)


# ── Tesseract (local fallback, no API key) ────────────────────────────────────

def _tesseract_extract(file_bytes: bytes, ext: str) -> str:
    import pytesseract
    from PIL import Image

    if ext == ".pdf":
        return _pdf_tesseract(file_bytes)
    else:
        image = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(image)


def _pdf_tesseract(file_bytes: bytes) -> str:
    import fitz
    import pytesseract
    from PIL import Image

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages_text = []

    for page in doc:
        text = page.get_text().strip()
        if text:
            pages_text.append(text)
        else:
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            pages_text.append(pytesseract.image_to_string(img))

    return "\n\n".join(pages_text)


# ── Mistral OCR ───────────────────────────────────────────────────────────────

def _mistral_extract(file_bytes: bytes, filename: str) -> str:
    # TODO: integrate Mistral OCR API
    raise NotImplementedError("Mistral OCR integration not yet implemented.")


# ── Azure Document Intelligence ───────────────────────────────────────────────

def _azure_extract(file_bytes: bytes, filename: str) -> str:
    # TODO: integrate Azure Document Intelligence
    raise NotImplementedError("Azure OCR integration not yet implemented.")
