"""
extraction/pptx/ppt_loader.py

Thin wrapper around python-pptx's Presentation() so the rest of the
pipeline depends on this module, not directly on python-pptx's API —
if the loading strategy ever needs to change (e.g. streaming from
bytes instead of a path), only this file changes.
"""

from __future__ import annotations
from pptx import Presentation
from pptx.presentation import Presentation as PresentationType


def load_presentation(pptx_path: str) -> PresentationType:
    return Presentation(pptx_path)
