from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import END, StateGraph

from graph.state import ResearchState
from agents.planner_agent import planner_node
from agents.search_agent import search_node
from agents.summarizer_agent import summarizer_agent
from agents.critic_agent import critic_agent
from agents.synthesizer_agent import synthesizer_agent


def _route_from_critic(state: ResearchState) -> str:
    """
    Decide whether to loop back for another summarization pass or proceed
    directly to synthesis based on the critic's feedback and iteration count.
    """
    critique = (state.get("critique") or "").upper()
    iteration = int(state.get("iteration", 0))

    if "NEEDS REVISION" in critique and iteration < 2:
        return "summarize"
    return "synthesize"


def build_graph():
    """
    Construct and compile the LangGraph StateGraph for the research workflow.
    """
    builder = StateGraph(ResearchState)

    # Nodes
    builder.add_node("planner", planner_node)
    builder.add_node("search", search_node)
    builder.add_node("summarize", summarizer_agent)
    builder.add_node("critic", critic_agent)
    builder.add_node("synthesize", synthesizer_agent)

    # Edges: START -> planner -> search -> summarize -> critic
    builder.set_entry_point("planner")
    builder.add_edge("planner", "search")
    builder.add_edge("search", "summarize")
    builder.add_edge("summarize", "critic")

    # Conditional edge based on critic feedback and iteration count.
    builder.add_conditional_edges(
        "critic",
        _route_from_critic,
        {
            "summarize": "summarize",
            "synthesize": "synthesize",
        },
    )

    # Synthesis leads to END.
    builder.add_edge("synthesize", END)

    return builder.compile()


_GRAPH = build_graph()


def run_research(query: str) -> Dict[str, Any]:
    """
    Convenience helper to execute the full research workflow for a query.

    Returns the final ResearchState as a plain dictionary, suitable for JSON
    serialization in the FastAPI layer.
    """
    initial_state: ResearchState = {
        "query": query,
        "search_results": [],
        "summaries": [],
        "critique": "",
        "final_report": "",
        "iteration": 0,
        "elapsed_seconds": 0.0,
        "timestamp": "",
        "model_used": "",
        "revision_count": 0,
        "sub_queries": [],
        "plan_reasoning": "",
        "search_results_per_query": [],
        "messages": [],
    }

    result = _GRAPH.invoke(initial_state)
    # Cast to plain dict for easier JSON handling.
    return dict(result)

