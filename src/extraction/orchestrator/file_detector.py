"""
extraction/orchestrator/file_detector.py

Detects whether a file is PPTX or PDF by inspecting its actual bytes —
not just trusting the file extension. A renamed, extension-less, or
mislabeled file still routes correctly this way.

Detection order: content sniffing first (reliable), extension as a
fallback only if content sniffing is inconclusive (e.g. a corrupted
zip that still has a .pptx name).

  - PDF files start with the literal bytes "%PDF-".
  - PPTX files are zip archives — but so are .docx and .xlsx, so it's
    not enough to check "is this a zip". A PPTX zip specifically
    contains a "ppt/presentation.xml" member; a DOCX has "word/..." and
    an XLSX has "xl/...". Checking for that member is what actually
    tells PPTX apart from other Office zip formats.
"""

from __future__ import annotations
import zipfile
from enum import Enum


class FileType(str, Enum):
    PPTX = "pptx"
    PDF = "pdf"
    UNKNOWN = "unknown"


def _looks_like_pdf(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(5) == b"%PDF-"
    except Exception:
        return False


def _looks_like_pptx(path: str) -> bool:
    try:
        if not zipfile.is_zipfile(path):
            return False
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            return any(n.startswith("ppt/presentation.xml") for n in names)
    except Exception:
        return False


def detect_file_type(path: str) -> FileType:
    if _looks_like_pdf(path):
        return FileType.PDF
    if _looks_like_pptx(path):
        return FileType.PPTX

    # content sniffing was inconclusive — fall back to extension
    ext = path.lower().rsplit(".", 1)[-1] if "." in path else ""
    if ext == "pdf":
        return FileType.PDF
    if ext in ("pptx", "ppt"):
        return FileType.PPTX

    return FileType.UNKNOWN


def is_ppt(path: str) -> bool:
    """Convenience boolean, matching the is_ppt flag you described —
    equivalent to `detect_file_type(path) == FileType.PPTX`."""
    return detect_file_type(path) == FileType.PPTX
