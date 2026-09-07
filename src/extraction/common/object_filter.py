"""
extraction/common/object_filter.py

Drops decorative/empty objects (divider lines, background rectangles)
that carry no text, table rows, chart data, or image content — no
reason to store, index, or pay embedding cost on empty geometry.

Applied AFTER extraction, right before chunking — kept separate from
shape_extractor.py so the raw extraction stays complete/debuggable,
and filtering is an explicit, visible step you can turn off if you
ever need the full geometry (e.g. for layout re-rendering).
"""

from __future__ import annotations
from extraction.common.schemas import PageResult, ExtractedObject


def is_content_object(obj: ExtractedObject) -> bool:
    """True if the object carries anything worth keeping."""
    if obj.type == "text":
        return bool(obj.text)
    if obj.type == "table":
        return bool(obj.rows)
    if obj.type == "chart":
        return bool(obj.categories or obj.series)
    if obj.type == "image":
        # keep images even without OCR text — they're still a content
        # marker in reading order — but drop if you'd rather not
        return True
    return False  # bare "shape" objects with no text/data


def filter_page(page: PageResult) -> PageResult:
    page.objects = [o for o in page.objects if is_content_object(o)]
    return page


def filter_document(doc):
    for page in doc.pages:
        filter_page(page)
    return doc
