"""
extraction/pptx/pipeline.py

Top-level entry point: extract_pptx(path) -> DocumentResult.
Ties together ppt_loader, shape_extractor, common.spatial_ordering,
and common.document_reconstructor. This is the only module in the
package other code should import from for PPTX extraction.
"""

from __future__ import annotations
import os

from extraction.common.schemas import DocumentResult, PageResult
from extraction.common.spatial_ordering import flatten_reading_order
from extraction.common.document_reconstructor import reconstruct_text
from extraction.pptx.ppt_loader import load_presentation
from extraction.pptx.shape_extractor import extract_slide_objects


def extract_slide(slide, slide_number: int, slide_width: int, slide_height: int) -> PageResult:
    objects = extract_slide_objects(slide, slide_height)
    ordered = flatten_reading_order(objects)

    notes_text = ""
    if slide.has_notes_slide:
        notes_text = slide.notes_slide.notes_text_frame.text.strip()

    return PageResult(
        page_number=slide_number,
        width=slide_width,
        height=slide_height,
        objects=ordered,
        reconstructed_text=reconstruct_text(ordered),
        notes=notes_text or None,
        layout_name=slide.slide_layout.name,
    )


def extract_pptx(pptx_path: str) -> DocumentResult:
    prs = load_presentation(pptx_path)
    pages = [
        extract_slide(slide, i, prs.slide_width, prs.slide_height)
        for i, slide in enumerate(prs.slides, start=1)
    ]
    document_id = os.path.splitext(os.path.basename(pptx_path))[0]
    return DocumentResult(document_id=document_id, source_type="pptx", pages=pages)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m extraction.pptx.pipeline <path-to-deck.pptx>")
        raise SystemExit(1)
    result = extract_pptx(sys.argv[1])
    print(result.to_json(indent=2))
