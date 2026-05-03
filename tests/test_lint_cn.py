"""Tests for Chinese typography lint."""

from lint_cn import check_text, is_chinese_dominant, lint_layout


def test_is_chinese_dominant_cn():
    assert is_chinese_dominant("这是一个中文句子，包含主要的汉字内容。") is True


def test_is_chinese_dominant_en():
    assert is_chinese_dominant("This is an English sentence.") is False


def test_is_chinese_dominant_mixed():
    # "Hi 你好" — 2 CJK out of 5 visible = 40%, meets 30% threshold = True
    assert is_chinese_dominant("Hi 你好") is True


def test_is_chinese_dominant_empty():
    assert is_chinese_dominant("") is False


def test_is_chinese_dominant_whitespace():
    assert is_chinese_dominant("   ") is False


class TestCheckText:
    def test_no_issues_clean_text(self):
        rules = {"no_ascii_punct": True, "no_cn_en_space": False}
        issues = check_text("这是一个干净的中文句子。", "test.path", rules)
        assert issues == []

    def test_ascii_punct_flag(self):
        rules = {"no_ascii_punct": True, "no_cn_en_space": False}
        issues = check_text("Dify，一个 AI 平台.", "test.path", rules)
        assert any("英文标点" in i for i in issues)

    def test_ascii_punct_disabled(self):
        rules = {"no_ascii_punct": False, "no_cn_en_space": False}
        issues = check_text("Dify，一个 AI 平台.", "test.path", rules)
        assert issues == []

    def test_cn_en_space_flag(self):
        rules = {"no_ascii_punct": False, "no_cn_en_space": True}
        issues = check_text("这是一个 AI 平台，支持 100 种模型。", "test.path", rules)
        assert any("多空格" in i for i in issues)

    def test_cn_en_space_default_off(self):
        rules = {"no_ascii_punct": False, "no_cn_en_space": False}
        issues = check_text("这是一个 AI 平台，支持 100 种模型。", "test.path", rules)
        assert issues == []

    def test_english_only_skipped(self):
        rules = {"no_ascii_punct": True, "no_cn_en_space": True}
        issues = check_text("This is an English sentence with comma, period.", "test.path", rules)
        # English-dominant text is skipped entirely
        assert issues == []


class TestLintLayout:
    def test_clean_layout(self):
        layout = {
            "pages": [
                {
                    "page": 1,
                    "cards": [
                        {
                            "slot": "main",
                            "data": {
                                "title": "这是一个干净的中文句子。",
                                "eyebrow": "PRODUCT INTRO",
                            },
                        }
                    ],
                }
            ]
        }
        issues = lint_layout(layout)
        assert issues == []

    def test_ascii_punct_in_layout(self):
        layout = {
            "pages": [
                {
                    "page": 1,
                    "cards": [{"slot": "main", "data": {"title": "一个 AI 平台."}}],
                }
            ]
        }
        issues = lint_layout(layout)
        assert any("英文标点" in i for i in issues)

    def test_lint_override_disables_ascii_punct(self):
        layout = {
            "lint": {"no_ascii_punct": False},
            "pages": [
                {
                    "page": 1,
                    "cards": [{"slot": "main", "data": {"title": "一个 AI 平台."}}],
                }
            ],
        }
        issues = lint_layout(layout)
        assert issues == []

    def test_lint_override_enables_cn_en_space(self):
        layout = {
            "lint": {"no_cn_en_space": True, "no_ascii_punct": False},
            "pages": [
                {
                    "page": 1,
                    "cards": [{"slot": "main", "data": {"title": "AI 平台 支持 100 种"}}],
                }
            ],
        }
        issues = lint_layout(layout)
        assert any("多空格" in i for i in issues)

    def test_empty_pages(self):
        layout = {"pages": []}
        issues = lint_layout(layout)
        assert issues == []

    def test_nested_data(self):
        layout = {
            "pages": [
                {
                    "page": 1,
                    "cards": [
                        {
                            "slot": "main",
                            "data": {
                                "items": [
                                    {"title": "正确的观点。", "desc": "描述文本。满足中文要求。"},
                                    {"title": "第二个观点。"},
                                ]
                            },
                        }
                    ],
                }
            ]
        }
        issues = lint_layout(layout)
        assert issues == []
