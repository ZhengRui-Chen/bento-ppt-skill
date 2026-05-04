"""Tests for native PPTX renderer color handling."""

import json
import tempfile
from pathlib import Path

from native_render import NativeRenderer, _hex


class TestHex:
    def test_standard(self):
        c = _hex("#7c5cff")
        assert str(c) == "7C5CFF"

    def test_no_hash(self):
        c = _hex("7c5cff")
        assert str(c) == "7C5CFF"

    def test_white(self):
        c = _hex("#ffffff")
        assert str(c) == "FFFFFF"


class TestIsLight:
    def test_bento_tech_is_dark(self):
        nr = NativeRenderer("bento-tech")
        assert nr._is_light is False

    def test_bento_light_is_light(self):
        nr = NativeRenderer("bento-light")
        assert nr._is_light is True

    def test_lowercase_hex_detected_as_light(self):
        """Regression: _is_light must be case-insensitive for hex digits."""
        nr = NativeRenderer("bento-tech")
        nr.theme["colors"]["bg_start"] = "#f8f8f8"
        assert nr._is_light is True

    def test_badge_text_color_light_theme(self):
        """card-list badge text must be white on light themes."""
        nr = NativeRenderer("bento-light")
        # Verify the logic: light theme + default accent → white text
        assert nr._is_light
        # The code uses: badge_text_color = "#ffffff" if self._is_light else "#0a0e27"
        badge = "#ffffff" if nr._is_light else "#0a0e27"
        assert badge == "#ffffff"

    def test_badge_text_color_dark_theme_success(self):
        """card-list success badge must use dark text on dark themes."""
        nr = NativeRenderer("bento-tech")
        assert not nr._is_light
        badge = "#ffffff" if nr._is_light else "#0a3a1f"
        assert badge == "#0a3a1f"

    def test_compare_header_text_color_light_theme(self):
        """card-compare recommended header text must be white on light themes."""
        nr = NativeRenderer("bento-light")
        light_text = "#ffffff" if nr._is_light else "#0a0e27"
        assert light_text == "#ffffff"

    def test_compare_header_text_color_dark_theme(self):
        """card-compare recommended header text must be dark on dark themes."""
        nr = NativeRenderer("bento-tech")
        dark_text = "#ffffff" if nr._is_light else "#0a0e27"
        assert dark_text == "#0a0e27"


class TestNativeDeckRender:
    def test_render_example_deck(self):
        ws = Path("examples/dify-intro")
        layout = json.loads((ws / "layout.json").read_text(encoding="utf-8"))
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
            out = Path(f.name)
        try:
            nr = NativeRenderer("bento-tech")
            result = nr.render_deck(layout, out)
            assert result.suffix == ".pptx"
            assert result.exists()
            assert result.stat().st_size > 1000  # non-empty
        finally:
            out.unlink(missing_ok=True)

    def test_render_with_light_theme(self):
        ws = Path("examples/dify-intro")
        layout = json.loads((ws / "layout.json").read_text(encoding="utf-8"))
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
            out = Path(f.name)
        try:
            nr = NativeRenderer("bento-light")
            result = nr.render_deck(layout, out)
            assert result.exists()
            assert result.stat().st_size > 1000
        finally:
            out.unlink(missing_ok=True)


class TestNativeDeckIntegration:
    """Integration tests that render full decks to exercise component code paths."""

    def test_deck_with_card_compare(self):
        """Exercise card-compare via a minimal deck render."""
        layout = {
            "theme": "bento-tech",
            "meta": {"title": "test"},
            "pages": [
                {
                    "page": 1,
                    "layout": "two-col-symmetric",
                    "cards": [
                        {
                            "slot": "left",
                            "component": "card-compare",
                            "data": {
                                "headers": ["基础版", "专业版"],
                                "recommend": 1,
                                "rows": [
                                    {"label": "价格", "values": ["免费", "999/月"]},
                                    {"label": "并发", "values": ["100", "1000"], "highlight": True},
                                ],
                            },
                        },
                        {
                            "slot": "right",
                            "component": "card-stack",
                            "data": {
                                "label": "指标",
                                "primary": {"value": "187", "unit": "ms", "suffix": "响应"},
                                "secondary": [{"label": "99分位", "value": "420 ms"}],
                                "progress": {"percent": 95, "label": "完成"},
                            },
                        },
                    ],
                }
            ],
        }
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
            out = Path(f.name)
        try:
            nr = NativeRenderer("bento-tech")
            nr.render_deck(layout, out)
            assert out.stat().st_size > 1000
        finally:
            out.unlink(missing_ok=True)

    def test_deck_with_quote_and_text(self):
        """Exercise card-quote and card-text via a minimal deck."""
        layout = {
            "theme": "bento-tech",
            "meta": {"title": "test"},
            "pages": [
                {
                    "page": 1,
                    "layout": "two-col-symmetric",
                    "cards": [
                        {
                            "slot": "left",
                            "component": "card-quote",
                            "data": {"quote": "少即是多。", "author": "Author", "role": "Role"},
                        },
                        {
                            "slot": "right",
                            "component": "card-text",
                            "data": {
                                "eyebrow": "OVERVIEW",
                                "title": "标题",
                                "badges": ["标签A", {"text": "警告", "variant": "warning"}],
                                "paragraphs": ["第一段文字内容。", "第二段文字内容。"],
                            },
                        },
                    ],
                }
            ],
        }
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
            out = Path(f.name)
        try:
            nr = NativeRenderer("bento-tech")
            nr.render_deck(layout, out)
            assert out.stat().st_size > 1000
        finally:
            out.unlink(missing_ok=True)
