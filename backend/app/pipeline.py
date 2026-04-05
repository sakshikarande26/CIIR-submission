import asyncio
import logging
import time
from datetime import datetime, timezone

from app.chunker import chunk_pages
from app.entity_resolver import resolve_entities
from app.extractor import extract_entities
from app.models import (
    CellValue,
    Citation,
    Chunk,
    Entity,
    PipelineMetadata,
    SearchResponse,
    Source,
)
from app.relevance import filter_relevant_chunks
from app.schema_inference import infer_schema
from app.scraper import scrape_pages
from app.search import web_search

logger = logging.getLogger(__name__)


def _build_chunk_lookup(chunks: list[Chunk]) -> dict[str, Chunk]:
    """Map chunk_id → Chunk for fast citation resolution."""
    return {c.chunk_id: c for c in chunks}


def _build_source_lookup(
    chunks: list[Chunk],
) -> dict[str, Source]:
    """Create Source objects keyed by URL (deduped)."""
    sources: dict[str, Source] = {}
    for c in chunks:
        if c.source_url not in sources:
            sources[c.source_url] = Source(
                source_id=c.chunk_id.rsplit("_chunk_", 1)[0],
                url=c.source_url,
                title=c.source_title,
                scraped_at=datetime.now(timezone.utc),
            )
    return sources


def _hydrate_entities(
    raw_entities: list[dict],
    chunk_lookup: dict[str, Chunk],
    source_lookup: dict[str, Source],
) -> list[Entity]:
    """Convert raw extractor dicts into full Entity models with Citation objects."""
    entities: list[Entity] = []

    for raw in raw_entities:
        name = raw.get("name", "Unknown")
        raw_attrs = raw.get("attributes", {})
        attributes: dict[str, CellValue] = {}

        for col_name, cell_data in raw_attrs.items():
            if not isinstance(cell_data, dict):
                attributes[col_name] = CellValue(value=str(cell_data) if cell_data else None)
                continue

            value = cell_data.get("value")
            raw_citations = cell_data.get("citations", [])

            # Only keep citations that reference real chunks
            citations: list[Citation] = []
            for cid in raw_citations:
                chunk = chunk_lookup.get(cid)
                if chunk:
                    source = source_lookup.get(chunk.source_url)
                    citations.append(
                        Citation(
                            source_id=source.source_id if source else "",
                            chunk_id=cid,
                            url=chunk.source_url,
                            title=chunk.source_title,
                            passage=chunk.chunk_text,
                        )
                    )

            # If there's a value but no valid citations, null it out
            # (the LLM hallucinated a chunk_id or cited nothing)
            if value and not citations:
                value = None

            attributes[col_name] = CellValue(value=value, citations=citations)

        entities.append(Entity(name=name, attributes=attributes))

    return entities


def _validate_entities(entities: list[Entity]) -> list[Entity]:
    """Remove entities that have no substance — all null values or zero citations."""
    valid: list[Entity] = []

    for entity in entities:
        # Count non-null attributes (excluding the Name column itself)
        filled = sum(
            1 for k, v in entity.attributes.items()
            if k != "Name" and v.value is not None
        )
        total_citations = sum(
            len(v.citations) for v in entity.attributes.values()
        )

        if filled == 0 and total_citations == 0:
            logger.debug("Dropped entity '%s': no filled attributes or citations", entity.name)
            continue

        valid.append(entity)

    dropped = len(entities) - len(valid)
    if dropped:
        logger.info("Validation: dropped %d empty entities, kept %d", dropped, len(valid))

    return valid


async def run_pipeline(query: str) -> SearchResponse:
    """Execute the full agentic search pipeline."""
    pipeline_start = time.perf_counter()

    # Step 1: Schema inference and web search run concurrently
    t0 = time.perf_counter()
    schema, search_results = await asyncio.gather(
        infer_schema(query),
        web_search(query),
    )
    search_time = time.perf_counter() - t0

    logger.info(
        "Schema: entity_type=%s, columns=%s, interpretation=%s",
        schema.entity_type, schema.columns, schema.query_interpretation,
    )
    logger.info("Search returned %d results", len(search_results))

    # Step 2: Scrape pages
    t1 = time.perf_counter()
    pages = await scrape_pages(search_results)
    scrape_time = time.perf_counter() - t1

    pages_scraped = sum(1 for p in pages if p.success)
    pages_failed = sum(1 for p in pages if not p.success)
    logger.info("Scraped %d pages (%d failed)", pages_scraped, pages_failed)

    # Step 3: Chunk
    chunks = chunk_pages(pages)
    logger.info("Created %d chunks", len(chunks))

    # Step 4: Relevance filtering — drop chunks unlikely to contain matching entities
    chunks = filter_relevant_chunks(chunks, query, schema.query_interpretation)
    logger.info("After relevance filter: %d chunks", len(chunks))

    # Step 5: Extract entities
    t2 = time.perf_counter()
    raw_entities = await extract_entities(schema, chunks, query=query)
    extraction_time = time.perf_counter() - t2
    logger.info("Extracted %d raw entities", len(raw_entities))

    # Step 6: Hydrate with full Citation objects
    chunk_lookup = _build_chunk_lookup(chunks)
    source_lookup = _build_source_lookup(chunks)
    entities = _hydrate_entities(raw_entities, chunk_lookup, source_lookup)

    # Step 7: Post-extraction validation — drop empty/unsupported entities
    entities = _validate_entities(entities)

    # Step 8: Entity resolution
    entities = resolve_entities(entities)
    logger.info("Resolved to %d unique entities", len(entities))

    total_time = time.perf_counter() - pipeline_start

    return SearchResponse(
        query=query,
        entity_type=schema.entity_type,
        columns=schema.columns,
        entities=entities,
        sources=list(source_lookup.values()),
        pipeline_metadata=PipelineMetadata(
            total_time_seconds=round(total_time, 2),
            search_time=round(search_time, 2),
            scrape_time=round(scrape_time, 2),
            extraction_time=round(extraction_time, 2),
            pages_scraped=pages_scraped,
            pages_failed=pages_failed,
            chunks_created=len(chunks),
            entities_found=len(entities),
        ),
    )
