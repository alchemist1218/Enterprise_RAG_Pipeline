"""
cleaning/pipeline.py

Top-level entry point: clean_document(doc) -> (DocumentResult, CleaningReport)

Stage order matters — each stage assumes the previous one already ran:

    0. drop empty decorative shapes   (nothing to compare, safe to go first)
    1. normalize text                  (must run before any text comparison)
    2. detect + strip boilerplate      (needs normalized text to match reliably)
    3. dedup text objects within page  (needs normalized, boilerplate-free text)
    4. recompute reconstructed_text    (must reflect all edits above)
    5. drop near-duplicate pages       (needs correct reconstructed_text)
    6. drop low-info pages             (needs correct reconstructed_text + final object list)
"""

from __future__ import annotations

from extraction.common.schemas import DocumentResult
from extraction.common.document_reconstructor import reconstruct_text
from extraction.common.object_filter import filter_document

from cleaning.text_normalizer import normalize_document
from cleaning.boilerplate_detector import detect_boilerplate, strip_boilerplate
from cleaning.deduplicator import dedup_text_objects_within_page, find_duplicate_pages
from cleaning.low_info_filter import filter_low_info_pages
from cleaning.report import CleaningReport


def clean_document(
    doc: DocumentResult,
    min_words: int = 15,
    boilerplate_min_page_fraction: float = 0.6,
    duplicate_page_similarity: float = 0.92,
) -> tuple[DocumentResult, CleaningReport]:
    report = CleaningReport(pages_before=len(doc.pages))

    # Stage 0: empty decorative shapes
    before_obj_counts = {p.page_number: len(p.objects) for p in doc.pages}
    doc = filter_document(doc)
    report.empty_shapes_removed = sum(
        before_obj_counts[p.page_number] - len(p.objects) for p in doc.pages
    )

    # Stage 1: normalize text
    doc = normalize_document(doc)

    # Stage 2: boilerplate
    boilerplate = detect_boilerplate(doc, min_page_fraction=boilerplate_min_page_fraction)
    report.boilerplate_texts_found = sorted(boilerplate)
    report.boilerplate_objects_removed = strip_boilerplate(doc, boilerplate)

    # Stage 3: dedup text objects within each page
    report.duplicate_text_objects_removed = sum(
        dedup_text_objects_within_page(page) for page in doc.pages
    )

    # Stage 4: recompute reconstructed_text now that objects have changed
    for page in doc.pages:
        page.reconstructed_text = reconstruct_text(page.objects)

    # Stage 5: near-duplicate pages
    dup_pages = find_duplicate_pages(doc, similarity_threshold=duplicate_page_similarity)
    if dup_pages:
        doc.pages = [p for p in doc.pages if p.page_number not in dup_pages]
    report.duplicate_pages_removed = dup_pages

    # Stage 6: low-info pages (tables/charts are protected regardless of word count)
    report.low_info_pages_removed = filter_low_info_pages(doc, min_words=min_words)

    report.pages_after = len(doc.pages)
    return doc, report


if __name__ == "__main__":
    import sys
    from extraction.pptx.pipeline import extract_pptx

    if len(sys.argv) != 2:
        print("Usage: python -m cleaning.pipeline <path-to-deck.pptx>")
        raise SystemExit(1)

    raw_doc = extract_pptx(sys.argv[1])
    cleaned_doc, cleaning_report = clean_document(raw_doc)
    print(cleaning_report.summary())
    print(cleaned_doc.to_json(indent=2))
