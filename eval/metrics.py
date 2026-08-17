"""Score persistence and retrieval utilities."""

import csv
import os
from pathlib import Path

import pandas as pd

_CSV_PATH = Path(os.path.expanduser("~")) / "scores.csv"
_HEADERS = ["task_id", "session_id", "agent", "score"]


def save_score(task_id: int, session_id: int, agent_name: str, score: int) -> None:
    """Append one scored result row to the CSV file."""
    write_header = not _CSV_PATH.exists()
    with _CSV_PATH.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_HEADERS)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "task_id": task_id,
            "session_id": session_id,
            "agent": agent_name,
            "score": score,
        })


def load_scores() -> pd.DataFrame:
    """Load the scores CSV into a pandas DataFrame."""
    if not _CSV_PATH.exists():
        raise FileNotFoundError(f"{_CSV_PATH} not found — run run_benchmark.py first.")
    return pd.read_csv(_CSV_PATH)
