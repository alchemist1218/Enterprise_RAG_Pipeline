"""
cleaning/low_info_filter.py

Flags/drops pages that carry too little text to be useful as a RAG
chunk — divider slides ("Section 2"), "Thank You" / "Questions?"
closers, near-blank pages.

Safety rule: a page with a table or chart object is NEVER dropped for
being "low word count," even if its prose text is short — a table can
be information-dense with almost no surrounding prose, and dropping it
on a word-count heuristic alone would silently delete real data.
"""

from __future__ import annotations
from extraction.common.schemas import DocumentResult, PageResult


def score_page(page: PageResult, min_words: int = 15) -> dict:
    word_count = len(page.reconstructed_text.split())
    has_data_object = any(o.type in ("table", "chart") for o in page.objects)
    is_low_info = word_count < min_words and not has_data_object
    return {
        "word_count": word_count,
        "has_data_object": has_data_object,
        "is_low_info": is_low_info,
    }


def filter_low_info_pages(doc: DocumentResult, min_words: int = 15) -> list[int]:
    dropped: list[int] = []
    kept_pages: list[PageResult] = []
    for page in doc.pages:
        score = score_page(page, min_words)
        if score["is_low_info"]:
            dropped.append(page.page_number)
        else:
            kept_pages.append(page)
    doc.pages = kept_pages
    return dropped
