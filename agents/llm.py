from __future__ import annotations

from typing import Any, Dict

from langchain_ollama import ChatOllama


# Central configuration for the local LLM backend.
MODEL_CONFIG: Dict[str, Any] = {
    "model": "llama3.2",
    "temperature": 0,
    "base_url": "http://localhost:11434",
}


def get_llm() -> ChatOllama:
    """
    Create and return a ChatOllama instance configured for local usage.

    All LLM calls in this project must go through this helper to ensure
    a single source of truth for model configuration.
    """
    return ChatOllama(
        model=MODEL_CONFIG["model"],
        temperature=MODEL_CONFIG["temperature"],
        base_url=MODEL_CONFIG["base_url"],
    )

