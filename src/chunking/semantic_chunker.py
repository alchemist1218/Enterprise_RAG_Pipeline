from __future__ import annotations
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from chunking.sentence_splitter import split_sentences

DEFAULT_DROP_SENSITIVITY = 0.5  # Cosine similarity threshold for dropping similar sentences

MAX_WORD_PER_CHUNKING = 300

MIN_SENTENCE_BEFORE_CUT = 2

def _tfidv_embedding_fn(sentences: list[str]) -> np.ndarray:
    """Computes TF-IDF embeddings for a list of sentences."""
     if len(sentences) <2:
       return np.zeros((len(sentences), 1))
    vectorizer = TfdfVectorizer(analyzer="char_w",ngram_range=(3,5))

    try:
      return vectorizer.fit_transform(sentences).toarray()
    except ValueError:
      return np.zeros((len(sentences),1))