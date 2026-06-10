"""Agent B — full MemoryOS agent with all three memory layers."""

import os

import openai
from dotenv import load_dotenv

from memory.working import WorkingMemory
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from memory.router import MemoryRouter

load_dotenv()

_SYSTEM_TEMPLATE = """\
You are a helpful assistant with memory of past conversations.

{context}
"""


class AgentB:
    """Memory-augmented LLM agent using working, episodic, and semantic memory layers."""

    def __init__(self):
        self._client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._working = WorkingMemory()
        self._episodic = EpisodicMemory()
        self._semantic = SemanticMemory()
        self._router = MemoryRouter()
        self._current_session_id: int = 0

    def respond(self, message: str, session_id: int, task_id: int) -> str:
        """Generate a response using all three memory layers as context."""
        self._current_session_id = session_id

        # Build context from all layers
        context = self._router.get_context(
            query=message,
            working_memory=self._working,
            episodic_memory=self._episodic,
            semantic_memory=self._semantic,
        )

        system_prompt = _SYSTEM_TEMPLATE.format(
            context=context if context else "No prior context available.",
        )

        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=512,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
        )
        reply = response.choices[0].message.content.strip()

        # Store this exchange in working memory
        self._working.add("user", message)
        self._working.add("assistant", reply)

        return reply

    def end_session(self) -> None:
        """Flush working memory into episodic and semantic stores at session end."""
        messages = self._working.get_all()
        if not messages:
            return

        # Persist to episodic store
        self._episodic.save_session(self._current_session_id, messages)

        # Compress into semantic profile
        conversation_text = "\n".join(
            f"{m['role'].capitalize()}: {m['content']}" for m in messages
        )
        self._semantic.update(conversation_text)

        # Clear working memory for next session
        self._working.clear()
