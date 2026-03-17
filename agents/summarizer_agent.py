from __future__ import annotations

from typing import List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agents.llm import get_llm
from graph.state import ResearchState


SUMMARIZER_SYSTEM_PROMPT = """You are an expert research summarizer.
Given raw search results, extract and summarize key information.

For each source, produce:
- A 1-sentence headline capturing the main point
- 2-3 sentences of supporting detail
- Any key statistics, dates, or named entities mentioned

Be objective, precise, and cite specific claims where possible.
Output as a numbered list, one entry per source."""


def summarizer_agent(state: ResearchState) -> ResearchState:
    """
    Summarize the collected search results into clear, structured entries per source.
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

        system_prompt = SUMMARIZER_SYSTEM_PROMPT
        human_prompt = (
            "Here are the raw web search results. Produce a numbered list as described "
            "in your instructions, one entry per logical source.\n\n"
            f"{joined_results}"
        )

        response = llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt),
            ]
        )
        text = response.content if isinstance(response, AIMessage) else str(response)

        summaries: List[str] = [text.strip()] if text and text.strip() else [
            "Summarizer returned an empty response."
        ]

        return {
            "summaries": summaries,
            "messages": [
                AIMessage(content="Summarizer agent produced structured summaries of search results."),
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

