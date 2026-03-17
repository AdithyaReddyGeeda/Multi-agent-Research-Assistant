from __future__ import annotations

import json
import logging
from typing import Any, Dict

from agents.llm import get_llm
from graph.state import ResearchState


logger = logging.getLogger(__name__)


PLANNER_SYSTEM_PROMPT = """You are a research planning specialist.
Your job is to decompose a complex research query into exactly 3
focused, non-overlapping sub-queries that together cover the topic
comprehensively.

Rules:
- Sub-query 1: Background and definitions (what is it, history)
- Sub-query 2: Current state and recent developments (latest news, data)
- Sub-query 3: Future outlook, challenges, and implications

Respond ONLY with valid JSON in this exact format, no other text:
{
  "sub_queries": ["sub-query 1", "sub-query 2", "sub-query 3"],
  "reasoning": "brief explanation of why you split it this way"
}"""


def planner_node(state: ResearchState) -> Dict[str, Any]:
    """
    Decomposes the main query into 3 focused sub-queries.
    Returns sub_queries list and plan_reasoning string.
    """
    query = state.get("query", "")
    logger.info("Planner agent: decomposing query: %s", query)

    llm = get_llm()
    messages: list[Dict[str, str]] = [
        {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
        {"role": "user", "content": f"Research query: {query}"},
    ]

    try:
        response = llm.invoke(messages)
        content = response.content.strip() if hasattr(response, "content") else str(response).strip()

        # Strip markdown code fences if present
        if content.startswith("```"):
            parts = content.split("```")
            if len(parts) >= 2:
                content = parts[1]
            if content.lstrip().startswith("json"):
                content = content.lstrip()[4:]
        content = content.strip()

        parsed = json.loads(content)
        sub_queries = parsed.get("sub_queries", [])
        reasoning = parsed.get("reasoning", "")

        # Validate: ensure exactly 3 sub-queries
        if len(sub_queries) != 3:
            raise ValueError(f"Expected 3 sub-queries, got {len(sub_queries)}")

        logger.info("Planner produced sub-queries: %s", sub_queries)
        return {
            "sub_queries": sub_queries,
            "plan_reasoning": reasoning,
        }

    except (json.JSONDecodeError, ValueError, KeyError) as exc:
        logger.warning("Planner JSON parse failed (%s), using fallback.", exc)
        # Fallback: create 3 simple sub-queries from original query
        fallback = [
            f"{query} background and overview",
            f"{query} latest developments 2025",
            f"{query} challenges and future implications",
        ]
        return {
            "sub_queries": fallback,
            "plan_reasoning": "Fallback: planner output could not be parsed.",
        }

