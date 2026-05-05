# Changelog

## [0.2.0] — 2026-05-06

### New
- 3rd theme: bento-paper (warm magazine/editorial, serif headings + sans body + mono meta)
- Default theme: bento-tech → bento-paper
- Font embedding in PPTX (Noto Serif SC, Noto Sans SC, IBM Plex Mono)
- Warm terracotta accent palette (#B8654A → #D4956B)
- SVG badge spacing and sizing improvements
- pptx-svg export writes to deck-svg.pptx (no longer overwrites deck.pptx)
- Native PPTX gradient background

### Fixed
- 3 V1 rendering bugs: stat truncation, quote line-break, card-text overflow
- Light-theme hardcoded color safety (_is_light property)
- Card-quote native renderer uses display font (serif)
- Font stack Fallback for Keynote (macOS system fonts in stack)
- Badge spacing in both SVG and native renderer
- SKILL.md "playwright" corrected to Chrome headless
- layout.json theme mismatch between SVG and PPTX output
- PPTX background rectangle overflow preventing white edge gaps

### Improved
- Tests: 42 → 62, coverage 54% → 58%
- Ruff rules: expanded from E9+F to E9+F+I+W+B+C4+SIM+RUF
- Pre-commit hooks (ruff, mypy, compileall, import-check, lint-cn)
- CLAUDE.md, AGENTS.md, .editorconfig, CHANGELOG.md
- Provider implementations: nanobanana (Gemini Imagen), unsplash (search)
- Example workspace now complete (.layout, brief.md, outline.json, research/)
- All docs updated for 3-theme default

## [0.1.0] — 2026-04-17

- Initial release: ppt-agent skill with 7-stage pipeline
- 6 Bento layouts + 9 card components
- 2 themes: bento-tech (dark), bento-light (light) with template inheritance
- Dual renderer: SVG (Jinja2) + Native (python-pptx)
- Image provider protocol, Chinese typography lint, Chrome headless preview
