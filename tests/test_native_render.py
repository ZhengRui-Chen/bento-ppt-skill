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
