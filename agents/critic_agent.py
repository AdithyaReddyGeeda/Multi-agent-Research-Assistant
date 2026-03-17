from __future__ import annotations

from typing import List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agents.llm import get_llm
from graph.state import ResearchState


def critic_agent(state: ResearchState) -> ResearchState:
    """
    Review the summaries and identify gaps, unsupported claims, or missing angles.

    The critic responds with either:
    - 'APPROVED' if the summaries are sufficient, or
    - 'NEEDS REVISION' plus a detailed explanation of what is missing.
    """
    llm = get_llm()
    summaries: List[str] = state.get("summaries", []) or []

    if not summaries:
        critique = "NEEDS REVISION: No summaries available for critique."
        new_iteration = int(state.get("iteration", 0)) + 1
        return {
            "critique": critique,
            "iteration": new_iteration,
            "messages": [
                AIMessage(content=critique),
            ],
        }

    try:
        joined_summaries = "\n\n---\n\n".join(summaries)

        system_prompt = (
            "You are a critical research reviewer. Review the summaries provided and "
            "identify: gaps in information, unsupported claims, missing perspectives, "
            "or areas needing more detail. If summaries are sufficient, respond with "
            "APPROVED. If not, respond with NEEDS REVISION and explain what is missing."
        )
        human_prompt = (
            "Here are the summaries you should review:\n\n"
            f"{joined_summaries}\n\n"
            "Provide your response following the instructions."
        )

        response = llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt),
            ]
        )
        text = response.content if isinstance(response, AIMessage) else str(response)
        critique = text.strip() or "APPROVED"

        new_iteration = int(state.get("iteration", 0)) + 1

        return {
            "critique": critique,
            "iteration": new_iteration,
            "messages": [
                AIMessage(content="Critic agent reviewed the summaries."),
            ],
        }
    except Exception as exc:  # noqa: BLE001
        error_msg = f"Critic agent encountered an error: {exc}"
        new_iteration = int(state.get("iteration", 0)) + 1
        return {
            "critique": f"NEEDS REVISION: {error_msg}",
            "iteration": new_iteration,
            "messages": [
                AIMessage(content=error_msg),
            ],
        }

