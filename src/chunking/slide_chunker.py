"""
chunking/slide_chunker.py

Implements the structure-aware chunking rules:

  Rule 1: One slide/page = one chunk, by default — a slide's text
          already reads as one coherent unit (title + body flow
          together), so don't split it further unless it's oversized.
  Rule 2: Tables and charts become their OWN separate chunks — mixing
          raw numbers into flowing prose dilutes both; a table read as
          "row | row | row" text is more useful as its own retrievable
          unit than blended into a paragraph.
  Rule 3: If a slide's text chunk would be oversized, split it further
          — but ONLY at sentence boundaries, never mid-sentence.
  Rule 4: Every chunk carries ChunkMetadata (document_id, page_number,
          role, source object ids) so retrieval results are traceable
          back to an exact slide.

Thresholds (MAX_WORDS_PER_CHUNK, MIN_WORDS_PER_CHUNK) are a starting
point, not a law — tune them once you've looked at real chunk output
from your own decks.
"""

from __future__ import annotations
from extraction.common.schemas import PageResult, ExtractedObject
from chunking.schemas import Chunk, ChunkMetadata
from chunking.sentance_splitter import split_into_sentence_chunks

MAX_WORDS_PER_CHUNK = 300   # above this, split further at sentence boundaries (Rule 3)
MIN_WORDS_PER_CHUNK = 3     # chunks below this are usually not worth keeping on their own


def _table_to_text(rows: list[list[str]]) -> str:
    """Renders table rows as readable pipe-separated lines — keeps the
    row/column structure legible in plain text, rather than losing it
    by just concatenating cell values."""
    return "\n".join(" | ".join(cell for cell in row if cell) for row in rows)


def _chart_to_text(obj: ExtractedObject) -> str:
    """Renders chart categories+values as a readable sentence, so the
    chunk is self-contained prose rather than a raw data dump."""
    title = obj.title or "Chart"
    if obj.categories and obj.series:
        parts = []
        for s in obj.series:
            pairs = ", ".join(f"{cat}: {val}" for cat, val in zip(obj.categories, s.get("values", [])))
            parts.append(f"{s.get('name', 'Series')} — {pairs}")
        return f"{title}. " + " | ".join(parts)
    return title

def chunk_page(page: PageResult, document_id: str, source_type: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    chunk_index = 0

    def next_chunk_id() -> str:
        nonlocal chunk_index
        cid = f"{document_id}_p{page.page_number}_c{chunk_index}"
        chunk_index += 1
        return cid

    # --- Rule 1 + 3: combine all plain text objects, split only if oversized ---
    text_objects = [o for o in page.objects if o.type == "text" and o.text]
    combined_text = "\n".join(o.text for o in text_objects).strip()

    if combined_text:
        word_count = len(combined_text.split())
        object_ids = [o.id for o in text_objects]

        if word_count <= MAX_WORDS_PER_CHUNK:
            pieces = [combined_text]
        else:
            pieces = split_into_sentence_chunks(combined_text, MAX_WORDS_PER_CHUNK)

        for piece in pieces:
            if len(piece.split()) < MIN_WORDS_PER_CHUNK:
                continue  # too small to be a meaningful standalone chunk
            chunks.append(Chunk(
                chunk_id=next_chunk_id(),
                text=piece,
                metadata=ChunkMetadata(
                    document_id=document_id, source_type=source_type,
                    page_number=page.page_number, role="body",
                    object_ids=object_ids,
                ),
            ))

    # --- Rule 2: tables get their own chunk(s) ---
    for obj in page.objects:
        if obj.type == "table" and obj.rows:
            table_text = _table_to_text(obj.rows)
            if table_text.strip():
                chunks.append(Chunk(
                    chunk_id=next_chunk_id(),
                    text=table_text,
                    metadata=ChunkMetadata(
                        document_id=document_id, source_type=source_type,
                        page_number=page.page_number, role="table",
                        object_ids=[obj.id],
                    ),
                ))

    # --- Rule 2: charts get their own chunk(s) ---
    for obj in page.objects:
        if obj.type == "chart" and (obj.categories or obj.series):
            chart_text = _chart_to_text(obj)
            chunks.append(Chunk(
                chunk_id=next_chunk_id(),
                text=chart_text,
                metadata=ChunkMetadata(
                    document_id=document_id, source_type=source_type,
                    page_number=page.page_number, role="chart",
                    object_ids=[obj.id],
                ),
            ))

    return chunks
