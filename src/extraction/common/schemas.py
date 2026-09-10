"""
extraction/common/schemas.py

Canonical output shapes for both the PPTX and PDF pipelines. Both
pipelines import ONLY these classes to build their result — never
hand-roll a dict — so the two extractors can't drift into different
JSON shapes over time.
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class BoundingBox:
    x: float
    y: float
    width: float
    height: float


@dataclass
class ExtractedObject:
    """One extracted object on a page/slide. Not every field applies to
    every type — `to_dict()` drops unset fields so the JSON stays clean
    per object type (a table doesn't carry `categories`, etc.)."""

    id: int
    type: str  # "text" | "table" | "chart" | "image" | "shape"
    bbox: BoundingBox

    # ordering / provenance
    shape_id: Optional[int] = None
    name: Optional[str] = None
    z_order: Optional[int] = None

    # text
    role: Optional[str] = None  # "title" | "subtitle" | "body" | "footer_meta"
    text: Optional[str] = None
    paragraphs: list[str] = field(default_factory=list)
    hyperlinks: list[dict] = field(default_factory=list)
    emphasis: list[dict] = field(default_factory=list)
    avg_font_size: Optional[float] = None

    # table
    rows: Optional[list[list[str]]] = None

    # chart
    chart_type: Optional[str] = None
    title: Optional[str] = None
    categories: list[str] = field(default_factory=list)
    series: list[dict] = field(default_factory=list)

    # image
    filename: Optional[str] = None
    content_type: Optional[str] = None
    xref: Optional[int] = None
    ocr_attempted: Optional[bool] = None  # None = OCR step didn't run at all;
                                           # True + no text = OCR ran and found nothing (real signal)

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: v for k, v in d.items() if v not in (None, [], "")}


@dataclass
class PageResult:
    """One slide (PPTX) or one page (PDF)."""

    page_number: int
    width: float
    height: float
    objects: list[ExtractedObject]
    reconstructed_text: str = ""

    # optional, format-specific extras
    notes: Optional[str] = None            # PPTX speaker notes
    layout_name: Optional[str] = None      # PPTX slide layout
    ocr_applied: Optional[bool] = None     # PDF OCR fallback flag

    def to_dict(self) -> dict:
        d = {
            "page_number": self.page_number,
            "width": self.width,
            "height": self.height,
            "objects": [o.to_dict() for o in self.objects],
            "reconstructed_text": self.reconstructed_text,
        }
        for optional_field in ("notes", "layout_name", "ocr_applied"):
            value = getattr(self, optional_field)
            if value is not None:
                d[optional_field] = value
        return d


@dataclass
class DocumentResult:
    """Top-level result — identical shape whether source_type is
    'pptx' or 'pdf'."""

    document_id: str
    source_type: str  # "pptx" | "pdf"
    pages: list[PageResult]

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "source_type": self.source_type,
            "pages": [p.to_dict() for p in self.pages],
        }

    def to_json(self, **kwargs: Any) -> str:
        return json.dumps(self.to_dict(), default=str, **kwargs)
