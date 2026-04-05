import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import SearchRequest, SearchResponse
from app.pipeline import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)

app = FastAPI(
    title="Agentic Search API",
    description="Structured entity extraction with source-level citations",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    return await run_pipeline(request.query)
