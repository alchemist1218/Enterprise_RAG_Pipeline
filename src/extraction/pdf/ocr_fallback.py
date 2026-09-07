"""
extraction/pdf/ocr_fallback.py

OCR is only applied to pages that fail a cheap text-density check, so
the pipeline stays fast on text-native PDFs and only pays OCR cost on
scanned pages. Optional dependency: if pytesseract/Pillow aren't
installed, needs_ocr() still works but ocr_page() raises clearly.
"""

from __future__ import annotations

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


def needs_ocr(fitz_page, text_threshold: int = 20) -> bool:
    return len(fitz_page.get_text().strip()) < text_threshold


def ocr_page(fitz_page, dpi: int = 300) -> str:
    if not OCR_AVAILABLE:
        raise RuntimeError(
            "pytesseract/Pillow not installed — "
            "pip install pytesseract pillow --break-system-packages "
            "(also requires the system tesseract binary)"
        )
    pix = fitz_page.get_pixmap(dpi=dpi)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return pytesseract.image_to_string(img)
