"""Semantic memory — a persistent JSON user profile updated by an LLM each session."""

import json
import os
from pathlib import Path

import openai
from dotenv import load_dotenv

load_dotenv()

_PROFILE_PATH = Path("semantic_profile.json")
_DEFAULT_PROFILE: dict = {
    "name": "",
    "job": "",
    "tools": [],
    "preferences": [],
    "past_problems": [],
    "other_facts": [],
}


class SemanticMemory:
    """Compresses session conversations into a structured user profile via LLM extraction."""

    def __init__(self):
        self._client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._profile: dict = self._load()

    # ── persistence ──────────────────────────────────────────────────────────

    def _load(self) -> dict:
        """Load profile from disk, creating a blank one if it doesn't exist."""
        if _PROFILE_PATH.exists():
            with _PROFILE_PATH.open() as f:
                return json.load(f)
        return dict(_DEFAULT_PROFILE)

    def _save(self) -> None:
        """Write the current profile to disk."""
        with _PROFILE_PATH.open("w") as f:
            json.dump(self._profile, f, indent=2)

    # ── public API ───────────────────────────────────────────────────────────

    def update(self, conversation_text: str) -> None:
        """Call the LLM to extract facts from *conversation_text* and merge them into the profile."""
        prompt = (
            "Extract key facts about the user from this conversation.\n"
            "Return ONLY a valid JSON object with these exact keys:\n"
            "  name, job, tools, preferences, past_problems, other_facts\n"
            "Arrays should contain short string items. "
            "Return an empty string for unknown scalar fields and an empty list for unknown arrays.\n\n"
            f"Conversation:\n{conversation_text}"
        )
        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        try:
            extracted: dict = json.loads(raw)
        except json.JSONDecodeError:
            return  # silently skip malformed extraction

        # Merge: scalar fields — overwrite if non-empty; list fields — union
        for key in ("name", "job"):
            if extracted.get(key):
                self._profile[key] = extracted[key]
        for key in ("tools", "preferences", "past_problems", "other_facts"):
            existing = set(self._profile.get(key, []))
            new_items = extracted.get(key, [])
            self._profile[key] = list(existing | set(new_items))

        self._save()

    def get_profile(self) -> str:
        """Return the user profile as a formatted string for prompt injection."""
        p = self._profile
        if not any([p["name"], p["job"], p["tools"], p["preferences"],
                    p["past_problems"], p["other_facts"]]):
            return "No user profile available yet."

        lines = ["=== User Profile ==="]
        if p["name"]:
            lines.append(f"Name: {p['name']}")
        if p["job"]:
            lines.append(f"Job: {p['job']}")
        if p["tools"]:
            lines.append(f"Tools: {', '.join(p['tools'])}")
        if p["preferences"]:
            lines.append(f"Preferences: {', '.join(p['preferences'])}")
        if p["past_problems"]:
            lines.append(f"Past problems solved: {', '.join(p['past_problems'])}")
        if p["other_facts"]:
            lines.append(f"Other facts: {', '.join(p['other_facts'])}")
        return "\n".join(lines)
