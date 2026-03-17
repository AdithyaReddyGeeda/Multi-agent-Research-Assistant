from __future__ import annotations

import json
from typing import Any, Dict

import httpx
import streamlit as st


BACKEND_URL = "http://localhost:8000"


def _post_research(query: str) -> Dict[str, Any]:
    payload = {"query": query}
    url = f"{BACKEND_URL}/research"
    # Allow plenty of time for the first model load / research run.
    with httpx.Client(timeout=180.0) as client:
        resp = client.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    st.set_page_config(page_title="Multi-Agent Research Assistant", layout="wide")

    st.title("Multi-Agent Research Assistant")

    with st.sidebar:
        st.markdown("**Model:** llama3.2 (Local)")
        st.markdown("---")
        st.markdown("**Agent Pipeline**")
        st.text(
            "Query → Search Agent\n"
            "      → Summarizer Agent\n"
            "      → Critic Agent\n"
            "      ↳ (loop if NEEDS REVISION)\n"
            "      → Synthesizer Agent\n"
            "      → Final Report"
        )

    st.markdown("Enter a complex research question and let the agents collaborate.")

    query = st.text_area(
        "Research query",
        placeholder="e.g. What are the latest advances in retrieval-augmented generation for small language models?",
        height=150,
    )

    if st.button("Research", type="primary"):
        if not query.strip():
            st.error("Please enter a research query first.")
            return

        with st.spinner("Agents are collaborating..."):
            try:
                result = _post_research(query.strip())
            except httpx.HTTPStatusError as http_err:
                try:
                    detail = http_err.response.json().get("detail")
                except Exception:  # noqa: BLE001
                    detail = http_err.response.text
                st.error(f"Backend returned an error: {detail}")
                return
            except Exception as exc:  # noqa: BLE001
                st.error(
                    "Failed to contact the backend API. "
                    "Make sure FastAPI is running on http://localhost:8000.\n\n"
                    f"Error: {exc}"
                )
                return

        final_report = result.get("final_report") or "No final report was generated."
        search_results = result.get("search_results") or []
        summaries = result.get("summaries") or []
        critique = result.get("critique") or ""

        st.subheader("Final Report")
        st.markdown(final_report, unsafe_allow_html=False)

        with st.expander("Search Results"):
            if search_results:
                for idx, res in enumerate(search_results, start=1):
                    st.markdown(f"### Result {idx}")
                    st.markdown(res)
            else:
                st.write("No search results available.")

        with st.expander("Agent Summaries"):
            if summaries:
                for idx, summary in enumerate(summaries, start=1):
                    st.markdown(f"### Summary {idx}")
                    st.markdown(summary)
            else:
                st.write("No summaries available.")

        with st.expander("Critic Feedback"):
            st.markdown(critique or "No critic feedback available.")


if __name__ == "__main__":
    main()

