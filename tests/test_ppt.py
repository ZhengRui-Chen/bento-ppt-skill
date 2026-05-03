"""Tests for CLI workspace management."""

import tempfile
from pathlib import Path

import pytest
from ppt import is_workspace, require_workspace, slugify


class TestSlugify:
    def test_basic(self):
        assert slugify("Dify 企业介绍") == "Dify-企业介绍"

    def test_special_chars(self):
        result = slugify("foo/bar:baz*test")
        assert "/" not in result
        assert ":" not in result

    def test_spaces(self):
        assert slugify("a  b   c") == "a-b-c"

    def test_empty(self):
        assert slugify("") == "untitled"


class TestWorkspace:
    def test_is_workspace_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / ".layout").write_text("test")
            assert is_workspace(ws)

    def test_is_workspace_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            assert not is_workspace(Path(tmp))

    def test_require_workspace_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp).resolve()
            (ws / ".layout").write_text("test")
            result = require_workspace(str(ws))
            assert result == ws

    def test_require_workspace_invalid(self):
        with tempfile.TemporaryDirectory() as tmp, pytest.raises(SystemExit):
            require_workspace(str(Path(tmp)))
