"""
extraction/orchestrator/runner.py

Walks raw_data_path, detects each file's real type, routes it to the
right pipeline (extract_pptx / extract_pdf), filters out empty
decorative objects, and writes one JSON file per input document.

A failure on a single file is logged and skipped rather than crashing
the whole batch — a directory of 200 mixed files shouldn't fail
entirely because file #47 is corrupted.
"""

from __future__ import annotations
import os
import logging
from pathlib import Path

from extraction.pptx.pipeline import extract_pptx
from extraction.pdf.pipeline import extract_pdf
from extraction.common.object_filter import filter_document
from extraction.orchestrator.config import PipelineConfig
from extraction.orchestrator.file_detector import detect_file_type, FileType

logger = logging.getLogger("extraction.runner")


def discover_files(raw_data_path: str, recursive: bool = True) -> list[str]:
    root = Path(raw_data_path)
    pattern = "**/*" if recursive else "*"
    return [str(p) for p in root.glob(pattern) if p.is_file()]


def route_and_extract(path: str, file_type: FileType):
    """Directs the flow based on detected type — this is the
    is_ppt-style branch: PPTX goes one way, PDF goes the other."""
    if file_type == FileType.PPTX:
        return extract_pptx(path)
    if file_type == FileType.PDF:
        return extract_pdf(path)
    raise ValueError(f"Unrecognized file type: {path}")


def run_pipeline(config: PipelineConfig) -> dict:
    """Processes every file in raw_data_path.
    Returns {"processed": [...], "skipped": [...], "failed": [...]}."""
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
            result = route_and_extract(path, file_type)
            result = filter_document(result)

            out_path = Path(config.output_path) / f"{Path(path).stem}.json"
            with open(out_path, "w") as f:
                f.write(result.to_json(indent=2))

            logger.info(f"[{file_type.value}] {path} -> {out_path}")
            summary["processed"].append(path)

        except Exception as e:
            logger.error(f"Failed to process {path}: {e}")
            summary["failed"].append({"path": path, "error": str(e)})

    return summary
