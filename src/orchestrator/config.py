"""
Global orchestration configuration.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass
class PipelineConfig:
    raw_data_path: str
    output_path: str
    recursive: bool = True
    skip_unknown_files: bool = True


def _resolve_config_path(config_path: str) -> Path:
    """Resolve config.yaml from repo root, source folder, or explicit CLI path."""
    candidate = Path(config_path)
    if candidate.is_absolute() and candidate.exists():
        return candidate

    cwd_candidate = Path.cwd() / candidate
    if cwd_candidate.exists():
        return cwd_candidate

    repo_root = Path(__file__).resolve().parents[2]
    src_candidate = repo_root / "src" / candidate
    if src_candidate.exists():
        return src_candidate

    configs_candidate = repo_root / "configs" / candidate
    if configs_candidate.exists():
        return configs_candidate

    return candidate


def load_config(config_path: str) -> PipelineConfig:
    resolved = _resolve_config_path(config_path)
    with open(resolved, "r") as f:
        raw = yaml.safe_load(f)

    if "raw_data_path" not in raw:
        raise ValueError(f"Config at {resolved} is missing required key: raw_data_path")

    return PipelineConfig(
        raw_data_path=raw["raw_data_path"],
        output_path=raw.get("output_path", "output"),
        recursive=raw.get("recursive", True),
        skip_unknown_files=raw.get("skip_unknown_files", True),
    )
