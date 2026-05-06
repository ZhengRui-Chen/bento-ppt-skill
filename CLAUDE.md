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

- **Dual renderer parity**: Every component needs both SVG template + Native Python method. Font categories must match.
- **Token-driven**: Colors/fonts/spacing all read from `theme.colors.*` / `theme.type_scale.*`, never hardcoded.
- **Cross-platform first**: OOXML theme fonts (`+mj-lt`/`+mn-lt`), NOT OS-specific font names. Test on Windows PPT.
- **OOXML schema discipline**: Element ordering in `a:rPr` is strict; `spc` is an attribute not a child.
- **Theme inheritance**: Derived themes need only `manifest.json`; templates fallback to `bento-tech/`.
- **Layout contract**: `layout.json` says "what goes where", themes say "how it looks".
- **No bare colors**: Always pick from the theme manifest so light/dark variants work.
- **CI must pass**: ruff, mypy, compileall, import-check, lint_cn on examples.

## OOXML rules (must follow — Windows Office rejects violations)

### `a:rPr` child element order (STRICT)

The schema sequence for `CT_TextCharacterProperties` / `a:rPr`:
`ln` → fill group (`solidFill`/`noFill`/`gradFill`) → effect group → `latin` → `ea` → `cs` → `sym` → `extLst`

**solidFill MUST come before latin/ea.** If `latin` appears before `solidFill`, Windows Office ignores the fill and uses default black text. macOS Keynote/PPT is lenient.

In `_add_textbox`, always: set `run.font.color.rgb` first → handle transparency (`_apply_rpr_extras`) → then `_apply_theme_font` last.

### Character spacing: ATTRIBUTE, not child element

`spc` on `a:rPr` is an **attribute** (`<a:rPr spc="300">`), NOT a child element. Value is in hundredths of a point.
- `spc="100"` = 1pt, `spc="300"` = 3pt (eyebrow), `spc="600"` = 6pt (deco)
- Do NOT use `<a:spc pts="..."/>` as a child of `a:rPr` — it doesn't exist in the schema.

### Font scheme: MODIFY, never DELETE & recreate

python-pptx creates a fontScheme with 30+ `<a:font script="...">` entries (Jpan, Hans, Hang, Arab, etc.) that Windows OOXML validators require. When changing theme fonts:
- **Do**: find existing `a:majorFont`/`a:minorFont`, modify `a:latin` typeface in place
- **Do NOT**: remove the entire `a:fontScheme` and rebuild it from scratch
- Use `theme_part._blob` to modify BEFORE `prs.save()` — no zipfile roundtrip

### Theme fonts for cross-platform rendering

Never use `run.font.name = "Songti SC"` or any OS-specific font name. Use OOXML theme font references:
- `+mj-lt` / `+mj-ea` = major font (headings/display, serif) → `font_category="display"`
- `+mn-lt` / `+mn-ea` = minor font (body, sans-serif) → `font_category="sans"`
- Set theme font scheme: majorFont Latin = Georgia, minorFont Latin = Arial
- EA fonts: omit typeface entirely → PowerPoint uses platform default CJK font

## SVG/Native font parity

Every `_add_textbox` call must explicitly set `font_category` to match the SVG template's font intent:
- SVG uses `font-family="{{ theme.fonts.display }}"` → native must use `font_category="display"`
- SVG uses `font-family="{{ theme.fonts.sans }}"` → native must use `font_category="sans"` (default)
- Ghost/deco text: use `font_category="sans"` — sans-serif reads lighter at low opacity than serif

## `_add_textbox` internal ordering

```python
run.font.color.rgb = _hex(color)        # 1. solidFill first
if transparency or letter_spacing:
    self._apply_rpr_extras(run, ...)     # 2. adds alpha to solidFill / sets spc attr
self._apply_theme_font(run, category)    # 3. latin + ea LAST (after fill)
```

## Component checklist (new component development)

1. SVG template: `themes/bento-tech/components/<name>.svg.j2`
2. Native method: `NativeRenderer._render_<name>()` in `native_render.py`
3. Data schema doc in `reference/bento-layouts-guide.md`
4. Verify `font_category` matches between SVG and native renderer
5. On first PPTX export, test on Windows PowerPoint (not just macOS Keynote)
