"""
cleaning/deduplicator.py

Two distinct dedup problems, handled separately:

1. Duplicate text OBJECTS within a single page — e.g. a title that got
   pasted twice, or a text box duplicated by accident during deck
   editing. Exact-match via hash; cheap and safe (no false positives).

2. Duplicate PAGES across the document — e.g. an appendix that
   reprints an earlier slide, or a re-exported PDF with a repeated
   page. Fuzzy similarity via difflib, since near-duplicates (same
   content, minor formatting differences) are common and exact-hash
   matching would miss them.
"""

from __future__ import annotations
import hashlib
from difflib import SequenceMatcher

from extraction.common.schemas import DocumentResult, PageResult


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()


def dedup_text_objects_within_page(page: PageResult) -> int:
    seen: set[str] = set()
    kept = []
    removed = 0
    for obj in page.objects:
        if obj.type == "text" and obj.text:
            h = _hash_text(obj.text)
            if h in seen:
                removed += 1
                continue
            seen.add(h)
        kept.append(obj)
    page.objects = kept
    return removed


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def find_duplicate_pages(doc: DocumentResult, similarity_threshold: float = 0.92) -> list[int]:
    """Returns page_numbers to drop, keeping the FIRST occurrence of any
    near-duplicate group. O(n^2) comparisons — fine for typical deck/
    report sizes; for very large documents, pre-bucket by length first."""
    to_drop: list[int] = []
    kept_texts: list[tuple[int, str]] = []

    for page in doc.pages:
        text = page.reconstructed_text
        if not text.strip():
            continue  # empty pages are handled by low_info_filter, not here
        is_duplicate = any(
            _similarity(text, kept_text) >= similarity_threshold
            for _, kept_text in kept_texts
        )
        if is_duplicate:
            to_drop.append(page.page_number)
        else:
            kept_texts.append((page.page_number, text))

    return to_drop
