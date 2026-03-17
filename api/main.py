from __future__ import annotations

import asyncio
from typing import Any, Dict

import httpx
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.llm import MODEL_CONFIG
from graph.workflow import run_research


class ResearchRequest(BaseModel):
    query: str


app = FastAPI(title="Multi-Agent Research Assistant")


# Allow requests from the Streamlit frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _check_ollama_available() -> bool:
    """
    Best-effort check that the local Ollama server is reachable.
    """
    base_url = str(MODEL_CONFIG.get("base_url", "http://localhost:11434")).rstrip("/")
    health_url = f"{base_url}/api/tags"

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(health_url)
        return resp.status_code == 200
    except Exception:  # noqa: BLE001
        return False


@app.on_event("startup")
async def startup_event() -> None:
    """
    On startup, ping the Ollama server and print a warning if it appears down.
    """
    available = await _check_ollama_available()
    if not available:
        print(
            "Warning: Ollama does not appear to be running at "
            f"{MODEL_CONFIG.get('base_url')}. "
            "Start Ollama and pull the model before using the API."
        )


@app.get("/health")
async def health() -> Dict[str, Any]:
    """
    Lightweight health check for the backend and the configured Ollama model.
    """
    available = await _check_ollama_available()
    return {
        "status": "ok" if available else "ollama-unreachable",
        "ollama_model": MODEL_CONFIG.get("model", "unknown"),
    }


@app.post("/research")
async def research(request: ResearchRequest) -> Dict[str, Any]:
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    import time

    start = time.time()

    try:
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, run_research, query),
            timeout=600.0,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Research timed out after 600s.")

    result["elapsed_seconds"] = round(time.time() - start, 1)
    result["timestamp"] = datetime.utcnow().isoformat()
    result["model_used"] = MODEL_CONFIG.get("model", "unknown")
    return result

