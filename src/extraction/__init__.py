"""
extraction/

Coordinate-aware context extraction for RAG pipelines, covering both
PPTX and PDF sources through a shared object/page/document schema.

Import each pipeline explicitly, not from this top-level package:

    from extraction.pptx.pipeline import extract_pptx
    from extraction.pdf.pipeline import extract_pdf

This package deliberately does NOT import both pipelines here — doing
so would force python-pptx AND fitz/pdfplumber to be installed just to
use extraction.common.schemas, even for callers who only work with one
format (or only need the shared schema, like the cleaning package does).

Both entry points return an extraction.common.schemas.DocumentResult.
"""

