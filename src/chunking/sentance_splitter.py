"""
chunking/sentence_splitter.py

A deliberately simple, dependency-free sentence splitter. Only used
as a FALLBACK when a slide's combined text is too long for one chunk
(see slide_chunker.py) — most slides never hit this path at all, since
Rule 1 is "one slide = one chunk" by default.

This is not a linguistically perfect sentence tokenizer (it can be
fooled by abbreviations like "Dr." or "e.g."). That's an accepted
trade-off: a proper NLP sentence tokenizer (e.g. spaCy) would be more
accurate but adds a heavy dependency for a fallback path that runs on
a minority of slides. Revisit this if oversized slides turn out to be
common in your decks.
"""

from __future__ import annotations
import re

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    return [s for s in _SENTENCE_BOUNDARY.split(text) if s.strip()]


def group_sentences_by_word_count(sentences: list[str], max_words: int) -> list[str]:
    """Greedily groups whole sentences into chunks, never splitting a
    sentence itself — only choosing WHERE between sentences to cut."""
    chunks: list[str] = []
    current: list[str] = []
    current_words = 0

    for sentence in sentences:
        word_count = len(sentence.split())
        if current and current_words + word_count > max_words:
            chunks.append(" ".join(current))
            current = []
            current_words = 0
        current.append(sentence)
        current_words += word_count

    if current:
        chunks.append(" ".join(current))

    return chunks


def split_into_sentence_chunks(text: str, max_words: int) -> list[str]:
    return group_sentences_by_word_count(split_sentences(text), max_words)
