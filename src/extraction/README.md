# extraction/

Coordinate-aware context extraction for RAG pipelines — PPTX and PDF,
unified behind one schema.

```
extraction/
├── __init__.py                 # exposes extract_pptx, extract_pdf
├── common/
│   ├── schemas.py               # BoundingBox / ExtractedObject / PageResult / DocumentResult
│   ├── spatial_ordering.py      # row-overlap grouping (used by pptx pipeline)
│   └── document_reconstructor.py# ordered objects -> reconstructed_text
├── pptx/
│   ├── ppt_loader.py             # Presentation() wrapper
│   ├── shape_extractor.py        # walks shapes incl. groups, dispatches by type
│   ├── text_extractor.py         # role inference + paragraphs/hyperlinks/emphasis
│   ├── table_extractor.py        # merge-aware table rows
│   ├── chart_extractor.py        # categories + series + chart title
│   ├── image_extractor.py        # picture metadata
│   └── pipeline.py               # extract_pptx(path) -> DocumentResult
└── pdf/
    ├── pdf_loader.py              # opens fitz + pdfplumber together
    ├── block_extractor.py         # text/image blocks + font-size title heuristic
    ├── column_detector.py         # multi-column reading order
    ├── table_extractor.py         # pdfplumber table finding
    ├── ocr_fallback.py            # OCR only for low-text-density pages
    └── pipeline.py                # extract_pdf(path) -> DocumentResult
```

## Why `common/` is small on purpose

PPTX and PDF only genuinely share two things: the **output schema**
and **row-based reading order** (which PDF also uses on single-column
pages via the same overlap-clustering idea, though its actual ordering
entry point is `pdf/column_detector.py` since PDF needs column-first
ordering, not row-first). Everything else — chart data, merge-aware
tables, OCR, placeholder types — is genuinely format-specific and
lives in its own subpackage. Resist the urge to force more into
`common/` than the two formats actually share.

## Install

```bash
pip install python-pptx pymupdf pdfplumber pillow pytesseract --break-system-packages
```

`pytesseract` also requires the system `tesseract` binary. If it's not
installed, everything still works except OCR fallback on scanned PDF
pages (`ocr_fallback.OCR_AVAILABLE` will be `False`).

## Usage

```python
from extraction.pptx.pipeline import extract_pptx
from extraction.pdf.pipeline import extract_pdf

deck = extract_pptx("market_research.pptx")
report = extract_pdf("annual_report.pdf")

# both are DocumentResult with the same shape
print(deck.to_json(indent=2))
print(report.to_json(indent=2))
```

Or from the command line:

```bash
python -m extraction.pptx.pipeline market_research.pptx
python -m extraction.pdf.pipeline annual_report.pdf
```

## Known limits (see the sketchnote for the full list)

- SmartArt / OLE objects in PPTX aren't extracted yet.
- OCR text loses precise per-word bbox alignment vs. native PDF text.
- Column detection uses a simple x-gap heuristic — dense 3+ column
  magazine layouts may need a smarter clustering approach.
- Nested (multi-level) PPTX groups aren't offset-corrected — only one
  level of grouping is flattened with fully accurate coordinates.
