"""MemoryOS Benchmark — minimal centred Streamlit dashboard."""

import time
import threading
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MemoryOS Benchmark",
    page_icon="◎",
    layout="centered",          # everything centred, no wide sprawl
    initial_sidebar_state="collapsed",
)

# ── Palette ───────────────────────────────────────────────────────────────────
# Soft cream background · violet accent · amber highlight
BG       = "#F7F5F2"
CARD     = "#FFFFFF"
VIOLET   = "#7C3AED"
AMBER    = "#F59E0B"
MUTED    = "#9CA3AF"
TEXT     = "#1C1917"
BORDER   = "#E7E5E4"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* page background */
  [data-testid="stAppViewContainer"] {{
      background: {BG};
  }}
  [data-testid="stHeader"] {{ background: transparent; }}

  /* hide the default hamburger / deploy toolbar */
  [data-testid="stToolbar"] {{ display: none; }}

  /* centred wrapper — Streamlit's layout="centered" already does max-width,
     but we tighten spacing */
  .block-container {{
      padding-top: 3rem;
      padding-bottom: 4rem;
  }}

  /* typography */
  html, body, [class*="css"] {{
      font-family: "Inter", "Segoe UI", sans-serif;
      color: {TEXT};
  }}

  /* tab strip */
  [data-testid="stTabs"] [data-baseweb="tab-list"] {{
      gap: 0.25rem;
      background: {BORDER};
      border-radius: 12px;
      padding: 4px;
  }}
  [data-testid="stTabs"] [data-baseweb="tab"] {{
      border-radius: 9px;
      padding: 6px 20px;
      font-size: 0.85rem;
      font-weight: 500;
      color: {MUTED};
      background: transparent;
  }}
  [data-testid="stTabs"] [aria-selected="true"] {{
      background: {CARD} !important;
      color: {VIOLET} !important;
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  }}

  /* metric cards */
  [data-testid="metric-container"] {{
      background: {CARD};
      border: 1px solid {BORDER};
      border-radius: 14px;
      padding: 1rem 1.2rem;
  }}
  [data-testid="stMetricLabel"] {{ color: {MUTED}; font-size: 0.78rem; }}
  [data-testid="stMetricValue"] {{ color: {TEXT}; font-size: 1.6rem; font-weight: 700; }}
  [data-testid="stMetricDelta"] svg {{ display:none; }}

  /* progress bar */
  [data-testid="stProgressBar"] > div > div {{
      background: linear-gradient(90deg, {VIOLET}, {AMBER});
      border-radius: 99px;
  }}
  [data-testid="stProgressBar"] > div {{
      background: {BORDER};
      border-radius: 99px;
  }}

  /* primary button */
  div.stButton > button[kind="primary"] {{
      background: {VIOLET};
      color: white;
      border: none;
      border-radius: 10px;
      padding: 0.55rem 2rem;
      font-weight: 600;
      letter-spacing: 0.01em;
      transition: opacity 0.15s;
  }}
  div.stButton > button[kind="primary"]:hover {{ opacity: 0.85; }}
  div.stButton > button[kind="primary"]:disabled {{
      background: {BORDER};
      color: {MUTED};
  }}

  /* secondary/download button */
  div.stDownloadButton > button {{
      background: transparent;
      border: 1.5px solid {VIOLET};
      color: {VIOLET};
      border-radius: 10px;
      font-weight: 500;
  }}

  /* expander */
  [data-testid="stExpander"] {{
      border: 1px solid {BORDER};
      border-radius: 12px;
      background: {CARD};
  }}

  /* dataframe */
  [data-testid="stDataFrame"] {{
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid {BORDER};
  }}

  /* info / success / warning boxes */
  [data-testid="stAlert"] {{
      border-radius: 12px;
      font-size: 0.88rem;
  }}

  /* thin horizontal rule */
  hr {{ border-color: {BORDER}; margin: 1.8rem 0; }}

  /* log lines */
  .log-line {{
      font-size: 0.82rem;
      color: {MUTED};
      padding: 3px 0;
      border-bottom: 1px solid {BORDER};
  }}
  .log-line b {{ color: {TEXT}; }}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
_CSV             = Path("results/scores.csv")
_TASKS_PER_SES   = 5
_TOTAL_TASKS     = 50
_ROLLING_WIN     = 5

# ── Shared thread state ───────────────────────────────────────────────────────
# Stored in st.session_state so it survives Streamlit reruns (the script
# re-executes top-to-bottom on every interaction — a plain module-level dict
# would reset to defaults each time).  The thread holds a direct reference to
# this dict object and mutates it; Streamlit reads it on the next rerun.
if "_state" not in st.session_state:
    st.session_state["_state"] = {
        "running":   False,
        "done":      False,
        "progress":  0.0,
        "log":       [],
        "crash_msg": "",
        "crash_tb":  "",
    }
_STATE = st.session_state["_state"]   # convenient shorthand

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_scores() -> Optional[pd.DataFrame]:
    """Return scores DataFrame or None if not yet generated."""
    if _CSV.exists() and _CSV.stat().st_size > 0:
        return pd.read_csv(_CSV)
    return None


def rolling_avg(arr: np.ndarray, window: int) -> np.ndarray:
    """Trailing rolling mean."""
    out = np.full_like(arr, np.nan, dtype=float)
    for i in range(len(arr)):
        out[i] = arr[max(0, i - window + 1): i + 1].mean()
    return out


def make_line_chart(df: pd.DataFrame) -> plt.Figure:
    """Violet/amber minimal line chart on cream background."""
    a = df[df["agent"] == "AgentA"].sort_values("task_id")
    b = df[df["agent"] == "AgentB"].sort_values("task_id")

    xa, xb = a["task_id"].values, b["task_id"].values
    sa = rolling_avg(a["score"].astype(float).values, _ROLLING_WIN)
    sb = rolling_avg(b["score"].astype(float).values, _ROLLING_WIN)

    fig, ax = plt.subplots(figsize=(11, 4))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # raw dots — very faint
    ax.scatter(xa, a["score"].values, color=AMBER,   alpha=0.18, s=14, zorder=2)
    ax.scatter(xb, b["score"].values, color=VIOLET,  alpha=0.18, s=14, zorder=2)

    # smoothed lines
    ax.plot(xa, sa, color=AMBER,  linestyle="--", linewidth=2,   label="Agent A — No Memory", zorder=3)
    ax.plot(xb, sb, color=VIOLET, linestyle="-",  linewidth=2.5, label="Agent B — MemoryOS",  zorder=3)

    # session dividers
    for s in range(2, _TOTAL_TASKS // _TASKS_PER_SES + 1):
        bx = (s - 1) * _TASKS_PER_SES + 0.5
        ax.axvline(x=bx, color=BORDER, linestyle="-", linewidth=1, zorder=1)
        ax.text(bx + 0.25, 5.15, f"S{s}", fontsize=6.5, color=MUTED, va="top")

    ax.set_xlim(0.5, _TOTAL_TASKS + 0.5)
    ax.set_ylim(0.5, 5.5)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.set_xlabel("Task", color=MUTED, fontsize=10)
    ax.set_ylabel("Score (1–5)", color=MUTED, fontsize=10)
    ax.tick_params(colors=MUTED, labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    ax.grid(axis="y", color=BORDER, linewidth=0.8, zorder=0)
    ax.legend(fontsize=9, frameon=True, facecolor=CARD,
              edgecolor=BORDER, labelcolor=TEXT)
    fig.tight_layout(pad=1.5)
    return fig


def make_bar_chart(df: pd.DataFrame) -> plt.Figure:
    """Per-session grouped bar chart."""
    a_df = df[df["agent"] == "AgentA"]
    b_df = df[df["agent"] == "AgentB"]
    sa = a_df.groupby("session_id")["score"].mean()
    sb = b_df.groupby("session_id")["score"].mean()
    sessions = sorted(sa.index)

    fig, ax = plt.subplots(figsize=(11, 3.2))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    w = 0.38
    xs = np.array(sessions)
    ax.bar(xs - w / 2, sa.values, w, color=AMBER,  alpha=0.85, label="Agent A", zorder=3)
    ax.bar(xs + w / 2, sb.values, w, color=VIOLET, alpha=0.85, label="Agent B", zorder=3)

    ax.set_xticks(xs)
    ax.set_xticklabels([f"S{i}" for i in sessions], color=MUTED, fontsize=9)
    ax.set_ylim(0, 5.8)
    ax.set_ylabel("Avg score", color=MUTED, fontsize=10)
    ax.tick_params(colors=MUTED, labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    ax.grid(axis="y", color=BORDER, linewidth=0.8, zorder=0)
    ax.legend(fontsize=9, frameon=True, facecolor=CARD,
              edgecolor=BORDER, labelcolor=TEXT)
    fig.tight_layout(pad=1.5)
    return fig


def run_benchmark_thread():
    """Benchmark runner — writes only to module-level _STATE dict, never st.session_state."""
    try:
        import os
        from dotenv import load_dotenv
        from tasks import TASKS
        from agents.agent_a import AgentA
        from agents.agent_b import AgentB
        from eval.judge import LLMJudge
        from eval.metrics import save_score

        load_dotenv()

        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError(
                "OPENAI_API_KEY not found. "
                "Add a .env file with: OPENAI_API_KEY=sk-..."
            )

        if _CSV.exists():
            _CSV.unlink()

        _STATE["log"]      = []
        _STATE["progress"] = 0.0
        _STATE["running"]  = True
        _STATE["done"]     = False

        agent_a, agent_b, judge = AgentA(), AgentB(), LLMJudge()

        sessions = {}
        for t in TASKS:
            sessions.setdefault(t["session"], []).append(t)

        def retry(fn, *args, **kwargs):
            for attempt in range(2):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt == 0:
                        time.sleep(2)
            return None

        done = 0
        for sid in sorted(sessions):
            for task in sessions[sid]:
                tid = task["task_id"]

                ra = retry(agent_a.respond, task["message"])
                sa = retry(judge.score, task, ra or "") or 1
                save_score(tid, sid, "AgentA", sa)

                rb = retry(agent_b.respond, task["message"], session_id=sid, task_id=tid)
                sb = retry(judge.score, task, rb or "") or 1
                save_score(tid, sid, "AgentB", sb)

                done += 1
                _STATE["progress"] = done / len(TASKS)
                _STATE["log"].append((tid, sid, sa, sb))

            agent_b.end_session()

        _STATE["running"] = False
        _STATE["done"]    = True

    except Exception as exc:
        import traceback
        _STATE["running"]   = False
        _STATE["done"]      = False
        _STATE["crash_msg"] = f"{type(exc).__name__}: {exc}"
        _STATE["crash_tb"]  = traceback.format_exc()


# ── Session state init ────────────────────────────────────────────────────────
# No session_state needed — all live state lives in _STATE dict above

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center; padding: 1rem 0 0.25rem;">
  <span style="font-size:2.6rem; letter-spacing:-1px; font-weight:800; color:{TEXT};">
    ◎ MemoryOS
  </span><br>
  <span style="font-size:1rem; color:{MUTED}; font-weight:400; letter-spacing:0.02em;">
    Does memory make AI agents smarter?
  </span>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Pill badges ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex; gap:10px; justify-content:center; margin-bottom:1.6rem;">
  <span style="background:{VIOLET}18; color:{VIOLET}; border-radius:99px;
               padding:4px 14px; font-size:0.78rem; font-weight:600;">
    50 tasks
  </span>
  <span style="background:{AMBER}22; color:#B45309; border-radius:99px;
               padding:4px 14px; font-size:0.78rem; font-weight:600;">
    10 sessions
  </span>
  <span style="background:#10B98118; color:#059669; border-radius:99px;
               padding:4px 14px; font-size:0.78rem; font-weight:600;">
    2 agents
  </span>
  <span style="background:#6B728018; color:#374151; border-radius:99px;
               padding:4px 14px; font-size:0.78rem; font-weight:600;">
    gpt-4o-mini
  </span>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_run, tab_results, tab_tasks = st.tabs(["Run", "Results", "Tasks"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — RUN
# ─────────────────────────────────────────────────────────────────────────────
with tab_run:
    st.markdown("<br>", unsafe_allow_html=True)

    # ── crash banner ─────────────────────────────────────────────────────────
    if _STATE["crash_msg"]:
        st.error(f"**Benchmark crashed:** {_STATE['crash_msg']}")
        with st.expander("Full traceback"):
            st.code(_STATE["crash_tb"], language="python")
        if st.button("Reset", type="primary"):
            _STATE.update(running=False, done=False, progress=0.0,
                          log=[], crash_msg="", crash_tb="")
            st.rerun()
        st.stop()

    # ── start / reset buttons ─────────────────────────────────────────────────
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if _STATE["running"] or _STATE["done"]:
            if st.button("↺ Reset & run again", use_container_width=True):
                _STATE.update(running=False, done=False, progress=0.0,
                              log=[], crash_msg="", crash_tb="")
                st.rerun()
        else:
            start = st.button(
                "Start benchmark",
                use_container_width=True,
                type="primary",
            )
            if start:
                _STATE.update(running=True, done=False, progress=0.0,
                              log=[], crash_msg="", crash_tb="")
                threading.Thread(target=run_benchmark_thread, daemon=True).start()
                st.rerun()

    st.markdown(f"""
    <p style="text-align:center; color:{MUTED}; font-size:0.82rem; margin-top:0.5rem;">
      ~210 API calls · gpt-4o-mini · est. $0.10–0.20 · 10–15 min
    </p>
    """, unsafe_allow_html=True)

    if _STATE["running"] or _STATE["done"]:
        st.markdown("<br>", unsafe_allow_html=True)
        pv = _STATE["progress"]
        pct = int(pv * 100)
        st.progress(pv, text=f"{pct}%  ·  {int(pv * 50)} / 50 tasks")

        if _STATE["done"]:
            st.success("All done — open the **Results** tab.")

        log = _STATE["log"]
        if log:
            st.markdown("<br>", unsafe_allow_html=True)
            lines_html = ""
            for tid, sid, sa, sb in reversed(log[-20:]):
                win = (
                    f"<span style='color:{VIOLET};font-weight:600'>B wins</span>"
                    if sb > sa else
                    f"<span style='color:{AMBER};font-weight:600'>A wins</span>"
                    if sa > sb else
                    f"<span style='color:{MUTED}'>Tie</span>"
                )
                lines_html += (
                    f"<div class='log-line'>"
                    f"Task <b>{tid:02d}</b> · S{sid} · "
                    f"A&nbsp;<b>{sa}</b> · B&nbsp;<b>{sb}</b> · {win}"
                    f"</div>"
                )
            st.markdown(
                f"<div style='border:1px solid {BORDER}; border-radius:12px;"
                f"padding:0.8rem 1rem; background:{CARD};'>{lines_html}</div>",
                unsafe_allow_html=True,
            )

        if _STATE["running"]:
            time.sleep(2)
            st.rerun()

    # legend
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:flex; gap:2rem; justify-content:center;">
      <div style="text-align:center;">
        <div style="width:36px; height:4px; background:{AMBER};
                    border-radius:99px; margin:0 auto 6px;"></div>
        <span style="font-size:0.78rem; color:{MUTED};">Agent A · no memory</span>
      </div>
      <div style="text-align:center;">
        <div style="width:36px; height:4px; background:{VIOLET};
                    border-radius:99px; margin:0 auto 6px;"></div>
        <span style="font-size:0.78rem; color:{MUTED};">Agent B · MemoryOS</span>
      </div>
    </div>
    <br>
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:1rem; margin-top:0.5rem;">
      <div style="background:{CARD}; border:1px solid {BORDER}; border-radius:12px;
                  padding:1rem; text-align:center;">
        <div style="font-size:1.4rem; margin-bottom:4px;">💾</div>
        <div style="font-size:0.78rem; font-weight:600; color:{TEXT};">Working</div>
        <div style="font-size:0.72rem; color:{MUTED}; margin-top:2px;">Python list · clears each session</div>
      </div>
      <div style="background:{CARD}; border:1px solid {BORDER}; border-radius:12px;
                  padding:1rem; text-align:center;">
        <div style="font-size:1.4rem; margin-bottom:4px;">🗄️</div>
        <div style="font-size:0.78rem; font-weight:600; color:{TEXT};">Episodic</div>
        <div style="font-size:0.72rem; color:{MUTED}; margin-top:2px;">ChromaDB · semantic search</div>
      </div>
      <div style="background:{CARD}; border:1px solid {BORDER}; border-radius:12px;
                  padding:1rem; text-align:center;">
        <div style="font-size:1.4rem; margin-bottom:4px;">🧬</div>
        <div style="font-size:0.78rem; font-weight:600; color:{TEXT};">Semantic</div>
        <div style="font-size:0.72rem; color:{MUTED}; margin-top:2px;">JSON profile · LLM-compressed</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — RESULTS
# ─────────────────────────────────────────────────────────────────────────────
with tab_results:
    df = load_scores()

    if df is None:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align:center; padding:3rem; background:{CARD};
                    border:1px solid {BORDER}; border-radius:16px;">
          <div style="font-size:2rem;">◌</div>
          <div style="color:{MUTED}; margin-top:0.5rem; font-size:0.9rem;">
            No results yet — run the benchmark first.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        a_df = df[df["agent"] == "AgentA"]
        b_df = df[df["agent"] == "AgentB"]
        avg_a = a_df["score"].mean()
        avg_b = b_df["score"].mean()
        improvement = ((avg_b - avg_a) / avg_a) * 100
        b_wins = int((df.pivot_table(index="task_id", columns="agent", values="score")
                      .assign(win=lambda d: d["AgentB"] > d["AgentA"])["win"].sum()))

        st.markdown("<br>", unsafe_allow_html=True)

        # KPI row
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("No-memory avg", f"{avg_a:.2f}")
        k2.metric("MemoryOS avg",  f"{avg_b:.2f}", delta=f"+{avg_b - avg_a:.2f}")
        k3.metric("Improvement",   f"+{improvement:.1f}%")
        k4.metric("B wins",        f"{b_wins} / 50")

        st.markdown("<hr>", unsafe_allow_html=True)

        # Line chart
        st.markdown(
            f"<p style='font-size:0.78rem; color:{MUTED}; "
            f"text-transform:uppercase; letter-spacing:0.08em;'>"
            f"Score over time</p>",
            unsafe_allow_html=True,
        )
        st.pyplot(make_line_chart(df), use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Bar chart
        st.markdown(
            f"<p style='font-size:0.78rem; color:{MUTED}; "
            f"text-transform:uppercase; letter-spacing:0.08em;'>"
            f"Per-session average</p>",
            unsafe_allow_html=True,
        )
        st.pyplot(make_bar_chart(df), use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Table
        st.markdown(
            f"<p style='font-size:0.78rem; color:{MUTED}; "
            f"text-transform:uppercase; letter-spacing:0.08em;'>"
            f"Raw scores</p>",
            unsafe_allow_html=True,
        )
        pivot = df.pivot_table(
            index=["session_id", "task_id"], columns="agent", values="score"
        ).reset_index()
        pivot.columns.name = None
        pivot["Winner"] = pivot.apply(
            lambda r: "◉ MemoryOS"  if r.get("AgentB", 0) > r.get("AgentA", 0) else
                      "○ Baseline"  if r.get("AgentA", 0) > r.get("AgentB", 0) else
                      "— Tie",
            axis=1,
        )
        st.dataframe(pivot, use_container_width=True, height=380)

        st.markdown("<br>", unsafe_allow_html=True)
        _, dl_col, _ = st.columns([1, 2, 1])
        with dl_col:
            st.download_button(
                "Download scores.csv",
                data=df.to_csv(index=False).encode(),
                file_name="scores.csv",
                mime="text/csv",
                use_container_width=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — TASKS
# ─────────────────────────────────────────────────────────────────────────────
with tab_tasks:
    from tasks import TASKS

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        sel_session = st.selectbox("Session", ["All"] + list(range(1, 11)))
    with c2:
        search = st.text_input("Search", placeholder="Rust, dbt, Akshita…")

    filtered = TASKS
    if sel_session != "All":
        filtered = [t for t in filtered if t["session"] == sel_session]
    if search:
        filtered = [t for t in filtered if search.lower() in t["message"].lower()]

    st.markdown(
        f"<p style='font-size:0.78rem; color:{MUTED};"
        f"margin-bottom:0.8rem;'>{len(filtered)} task(s)</p>",
        unsafe_allow_html=True,
    )

    df_sc = load_scores()

    for task in filtered:
        tid = task["task_id"]
        label = f"**{tid:02d}** · S{task['session']} · {task['message'][:65]}…"
        with st.expander(label):
            st.markdown(
                f"<p style='color:{TEXT}; font-size:0.9rem;'>{task['message']}</p>",
                unsafe_allow_html=True,
            )
            kw_html = " ".join(
                f"<span style='background:{VIOLET}12; color:{VIOLET}; border-radius:6px;"
                f"padding:2px 8px; font-size:0.75rem; font-weight:500;'>{k}</span>"
                for k in task["expected_keywords"]
            )
            st.markdown(kw_html, unsafe_allow_html=True)

            if df_sc is not None:
                ra = df_sc[(df_sc["task_id"] == tid) & (df_sc["agent"] == "AgentA")]
                rb = df_sc[(df_sc["task_id"] == tid) & (df_sc["agent"] == "AgentB")]
                if not ra.empty and not rb.empty:
                    sa, sb = int(ra["score"].iloc[0]), int(rb["score"].iloc[0])
                    st.markdown("<br>", unsafe_allow_html=True)
                    sc1, sc2 = st.columns(2)
                    sc1.metric("Agent A", f"{sa} / 5")
                    sc2.metric("Agent B", f"{sb} / 5", delta=sb - sa)
