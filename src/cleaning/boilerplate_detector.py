"""
cleaning/boilerplate_detector.py

Detects text that repeats across most of the document — page headers,
footers, "Confidential" watermarks, recurring section dividers — and
strips it. This is exactly the kind of thing we saw in the pharma
dashboard example: identical divider rectangles and repeated labels
on every slide add nothing per-slide, but WOULD get embedded and
retrieved as if they were unique content on every single chunk.

Frequency-based, not a hardcoded phrase list: works on any deck/report
without knowing its specific boilerplate strings in advance.
"""

from __future__ import annotations
from collections import Counter

from extraction.common.schemas import DocumentResult


def detect_boilerplate(doc: DocumentResult, min_page_fraction: float = 0.6) -> set[str]:
    """A text string counts as boilerplate if it appears (once per page,
    not counted twice on the same page) on at least `min_page_fraction`
    of all pages."""
    total_pages = len(doc.pages)
    if total_pages < 3:
        return set()  # not enough pages to detect a meaningful pattern

    text_page_counts: Counter[str] = Counter()
    for page in doc.pages:
        seen_this_page = set()
        for obj in page.objects:
            if obj.type == "text" and obj.text:
                norm = obj.text.strip().lower()
                if norm and norm not in seen_this_page:
                    text_page_counts[norm] += 1
                    seen_this_page.add(norm)

    threshold = max(2, int(total_pages * min_page_fraction))
    return {text for text, count in text_page_counts.items() if count >= threshold}


def strip_boilerplate(doc: DocumentResult, boilerplate_texts: set[str]) -> int:
    """Removes objects whose text matches a detected boilerplate string.
    Returns the count of objects removed."""
    removed = 0
    for page in doc.pages:
        kept = []
        for obj in page.objects:
            if obj.type == "text" and obj.text and obj.text.strip().lower() in boilerplate_texts:
                removed += 1
                continue
            kept.append(obj)
        page.objects = kept
    return removed
