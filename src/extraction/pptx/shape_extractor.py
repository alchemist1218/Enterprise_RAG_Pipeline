"""
extraction/pptx/shape_extractor.py

Walks a slide's shape tree (including one level of groups) and
dispatches each shape to the right specialized extractor, building a
flat, unordered list of ExtractedObject. Ordering is a separate
concern — see extraction/common/spatial_ordering.py.
"""

from __future__ import annotations
from pptx.enum.shapes import MSO_SHAPE_TYPE

from extraction.common.schemas import ExtractedObject, BoundingBox
from extraction.pptx.text_extractor import infer_role, extract_text_runs
from extraction.pptx.table_extractor import extract_table
from extraction.pptx.chart_extractor import extract_chart
from extraction.pptx.image_extractor import extract_image_meta
from extraction.pptx.image_ocr import ocr_image_shape, OCR_AVAILABLE


def _bbox(shape) -> BoundingBox:
    return BoundingBox(x=shape.left, y=shape.top, width=shape.width, height=shape.height)


def extract_slide_objects(slide, slide_height: int) -> list[ExtractedObject]:
    objects: list[ExtractedObject] = []
    obj_id = 0

    for z_order, shape in enumerate(slide.shapes):
        # Note: nested (multi-level) groups may need cumulative offset math
        # for full coordinate fidelity — this handles one level directly.
        sub_shapes = shape.shapes if shape.shape_type == MSO_SHAPE_TYPE.GROUP else [shape]

        for sub_shape in sub_shapes:
            obj_id += 1
            common_kwargs = dict(
                id=obj_id,
                bbox=_bbox(sub_shape),
                shape_id=sub_shape.shape_id,
                name=sub_shape.name,
                z_order=z_order,
            )

            if getattr(sub_shape, "has_chart", False) and sub_shape.has_chart:
                chart_data = extract_chart(sub_shape) or {}
                objects.append(ExtractedObject(type="chart", **common_kwargs, **chart_data))

            elif getattr(sub_shape, "has_table", False) and sub_shape.has_table:
                rows = extract_table(sub_shape)
                objects.append(ExtractedObject(type="table", **common_kwargs, rows=rows))

            elif sub_shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                img_meta = extract_image_meta(sub_shape)
                ocr_text = ocr_image_shape(sub_shape)  # None if OCR unavailable or found nothing
                objects.append(ExtractedObject(
                    type="image", **common_kwargs, **img_meta,
                    text=ocr_text,
                    ocr_attempted=OCR_AVAILABLE,  # True even if ocr_text ends up None/empty
                ))

            elif getattr(sub_shape, "has_text_frame", False) and sub_shape.has_text_frame and sub_shape.text_frame.text.strip():
                role = infer_role(sub_shape, slide_height)
                paragraphs, hyperlinks, emphasis = extract_text_runs(sub_shape)
                objects.append(ExtractedObject(
                    type="text", **common_kwargs,
                    role=role,
                    text="\n".join(paragraphs),
                    paragraphs=paragraphs,
                    hyperlinks=hyperlinks,
                    emphasis=emphasis,
                ))

            else:
                objects.append(ExtractedObject(type="shape", **common_kwargs))

    return objects
