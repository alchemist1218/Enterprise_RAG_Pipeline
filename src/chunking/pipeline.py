"""
chunking/pipeline.py

Top-level entry points for chunking. Reads already-extracted JSON
(the output of extraction/), runs chunk_page() over every page, and
writes one {document_id}_chunks.json per input document.

    chunk_document_json(path)          -> list[Chunk]  (single file)
    chunk_directory(input_dir, out_dir) -> summary dict (batch)
"""

from __future__ import annotations
import os
from pathlib import Path

from chunking.loader import load_document_json
from chunking.schemas import Chunk, chunks_to_json
from chunking.slide_chunker import chunk_page


def chunk_document_json(json_path: str) -> list[Chunk]:
    doc = load_document_json(json_path)
    chunks: list[Chunk] = []
    for page in doc.pages:
        chunks.extend(chunk_page(page, doc.document_id, doc.source_type))
    return chunks


def chunk_directory(input_dir: str, output_dir: str) -> dict:
    """Chunks every .json file in input_dir (extraction output),
    writes {document_id}_chunks.json per file into output_dir.
    Returns {"processed": [...], "failed": [...]}."""
    os.makedirs(output_dir, exist_ok=True)
    summary = {"processed": [], "failed": []}

    for json_path in Path(input_dir).glob("*.json"):
        try:
            chunks = chunk_document_json(str(json_path))
            out_path = Path(output_dir) / f"{json_path.stem}_chunks.json"
            with open(out_path, "w") as f:
                f.write(chunks_to_json(chunks))
            summary["processed"].append({"file": str(json_path), "chunk_count": len(chunks)})
        except Exception as e:
            summary["failed"].append({"file": str(json_path), "error": str(e)})

    return summary


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python -m chunking.pipeline <extracted_json_dir> <chunks_output_dir>")
        raise SystemExit(1)

    summary = chunk_directory(sys.argv[1], sys.argv[2])
    total_chunks = sum(p["chunk_count"] for p in summary["processed"])
    print(f"Processed: {len(summary['processed'])} files -> {total_chunks} chunks")
    print(f"Failed: {len(summary['failed'])}")
    for f in summary["failed"]:
        print(f"  - {f['file']}: {f['error']}")
