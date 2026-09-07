"""
extraction/pdf/pdf_loader.py

PDF extraction needs two libraries: PyMuPDF (fitz) for fast text/image
block coordinates, and pdfplumber for its table-finding algorithm —
neither library alone covers both well. This module opens both against
the same file and yields them page-by-page in lockstep.
"""

from __future__ import annotations
from contextlib import contextmanager

import fitz
import pdfplumber


@contextmanager
def open_pdf(pdf_path: str):
    """Yields (fitz_doc, plumber_doc). Use pages(fitz_doc, plumber_doc)
    to iterate matched page pairs."""
    fitz_doc = fitz.open(pdf_path)
    with pdfplumber.open(pdf_path) as plumber_doc:
        yield fitz_doc, plumber_doc
    fitz_doc.close()


def iter_page_pairs(fitz_doc, plumber_doc):
    for i, (fitz_page, plumber_page) in enumerate(zip(fitz_doc, plumber_doc.pages), start=1):
        yield i, fitz_page, plumber_page
