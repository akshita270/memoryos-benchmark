"""Agent A — stateless baseline with no memory of any kind."""

import os

import openai
from dotenv import load_dotenv

load_dotenv()

_SYSTEM_PROMPT = "You are a helpful assistant."


class AgentA:
    """Stateless LLM agent; every call is completely independent."""

    def __init__(self):
        self._client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def respond(self, message: str) -> str:
        """Send *message* to the LLM and return its response with no history attached."""
        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=512,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
        )
        return response.choices[0].message.content.strip()
