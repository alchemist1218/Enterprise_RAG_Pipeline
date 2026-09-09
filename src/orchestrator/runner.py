"""
Global runner for enterprise RAG pipeline.

This single orchestrator owns the sequence:
    detect file type -> route pdf/pptx extractor -> clean -> write output
Later stages such as chunking or embedding can be added here.
"""

from __future__ import annotations
import os
import logging
from pathlib import Path

from extraction.pptx.pipeline import extract_pptx
from extraction.pdf.pipeline import extract_pdf
from extraction.common.object_filter import filter_document
from cleaning.pipeline import clean_document
from orchestrator.config import PipelineConfig
from orchestrator.file_detector import detect_file_type, FileType

logger = logging.getLogger("orchestrator.runner")


def discover_files(raw_data_path: str, recursive: bool = True) -> list[str]:
    root = Path(raw_data_path)
    pattern = "**/*" if recursive else "*"
    files = []
    for p in root.glob(pattern):
        if not p.is_file():
            continue
        if p.name.startswith("~$"):
            continue
        if p.name.startswith("."):
            continue
        files.append(str(p))
    return files


def route_and_extract(path: str, file_type: FileType):
    """Send each file to the correct parser implementation."""
    if file_type == FileType.PPTX:
        return extract_pptx(path)
    if file_type == FileType.PDF:
        return extract_pdf(path)
    raise ValueError(f"Unrecognized file type: {path}")


def run_pipeline(config: PipelineConfig) -> dict:
    """Run one top-level flow with extraction and cleaning chained together."""
    os.makedirs(config.output_path, exist_ok=True)
    files = discover_files(config.raw_data_path, config.recursive)

    summary = {"processed": [], "skipped": [], "failed": []}

    for path in files:
        file_type = detect_file_type(path)

        if file_type == FileType.UNKNOWN:
            logger.warning(f"Skipping unrecognized file: {path}")
            summary["skipped"].append(path)
            if not config.skip_unknown_files:
                raise ValueError(f"Unrecognized file (and skip_unknown_files=False): {path}")
            continue

        try:
            raw_doc = route_and_extract(path, file_type)
            raw_doc = filter_document(raw_doc)

            # Single global orchestration chain: extraction -> cleaning
            cleaned_doc, cleaning_report = clean_document(raw_doc)

            out_path = Path(config.output_path) / f"{Path(path).stem}.json"
            with open(out_path, "w") as f:
                f.write(cleaned_doc.to_json(indent=2))

            logger.info(f"[{file_type.value}] {path} -> {out_path}")
            summary["processed"].append(path)

        except Exception as e:
            logger.error(f"Failed to process {path}: {e}")
            summary["failed"].append({"path": path, "error": str(e)})

    return summary
