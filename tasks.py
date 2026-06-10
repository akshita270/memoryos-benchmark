"""50 scripted benchmark tasks across 10 sessions for the MemoryOS evaluation."""

TASKS = [
    # ── Session 1: Introduce basic identity ──────────────────────────────────
    {
        "session": 1, "task_id": 1,
        "message": "Hi, I'm Akshita. I'm a data analyst who codes primarily in Python.",
        "expected_keywords": ["Akshita", "Python", "data analyst"],
    },
    {
        "session": 1, "task_id": 2,
        "message": "I work at a fintech startup and my main job is building dashboards for the risk team.",
        "expected_keywords": ["fintech", "dashboards", "risk team"],
    },
    {
        "session": 1, "task_id": 3,
        "message": "My favourite tools are pandas, dbt, and Metabase. I try to avoid Excel whenever possible.",
        "expected_keywords": ["pandas", "dbt", "Metabase", "Excel"],
    },
    {
        "session": 1, "task_id": 4,
        "message": "One recurring problem I face is slow SQL queries on our Postgres database with 50M+ rows.",
        "expected_keywords": ["SQL", "Postgres", "slow", "50M"],
    },
    {
        "session": 1, "task_id": 5,
        "message": "I fixed that last quarter by adding a partial index and switching to columnar storage for archive tables.",
        "expected_keywords": ["partial index", "columnar", "archive"],
    },

    # ── Session 2: Introduce preferences & workflow ───────────────────────────
    {
        "session": 2, "task_id": 6,
        "message": "I prefer dark-mode IDEs. I use VS Code with the Dracula theme.",
        "expected_keywords": ["dark-mode", "VS Code", "Dracula"],
    },
    {
        "session": 2, "task_id": 7,
        "message": "I always write type hints in Python and enforce them with mypy in CI.",
        "expected_keywords": ["type hints", "mypy", "CI"],
    },
    {
        "session": 2, "task_id": 8,
        "message": "My team follows trunk-based development. We deploy to production every day via GitHub Actions.",
        "expected_keywords": ["trunk-based", "GitHub Actions", "deploy"],
    },
    {
        "session": 2, "task_id": 9,
        "message": "I recently started learning Rust in my spare time. I want to rewrite some hot-path Python utilities in it.",
        "expected_keywords": ["Rust", "hot-path", "Python utilities"],
    },
    {
        "session": 2, "task_id": 10,
        "message": "I struggle with borrow checker errors in Rust. Lifetimes still confuse me.",
        "expected_keywords": ["borrow checker", "lifetimes", "Rust"],
    },

    # ── Session 3: Deeper technical context ──────────────────────────────────
    {
        "session": 3, "task_id": 11,
        "message": "Our data stack: ingestion via Airbyte, transformation with dbt, warehouse is BigQuery.",
        "expected_keywords": ["Airbyte", "dbt", "BigQuery"],
    },
    {
        "session": 3, "task_id": 12,
        "message": "I wrote a Python script last month that auto-generates dbt documentation from table comments in BigQuery.",
        "expected_keywords": ["dbt documentation", "BigQuery", "auto-generates"],
    },
    {
        "session": 3, "task_id": 13,
        "message": "I care a lot about data quality. I use Great Expectations to validate pipelines.",
        "expected_keywords": ["data quality", "Great Expectations", "pipelines"],
    },
    {
        "session": 3, "task_id": 14,
        "message": "My biggest professional goal this year is to become a staff engineer.",
        "expected_keywords": ["staff engineer", "professional goal"],
    },
    {
        "session": 3, "task_id": 15,
        "message": "I'm preparing for staff-level interviews by working through system design problems daily.",
        "expected_keywords": ["staff-level", "system design", "interviews"],
    },

    # ── Session 4: Recall basic identity ─────────────────────────────────────
    {
        "session": 4, "task_id": 16,
        "message": "Can you remind me — what did I tell you about my job?",
        "expected_keywords": ["data analyst", "fintech", "dashboards", "risk"],
    },
    {
        "session": 4, "task_id": 17,
        "message": "What programming language do I mainly use?",
        "expected_keywords": ["Python"],
    },
    {
        "session": 4, "task_id": 18,
        "message": "What tools have I mentioned I like working with?",
        "expected_keywords": ["pandas", "dbt", "Metabase"],
    },
    {
        "session": 4, "task_id": 19,
        "message": "What database problem did I solve last quarter?",
        "expected_keywords": ["Postgres", "slow", "partial index", "columnar"],
    },
    {
        "session": 4, "task_id": 20,
        "message": "What new language am I currently learning?",
        "expected_keywords": ["Rust"],
    },

    # ── Session 5: Recall preferences & workflow ─────────────────────────────
    {
        "session": 5, "task_id": 21,
        "message": "What editor and theme do I use?",
        "expected_keywords": ["VS Code", "Dracula"],
    },
    {
        "session": 5, "task_id": 22,
        "message": "How does my team deploy code?",
        "expected_keywords": ["trunk-based", "GitHub Actions", "daily"],
    },
    {
        "session": 5, "task_id": 23,
        "message": "What Python best practices do I follow in my projects?",
        "expected_keywords": ["type hints", "mypy"],
    },
    {
        "session": 5, "task_id": 24,
        "message": "What is my main struggle with Rust right now?",
        "expected_keywords": ["borrow checker", "lifetimes"],
    },
    {
        "session": 5, "task_id": 25,
        "message": "What is my data stack at work?",
        "expected_keywords": ["Airbyte", "dbt", "BigQuery"],
    },

    # ── Session 6: Recall deeper context ─────────────────────────────────────
    {
        "session": 6, "task_id": 26,
        "message": "What script did I build last month at work?",
        "expected_keywords": ["dbt documentation", "BigQuery", "auto-generates"],
    },
    {
        "session": 6, "task_id": 27,
        "message": "How do I ensure data quality in my pipelines?",
        "expected_keywords": ["Great Expectations"],
    },
    {
        "session": 6, "task_id": 28,
        "message": "What is my biggest career goal this year?",
        "expected_keywords": ["staff engineer"],
    },
    {
        "session": 6, "task_id": 29,
        "message": "How am I preparing for that career goal?",
        "expected_keywords": ["system design", "interviews", "daily"],
    },
    {
        "session": 6, "task_id": 30,
        "message": "Which tool do I specifically avoid and why?",
        "expected_keywords": ["Excel"],
    },

    # ── Session 7: Cross-session synthesis ───────────────────────────────────
    {
        "session": 7, "task_id": 31,
        "message": "Given what you know about my stack and preferences, what would be a good next tool for me to learn?",
        "expected_keywords": ["Python", "dbt", "BigQuery", "data"],
    },
    {
        "session": 7, "task_id": 32,
        "message": "Based on my career goals, should I focus more on Rust or system design this month?",
        "expected_keywords": ["staff engineer", "system design", "Rust"],
    },
    {
        "session": 7, "task_id": 33,
        "message": "I want to add automated data quality checks to the dbt docs script I built. Where should I start?",
        "expected_keywords": ["dbt", "Great Expectations", "BigQuery", "documentation"],
    },
    {
        "session": 7, "task_id": 34,
        "message": "My Postgres issue came back on a new table. What did I do last time to fix it?",
        "expected_keywords": ["partial index", "columnar", "archive"],
    },
    {
        "session": 7, "task_id": 35,
        "message": "How would I set up mypy in a new project that also uses dbt macros?",
        "expected_keywords": ["mypy", "type hints", "dbt"],
    },

    # ── Session 8: Deeper synthesis ───────────────────────────────────────────
    {
        "session": 8, "task_id": 36,
        "message": "I want to write a Rust CLI tool to speed up one of my Python data-processing scripts. What should I keep in mind?",
        "expected_keywords": ["Rust", "Python", "borrow checker", "hot-path"],
    },
    {
        "session": 8, "task_id": 37,
        "message": "Can you design a GitHub Actions workflow for my team's deployment process?",
        "expected_keywords": ["GitHub Actions", "trunk-based", "deploy"],
    },
    {
        "session": 8, "task_id": 38,
        "message": "I need to present my dbt automation work to the engineering team. Help me write a 3-sentence summary.",
        "expected_keywords": ["dbt", "BigQuery", "documentation", "auto-generates"],
    },
    {
        "session": 8, "task_id": 39,
        "message": "What would a staff engineer at a fintech look like day-to-day, given my current role?",
        "expected_keywords": ["staff engineer", "fintech", "data analyst", "risk"],
    },
    {
        "session": 8, "task_id": 40,
        "message": "How can I improve data quality monitoring beyond what I'm already doing?",
        "expected_keywords": ["Great Expectations", "BigQuery", "dbt", "pipelines"],
    },

    # ── Session 9: Highly personalised advice ────────────────────────────────
    {
        "session": 9, "task_id": 41,
        "message": "Write a short personal bio I could use on a conference speaker application.",
        "expected_keywords": ["Akshita", "data analyst", "fintech", "Python", "dbt"],
    },
    {
        "session": 9, "task_id": 42,
        "message": "Suggest 3 system design problems I should practice given my background.",
        "expected_keywords": ["fintech", "data", "system design", "staff engineer"],
    },
    {
        "session": 9, "task_id": 43,
        "message": "I want to open-source the dbt documentation script. Write a one-paragraph project description for the README.",
        "expected_keywords": ["dbt", "BigQuery", "documentation", "Python"],
    },
    {
        "session": 9, "task_id": 44,
        "message": "Help me write a Slack message to my team about switching to columnar storage for our archive tables.",
        "expected_keywords": ["columnar", "archive", "Postgres", "team"],
    },
    {
        "session": 9, "task_id": 45,
        "message": "What are the top 3 things I should highlight in a staff engineer promotion packet?",
        "expected_keywords": ["staff engineer", "fintech", "data quality", "dbt"],
    },

    # ── Session 10: Full-context complex tasks ────────────────────────────────
    {
        "session": 10, "task_id": 46,
        "message": "Design a 6-month learning plan for me to reach staff engineer level.",
        "expected_keywords": ["staff engineer", "Rust", "system design", "Python", "fintech"],
    },
    {
        "session": 10, "task_id": 47,
        "message": "What are the biggest technical risks in my current data stack and how would you mitigate them?",
        "expected_keywords": ["Airbyte", "dbt", "BigQuery", "Great Expectations", "risk"],
    },
    {
        "session": 10, "task_id": 48,
        "message": "Write a performance review self-assessment paragraph for this year.",
        "expected_keywords": ["Akshita", "dbt", "Postgres", "data quality", "fintech"],
    },
    {
        "session": 10, "task_id": 49,
        "message": "If I were to build an internal AI assistant for my risk team using the tools I already know, what would the architecture look like?",
        "expected_keywords": ["Python", "BigQuery", "fintech", "risk", "dashboards"],
    },
    {
        "session": 10, "task_id": 50,
        "message": "Summarise everything you know about me and give me your top 3 recommendations for the next 90 days.",
        "expected_keywords": ["Akshita", "staff engineer", "Rust", "dbt", "fintech", "data analyst"],
    },
]
