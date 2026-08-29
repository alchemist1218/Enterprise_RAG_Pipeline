"""
extraction/pptx/image_extractor.py

Basic metadata for picture shapes. Does not decode/OCR image content —
that's a deliberate scope boundary; add an OCR step here later if
slides start carrying text-in-image content that needs indexing.
"""

from __future__ import annotations


def extract_image_meta(shape) -> dict:
    meta = {"filename": None, "content_type": None}
    try:
        image = shape.image
        meta["filename"] = image.filename
        meta["content_type"] = image.content_type
    except Exception:
        pass
    return meta
