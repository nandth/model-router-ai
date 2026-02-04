"""Input sanitization utilities.

keep this minimal: we want to accept pasted code snippets (multiline,
tabs, quotes, backticks) without mutating them, while still blocking obvious abuse
cases like empty/whitespace-only prompts or embedded NUL bytes.
"""

from __future__ import annotations

import re


# Allow fairly large prompts to accommodate pasted code snippets.
DEFAULT_MAX_PROMPT_CHARS = 50_000

# Control characters that are almost never useful in prompts and can cause issues in
# logs/terminals. We explicitly allow common whitespace used in code: \t, \n, \r.
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def sanitize_prompt(prompt: str) -> str:
    """
    Sanitize prompt while preserving formatting.

    - Normalizes CRLF/CR -> LF so downstream logic behaves consistently.
    - Removes NUL/control chars that can break parsers/logs.
    """
    if prompt is None:
        return ""

    # Normalize line endings for consistency across Windows/macOS/Linux clients.
    prompt = prompt.replace("\r\n", "\n").replace("\r", "\n")

    # Drop control characters (including NUL). Keep tabs and newlines.
    prompt = _CONTROL_CHARS_RE.sub("", prompt)

    return prompt


def validate_prompt(prompt: str, *, max_chars: int = DEFAULT_MAX_PROMPT_CHARS) -> str:
    """Validate and sanitize prompt; raises ValueError on invalid input."""
    prompt = sanitize_prompt(prompt)

    if not prompt.strip():
        raise ValueError("prompt must not be empty")

    if len(prompt) > max_chars:
        raise ValueError(f"prompt too long (max {max_chars} characters)")

    return prompt

