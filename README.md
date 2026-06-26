---
title: MemoryOS Benchmark
emoji: 🧠
colorFrom: green
colorTo: red
sdk: docker
app_port: 7860
tags:
- streamlit
pinned: false
short_description: AI agents with vs without memory, benchmarked
---

# MemoryOS Benchmark

A controlled benchmark that proves an AI agent equipped with a three-layer memory system
consistently outperforms a stateless baseline across 50 scripted tasks spanning 10 sessions.
The benchmark follows a fictional user named **Akshita** — a fintech data analyst — whose
facts, preferences, and history are introduced in early sessions and must be recalled and
combined in later ones.

---

## Install

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
# then edit .env and set OPENAI_API_KEY=sk-...
```

---

## Run

```bash
# Step 1 — run the benchmark (takes ~10–15 minutes, ~210 API calls)
python run_benchmark.py

# Step 2 — visualise the results
python plot_results.py
```

Results are saved to `results/scores.csv` and the graph to `results/benchmark_graph.png`.

---

## What the graph shows

The graph plots the score (1–5) of each agent across all 50 tasks:

- **Agent A (red dashed)** — no memory. Scores well on stand-alone questions in sessions 1–3
  but flatlines on recall and synthesis tasks in sessions 4–10 because it has no context.
- **Agent B (green solid)** — MemoryOS. Starts at a similar baseline but its score rises
  steadily as its memory fills with facts about Akshita, diverging clearly from Agent A
  by session 4 and reaching near-perfect scores on complex synthesis tasks in sessions 7–10.

The divergence between the two lines is the empirical payoff of giving an agent memory.

---

## Memory Architecture

MemoryOS uses three complementary layers, each serving a different time horizon:

| Layer | Storage | Cleared? | Purpose |
|---|---|---|---|
| **Working memory** | Python list | Every session | Current conversation turns — like RAM |
| **Episodic memory** | ChromaDB (local) | Never | Verbatim past messages retrieved by semantic search — like a diary |
| **Semantic memory** | JSON file | Never | LLM-compressed user profile (name, job, tools, preferences) — like a Wikipedia article about the user |

The **MemoryRouter** combines all three layers before every LLM call using a simple rule:
always include the semantic profile, add the top-3 episodic matches for the current query,
and append the last 3 turns of the current session.  No LLM call is made inside the router —
it is purely deterministic.

---

## Why This Matters

Every production AI assistant — customer support bots, coding copilots, personal AI —
eventually hits the same wall: the user has to re-explain themselves in every new session.
MemoryOS shows a concrete, cheap path to eliminating that friction.  The three layers map
directly to human memory: working memory is short-term, episodic is autobiographical, and
semantic is factual long-term knowledge.  Building agents on this architecture means they
accumulate value over time rather than starting from zero on every conversation.
