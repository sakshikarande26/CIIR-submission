import json
import logging

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY_EXTRACTOR, GEMINI_MODEL
from app.models import Chunk, InferredSchema

logger = logging.getLogger(__name__)

# Smaller batches = more focused extraction per call
_BATCH_SIZE = 20


def _build_extraction_prompt(
    query: str,
    schema: InferredSchema,
    chunks: list[Chunk],
) -> str:
    columns_str = ", ".join(f'"{c}"' for c in schema.columns)

    passages = "\n\n".join(
        f"[{c.chunk_id}]\n{c.chunk_text}" for c in chunks
    )

    return f"""\
You are a precise information extraction system for an academic information retrieval lab. Your goal is MAXIMUM PRECISION — only extract entities you are confident are correct.

USER QUERY: "{query}"
INTERPRETATION: {schema.query_interpretation}
ENTITY TYPE TO EXTRACT: {schema.entity_type}
COLUMNS: [{columns_str}]

SCOPE RULES (read carefully):
- ONLY extract {schema.entity_type} entities that directly answer the query "{query}".
- If the query specifies a location or domain (e.g., "in Brooklyn", "in healthcare"), ONLY include entities genuinely within that scope. Do NOT include entities merely mentioned on the same page that exist outside the scope.
- Do NOT extract entities used as comparisons, examples of competitors, or historical references unless they themselves match the query.
- If an entity is ambiguous or you are unsure whether it matches the query scope, DO NOT include it.
- It is far better to return 5 correct entities than 20 where half are wrong.

VALUE RULES:
- If a value is not EXPLICITLY stated in the passage text, set it to null. Never guess, infer, or use world knowledge.
- Every non-null value MUST have a citation to the specific chunk_id where that exact fact appears.
- If you cannot quote specific text from the passage that states a fact, the value MUST be null.

CITATION RULES:
- Use ONLY chunk_ids that appear in the passages below (e.g. "source_0_chunk_0").
- Each citation must actually support the value. Do not cite a chunk just because it mentions the entity.
- If a value is null, citations must be an empty list.

OUTPUT: A JSON array. Each element:
{{
  "name": "<entity name>",
  "attributes": {{
    "<Column>": {{"value": "<string or null>", "citations": ["<chunk_id>", ...]}},
    ...
  }}
}}

Every column from [{columns_str}] must appear in attributes, even if null.
If NO entities match the query in these passages, return an empty array: []

PASSAGES:
{passages}
"""


async def extract_entities(
    schema: InferredSchema,
    chunks: list[Chunk],
    query: str = "",
) -> list[dict]:
    """Send chunks to Gemini and extract structured entities with citations.

    Returns the raw list of entity dicts (parsed JSON) so the pipeline can
    attach full Citation objects with passage text.
    """
    if not chunks:
        return []

    client = genai.Client(api_key=GEMINI_API_KEY_EXTRACTOR)
    all_entities: list[dict] = []

    for i in range(0, len(chunks), _BATCH_SIZE):
        batch = chunks[i : i + _BATCH_SIZE]
        prompt = _build_extraction_prompt(query, schema, batch)

        try:
            response = await client.aio.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            )
            entities = json.loads(response.text)
            if isinstance(entities, list):
                all_entities.extend(entities)
            else:
                logger.warning("Gemini returned non-list: %s", type(entities))
        except (json.JSONDecodeError, Exception) as e:
            logger.error("Extraction failed for batch %d: %s", i, e)

    return all_entities
