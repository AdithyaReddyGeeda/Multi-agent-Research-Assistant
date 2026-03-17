from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

from langchain_community.tools import DuckDuckGoSearchRun

from graph.state import ResearchState


logger = logging.getLogger(__name__)
_search = DuckDuckGoSearchRun()


def _search_single(sub_query: str, index: int) -> Dict[str, Any]:
    """Run a single DuckDuckGo search for one sub-query."""
    try:
        time.sleep(index * 1.2)  # stagger requests to avoid rate limiting
        result = _search.run(sub_query)
        logger.info("Search %d complete: %d chars", index, len(result))
        return {"sub_query": sub_query, "result": result, "index": index}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Search %d failed: %s", index, exc)
        return {
            "sub_query": sub_query,
            "result": f"Search failed for: {sub_query}",
            "index": index,
        }


def search_node(state: ResearchState) -> Dict[str, Any]:
    """
    Runs parallel DuckDuckGo searches for all sub-queries from the planner.
    Falls back to searching the original query if no sub-queries exist.
    """
    sub_queries = state.get("sub_queries") or []
    original_query = state.get("query", "")

    # Fallback: if planner didn't run, search original query only
    if not sub_queries:
        logger.warning("No sub-queries found, falling back to original query.")
        sub_queries = [original_query]

    logger.info("Running %d parallel searches...", len(sub_queries))

    results_per_query: List[Dict[str, Any]] = []

    # Run searches in parallel (max 3 workers)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_search_single, sq, i): i
            for i, sq in enumerate(sub_queries)
        }
        for future in as_completed(futures):
            res = future.result()
            results_per_query.append(res)

    # Sort by original index to maintain order
    results_per_query.sort(key=lambda x: x["index"])
    flat_results: List[str] = [r["result"] for r in results_per_query]

    logger.info("All parallel searches complete.")
    return {
        "search_results": flat_results,
        "search_results_per_query": results_per_query,
    }

