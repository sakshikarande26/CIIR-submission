"""Lightweight keyword-based relevance scoring for chunks.

Filters out chunks that are unlikely to contain entities matching the query
before sending them to the LLM, reducing noise and improving extraction precision.
"""

import re
import logging

from app.models import Chunk

logger = logging.getLogger(__name__)

# Minimum relevance score (0-1) for a chunk to be sent to the extractor
_MIN_RELEVANCE = 0.15


def _tokenize(text: str) -> set[str]:
    """Lowercase word tokenization, stripping punctuation."""
    return set(re.findall(r'[a-z0-9]+', text.lower()))


def _score_chunk(chunk_tokens: set[str], query_tokens: set[str]) -> float:
    """Compute Jaccard-style relevance: fraction of query terms found in chunk."""
    if not query_tokens:
        return 1.0
    overlap = chunk_tokens & query_tokens
    return len(overlap) / len(query_tokens)


def filter_relevant_chunks(
    chunks: list[Chunk],
    query: str,
    query_interpretation: str,
    min_relevance: float = _MIN_RELEVANCE,
) -> list[Chunk]:
    """Keep only chunks that have enough keyword overlap with the query.

    Uses both the raw query and the query_interpretation to build
    the keyword set, so "AI startups in healthcare" produces tokens
    from both the query and "Startup companies applying artificial
    intelligence to the healthcare industry".
    """
    combined = f"{query} {query_interpretation}"
    query_tokens = _tokenize(combined)

    # Remove very common stopwords that would inflate every chunk's score
    stopwords = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at',
        'to', 'for', 'of', 'and', 'or', 'that', 'this', 'with', 'from',
        'by', 'it', 'be', 'as', 'do', 'has', 'had', 'have', 'not', 'but',
        'what', 'which', 'who', 'how', 'all', 'each', 'every', 'about',
    }
    query_tokens -= stopwords

    if not query_tokens:
        return chunks

    kept: list[Chunk] = []
    dropped = 0

    for chunk in chunks:
        chunk_tokens = _tokenize(chunk.chunk_text)
        score = _score_chunk(chunk_tokens, query_tokens)

        if score >= min_relevance:
            kept.append(chunk)
        else:
            dropped += 1

    if dropped:
        logger.info(
            "Relevance filter: kept %d/%d chunks (dropped %d below %.0f%% threshold)",
            len(kept), len(chunks), dropped, min_relevance * 100,
        )

    return kept
