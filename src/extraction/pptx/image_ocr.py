"""
extraction/pptx/image_ocr.py

Chart screenshots (pasted images, not native PPTX chart objects) carry
no structured data python-pptx can read — this runs OCR on the image
bytes to at least recover the visible text/numbers/labels.

This is best-effort: OCR gives you raw text like "42%" and "Product A"
with no guaranteed link between a number and its label the way
chart_extractor.py's categories/series pairing does. Treat OCR output
as supplementary text to embed, not structured data to compute on.

Requires: pip install pytesseract pillow --break-system-packages
(also needs the system tesseract binary)
"""

from __future__ import annotations
import io

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


def ocr_image_shape(shape) -> str | None:
    """Runs OCR on a picture shape's raw image bytes. Returns None if
    OCR isn't available or the shape has no readable image blob."""
    if not OCR_AVAILABLE:
        return None
    try:
        image_bytes = shape.image.blob
    except Exception:
        return None

    try:
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img).strip()
        return text or None
    except Exception:
        return None
