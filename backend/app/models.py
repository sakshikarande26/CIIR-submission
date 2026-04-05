from datetime import datetime
from pydantic import BaseModel


# ── Request ──────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str


# ── Schema Inference ─────────────────────────────────────────────────────────

class InferredSchema(BaseModel):
    entity_type: str
    columns: list[str]
    query_interpretation: str


# ── Search ───────────────────────────────────────────────────────────────────

class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str
    rank_position: int


# ── Scraping ─────────────────────────────────────────────────────────────────

class ScrapedPage(BaseModel):
    url: str
    title: str
    raw_content: str
    success: bool


# ── Chunking ─────────────────────────────────────────────────────────────────

class Chunk(BaseModel):
    chunk_id: str
    source_url: str
    source_title: str
    chunk_text: str


# ── Extraction / Response ────────────────────────────────────────────────────

class Citation(BaseModel):
    source_id: str
    chunk_id: str
    url: str
    title: str
    passage: str


class CellValue(BaseModel):
    value: str | None = None
    citations: list[Citation] = []


class Entity(BaseModel):
    name: str
    attributes: dict[str, CellValue]


class Source(BaseModel):
    source_id: str
    url: str
    title: str
    scraped_at: datetime


class PipelineMetadata(BaseModel):
    total_time_seconds: float
    search_time: float
    scrape_time: float
    extraction_time: float
    pages_scraped: int
    pages_failed: int
    chunks_created: int
    entities_found: int


class SearchResponse(BaseModel):
    query: str
    entity_type: str
    columns: list[str]
    entities: list[Entity]
    sources: list[Source]
    pipeline_metadata: PipelineMetadata
