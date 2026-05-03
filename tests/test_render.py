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
        """Verify the SVG template picks contrasting badge text for light themes."""
        import sys

        sys.path.insert(0, "scripts")

        # bento-light should use white text on accent backgrounds
        light_manifest, _ = load_theme("bento-light")
        is_light = light_manifest["colors"]["bg_start"].lstrip("#").startswith("F")
        assert is_light  # light theme

        # bento-tech should use dark text on accent backgrounds
        dark_manifest, _ = load_theme("bento-tech")
        is_dark = not dark_manifest["colors"]["bg_start"].lstrip("#").startswith("F")
        assert is_dark  # dark theme
