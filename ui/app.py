from __future__ import annotations

import textwrap
import time
from datetime import datetime
from typing import Any, Dict, List

import httpx
import streamlit as st


BACKEND_URL = "http://localhost:8000"


def _inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-primary: #0D1117;
            --bg-secondary: #161B22;
            --bg-tertiary: #21262D;
            --accent-blue: #58A6FF;
            --accent-green: #3FB950;
            --accent-amber: #D29922;
            --accent-red: #F85149;
            --text-primary: #E6EDF3;
            --text-secondary: #8B949E;
            --text-accent: #58A6FF;
            --border: #30363D;
            --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
            --font-serif: 'Georgia', 'Times New Roman', serif;
            --font-sans: 'Inter', 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        }

        header[data-testid="stHeader"] { display: none; }
        footer, #MainMenu {visibility: hidden;}
        button[kind="header"] {display: none;}

        body, .stApp {
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
            font-family: var(--font-sans) !important;
        }

        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 1.5rem !important;
            padding-left: 2.5rem !important;
            padding-right: 2.5rem !important;
        }

        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--bg-tertiary);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--accent-blue);
        }

        h1, h2, h3, h4 {
            color: var(--text-accent) !important;
            font-family: var(--font-serif) !important;
        }
        p, span, li, label {
            color: var(--text-primary) !important;
            font-family: var(--font-sans) !important;
        }

        textarea, input, .stTextArea textarea {
            background-color: var(--bg-tertiary) !important;
            color: var(--text-primary) !important;
            border-radius: 6px !important;
            border: 1px solid var(--border) !important;
            font-family: var(--font-mono) !important;
        }
        textarea:focus, input:focus {
            border-color: var(--accent-blue) !important;
            box-shadow: 0 0 0 1px var(--accent-blue) !important;
        }

        .stButton > button {
            background-color: var(--accent-blue) !important;
            color: #02040A !important;
            border-radius: 6px !important;
            border: none !important;
            font-family: var(--font-mono) !important;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.78rem;
            padding: 0.5rem 1.6rem;
        }
        .stButton > button:hover {
            filter: brightness(1.08);
        }

        section[data-testid="stSidebar"] {
            background-color: var(--bg-primary) !important;
            border-right: 1px solid var(--border);
            padding-top: 1.5rem;
        }

        .sidebar-card {
            background-color: var(--bg-secondary);
            border-radius: 8px;
            border: 1px solid var(--border);
            padding: 0.9rem 0.9rem;
            margin-bottom: 0.9rem;
        }

        .sidebar-label {
            font-family: var(--font-mono);
            font-size: 0.68rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: var(--text-secondary);
            margin-bottom: 0.25rem;
        }

        .sidebar-value {
            font-family: var(--font-mono);
            font-size: 0.8rem;
        }

        .agent-box {
            border-radius: 6px;
            border: 1px solid var(--accent-blue);
            padding: 0.35rem 0.6rem;
            margin: 0.1rem 0;
            font-family: var(--font-mono);
            font-size: 0.8rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background-color: var(--bg-secondary);
        }
        .agent-box-critic { border-color: var(--accent-amber); }
        .agent-box-synth { border-color: var(--accent-green); }
        .agent-box-planner { border-color: #BC8CFF; }
        .agent-arrow {
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.7rem;
            margin: 0.1rem 0;
        }

        .query-label {
            font-family: var(--font-mono);
            font-size: 0.72rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: var(--text-secondary);
            margin-bottom: 0.2rem;
        }
        .char-count {
            font-family: var(--font-mono);
            font-size: 0.7rem;
            color: var(--text-secondary);
        }

        .processing-card {
            background-color: var(--bg-secondary);
            border-radius: 8px;
            border: 1px solid var(--border);
            padding: 0.85rem 1rem;
            margin-top: 1.0rem;
            font-family: var(--font-mono);
            font-size: 0.78rem;
        }
        .processing-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.25rem;
        }
        .processing-name { color: var(--text-secondary); }
        .processing-status { color: var(--accent-blue); }
        .processing-status-complete { color: var(--accent-green); }
        .processing-bar {
            height: 2px;
            background-color: var(--bg-tertiary);
            margin-bottom: 0.3rem;
            overflow: hidden;
        }
        .processing-bar-inner {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-green));
            width: 100%;
        }

        .report-card {
            background-color: var(--bg-secondary);
            border-radius: 8px;
            border: 1px solid var(--border);
            padding: 1.5rem 1.6rem;
            position: relative;
        }
        .report-meta {
            font-family: var(--font-mono);
            font-size: 0.72rem;
            color: var(--text-secondary);
            margin-bottom: 0.45rem;
        }
        .report-divider {
            border-bottom: 1px solid var(--border);
            margin: 0.4rem 0 0.8rem 0;
        }
        .copy-button {
            position: absolute;
            top: 0.8rem;
            right: 1.0rem;
            font-size: 0.8rem;
            cursor: pointer;
            color: var(--text-secondary);
        }
        .copy-button:hover { color: var(--accent-blue); }

        .source-card {
            background-color: var(--bg-secondary);
            border-radius: 8px;
            border-left: 3px solid var(--accent-blue);
            border-top: 1px solid var(--border);
            border-right: 1px solid var(--border);
            border-bottom: 1px solid var(--border);
            padding: 0.9rem 1rem;
            margin-bottom: 0.7rem;
        }
        .source-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background-color: var(--accent-blue);
            color: #02040A;
            font-family: var(--font-mono);
            font-size: 0.7rem;
            margin-right: 0.4rem;
        }

        .logs-container {
            background-color: #05070C;
            border-radius: 8px;
            border: 1px solid var(--border);
            padding: 0.7rem 0.9rem;
            max-height: 400px;
            overflow-y: auto;
            font-family: var(--font-mono);
            font-size: 0.78rem;
            color: var(--accent-green);
        }
        .logs-line { white-space: pre; }
        .logs-cursor {
            animation: blink 1s step-start 0s infinite;
        }
        @keyframes blink { 50% { opacity: 0; } }

        .banner-approved {
            background-color: rgba(63, 185, 80, 0.12);
            border: 1px solid var(--accent-green);
            border-radius: 6px;
            padding: 0.6rem 0.8rem;
            font-family: var(--font-mono);
            font-size: 0.78rem;
            color: var(--accent-green);
            margin-bottom: 0.9rem;
        }
        .banner-revision {
            background-color: rgba(210, 153, 34, 0.12);
            border: 1px solid var(--accent-amber);
            border-radius: 6px;
            padding: 0.6rem 0.8rem;
            font-family: var(--font-mono);
            font-size: 0.78rem;
            color: var(--accent-amber);
            margin-bottom: 0.9rem;
        }

        .footer-text {
            font-family: var(--font-mono);
            font-size: 0.72rem;
            color: var(--text-secondary);
            text-align: center;
            margin-top: 1.4rem;
        }
        .github-badge {
            color: var(--accent-blue);
            text-decoration: none;
        }
        .github-badge:hover { text-decoration: underline; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _init_state() -> None:
    if "query" not in st.session_state:
        st.session_state.query = ""
    if "results" not in st.session_state:
        st.session_state.results = None
    if "is_loading" not in st.session_state:
        st.session_state.is_loading = False
    if "agent_statuses" not in st.session_state:
        st.session_state.agent_statuses = {
            "search": "idle",
            "summarizer": "idle",
            "critic": "idle",
            "synthesizer": "idle",
        }
    if "logs" not in st.session_state:
        st.session_state.logs: List[str] = []


def _post_research(query: str) -> Dict[str, Any]:
    payload = {"query": query}
    url = f"{BACKEND_URL}/research"
    with httpx.Client(timeout=600.0) as client:
        resp = client.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()


def _append_log(line: str) -> None:
    st.session_state.logs.append(line)


def _render_header() -> None:
    col_left, col_mid, col_right = st.columns([1.2, 2.4, 1.8])
    with col_left:
        st.markdown(
            '<div class="sidebar-label">RESEARCH SYSTEM v1.0</div>',
            unsafe_allow_html=True,
        )
    with col_mid:
        st.markdown(
            """
            <div style="margin-top:0.1rem;">
              <div style="font-family:var(--font-serif);font-size:2.25rem;color:var(--text-accent);">
                Multi-Agent Research Assistant
              </div>
              <div style="font-family:var(--font-serif);font-style:italic;font-size:0.9rem;color:var(--text-secondary);">
                Powered by LangGraph · LLaMA 3.2 · Local Inference
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_right:
        st.markdown(
            """
            <div style="display:flex;flex-wrap:wrap;justify-content:flex-end;">
              <div class="status-pill">
                <span style="color:var(--accent-green);">●</span><span>LLaMA 3.2</span>
              </div>
              <div class="status-pill">
                <span style="color:var(--accent-blue);">●</span><span>LangGraph</span>
              </div>
              <div class="status-pill">
                <span style="color:var(--accent-amber);">●</span><span>Local</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_sidebar() -> None:
    st.markdown(
        '<div class="sidebar-label">CONFIGURATION</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-card">
          <div class="sidebar-label">MODEL INFO</div>
          <div class="sidebar-value"><span style="color:var(--text-secondary);">Active Model</span><br>
              <span style="color:var(--accent-blue);">llama3.2</span></div>
          <div style="height:0.4rem;"></div>
          <div class="sidebar-value"><span style="color:var(--text-secondary);">Endpoint</span><br>
              <span style="color:var(--text-secondary);">localhost:11434</span></div>
          <div style="height:0.4rem;"></div>
          <div class="sidebar-value"><span style="color:var(--text-secondary);">Search Engine</span><br>
              <span style="color:var(--text-secondary);">DuckDuckGo</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-card">
          <div class="sidebar-label">AGENT PIPELINE</div>
          <div class="agent-box agent-box-planner">
            <span>🧠 Planner</span><span style="color:#BC8CFF;">sub-queries</span>
          </div>
          <div class="agent-arrow">↓</div>
          <div class="agent-box">
            <span>🔍 Search</span>
            <span style="color:var(--text-secondary);">web retrieval</span>
          </div>
          <div class="agent-arrow">│</div>
          <div class="agent-box">
            <span>📝 Summarizer</span>
            <span style="color:var(--text-secondary);">evidence distillation</span>
          </div>
          <div class="agent-arrow">│</div>
          <div class="agent-box agent-box-critic">
            <span>🔎 Critic</span>
            <span style="color:var(--text-secondary);">quality control</span>
          </div>
          <div class="agent-arrow">│  (loop if needed)</div>
          <div class="agent-box agent-box-synth">
            <span>✍️ Synthesizer</span>
            <span style="color:var(--text-secondary);">report writing</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-card">
          <div class="sidebar-label">EXAMPLE QUERIES</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    example_queries = [
        "Impact of LLMs on scientific research",
        "Quantum computing recent breakthroughs",
        "Climate change mitigation strategies 2025",
    ]
    for eq in example_queries:
        if st.button(eq, key=f"eq_{eq[:20]}"):
            st.session_state.prefill_query = eq


def _render_query_section() -> tuple[bool, str]:
    st.markdown(
        '<div class="query-label">RESEARCH QUERY</div>',
        unsafe_allow_html=True,
    )
    default_query = st.session_state.get("prefill_query", "")
    query = st.text_area(
        "",
        key="query",
        placeholder=(
            "Enter your research question... e.g. "
            "What are the latest advances in multimodal AI?"
        ),
        value=default_query,
        height=120,
        label_visibility="collapsed",
    )
    if "prefill_query" in st.session_state:
        del st.session_state["prefill_query"]
    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown(
            f'<div class="char-count">{len(query)} characters</div>',
            unsafe_allow_html=True,
        )
    with col_r:
        trigger = st.button("Research", key="run_button")
    return trigger, query


def _animate_processing(start_time: float) -> None:
    placeholder = st.empty()
    agents = [
        ("PLANNER", "🧠 Planner"),
        ("SEARCH", "🔍 Search"),
        ("SUMMARIZER", "📝 Summarizer"),
        ("CRITIC", "🔎 Critic"),
        ("SYNTHESIZER", "✍️ Synthesizer"),
    ]
    local_status = {a[0]: "pending" for a in agents}

    for code, label in agents:
        elapsed = time.time() - start_time
        _append_log(f"[{elapsed:05.1f}] {code:<11} → processing...")
        local_status[code] = "running"

        with placeholder.container():
            st.markdown(
                f'<div class="processing-card">'
                f'<div style="margin-bottom:0.35rem;color:var(--text-secondary);">'
                f'Agent execution trace · elapsed {elapsed:0.1f}s</div>',
                unsafe_allow_html=True,
            )
            for c, lab in agents:
                st.markdown(
                    '<div class="processing-row">'
                    f'<div class="processing-name">{lab}</div>'
                    f'<div class="processing-status{"-complete" if local_status[c] == "complete" else ""}">'
                    f'{"✓ complete" if local_status[c] == "complete" else "processing..."}</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="processing-bar"><div class="processing-bar-inner"></div></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
        time.sleep(0.4)
        local_status[code] = "complete"
        elapsed = time.time() - start_time
        _append_log(f"[{elapsed:05.1f}] {code:<11} → complete ✓")


def _render_plan_tab(results: Dict[str, Any]) -> None:
    sub_queries = results.get("sub_queries") or []
    reasoning = results.get("plan_reasoning") or ""

    st.markdown(
        '<div style="font-family:var(--font-mono);font-size:0.72rem;'
        'letter-spacing:0.15em;text-transform:uppercase;'
        'color:var(--text-secondary);margin-bottom:0.75rem;">'
        "RESEARCH PLAN</div>",
        unsafe_allow_html=True,
    )

    if reasoning:
        st.markdown(
            f'<div style="background:var(--bg-secondary);border-radius:8px;'
            f'border:1px solid var(--border);padding:0.75rem 1rem;'
            f'font-size:0.85rem;color:var(--text-secondary);margin-bottom:1rem;">'
            f'<span style="color:var(--accent-blue);font-family:var(--font-mono);'
            f'font-size:0.7rem;">PLANNER REASONING</span><br/><br/>{reasoning}</div>',
            unsafe_allow_html=True,
        )

    if not sub_queries:
        st.write("No plan available.")
        return

    colors = ["#58A6FF", "#3FB950", "#D29922"]
    for i, sq in enumerate(sub_queries, start=1):
        color = colors[(i - 1) % len(colors)]
        st.markdown(
            f'<div style="background:var(--bg-secondary);border-radius:8px;'
            f'border-left:3px solid {color};border-top:1px solid var(--border);'
            f'border-right:1px solid var(--border);border-bottom:1px solid var(--border);'
            f'padding:0.75rem 1rem;margin-bottom:0.6rem;">'
            f'<div style="font-family:var(--font-mono);font-size:0.7rem;'
            f'color:{color};margin-bottom:0.3rem;">SUB-QUERY {i}</div>'
            f'<div style="font-size:0.9rem;color:var(--text-primary);">{sq}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )


def _render_report_tab(results: Dict[str, Any]) -> None:
    final_report = results.get("final_report") or "No final report was generated."
    query = results.get("query", "")
    model_name = results.get("model_used", "llama3.2")
    elapsed = results.get("elapsed_seconds", "")
    elapsed_str = f" · {elapsed}s" if elapsed else ""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    truncated_query = (query[:50] + "...") if len(query) > 50 else query

    st.markdown(
        """
        <div class="report-card">
          <div class="copy-button" onclick="
            const txt = document.getElementById('report-body')?.innerText || '';
            navigator.clipboard.writeText(txt);
          ">📋 copy</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="report-meta">Generated · {ts} · {model_name}{elapsed_str}'
        + (f" · {truncated_query}" if truncated_query else "")
        + "</div>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="report-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div id="report-body">', unsafe_allow_html=True)
    st.markdown(final_report, unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)


def _render_sources_tab(results: Dict[str, Any]) -> None:
    search_results = results.get("search_results") or []
    if not search_results:
        st.write("No sources available.")
        return
    for idx, res in enumerate(search_results, start=1):
        st.markdown(
            f"""
            <div class="source-card">
              <div style="display:flex;align-items:center;margin-bottom:0.25rem;">
                <div class="source-badge">{idx}</div>
                <div style="font-family:var(--font-mono);font-size:0.8rem;color:var(--text-secondary);">
                  Source {idx}
                </div>
              </div>
              <div style="font-size:0.85rem;color:var(--text-secondary);white-space:pre-wrap;">
                {textwrap.shorten(res, width=800, placeholder=" …")}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_logs_tab() -> None:
    if not st.session_state.logs:
        st.write("No logs yet.")
        return
    st.markdown('<div class="logs-container">', unsafe_allow_html=True)
    for line in st.session_state.logs:
        st.markdown(f'<div class="logs-line">{line}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="logs-line"><span class="logs-cursor">█</span></div></div>',
        unsafe_allow_html=True,
    )


def _render_critique_tab(results: Dict[str, Any]) -> None:
    critique = (results.get("critique") or "").strip()
    upper = critique.upper()
    if "NEEDS REVISION" in upper:
        st.markdown(
            '<div class="banner-revision">NEEDS REVISION · The critic has requested further refinement of the summaries.</div>',
            unsafe_allow_html=True,
        )
    elif critique:
        st.markdown(
            '<div class="banner-approved">✓ All summaries passed critic review.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="banner-approved">✓ Critic did not raise additional issues.</div>',
            unsafe_allow_html=True,
        )

    if critique:
        st.markdown(
            """
            <div style="background-color:var(--bg-secondary);border-radius:8px;
                        border:1px solid var(--border);padding:0.9rem 1rem;
                        font-size:0.9rem;white-space:pre-wrap;">
            """,
            unsafe_allow_html=True,
        )
        st.markdown(critique, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.write("No detailed critique text available.")


def main() -> None:
    st.set_page_config(page_title="Multi-Agent Research Assistant", layout="wide")
    _inject_css()
    _init_state()

    st.markdown(
        '<div style="border-bottom:1px solid var(--border);padding:1.6rem 0 1.2rem 0;margin-bottom:1.0rem;">',
        unsafe_allow_html=True,
    )
    _render_header()
    st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([1.1, 2.9])
    with left:
        _render_sidebar()
    with right:
        triggered, query = _render_query_section()

        if triggered:
            if not query.strip():
                st.warning("Please enter a research query first.")
            else:
                st.session_state.is_loading = True
                st.session_state.results = None
                st.session_state.logs = []
                start_time = time.time()
                _append_log("[00:00.0] SYSTEM     → Research run started")
                _animate_processing(start_time)
                try:
                    result = _post_research(query.strip())
                    st.session_state.results = result
                    elapsed = time.time() - start_time
                    _append_log(
                        f"[{elapsed:05.1f}] SYSTEM     → Backend response received"
                    )
                except httpx.HTTPStatusError as http_err:
                    detail = None
                    try:
                        detail = http_err.response.json().get("detail")
                    except Exception:
                        detail = http_err.response.text
                    _append_log(
                        "[00:00.0] ERROR      → Backend returned HTTP error"
                    )
                    st.error(f"Backend returned an error: {detail}")
                except Exception as exc:
                    _append_log("[00:00.0] ERROR      → Failed to contact backend")
                    st.error(
                        "Failed to contact the backend API. "
                        "Make sure FastAPI is running on http://localhost:8000.\n\n"
                        f"Error: {exc}"
                    )
                finally:
                    st.session_state.is_loading = False

        results = st.session_state.results
        if results:
            tabs = st.tabs(["REPORT", "PLAN", "SOURCES", "AGENT LOGS", "CRITIQUE"])
            with tabs[0]:
                _render_report_tab(results)
            with tabs[1]:
                _render_plan_tab(results)
            with tabs[2]:
                _render_sources_tab(results)
            with tabs[3]:
                _render_logs_tab()
            with tabs[4]:
                _render_critique_tab(results)

        st.markdown(
            """
            <div class="footer-text">
              Built with LangGraph · LangChain · Ollama · Streamlit · DuckDuckGo<br/>
              <a class="github-badge" href="https://github.com/AdithyaReddyGeeda/Multi-agent-Research-Assistant" target="_blank">
                View on GitHub →
              </a>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()

