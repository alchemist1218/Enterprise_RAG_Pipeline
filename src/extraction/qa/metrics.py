"""
extraction/qa/metrics.py

Cheap, automated heuristics for spotting likely extraction failures
across a large batch — no manual reading required to compute these.

None of these PROVE a slide extracted correctly; they only flag
slides that look suspicious so a human reviews the highest-risk ones
first instead of reading 1000 slides in file order.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from extraction.common.schemas import PageResult


@dataclass
class SlideQualityFlags:
    document_id: str
    page_number: int
    char_count: int
    object_count: int
    flags: list[str] = field(default_factory=list)
    risk_score: int = 0

    def add_flag(self, name: str, weight: int = 1):
        self.flags.append(name)
        self.risk_score += weight


# Tune these thresholds against your own deck style once you've done
# an initial manual pass — pharma dashboards and text-heavy report
# decks will want different cutoffs.
MIN_CHARS_PER_SLIDE = 20          # below this, the slide is suspiciously empty
LOW_CHARS_PER_SLIDE = 60          # below this, flag as "thin" (not necessarily wrong)
HIGH_SHAPE_RATIO = 0.6            # if >60% of objects are contentless "shape" type


def evaluate_slide(page: PageResult) -> SlideQualityFlags:
    q = SlideQualityFlags(
        document_id="",  # filled in by caller, which has doc-level context
        page_number=page.page_number,
        char_count=len(page.reconstructed_text or ""),
        object_count=len(page.objects),
    )

    # 1. Suspiciously empty slide — likely extraction miss or a fully
    #    visual/decorative slide with no real text content
    if q.char_count < MIN_CHARS_PER_SLIDE:
        q.add_flag("near_empty_text", weight=5)
    elif q.char_count < LOW_CHARS_PER_SLIDE:
        q.add_flag("thin_text", weight=2)

    # 2. Charts that were detected but came back with no usable data
    #    (unsupported chart type, or python-pptx couldn't read the series)
    for obj in page.objects:
        if obj.type == "chart" and not (obj.categories or obj.series):
            q.add_flag("chart_extraction_empty", weight=4)

    # 3. Tables detected but empty — merge-cell edge case, or a
    #    malformed table object
    for obj in page.objects:
        if obj.type == "table" and not obj.rows:
            q.add_flag("table_extraction_empty", weight=4)

    # 4. Images with no OCR text at all — could be a blank/decorative
    #    image (fine) or a chart screenshot OCR failed to read (not fine).
    #    Can't tell which from here — that's exactly why it's flagged,
    #    not silently accepted.
    image_objs = [o for o in page.objects if o.type == "image"]
    images_without_text = [o for o in image_objs if not o.text]
    if images_without_text:
        q.add_flag(f"image_no_ocr_text(x{len(images_without_text)})", weight=2)

    # 5. Slide dominated by contentless "shape" objects relative to
    #    real content — may indicate misclassification upstream
    if q.object_count > 0:
        shape_only = sum(1 for o in page.objects if o.type == "shape")
        if shape_only / q.object_count > HIGH_SHAPE_RATIO:
            q.add_flag("high_shape_noise_ratio", weight=1)

    return q
