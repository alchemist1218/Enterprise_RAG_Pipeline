"""
extraction/pdf/table_extractor.py

Table detection via pdfplumber's ruled-line/alignment algorithm.
PyMuPDF has no equivalent table API, which is why this pipeline needs
both libraries (see pdf_loader.py).
"""

from __future__ import annotations
from extraction.common.schemas import ExtractedObject, BoundingBox


def extract_tables_for_page(plumber_page, start_id: int = 0) -> list[ExtractedObject]:
    tables = []
    obj_id = start_id
    for t in plumber_page.find_tables():
        x0, y0, x1, y1 = t.bbox
        obj_id += 1
        tables.append(ExtractedObject(
            id=obj_id,
            type="table",
            bbox=BoundingBox(x=x0, y=y0, width=x1 - x0, height=y1 - y0),
            rows=t.extract(),
        ))
    return tables
