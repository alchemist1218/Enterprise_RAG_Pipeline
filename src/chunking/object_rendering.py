from __future__ import annotations
from extraction.common.schemas import ExtractedObject

def table_to_text( rows : list[list[str]]) -> str:
    """Converts a table (list of rows, each a list of strings) into a single string."""
    return "\n".join(["\t".join(row) for row in rows])

def chart_to_text( obj : ExtractedObject) -> str:
    """Converts a chart object into a string representation."""
    title = obj.title or "Chart"
    if obj.categories and obj.series:
        parts = []
        for s in obj.series:
            pairs = ", ".join(f"{cat}: {val}" for cat, val in zip(obj.categories, s.get("values", [])))
            parts.append(f"{s.get('name', 'Series')} — {pairs}")
        return f"{title}. " + " | ".join(parts)
    return title