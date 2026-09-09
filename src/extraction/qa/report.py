"""
extraction/qa/report.py

Runs quality metrics across every extracted JSON in a directory,
produces:
  1. a CSV with one row per slide, sorted by risk score (highest first)
  2. a manual review list: every flagged slide + a random sample of
     "clean" slides (to catch systematic issues the heuristics missed)

This is a triage tool, not a pass/fail judge — the risk score tells
you WHERE to look first across 1000 slides, not whether any single
slide is definitely wrong.
"""

from __future__ import annotations
import json
import csv
import random
from pathlib import Path

from extraction.common.schemas import DocumentResult, PageResult, ExtractedObject, BoundingBox
from extraction.qa.metrics import evaluate_slide, SlideQualityFlags


def _load_document(json_path: str) -> DocumentResult:
    with open(json_path) as f:
        raw = json.load(f)

    pages = []
    for p in raw["pages"]:
        objects = []
        for o in p["objects"]:
            bbox = BoundingBox(**o["bbox"]) if "bbox" in o else BoundingBox(0, 0, 0, 0)
            o = {**o, "bbox": bbox}
            objects.append(ExtractedObject(**{k: v for k, v in o.items() if k in ExtractedObject.__dataclass_fields__}))
        pages.append(PageResult(
            page_number=p["page_number"],
            width=p["width"],
            height=p["height"],
            objects=objects,
            reconstructed_text=p.get("reconstructed_text", ""),
            notes=p.get("notes"),
            layout_name=p.get("layout_name"),
            ocr_applied=p.get("ocr_applied"),
        ))
    return DocumentResult(document_id=raw["document_id"], source_type=raw["source_type"], pages=pages)


def evaluate_directory(output_dir: str) -> list[SlideQualityFlags]:
    """Runs quality metrics over every .json file in output_dir."""
    results = []
    for json_path in Path(output_dir).glob("*.json"):
        doc = _load_document(str(json_path))
        for page in doc.pages:
            q = evaluate_slide(page)
            q.document_id = doc.document_id
            results.append(q)
    return results


def write_report_csv(results: list[SlideQualityFlags], out_csv: str):
    """Full report, one row per slide, worst-first."""
    results_sorted = sorted(results, key=lambda r: r.risk_score, reverse=True)
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["document_id", "page_number", "risk_score", "char_count", "object_count", "flags"])
        for r in results_sorted:
            writer.writerow([r.document_id, r.page_number, r.risk_score, r.char_count, r.object_count, "; ".join(r.flags)])


def build_review_sample(
    results: list[SlideQualityFlags],
    random_sample_size: int = 30,
    flagged_cap: int = 100,
    seed: int = 42,
) -> list[SlideQualityFlags]:
    """Manual review list = every flagged slide (capped) + a random
    sample of clean slides. The random sample matters even though those
    slides "passed" — it's how you catch a systematic bug the heuristics
    don't know to look for (e.g. every 3rd slide's title getting cut off
    in a way that doesn't reduce char_count much)."""
    flagged = [r for r in results if r.risk_score > 0]
    clean = [r for r in results if r.risk_score == 0]

    flagged_sorted = sorted(flagged, key=lambda r: r.risk_score, reverse=True)[:flagged_cap]

    rng = random.Random(seed)
    random_sample = rng.sample(clean, min(random_sample_size, len(clean)))

    return flagged_sorted + random_sample


def print_summary(results: list[SlideQualityFlags]):
    total = len(results)
    flagged = sum(1 for r in results if r.risk_score > 0)
    print(f"Total slides evaluated: {total}")
    print(f"Flagged (risk_score > 0): {flagged} ({flagged/total:.1%})" if total else "No slides found.")

    flag_counts: dict[str, int] = {}
    for r in results:
        for f in r.flags:
            key = f.split("(")[0]  # collapse "image_no_ocr_text(x3)" -> "image_no_ocr_text"
            flag_counts[key] = flag_counts.get(key, 0) + 1

    print("\nFlag breakdown:")
    for name, count in sorted(flag_counts.items(), key=lambda x: -x[1]):
        print(f"  {name}: {count}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m extraction.qa.report <output_dir>")
        raise SystemExit(1)

    output_dir = sys.argv[1]
    results = evaluate_directory(output_dir)

    print_summary(results)
    write_report_csv(results, "qa_report.csv")
    print("\nFull report written to qa_report.csv (sorted worst-first)")

    sample = build_review_sample(results)
    with open("qa_review_sample.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["document_id", "page_number", "risk_score", "flags", "reason"])
        for r in sample:
            reason = "FLAGGED" if r.risk_score > 0 else "RANDOM_SAMPLE"
            writer.writerow([r.document_id, r.page_number, r.risk_score, "; ".join(r.flags), reason])
    print(f"Manual review sample ({len(sample)} slides) written to qa_review_sample.csv")
