"""
extraction/common/spatial_ordering.py

Row-based reading-order reconstruction shared across formats that use
a single-column, top-to-bottom/left-to-right layout (PPTX slides, and
single-column PDF pages).

Multi-column PDF layouts use extraction/pdf/column_detector.py instead
of this module — column-first ordering is a different problem than
row grouping and doesn't share logic worth factoring out.

Uses overlap-based row clustering rather than a fixed pixel tolerance,
so it scales across slide/page sizes and mixed object heights.
"""

from __future__ import annotations
from extraction.common.schemas import ExtractedObject, BoundingBox


def _bbox_tuple(obj: ExtractedObject) -> tuple[float, float, float, float]:
    b: BoundingBox = obj.bbox
    return b.x, b.y, b.width, b.height


def vertical_overlap_ratio(a: ExtractedObject, b: ExtractedObject) -> float:
    """Fraction of the shorter object's height that overlaps vertically.
    Scale-independent — replaces a fixed-pixel Y tolerance."""
    _, ay, _, ah = _bbox_tuple(a)
    _, by, _, bh = _bbox_tuple(b)
    top = max(ay, by)
    bottom = min(ay + ah, by + bh)
    overlap = max(0.0, bottom - top)
    shorter = min(ah, bh)
    return overlap / shorter if shorter else 0.0


def group_into_rows(
    objects: list[ExtractedObject], min_overlap: float = 0.4
) -> list[list[ExtractedObject]]:
    """Clusters objects into visual rows by vertical overlap, then sorts
    each row left-to-right (ties broken by z-order for overlapping shapes)."""
    objs = sorted(objects, key=lambda o: o.bbox.y)
    rows: list[list[ExtractedObject]] = []

    for o in objs:
        placed = False
        for row in rows:
            if any(vertical_overlap_ratio(o, r) >= min_overlap for r in row):
                row.append(o)
                placed = True
                break
        if not placed:
            rows.append([o])

    for row in rows:
        row.sort(key=lambda o: (o.bbox.x, o.z_order or 0))

    rows.sort(key=lambda row: min(o.bbox.y for o in row))
    return rows


def flatten_reading_order(objects: list[ExtractedObject], min_overlap: float = 0.4) -> list[ExtractedObject]:
    """Convenience wrapper: row-group then flatten to a single ordered list."""
    return [o for row in group_into_rows(objects, min_overlap) for o in row]
