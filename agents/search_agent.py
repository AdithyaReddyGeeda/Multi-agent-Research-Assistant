from __future__ import annotations

from typing import List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agents.llm import get_llm
from graph.state import ResearchState
from tools.search_tool import run_search


def search_agent(state: ResearchState) -> ResearchState:
    """
    Use the LLM to refine the user's query into concrete web search queries,
    then execute them via DuckDuckGo and store the raw results.
    """
    llm = get_llm()
    query = state.get("query", "").strip()

    if not query:
        fallback = "No query provided to search agent."
        return {
            "search_results": [fallback],
            "messages": [
                AIMessage(content=fallback),
            ],
        }

    try:
        system_prompt = (
            "You are a research search specialist. Given a user research query, "
            "propose up to 3 concrete web search queries that will retrieve the "
            "most relevant and recent information. Return them as plain text, "
            "one query per line."
        )
        human_prompt = f"User research query:\n{query}\n\nReturn 1–3 search queries, one per line."

        response = llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt),
            ]
        )
        text = response.content if isinstance(response, AIMessage) else str(response)
        candidate_queries: List[str] = [
            line.strip() for line in text.splitlines() if line.strip()
        ]

        # Ensure at least the original query is searched.
        if not candidate_queries:
            candidate_queries = [query]

        # Limit to at most 3 searches to keep things snappy.
        candidate_queries = candidate_queries[:3]

        results: List[str] = []
        for q in candidate_queries:
            try:
                result_text = run_search(q)
                results.append(f"Search query: {q}\n\n{result_text}")
            except Exception as inner_exc:  # noqa: BLE001
                results.append(f"Failed to fetch results for '{q}': {inner_exc}")

        if not results:
            results = ["Search agent could not retrieve any results."]

        return {
            "search_results": results,
            "messages": [
                AIMessage(
                    content="Search agent completed web searches for the query."
                ),
            ],
        }
    except Exception as exc:  # noqa: BLE001
        error_msg = f"Search agent encountered an error: {exc}"
        return {
            "search_results": [error_msg],
            "messages": [
                AIMessage(content=error_msg),
            ],
        }

