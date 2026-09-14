"""
chunking/schemas.py

Output shape for the chunking stage. Same philosophy as
extraction/common/schemas.py — one canonical dataclass so nothing
downstream (embeddings, vector DB) has to guess the JSON shape.

Every Chunk carries its source metadata with it (which document, which
slide/page, what role/type it was) — this is what lets you later cite
"this answer came from slide 5 of deck X" instead of returning bare
text with no provenance.
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict


@dataclass
class ChunkMetadata:
    document_id: str
    source_type: str        # "pptx" | "pdf"
    page_number: int
    role: str = "body"      # "title" | "body" | "table" | "chart"
    object_ids: list[int] = field(default_factory=list)  # which extracted object(s) this chunk came from


@dataclass
class Chunk:
    chunk_id: str            # e.g. "pharma_dashboards_p1_c0"
    text: str
    metadata: ChunkMetadata

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "metadata": asdict(self.metadata),
        }


def chunks_to_json(chunks: list[Chunk], **kwargs) -> str:
    return json.dumps([c.to_dict() for c in chunks], indent=2, **kwargs)
