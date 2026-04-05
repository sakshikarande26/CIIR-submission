import re

from app.config import CHUNK_MIN_WORDS, CHUNK_MAX_WORDS
from app.models import Chunk, ScrapedPage

# Abbreviations whose trailing period should NOT trigger a sentence split
_ABBREVIATIONS = [
    'Dr', 'Mr', 'Ms', 'Mrs', 'Prof', 'Sr', 'Jr', 'St', 'vs',
    'Inc', 'Corp', 'Ltd', 'Co', 'Gen', 'Gov', 'Sgt', 'Capt',
    'Vol', 'Dept', 'Univ', 'Est', 'Approx', 'Fig', 'Ref',
]
# Also protect patterns like U.S., A.I., U.K.
_ABBREV_RE = re.compile(
    r'\b(' + '|'.join(re.escape(a) for a in _ABBREVIATIONS) + r')\.',
    re.IGNORECASE,
)
_INITIALS_RE = re.compile(r'\b([A-Z]\.){2,}')  # U.S., A.I., etc.
_PLACEHOLDER = '\x00'  # Null byte as placeholder for protected periods


def _split_into_sentences(text: str) -> list[str]:
    """Split text on sentence boundaries, protecting abbreviations."""
    text = re.sub(r'\s+', ' ', text).strip()

    # Protect abbreviation periods with placeholder
    text = _ABBREV_RE.sub(lambda m: m.group(0).replace('.', _PLACEHOLDER), text)
    text = _INITIALS_RE.sub(lambda m: m.group(0).replace('.', _PLACEHOLDER), text)

    # Split on sentence-ending punctuation followed by space + uppercase
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)

    # Restore placeholders
    parts = [p.replace(_PLACEHOLDER, '.').strip() for p in parts]
    return [s for s in parts if s]


def _chunk_text(sentences: list[str], min_words: int, max_words: int) -> list[str]:
    """Group sentences into chunks of roughly min_words–max_words."""
    chunks: list[str] = []
    current: list[str] = []
    current_word_count = 0

    for sentence in sentences:
        word_count = len(sentence.split())

        # If adding this sentence would exceed max_words and we already
        # have enough for a chunk, flush first
        if current_word_count + word_count > max_words and current_word_count >= min_words:
            chunks.append(" ".join(current))
            current = []
            current_word_count = 0

        current.append(sentence)
        current_word_count += word_count

        if current_word_count >= min_words:
            chunks.append(" ".join(current))
            current = []
            current_word_count = 0

    # Handle leftover
    if current:
        remainder = " ".join(current)
        if chunks and current_word_count < min_words // 2:
            # Attach small remainder to the last chunk
            chunks[-1] = chunks[-1] + " " + remainder
        else:
            chunks.append(remainder)

    return chunks


def chunk_pages(pages: list[ScrapedPage]) -> list[Chunk]:
    """Split scraped pages into passage-level chunks with source tracking."""
    all_chunks: list[Chunk] = []

    for source_idx, page in enumerate(pages):
        if not page.success or not page.raw_content.strip():
            continue

        sentences = _split_into_sentences(page.raw_content)
        if not sentences:
            continue

        text_chunks = _chunk_text(sentences, CHUNK_MIN_WORDS, CHUNK_MAX_WORDS)

        for chunk_idx, text in enumerate(text_chunks):
            all_chunks.append(
                Chunk(
                    chunk_id=f"source_{source_idx}_chunk_{chunk_idx}",
                    source_url=page.url,
                    source_title=page.title,
                    chunk_text=text,
                )
            )

    return all_chunks
