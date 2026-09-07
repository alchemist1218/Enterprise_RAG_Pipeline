"""
cleaning/text_normalizer.py

Normalizes text on every ExtractedObject in place: unicode
normalization (so visually-identical characters compare equal),
whitespace collapsing, and stripping control characters that
sometimes leak in from OCR or malformed source files.

Runs FIRST in the pipeline — boilerplate detection and dedup both
compare text for equality/similarity, and that only works reliably on
normalized text (otherwise "Confidential " and "Confidential" with a
trailing space count as different strings and boilerplate detection
misses them).
"""

from __future__ import annotations
import re
import unicodedata

from extraction.common.schemas import DocumentResult

_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_MULTI_SPACE_RE = re.compile(r"[ \t]+")
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")


def normalize_text(text: str) -> str:
    if not text:
        return text
    text = unicodedata.normalize("NFKC", text)
    text = _CONTROL_CHARS_RE.sub("", text)
    text = _MULTI_SPACE_RE.sub(" ", text)
    text = _MULTI_NEWLINE_RE.sub("\n\n", text)
    return text.strip()


def normalize_document(doc: DocumentResult) -> DocumentResult:
    for page in doc.pages:
        for obj in page.objects:
            if obj.text:
                obj.text = normalize_text(obj.text)
            if obj.paragraphs:
                obj.paragraphs = [normalize_text(p) for p in obj.paragraphs if normalize_text(p)]
    return doc
