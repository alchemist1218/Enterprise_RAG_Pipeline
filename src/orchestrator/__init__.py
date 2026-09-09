"""
Global orchestration layer for the enterprise RAG pipeline.

This package intentionally sits above extraction-specific modules so we can
route files, run extraction, run cleaning, and later chain other
modules in a single place.
"""

from .config import PipelineConfig, load_config
from .runner import discover_files, route_and_extract, run_pipeline

__all__ = [
    "PipelineConfig",
    "load_config",
    "discover_files",
    "route_and_extract",
    "run_pipeline",
]
