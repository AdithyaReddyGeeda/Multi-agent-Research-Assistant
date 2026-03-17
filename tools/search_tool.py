from __future__ import annotations

import time
from typing import Optional

from langchain_community.tools import DuckDuckGoSearchRun


_search = DuckDuckGoSearchRun()


def run_search(query: str, *, max_results: Optional[int] = None) -> str:
    """
    Run a DuckDuckGo search for the given query and return the raw text result.

    A short sleep is added to be gentle with DuckDuckGo rate limits, especially
    if this function is called multiple times in quick succession.
    """
    # Basic backoff between calls to respect rate limits.
    time.sleep(1.0)
    if max_results is not None:
        return _search.run({"query": query, "max_results": max_results})
    return _search.run(query)

