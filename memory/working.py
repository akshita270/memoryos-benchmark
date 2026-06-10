"""In-session working memory — a simple list that clears after each session."""


class WorkingMemory:
    """Stores the current session's conversation turns as a list of role/content dicts."""

    def __init__(self):
        self._messages: list[dict] = []

    def add(self, role: str, content: str) -> None:
        """Append a new turn to working memory."""
        self._messages.append({"role": role, "content": content})

    def get_all(self) -> list[dict]:
        """Return all stored messages for prompt injection."""
        return list(self._messages)

    def clear(self) -> None:
        """Wipe working memory at the end of a session."""
        self._messages.clear()

    def format_for_prompt(self, max_turns: int = 3) -> str:
        """Return the last *max_turns* exchanges as a readable string."""
        recent = self._messages[-max_turns * 2:]  # each exchange = 2 messages
        lines = [f"{m['role'].capitalize()}: {m['content']}" for m in recent]
        return "\n".join(lines) if lines else "No conversation so far."
