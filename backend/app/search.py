import logging

import httpx

from app.config import SERPAPI_API_KEY, SEARCH_NUM_RESULTS, SERPAPI_SEARCH_URL
from app.models import SearchResult

logger = logging.getLogger(__name__)


async def web_search(query: str) -> list[SearchResult]:
    """Call SerpAPI (Google Search) and return top organic results."""
    params = {
        "q": query,
        "engine": "google",
        "api_key": SERPAPI_API_KEY,
        "num": SEARCH_NUM_RESULTS,
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                SERPAPI_SEARCH_URL, params=params, timeout=15
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.error("SerpAPI request failed: %s", e)
            return []

    data = resp.json()
    organic = data.get("organic_results", [])

    results: list[SearchResult] = []
    for item in organic[:SEARCH_NUM_RESULTS]:
        results.append(
            SearchResult(
                url=item.get("link", ""),
                title=item.get("title", ""),
                snippet=item.get("snippet", ""),
                rank_position=item.get("position", len(results) + 1),
            )
        )
    return results
