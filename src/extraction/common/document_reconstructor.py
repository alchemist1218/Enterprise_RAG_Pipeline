"""
extraction/common/document_reconstructor.py

Turns an already-ordered list of ExtractedObject into the linearized
`reconstructed_text` string stored on PageResult. Kept as its own
module because both pipelines need identical logic here, and it's a
natural seam to extend later (e.g. inserting "[TABLE]" markers,
summarizing charts inline, etc.) without touching either extractor.
"""

from __future__ import annotations
from extraction.common.schemas import ExtractedObject


def reconstruct_text(ordered_objects: list[ExtractedObject]) -> str:
    lines = []
    for obj in ordered_objects:
        if obj.type == "text" and obj.text:
            lines.append(obj.text)
        elif obj.type == "chart":
            chart_line = obj.title or "[chart]"
            if obj.categories and obj.series:
                summary = ", ".join(
                    f"{s['name']}: {list(zip(obj.categories, s['values']))}"
                    for s in obj.series
                )
                chart_line = f"{chart_line} ({summary})"
            lines.append(chart_line)
        elif obj.type == "table" and obj.rows:
            lines.append("\n".join(" | ".join(row) for row in obj.rows))
    return "\n".join(lines)
