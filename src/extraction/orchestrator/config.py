"""
extraction/orchestrator/config.py

Loads pipeline configuration from YAML. Kept as its own module for the
same reason as ppt_loader.py / pdf_loader.py — if config ever needs to
come from CLI flags, env vars, or a different file format, only this
module changes.

Requires: pip install pyyaml --break-system-packages
"""

from __future__ import annotations
from dataclasses import dataclass
import yaml


@dataclass
class PipelineConfig:
    raw_data_path: str          # directory containing mixed .pptx / .pdf files
    output_path: str            # where per-file JSON results are written
    recursive: bool = True      # walk subdirectories of raw_data_path
    skip_unknown_files: bool = True  # False = raise on an unrecognized file instead of skipping


def load_config(config_path: str) -> PipelineConfig:
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    if "raw_data_path" not in raw:
        raise ValueError(f"Config at {config_path} is missing required key: raw_data_path")

    return PipelineConfig(
        raw_data_path=raw["raw_data_path"],
        output_path=raw.get("output_path", "output"),
        recursive=raw.get("recursive", True),
        skip_unknown_files=raw.get("skip_unknown_files", True),
    )
