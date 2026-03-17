from __future__ import annotations

from typing import List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agents.llm import get_llm
from graph.state import ResearchState


def synthesizer_agent(state: ResearchState) -> ResearchState:
    """
    Combine the summaries and critic feedback into a final structured report.
    """
    llm = get_llm()
    summaries: List[str] = state.get("summaries", []) or []
    critique: str = state.get("critique", "") or ""
    query = state.get("query", "") or ""

    if not summaries:
        fallback = "Final report could not be generated because no summaries were available."
        return {
            "final_report": fallback,
            "messages": [
                AIMessage(content=fallback),
            ],
        }

    try:
        joined_summaries = "\n\n---\n\n".join(summaries)

        system_prompt = (
            "You are an expert research writer. Using the summaries and critic feedback, "
            "write a comprehensive, well-structured research report with sections:\n"
            "## Summary, ## Key Findings, ## Analysis, ## Conclusion.\n"
            "Use markdown formatting. Be clear, objective, and well organized."
        )

        human_parts = [
            f"Original research query:\n{query}\n" if query else "",
            "Summaries:\n",
            joined_summaries,
            "\n\nCritic feedback:\n",
            critique or "No additional critique provided.",
        ]
        human_prompt = "".join(human_parts)

        response = llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt),
            ]
        )
        text = response.content if isinstance(response, AIMessage) else str(response)
        final_report = text.strip() or "Final report generation returned an empty response."

        return {
            "final_report": final_report,
            "messages": [
                AIMessage(content="Synthesizer agent produced the final research report."),
            ],
        }
    except Exception as exc:  # noqa: BLE001
        error_msg = f"Final report generation failed: {exc}"
        return {
            "final_report": error_msg,
            "messages": [
                AIMessage(content=error_msg),
            ],
        }

