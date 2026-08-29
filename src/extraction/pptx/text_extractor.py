"""
extraction/pptx/text_extractor.py

Semantic role detection and paragraph/run-level text extraction for
PPTX text frames.
"""

from __future__ import annotations
from pptx.enum.shapes import PP_PLACEHOLDER


def infer_role(shape, slide_height: int) -> str:
    """Ground-truth role from placeholder_format.type when available;
    falls back to a position heuristic for freeform text boxes."""
    if shape.is_placeholder:
        ph_type = shape.placeholder_format.type
        if ph_type in (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE):
            return "title"
        if ph_type == PP_PLACEHOLDER.SUBTITLE:
            return "subtitle"
        if ph_type == PP_PLACEHOLDER.BODY:
            return "body"
        if ph_type in (PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.SLIDE_NUMBER, PP_PLACEHOLDER.DATE):
            return "footer_meta"

    if shape.top is not None and slide_height and shape.top < slide_height * 0.15:
        return "title"
    return "body"


def extract_text_runs(shape) -> tuple[list[str], list[dict], list[dict]]:
    """Returns (paragraph texts, hyperlinks, emphasized runs)."""
    paragraphs: list[str] = []
    hyperlinks: list[dict] = []
    emphasis: list[dict] = []

    for para in shape.text_frame.paragraphs:
        text = "".join(run.text for run in para.runs).strip()
        if text:
            paragraphs.append(text)

        for run in para.runs:
            if run.hyperlink and run.hyperlink.address:
                hyperlinks.append({"text": run.text, "url": run.hyperlink.address})

            is_bold = bool(run.font.bold)
            has_color = False
            try:
                has_color = run.font.color is not None and run.font.color.type is not None
            except Exception:
                pass

            if is_bold or has_color:
                emphasis.append({"text": run.text, "bold": is_bold, "colored": has_color})

    return paragraphs, hyperlinks, emphasis
