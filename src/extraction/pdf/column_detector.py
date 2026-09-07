"""
extraction/pdf/column_detector.py

Multi-column reading order for PDF pages. This is a different problem
than PPTX's row-overlap grouping (extraction/common/spatial_ordering.py)
and deliberately isn't unified with it: PDFs need column-first ordering
(all of column 1 top-to-bottom, then column 2), not row-first grouping.
"""

from __future__ import annotations
from extraction.common.schemas import ExtractedObject


def detect_columns(blocks: list[ExtractedObject], page_width: float, gap_ratio: float = 0.06) -> list[float]:
    """Clusters block left-edges into column start x-positions using a
    gap threshold relative to page width."""
    if not blocks:
        return [0.0]
    xs = sorted(b.bbox.x for b in blocks)
    gap = page_width * gap_ratio

    columns: list[list[float]] = []
    current = [xs[0]]
    for x in xs[1:]:
        if x - current[-1] > gap:
            columns.append(current)
            current = []
        current.append(x)
    columns.append(current)

    return sorted(min(c) for c in columns)


def order_by_columns(blocks: list[ExtractedObject], page_width: float) -> list[ExtractedObject]:
    boundaries = detect_columns(blocks, page_width)

    def col_index(x: float) -> int:
        idx = 0
        for i, b in enumerate(boundaries):
            if b <= x:
                idx = i
        return idx

    return sorted(blocks, key=lambda b: (col_index(b.bbox.x), b.bbox.y))
