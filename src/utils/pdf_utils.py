"""
Utility module for PDF page processing.
Used by: mod_01_splitting.py

Features:
- Extracts clean text from each PDF page.
- Renders page as a PIL image.
- Performs OCR automatically if text is empty or low-confidence.
"""

import io
import fitz  # PyMuPDF
from PIL import Image
import numpy as np

try:
    import pytesseract
except Exception:
    pytesseract = None


def _render_page_as_image(page, dpi=150):
    """
    Converts a PDF page to a high-quality PIL Image.
    """
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img_data = pix.tobytes("png")
    return Image.open(io.BytesIO(img_data))


def _clean_text(text: str) -> str:
    """
    Removes excessive whitespace and newlines from page text.
    """
    if not text:
        return ""
    text = text.replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split())
    return text.strip()


def get_page_content(doc: fitz.Document, page_index: int):
    """
    Extracts (text, PIL image) for the given page.
    If text extraction fails or is too short, falls back to OCR (if pytesseract is available).
    
    Returns:
        tuple: (text, image)
    """
    try:
        page = doc.load_page(page_index)

        # Step 1: Extract text using PyMuPDF's built-in engine
        text = _clean_text(page.get_text("text"))

        # Step 2: Render image for possible OCR fallback
        image = _render_page_as_image(page, dpi=150)

        # Step 3: OCR fallback if text is empty or very short
        if (not text or len(text) < 25) and pytesseract is not None:
            try:
                ocr_text = pytesseract.image_to_string(image)
                ocr_text = _clean_text(ocr_text)
                if len(ocr_text) > len(text):
                    text = ocr_text
            except Exception:
                pass

        return text, image

    except Exception as e:
        # Fallback in case of rendering or reading error
        return "", Image.new("RGB", (100, 100), color="white")
