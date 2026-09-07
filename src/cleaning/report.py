"""
cleaning/report.py

Audit trail of everything the cleaning pipeline removed or flagged.
Returned alongside the cleaned DocumentResult so removals are never
silent — if a fact goes missing from your RAG answers later, this is
where you check first.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict


@dataclass
class CleaningReport:
    empty_shapes_removed: int = 0
    boilerplate_texts_found: list[str] = field(default_factory=list)
    boilerplate_objects_removed: int = 0
    duplicate_text_objects_removed: int = 0
    duplicate_pages_removed: list[int] = field(default_factory=list)
    low_info_pages_removed: list[int] = field(default_factory=list)
    pages_before: int = 0
    pages_after: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        return (
            f"{self.pages_before} pages -> {self.pages_after} pages | "
            f"empty shapes removed: {self.empty_shapes_removed} | "
            f"boilerplate objects removed: {self.boilerplate_objects_removed} "
            f"({len(self.boilerplate_texts_found)} distinct boilerplate texts) | "
            f"duplicate text objects removed: {self.duplicate_text_objects_removed} | "
            f"duplicate pages dropped: {self.duplicate_pages_removed} | "
            f"low-info pages dropped: {self.low_info_pages_removed}"
        )
