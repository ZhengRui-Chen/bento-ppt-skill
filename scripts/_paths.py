"""Shared path resolution + utilities — used by render.py, native_render.py, ppt.py."""

from __future__ import annotations

import os
import re
from pathlib import Path


def get_skill_dir() -> Path:
    """Resolve the skill root directory.

    Prefers $CLAUDE_SKILL_DIR (set by Claude Code skill runtime).
    Falls back to the repository root (two levels up from this file)
    for dev clones and CI.
    """
    d = Path(os.environ.get("CLAUDE_SKILL_DIR", str(Path.home() / ".claude/skills/ppt-agent"))).resolve()
    if not d.exists():
        d = Path(__file__).resolve().parent.parent  # repo root
    return d


def slugify(name: str) -> str:
    """Canonical slug: lowercase, non-alphanumeric → hyphens."""
    s = re.sub(r"[\s/\\:*?\"<>|]+", "-", name.strip())
    s = re.sub(r"-+", "-", s).strip("-")
    return (s or "untitled").lower()


# Module-level constant for convenience
SKILL_DIR = get_skill_dir()
