# Changelog

## [0.1.0] — 2026-04-17

- Initial release: ppt-agent skill with 7-stage pipeline
- 6 Bento layouts: single-focus, two-col-symmetric, two-col-asymmetric, three-col, major-minor, hero-top, mixed-grid
- 9 card components: hero, stat, stack, list, quote, text, image, chart-bar, compare
- 2 themes: bento-tech (dark), bento-light (light) with template inheritance
- Dual renderer: SVG (Jinja2) for visual quality + Native (python-pptx) for 100% editability
- Image provider protocol: url_download, nanobanana (stub), unsplash (stub)
- Chinese typography lint (lint_cn.py)
- Chrome headless screenshot + HTML preview (shoot.py)
