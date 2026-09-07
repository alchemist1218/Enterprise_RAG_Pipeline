"""
extraction/common/label_flagger.py

Flags text that looks like a reused template placeholder whose content
doesn't match its own label (e.g. a "Market Share / Status" header
sitting above a plain count like "14 Assets" instead of a percentage).

Deliberately does NOT try to auto-correct the label — guessing the
"right" replacement text risks inserting wrong information, which is
worse than leaving it alone. This only adds a `flagged_for_review`
note so a human (or a downstream LLM cleanup pass with real judgment)
can decide what to do.
"""

from __future__ import annotations
import re
from extraction.common.schemas import PageResult

PERCENT_RE = re.compile(r"\d+(\.\d+)?%")


def flag_mismatched_labels(page: PageResult, label_terms: list[str] | None = None) -> list[str]:
    """Returns a list of human-readable warnings for this page. Does not
    mutate the page — call sites decide what to do with the warnings."""
    label_terms = label_terms or ["market share", "share / status"]
    warnings = []

    for obj in page.objects:
        if obj.type != "text" or not obj.paragraphs:
            continue
        joined = " ".join(obj.paragraphs).lower()

        has_label = any(term in joined for term in label_terms)
        if not has_label:
            continue

        # if the label mentions "share" but nothing in this object looks
        # like a percentage, the label likely doesn't match its content
        if "share" in joined and not PERCENT_RE.search(joined):
            warnings.append(
                f"Page {page.page_number}: text block {obj.id!r} says "
                f"{obj.paragraphs!r} — label mentions 'share' but no "
                f"percentage found; likely a stale template label."
            )

    return warnings
