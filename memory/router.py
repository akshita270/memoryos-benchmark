"""Rule-based memory router — assembles context from all three memory layers."""

from memory.working import WorkingMemory
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory


class MemoryRouter:
    """Combines semantic profile, episodic retrieval, and working memory into one context string."""

    def get_context(
        self,
        query: str,
        working_memory: WorkingMemory,
        episodic_memory: EpisodicMemory,
        semantic_memory: SemanticMemory,
    ) -> str:
        """Return a single context string to inject into the agent's system prompt.

        Priority order:
        1. Semantic profile (always included if non-empty).
        2. Top-3 episodic matches for *query*.
        3. Last 3 turns of working memory (current session).
        """
        sections: list[str] = []

        # Layer 1 — semantic (long-term user knowledge)
        profile = semantic_memory.get_profile()
        if profile and profile != "No user profile available yet.":
            sections.append(profile)

        # Layer 2 — episodic (relevant past interactions)
        past_messages = episodic_memory.search(query, top_k=3)
        if past_messages:
            episode_block = "=== Relevant Past Interactions ===\n" + "\n---\n".join(past_messages)
            sections.append(episode_block)

        # Layer 3 — working (current session so far)
        current = working_memory.format_for_prompt(max_turns=3)
        if current and current != "No conversation so far.":
            sections.append(f"=== Current Session ===\n{current}")

        return "\n\n".join(sections) if sections else ""
