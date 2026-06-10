"""Read results/scores.csv and produce a comparison graph saved to results/benchmark_graph.png."""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from eval.metrics import load_scores

_TASKS_PER_SESSION = 5
_TOTAL_TASKS = 50
_ROLLING_WINDOW = 5
_OUTPUT_PATH = "results/benchmark_graph.png"


def main():
    df = load_scores()

    agent_a = df[df["agent"] == "AgentA"].sort_values("task_id")
    agent_b = df[df["agent"] == "AgentB"].sort_values("task_id")

    x = agent_a["task_id"].values
    scores_a = agent_a["score"].astype(float).values
    scores_b = agent_b["score"].astype(float).values

    # Rolling average (pad edges with NaN so the window lines up correctly)
    def rolling_avg(arr, window):
        result = np.full_like(arr, np.nan, dtype=float)
        for i in range(len(arr)):
            start = max(0, i - window + 1)
            result[i] = arr[start : i + 1].mean()
        return result

    smooth_a = rolling_avg(scores_a, _ROLLING_WINDOW)
    smooth_b = rolling_avg(scores_b, _ROLLING_WINDOW)

    # ── Plot ─────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(14, 6))

    # Raw scores as faint dots
    ax.scatter(x, scores_a, color="red", alpha=0.2, s=18, zorder=2)
    ax.scatter(x, scores_b, color="green", alpha=0.2, s=18, zorder=2)

    # Smoothed lines
    ax.plot(x, smooth_a, color="red", linestyle="--", linewidth=2.0,
            label="Agent A — No Memory", zorder=3)
    ax.plot(x, smooth_b, color="green", linestyle="-", linewidth=2.5,
            label="Agent B — MemoryOS", zorder=3)

    # Session boundary lines
    for session_num in range(2, _TOTAL_TASKS // _TASKS_PER_SESSION + 1):
        boundary_x = (session_num - 1) * _TASKS_PER_SESSION + 0.5
        ax.axvline(x=boundary_x, color="grey", linestyle=":", linewidth=0.9, alpha=0.7)
        ax.text(boundary_x + 0.2, 4.85, f"S{session_num}",
                fontsize=7, color="grey", va="top")

    # Formatting
    ax.set_xlim(0.5, _TOTAL_TASKS + 0.5)
    ax.set_ylim(0.5, 5.5)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.set_xlabel("Task ID", fontsize=12)
    ax.set_ylabel("Score (1 – 5)", fontsize=12)
    ax.set_title(
        "MemoryOS Benchmark — Does Memory Make Agents Smarter?",
        fontsize=14, fontweight="bold", pad=14,
    )
    ax.legend(fontsize=11, loc="lower right")
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(_OUTPUT_PATH, dpi=150)
    print(f"Graph saved to {_OUTPUT_PATH}")
    plt.show()


if __name__ == "__main__":
    main()
