"""
cleaning/

Format-agnostic pre-processing on the unified DocumentResult schema
(produced by either extraction.pptx.pipeline.extract_pptx or
extraction.pdf.pipeline.extract_pdf). Runs after extraction, before
chunking.

    from cleaning.pipeline import clean_document

    cleaned_doc, report = clean_document(doc)
"""

from cleaning.pipeline import clean_document

__all__ = ["clean_document"]
