"""
extraction/pptx/table_extractor.py

Table row extraction. Merge-spanned cells are emitted as empty strings
rather than repeating the origin cell's text, so row/column counts stay
consistent with the visual grid instead of silently duplicating content.
"""

from __future__ import annotations


def extract_table(shape) -> list[list[str]]:
    table = shape.table
    rows: list[list[str]] = []
    for row in table.rows:
        row_data = []
        for cell in row.cells:
            if cell.is_spanned:
                row_data.append("")
            else:
                row_data.append(cell.text.strip())
        rows.append(row_data)
    return rows
