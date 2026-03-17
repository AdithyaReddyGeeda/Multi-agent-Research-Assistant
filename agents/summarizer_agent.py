from __future__ import annotations

from typing import List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agents.llm import get_llm
from graph.state import ResearchState


def summarizer_agent(state: ResearchState) -> ResearchState:
    """
    Summarize the collected search results into clear, concise paragraphs.
    """
    llm = get_llm()
    search_results: List[str] = state.get("search_results", []) or []

    if not search_results:
        fallback = "No search results available for summarization."
        return {
            "summaries": [fallback],
            "messages": [
                AIMessage(content=fallback),
            ],
        }

    try:
        joined_results = "\n\n---\n\n".join(search_results)

        system_prompt = (
            "You are an expert summarizer. Given search results, extract and summarize "
            "the key facts, data points, and insights in clear concise paragraphs. "
            "Be objective and thorough."
        )
        human_prompt = (
            "Summarize the following web search results into a small number of concise, "
            "well-structured paragraphs focusing on the most important information.\n\n"
            f"{joined_results}"
        )

        response = llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt),
            ]
        )
        text = response.content if isinstance(response, AIMessage) else str(response)

        # Keep a single composite summary as the first element.
        summaries: List[str] = [text.strip()] if text.strip() else [
            "Summarizer returned an empty response."
        ]

        return {
            "summaries": summaries,
            "messages": [
                AIMessage(content="Summarizer agent produced summaries of search results."),
            ],
        }
    except Exception as exc:  # noqa: BLE001
        error_msg = f"Summarizer agent encountered an error: {exc}"
        return {
            "summaries": [error_msg],
            "messages": [
                AIMessage(content=error_msg),
            ],
        }

