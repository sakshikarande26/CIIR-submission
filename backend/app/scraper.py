import asyncio
import logging

import httpx
import trafilatura

from app.config import SCRAPE_SEMAPHORE_LIMIT, SCRAPE_TIMEOUT_SECONDS
from app.models import ScrapedPage, SearchResult

logger = logging.getLogger(__name__)


async def _fetch_page(
    client: httpx.AsyncClient,
    result: SearchResult,
    semaphore: asyncio.Semaphore,
) -> ScrapedPage:
    """Download and extract main content from a single URL."""
    async with semaphore:
        try:
            resp = await client.get(
                result.url,
                timeout=SCRAPE_TIMEOUT_SECONDS,
                follow_redirects=True,
            )
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            logger.warning("Failed to fetch %s: %s", result.url, e)
            return ScrapedPage(
                url=result.url, title=result.title, raw_content="", success=False
            )

        # trafilatura extraction is CPU-bound; run in thread pool
        loop = asyncio.get_running_loop()
        text = await loop.run_in_executor(
            None,
            lambda: trafilatura.extract(html, include_comments=False) or "",
        )

        if not text:
            logger.warning("No content extracted from %s", result.url)
            return ScrapedPage(
                url=result.url, title=result.title, raw_content="", success=False
            )

        return ScrapedPage(
            url=result.url, title=result.title, raw_content=text, success=True
        )


async def scrape_pages(results: list[SearchResult]) -> list[ScrapedPage]:
    """Scrape all search result URLs concurrently."""
    semaphore = asyncio.Semaphore(SCRAPE_SEMAPHORE_LIMIT)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; AgenticSearchBot/1.0; "
            "+https://github.com/example/agentic-search)"
        )
    }
    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [_fetch_page(client, r, semaphore) for r in results]
        pages = await asyncio.gather(*tasks)
    return list(pages)
