"""
Global file type detection used by the top-level orchestrator.
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

    ext = path.lower().rsplit(".", 1)[-1] if "." in path else ""
    if ext == "pdf":
        return FileType.PDF
    if ext in ("pptx", "ppt"):
        return FileType.PPTX

    return FileType.UNKNOWN


def is_ppt(path: str) -> bool:
    return detect_file_type(path) == FileType.PPTX
