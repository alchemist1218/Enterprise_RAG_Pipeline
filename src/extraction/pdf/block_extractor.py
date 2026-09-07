"""
extraction/pdf/block_extractor.py

Raw text/image block extraction with coordinates, plus a font-size +
position title heuristic. PDFs have no placeholder-type metadata like
PPTX does, so role detection here is heuristic-only, not ground-truth.
"""

from __future__ import annotations
from extraction.common.schemas import ExtractedObject, BoundingBox


def extract_text_blocks(fitz_page, start_id: int = 0) -> list[ExtractedObject]:
    blocks = []
    obj_id = start_id
    for b in fitz_page.get_text("dict")["blocks"]:
        if b["type"] != 0:  # 0 = text block, 1 = image block
            continue
        text = "".join(
            span["text"] for line in b["lines"] for span in line["spans"]
        ).strip()
        if not text:
            continue

        sizes = [span["size"] for line in b["lines"] for span in line["spans"]]
        avg_size = sum(sizes) / len(sizes) if sizes else 0.0

        x0, y0, x1, y1 = b["bbox"]
        obj_id += 1
        blocks.append(ExtractedObject(
            id=obj_id,
            type="text",
            bbox=BoundingBox(x=x0, y=y0, width=x1 - x0, height=y1 - y0),
            text=text,
            paragraphs=[text],
            avg_font_size=avg_size,
        ))
    return blocks


def extract_image_blocks(fitz_page, start_id: int = 0) -> list[ExtractedObject]:
    images = []
    obj_id = start_id
    for img in fitz_page.get_image_info(xrefs=True):
        x0, y0, x1, y1 = img["bbox"]
        obj_id += 1
        images.append(ExtractedObject(
            id=obj_id,
            type="image",
            bbox=BoundingBox(x=x0, y=y0, width=x1 - x0, height=y1 - y0),
            xref=img.get("xref"),
        ))
    return images


def infer_role(block: ExtractedObject, page_height: float, max_font_size: float) -> str:
    is_large_font = bool(max_font_size) and (block.avg_font_size or 0) >= max_font_size * 0.9
    is_near_top = block.bbox.y < page_height * 0.12
    return "title" if (is_large_font and is_near_top) else "body"
