"""
extraction/common/loader.py

Reconstructs a DocumentResult (the same dataclass tree the pipelines
build) from a saved .json file on disk. Used by anything that runs
AFTER extraction and needs to read already-extracted output —
extraction/qa/report.py and chunking/pipeline.py both use this,
instead of each re-implementing their own JSON-to-dataclass parsing.
"""

from __future__ import annotations
import json
from extraction.common.schemas import DocumentResult, PageResult, ExtractedObject, BoundingBox


def load_document_json(json_path: str) -> DocumentResult:
    with open(json_path) as f:
        raw = json.load(f)

    pages = []
    for p in raw["pages"]:
        objects = []
        for o in p["objects"]:
            bbox = BoundingBox(**o["bbox"]) if "bbox" in o else BoundingBox(0, 0, 0, 0)
            o = {**o, "bbox": bbox}
            objects.append(ExtractedObject(**{
                k: v for k, v in o.items() if k in ExtractedObject.__dataclass_fields__
            }))
        pages.append(PageResult(
            page_number=p["page_number"],
            width=p["width"],
            height=p["height"],
            objects=objects,
            reconstructed_text=p.get("reconstructed_text", ""),
            notes=p.get("notes"),
            layout_name=p.get("layout_name"),
            ocr_applied=p.get("ocr_applied"),
        ))
    return DocumentResult(document_id=raw["document_id"], source_type=raw["source_type"], pages=pages)
