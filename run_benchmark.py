"""Master benchmark script — runs all 50 tasks through both agents and records scores."""

import time
from pathlib import Path

from dotenv import load_dotenv

from tasks import TASKS
from agents.agent_a import AgentA
from agents.agent_b import AgentB
from eval.judge import LLMJudge
from eval.metrics import save_score

load_dotenv()

# Clear previous results so each run starts fresh
_CSV = Path("results/scores.csv")
if _CSV.exists():
    _CSV.unlink()


def run_with_retry(fn, *args, retries: int = 1, **kwargs):
    """Call *fn* with *args/kwargs*, retrying once on exception before returning None."""
    for attempt in range(retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            if attempt < retries:
                print(f"  [warn] attempt {attempt + 1} failed ({exc}), retrying...")
                time.sleep(2)
            else:
                print(f"  [error] skipping after {retries + 1} attempts: {exc}")
                return None


def main():
    agent_a = AgentA()
    agent_b = AgentB()
    judge = LLMJudge()

    # Group tasks by session so we know when to call end_session()
    sessions: dict[int, list[dict]] = {}
    for task in TASKS:
        sessions.setdefault(task["session"], []).append(task)

    print("=" * 60)
    print("  MemoryOS Benchmark — 50 tasks, 2 agents, 10 sessions")
    print("=" * 60)

    for session_id in sorted(sessions):
        session_tasks = sessions[session_id]
        print(f"\n--- Session {session_id} ---")

        for task in session_tasks:
            tid = task["task_id"]

            # ── Agent A (no memory) ──────────────────────────────────────────
            response_a = run_with_retry(agent_a.respond, task["message"])
            if response_a is None:
                score_a = 1
            else:
                score_a = run_with_retry(judge.score, task, response_a) or 1
            save_score(tid, session_id, "AgentA", score_a)

            # ── Agent B (MemoryOS) ───────────────────────────────────────────
            response_b = run_with_retry(
                agent_b.respond, task["message"], session_id=session_id, task_id=tid
            )
            if response_b is None:
                score_b = 1
            else:
                score_b = run_with_retry(judge.score, task, response_b) or 1
            save_score(tid, session_id, "AgentB", score_b)

            print(f"  Task {tid:02d} | AgentA: {score_a} | AgentB: {score_b}")

        # Flush AgentB's memory at end of each session
        agent_b.end_session()

    print("\n" + "=" * 60)
    print("  Benchmark complete. Run  python plot_results.py  to see the graph.")
    print("=" * 60)


if __name__ == "__main__":
    main()
