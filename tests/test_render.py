"""Tests for theme loading and rendering."""

from pathlib import Path

import pytest
from render import load_theme, render_all, render_page


class TestLoadTheme:
    def test_bento_tech(self):
        manifest, env = load_theme("bento-tech")
        assert manifest["name"] == "bento-tech"
        assert "layouts" in manifest
        assert "colors" in manifest
        assert "single-focus" in manifest["layouts"]
        assert "text_primary" in manifest["colors"]
        # Verify templates
        assert "slide-base.svg.j2" in env.list_templates()
        assert "layouts/_base.svg.j2" in env.list_templates()

    def test_bento_light(self):
        manifest, env = load_theme("bento-light")
        assert manifest["name"] == "bento-light"
        # Should inherit templates from bento-tech
        assert "slide-base.svg.j2" in env.list_templates()

    def test_bento_light_colors(self):
        manifest, _ = load_theme("bento-light")
        # Verify light theme has light background
        assert manifest["colors"]["bg_start"].lstrip("#").startswith("F")

    def test_bento_tech_colors(self):
        manifest, _ = load_theme("bento-tech")
        # Verify dark theme has dark background
        assert not manifest["colors"]["bg_start"].lstrip("#").startswith("F")

    def test_nonexistent_theme(self):
        with pytest.raises(SystemExit):
            load_theme("nonexistent-theme")


class TestRenderAll:
    def test_render_example_bento_tech(self):
        ws = Path("examples/dify-intro")
        result = render_all(ws, theme="bento-tech")
        assert result["rendered"] == 8
        assert result["theme"] == "bento-tech"
        slides = sorted((ws / "slides").glob("*.svg"))
        assert len(slides) == 8

    def test_render_example_bento_light(self):
        ws = Path("examples/dify-intro")
        result = render_all(ws, theme="bento-light")
        assert result["rendered"] == 8
        assert result["theme"] == "bento-light"


class TestRenderPage:
    def test_render_single_page(self):
        ws = Path("examples/dify-intro")
        result = render_page(ws, 1, theme="bento-tech")
        assert result["page"] == 1
        assert Path(result["file"]).exists()

    def test_render_nonexistent_page(self):
        ws = Path("examples/dify-intro")
        with pytest.raises(SystemExit):
            render_page(ws, 99, theme="bento-tech")


class TestThemeColorContrast:
    """Verify that hardcoded dark text colors are not used in light themes."""

    def test_badge_text_variants(self):
        """Verify light-theme SVG templates output white badge text, not dark."""
        light_manifest, _ = load_theme("bento-light")
        is_light = light_manifest["colors"]["bg_start"].lstrip("#").startswith(("F", "f"))
        assert is_light

        dark_manifest, _ = load_theme("bento-tech")
        is_dark = not dark_manifest["colors"]["bg_start"].lstrip("#").startswith(("F", "f"))
        assert is_dark

    def test_card_list_svg_light_theme_uses_white_badge_text(self):
        """Regression: card-list.svg.j2 must emit white fill on light themes, not #0a0e27."""
        manifest, env = load_theme("bento-light")
        card = {"slot": "main", "component": "card-list", "data": {"items": [{"title": "test"}]}}
        from render import render_card

        svg = render_card(env, manifest, card, slot_w=500, slot_h=500)
        # badge text fill must be #ffffff for light theme on default accent, not #0a0e27
        assert 'fill="#ffffff"' in svg
        assert 'fill="#0a0e27"' not in svg

    def test_card_list_svg_dark_theme_uses_dark_badge_text(self):
        """Regression: card-list.svg.j2 must use #0a0e27 on dark themes."""
        manifest, env = load_theme("bento-tech")
        card = {"slot": "main", "component": "card-list", "data": {"items": [{"title": "test"}]}}
        from render import render_card

        svg = render_card(env, manifest, card, slot_w=500, slot_h=500)
        assert 'fill="#0a0e27"' in svg

    def test_card_compare_svg_light_theme_uses_white_header_text(self):
        """Regression: card-compare.svg.j2 must emit white fill on light themes."""
        manifest, env = load_theme("bento-light")
        card = {
            "slot": "main",
            "component": "card-compare",
            "data": {"headers": ["A", "B"], "recommend": 0, "rows": []},
        }
        from render import render_card

        svg = render_card(env, manifest, card, slot_w=500, slot_h=400)
        # recommended header text must be #ffffff for light theme
        assert 'fill="#ffffff"' in svg
        # must not have dark fill on the recommended header
        assert 'fill="#0a0e27"' not in svg

    def test_card_compare_svg_dark_theme_uses_dark_header_text(self):
        """Regression: card-compare.svg.j2 must use #0a0e27 on dark themes."""
        manifest, env = load_theme("bento-tech")
        card = {
            "slot": "main",
            "component": "card-compare",
            "data": {"headers": ["A", "B"], "recommend": 0, "rows": []},
        }
        from render import render_card

        svg = render_card(env, manifest, card, slot_w=500, slot_h=400)
        assert 'fill="#0a0e27"' in svg


class TestRenderCardEdgeCases:
    def test_render_card_no_component(self):
        manifest, env = load_theme("bento-tech")
        from render import render_card

        result = render_card(env, manifest, {"data": {}}, slot_w=500, slot_h=500)
        assert result == ""

    def test_render_card_missing_template(self):
        manifest, env = load_theme("bento-tech")
        import pytest
        from render import render_card

        with pytest.raises(SystemExit):
            render_card(env, manifest, {"component": "nonexistent-component"}, slot_w=500, slot_h=500)


class TestRenderOnePageErrors:
    def test_missing_layout_field(self):
        manifest, env = load_theme("bento-tech")
        import pytest
        from render import render_one_page

        with pytest.raises(SystemExit):
            render_one_page(env, manifest, {"page": 1}, total_pages=1, meta={})

    def test_invalid_layout_name(self):
        manifest, env = load_theme("bento-tech")
        import pytest
        from render import render_one_page

        with pytest.raises(SystemExit):
            render_one_page(env, manifest, {"page": 1, "layout": "nonexistent-layout"}, total_pages=1, meta={})


class TestBentoPaper:
    def test_load_theme(self):
        manifest, _ = load_theme("bento-paper")
        assert manifest["name"] == "bento-paper"
        assert manifest["effects"]["bg_texture"] == "dots"
        assert "Noto Serif SC" in manifest["fonts"]["display"]

    def test_render_example(self):
        ws = Path("examples/dify-intro")
        result = render_all(ws, theme="bento-paper")
        assert result["rendered"] == 8
        assert result["theme"] == "bento-paper"

    def test_font_hierarchy_in_svg(self):
        """Verify serif headings + sans body + mono eyebrow in rendered output."""
        manifest, env = load_theme("bento-paper")
        from render import render_one_page

        page = {
            "page": 1,
            "layout": "single-focus",
            "cards": [{"slot": "main", "component": "card-hero", "data": {"eyebrow": "MAGAZINE", "title": "标题", "subtitle": "副标题"}}],
        }
        svg = render_one_page(env, manifest, page, total_pages=1, meta={})
        # 验证 Google Fonts 排在 font-family 首位（SVG 中单引号转义为 &#39;）
        assert "&#39;Noto Serif SC&#39;, &#39;Playfair Display&#39;" in svg
        assert "&#39;IBM Plex Mono&#39;, &#39;SF Mono&#39;" in svg
        assert "#F5F0E8" in svg
        assert "#B8654A" in svg
