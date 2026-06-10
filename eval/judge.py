"""LLM-as-judge scorer using gpt-4o-mini."""

import os

import openai
from dotenv import load_dotenv

load_dotenv()

_JUDGE_PROMPT = """\
You are an evaluator for an AI assistant benchmark.

A user sent this message:
"{message}"

The expected answer should reference these keywords: {keywords}

The agent responded:
"{response}"

Score the response from 1 to 5:
  5 = perfectly addresses the message AND references relevant user context / keywords
  4 = good answer, references most keywords or shows awareness of user context
  3 = answers the message but ignores user context and keywords
  2 = partially answers but misses key points
  1 = wrong, irrelevant, or generic answer

Reply with ONLY a single integer between 1 and 5. Nothing else."""


class LLMJudge:
    """Scores agent responses on a 1-5 scale using an LLM as the evaluator."""

    def __init__(self):
        self._client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def score(self, task: dict, agent_response: str) -> int:
        """Return a 1-5 integer score for *agent_response* given the *task*."""
        prompt = _JUDGE_PROMPT.format(
            message=task["message"],
            keywords=task["expected_keywords"],
            response=agent_response,
        )
        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=8,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.choices[0].message.content.strip()
        try:
            score = int(raw[0])  # take first character to handle any stray whitespace
            return max(1, min(5, score))
        except (ValueError, IndexError):
            return 3  # fallback to neutral score on parse failure
