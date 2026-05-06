# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync --locked --all-extras --dev     # Install all deps
uv run ruff check .                     # Lint
uv run ruff format --check .            # Format check
uv run mypy                             # Type check
uv run pytest -v                        # Run tests (single test: pytest -k "pattern")
uv run pre-commit run --all-files       # Full pre-commit (includes compileall, import-check, lint_cn)

# Skill CLI
uv run python scripts/ppt.py new "<topic>"           # AI-generated outline + layout
uv run python scripts/ppt.py fetch <ws>              # Download images for a workspace
uv run python scripts/ppt.py scaffold <ws>           # Same as `render` (historical alias)
uv run python scripts/ppt.py render <ws> [--page N] [--theme <name>]  # SVG render
uv run python scripts/ppt.py shoot <ws>              # Chrome screenshots → deck.html
uv run python scripts/ppt.py export <ws> --format pptx  # Native PPTX (recommended)
uv run python scripts/ppt.py export <ws> --format pptx-svg  # SVG→PPTX (prettier, not editable)
uv run python scripts/ppt.py export <ws> --format pdf     # Chrome → PDF
uv run python scripts/ppt.py export <ws> --format html    # Standalone HTML
```

## Architecture

Two independent render pipelines share `layout.json` + theme `manifest.json` as input contract:

```
                    ┌──→ render.py (Jinja2) → slides/*.svg ──→ shoot.py → deck.html
layout.json ────────┤
(theme manifest)    └──→ native_render.py (python-pptx) → deck.pptx (100% editable)
```

**SVG pipeline** — produces perfect visuals (gradients, textures, spot lights). Used for HTML preview and screenshots.
**Native pipeline** — produces editable PowerPoint shapes. Sacrifices visual effects (no gradients/textures in cards) for editability. Default for `--format pptx`.

There's also a legacy **SVG→PPTX** path (`to_pptx_svg` in export.py) that embeds SVG screenshots as slide images with an OOXML svgBlip reference. Better visuals than native, but each slide is a single uneditable image. Use `--format pptx-svg`.

Theme templates live in `themes/bento-tech/` (base). Derived themes (`bento-paper`, `bento-ink`, `bento-light`) only need `manifest.json` + optional `slide-base.svg.j2` override. Jinja2 falls back to bento-tech for all other templates.

`ppt.py` uses `sys.path.insert(0, str(Path(__file__).parent))` to import sibling scripts. Don't change this pattern without also fixing the circular-import issue in `export.py::to_pptx` (it imports `native_render` inside the function body).

Reference docs in `reference/`:
- `bento-layouts-guide.md` — layout.json schema (layouts, slots, components, data fields)
- `pptx-rendering.md` — Native vs SVG PPTX tradeoffs
- `theme-authoring.md` — How to add a new theme
- `extension-guide.md` — Full extension spec

## Key principles

- **Dual renderer parity**: Every component needs both SVG template + Native Python method. Font categories must match.
- **Token-driven**: Colors/fonts/spacing all read from `theme.colors.*` / `theme.type_scale.*`, never hardcoded.
- **Cross-platform first**: OOXML theme fonts (`+mj-lt`/`+mn-lt`), NOT OS-specific font names. Test on Windows PPT.
- **OOXML schema discipline**: Element ordering in `a:rPr` is strict; `spc` is an attribute not a child.
- **Theme inheritance**: Derived themes need only `manifest.json`; templates fallback to `bento-tech/`.
- **Layout contract**: `layout.json` says "what goes where", themes say "how it looks".
- **No bare colors**: Always pick from the theme manifest so light/dark variants work.
- **CI must pass**: ruff, mypy, compileall, import-check, lint_cn on examples.
- **Tests required for new components**: SVG render path (`test_render.py`), native PPTX path (`test_native_render.py`). Note: `shoot.py` and `export.py` (non-PPTX) currently lack test coverage — new work there should add tests.

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

## Known sharp edges

- **`_is_light` (native_render.py:74) uses a broken heuristic** — `bg_start.startswith(("F","f"))` misclassifies `#abcdef` as dark and `#123456` as light. Should use relative luminance. Currently all three themes happen to work (bento-tech is dark, paper/ink are light), but new themes will break this.
- **`export.py::_embed_fonts` is dead code** — 90-line function, never called. Font embedding was removed because OOXML requires GUID-XOR-obfuscated fonts. Don't resurrect it.
- **Theme slot fallback is inconsistent** — `render.py::load_theme` falls back to bento-tech for missing templates; `native_render.py::_load_manifest` does NOT. A derived theme without explicit `layouts` in manifest will silently produce empty PPTX slides.
- **`deck.html` hardcodes dark background** (`#07091a` in shoot.py:111). Fine for bento-tech, wrong for light themes. Currently a dev preview, not a deliverable.
- **`scaffold` is an alias** — `cmd_scaffold()` and `cmd_render(ws, page=None)` both call `render_all()`. Don't add logic to one without the other.
- **`fetch.py` rewrites `layout.json`** with `json.dumps(indent=2)`, clobbering any custom formatting. Read-modify-write with care.
- **No schema validation on `layout.json`** — the contract is documented in reference guides but not enforced. Invalid layout names or missing data fields produce cryptic errors or silent empty output.

## Component checklist (new component development)

1. SVG template: `themes/bento-tech/components/<name>.svg.j2`
2. Native method: `NativeRenderer._render_<name>()` in `native_render.py`
3. Data schema doc in `reference/bento-layouts-guide.md`
4. Verify `font_category` matches between SVG and native renderer
5. On first PPTX export, test on Windows PowerPoint (not just macOS Keynote)
