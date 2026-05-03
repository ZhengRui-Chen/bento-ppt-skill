# CLAUDE.md — bento-ppt-skill

Bento Grid style 16:9 SVG & PPTX slide deck generator, implemented as a Claude Code skill.

## Commands

```bash
uv sync --locked --all-extras --dev   # Install all deps
uv run ruff check .                   # Lint
uv run ruff format --check .          # Format check
uv run mypy                           # Type check
uv run python -m compileall -q scripts  # Syntax check
uv run pytest -v                      # Run tests
uv run pre-commit run --all-files     # Full pre-commit

# Skill CLI
uv run python scripts/ppt.py new "<topic>"
uv run python scripts/ppt.py fetch <ws>
uv run python scripts/ppt.py scaffold <ws>
uv run python scripts/ppt.py render <ws> [--page N] [--theme <name>]
uv run python scripts/ppt.py shoot <ws>
uv run python scripts/ppt.py export <ws> --format pptx
```

## Architecture

```
layout.json (AI-authored spec)
  ├──→ render.py (Jinja2/SVG) → slides/*.svg → shoot.py → deck.html
  └──→ native_render.py (python-pptx) → deck.pptx (100% editable)
```

## Key principles

- **Dual renderer parity**: Every component needs both SVG template + Native Python method.
- **Token-driven**: Colors/fonts/spacing all read from `theme.colors.*` / `theme.type_scale.*`, never hardcoded.
- **Theme inheritance**: Derived themes need only `manifest.json`; templates fallback to `bento-tech/`.
- **Layout contract**: `layout.json` says "what goes where", themes say "how it looks".
- **No bare colors**: Always pick from the theme manifest so light/dark variants work.
- **CI must pass**: ruff, mypy, compileall, import-check, lint_cn on examples.

## Component checklist (new component development)

1. SVG template: `themes/bento-tech/components/<name>.svg.j2`
2. Native method: `NativeRenderer._render_<name>()` in `native_render.py`
3. Data schema doc in `reference/bento-layouts-guide.md`
