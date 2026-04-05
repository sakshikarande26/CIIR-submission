import logging
import re

from thefuzz import fuzz

from app.config import FUZZY_MATCH_THRESHOLD
from app.models import CellValue, Entity

logger = logging.getLogger(__name__)

_SUFFIX_RE = re.compile(
    r"\b(inc\.?|corp\.?|llc|ltd\.?|co\.?|plc|gmbh|s\.?a\.?)\s*$",
    re.IGNORECASE,
)


def _normalize_name(name: str) -> str:
    """Strip legal suffixes and extra whitespace for comparison."""
    name = _SUFFIX_RE.sub("", name).strip()
    name = re.sub(r"\s+", " ", name)
    return name.lower()


def _merge_cell_values(a: CellValue, b: CellValue) -> CellValue:
    """Merge two CellValues, preferring the non-null one and combining citations."""
    if a.value and not b.value:
        value = a.value
    elif b.value and not a.value:
        value = b.value
    elif a.value and b.value:
        # Keep the longer / more informative value
        value = a.value if len(a.value) >= len(b.value) else b.value
    else:
        value = None

    # Merge citation lists, dedup by chunk_id
    seen_chunk_ids: set[str] = set()
    merged_citations = []
    for c in a.citations + b.citations:
        if c.chunk_id not in seen_chunk_ids:
            seen_chunk_ids.add(c.chunk_id)
            merged_citations.append(c)

    return CellValue(value=value, citations=merged_citations)


def _merge_entities(primary: Entity, duplicate: Entity) -> Entity:
    """Merge duplicate into primary. Primary wins on name; attributes are merged."""
    merged_attrs: dict[str, CellValue] = {}
    all_keys = set(primary.attributes.keys()) | set(duplicate.attributes.keys())

    for key in all_keys:
        a = primary.attributes.get(key, CellValue())
        b = duplicate.attributes.get(key, CellValue())
        merged_attrs[key] = _merge_cell_values(a, b)

    # Keep whichever entity has more filled attributes as the "primary" name
    primary_filled = sum(1 for v in primary.attributes.values() if v.value)
    dup_filled = sum(1 for v in duplicate.attributes.values() if v.value)
    name = primary.name if primary_filled >= dup_filled else duplicate.name

    return Entity(name=name, attributes=merged_attrs)


def resolve_entities(entities: list[Entity]) -> list[Entity]:
    """Deduplicate entities using fuzzy name matching."""
    if not entities:
        return []

    resolved: list[Entity] = []

    for entity in entities:
        merged = False
        for i, existing in enumerate(resolved):
            # token_set_ratio handles "Tempus" vs "Tempus AI" well (subset match)
            # but is less aggressive than token_sort_ratio on unrelated names
            name_a = _normalize_name(entity.name)
            name_b = _normalize_name(existing.name)
            score = fuzz.token_set_ratio(name_a, name_b)
            # Penalize if the shorter name is very short (1-2 words)
            # to avoid merging "H1" with "H1B Visa" or "AI" with "AI Labs"
            shorter = min(len(name_a.split()), len(name_b.split()))
            if shorter <= 2 and score < 100:
                score = min(score, fuzz.ratio(name_a, name_b))
            if score >= FUZZY_MATCH_THRESHOLD:
                resolved[i] = _merge_entities(existing, entity)
                merged = True
                logger.info(
                    "Merged '%s' into '%s' (score=%d)",
                    entity.name,
                    existing.name,
                    score,
                )
                break
        if not merged:
            resolved.append(entity)

    return resolved
