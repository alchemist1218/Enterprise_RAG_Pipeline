"""
extraction/pdf/pipeline.py

Top-level entry point: extract_pdf(path) -> DocumentResult, matching
the same schema extraction.pptx.pipeline.extract_pptx produces. This
is the only module in the package other code should import from for
PDF extraction.
"""

from __future__ import annotations
import os

from extraction.common.schemas import DocumentResult, PageResult
from extraction.common.document_reconstructor import reconstruct_text
from extraction.pdf.pdf_loader import open_pdf, iter_page_pairs
from extraction.pdf.block_extractor import extract_text_blocks, extract_image_blocks, infer_role
from extraction.pdf.column_detector import order_by_columns
from extraction.pdf.table_extractor import extract_tables_for_page
from extraction.pdf.ocr_fallback import needs_ocr, ocr_page, OCR_AVAILABLE


def _block_inside_any_table(block, tables) -> bool:
    for t in tables:
        tb = t.bbox
        if (block.bbox.x >= tb.x and block.bbox.y >= tb.y
                and block.bbox.x <= tb.x + tb.width
                and block.bbox.y <= tb.y + tb.height):
            return True
    return False


def extract_page(fitz_page, plumber_page, page_number: int) -> PageResult:
    page_width, page_height = fitz_page.rect.width, fitz_page.rect.height

    ocr_text = None
    if needs_ocr(fitz_page) and OCR_AVAILABLE:
        ocr_text = ocr_page(fitz_page)
        text_blocks = []
    else:
        text_blocks = extract_text_blocks(fitz_page)

    tables = extract_tables_for_page(plumber_page, start_id=len(text_blocks))
    # drop text blocks that fall inside a detected table to avoid double-counting
    text_blocks = [b for b in text_blocks if not _block_inside_any_table(b, tables)]

    max_font_size = max((b.avg_font_size or 0 for b in text_blocks), default=0)
    for b in text_blocks:
        b.role = infer_role(b, page_height, max_font_size)

    ordered_text = order_by_columns(text_blocks, page_width)
    images = extract_image_blocks(fitz_page, start_id=len(text_blocks) + len(tables))

    all_objects = ordered_text + tables + images

    return PageResult(
        page_number=page_number,
        width=page_width,
        height=page_height,
        objects=all_objects,
        reconstructed_text=ocr_text if ocr_text else reconstruct_text(ordered_text + tables),
        ocr_applied=ocr_text is not None,
    )


def extract_pdf(pdf_path: str) -> DocumentResult:
    pages = []
    with open_pdf(pdf_path) as (fitz_doc, plumber_doc):
        for page_number, fitz_page, plumber_page in iter_page_pairs(fitz_doc, plumber_doc):
            pages.append(extract_page(fitz_page, plumber_page, page_number))

    document_id = os.path.splitext(os.path.basename(pdf_path))[0]
    return DocumentResult(document_id=document_id, source_type="pdf", pages=pages)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m extraction.pdf.pipeline <path-to-file.pdf>")
        raise SystemExit(1)
    result = extract_pdf(sys.argv[1])
    print(result.to_json(indent=2))
