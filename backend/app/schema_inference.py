import json
import logging

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY_SCHEMA, GEMINI_MODEL
from app.models import InferredSchema

logger = logging.getLogger(__name__)

SCHEMA_PROMPT = """\
You are an expert information retrieval assistant.

Given a user search query, infer:
1. The **entity_type** — the category of real-world thing the user is looking for (e.g. "company", "restaurant", "university", "person", "product").
2. A list of **columns** — the most useful attributes to collect for each entity. Always include "Name" as the first column. Choose 5-8 columns that would make a useful comparison table.
3. A **query_interpretation** — a one-sentence clarification of what the user is actually looking for. Be specific about scope, location, and constraints. This will be used to filter extraction results, so precision matters.

Respond with JSON matching this exact schema:
{
  "entity_type": "<string>",
  "columns": ["Name", ...],
  "query_interpretation": "<one-sentence description of exactly what entities to extract>"
}

Examples:
- Query: "AI startups in healthcare" → {"entity_type": "company", "columns": ["Name", "Founded", "Funding", "Focus Area", "Location", "Website"], "query_interpretation": "Startup companies applying artificial intelligence to the healthcare industry"}
- Query: "top pizza places in Brooklyn" → {"entity_type": "restaurant", "columns": ["Name", "Address", "Rating", "Price Range", "Cuisine Style", "Known For"], "query_interpretation": "Pizza restaurants located in Brooklyn, New York"}
- Query: "top colleges in UMass Amherst" → {"entity_type": "college", "columns": ["Name", "Department", "Programs Offered", "Ranking", "Notable Faculty"], "query_interpretation": "Schools, colleges, and academic departments within the University of Massachusetts Amherst"}

Now process this query:
"""


async def infer_schema(query: str) -> InferredSchema:
    """Ask Gemini to infer entity type and columns from the user query."""
    client = genai.Client(api_key=GEMINI_API_KEY_SCHEMA)

    try:
        response = await client.aio.models.generate_content(
            model=GEMINI_MODEL,
            contents=SCHEMA_PROMPT + query,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        data = json.loads(response.text)
        return InferredSchema(
            entity_type=data["entity_type"],
            columns=data["columns"],
            query_interpretation=data.get("query_interpretation", query),
        )
    except Exception as e:
        logger.error("Schema inference failed: %s", e)
        return InferredSchema(entity_type="entity", columns=["Name", "Description"], query_interpretation=query)
