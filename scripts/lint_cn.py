"""中文版式硬约束检查（layout.json 渲染前）。

两条规则（命中阻断渲染）：
1. no_ascii_punct（默认开）：中文段里禁用 ASCII 标点 , . : ; ! ?
   - 错 "Dify，一个 AI 平台."  对 "Dify，一个 AI 平台。"
2. no_cn_en_space（默认关）：中英文/数字之间不加空格
   - 错 "1 米 93"  对 "1米93"
   - 默认关：PPT 场景"AI 应用"这种带空格的写法是主流英文排版习惯
   - 公众号/短文案场景应在 layout.json 顶层覆盖：{"lint": {"no_cn_en_space": true}}

启发式：一个文本片段里中文字符 ≥ 30% → 视为"中文段"启用规则；英文段跳过。
扫描 layout.json 里 pages[].cards[].data 下所有字符串字段（递归）。
"""

from __future__ import annotations

import json
import re
from pathlib import Path

SPACE_BETWEEN_CN_EN_RE = re.compile(
    r"([\u4e00-\u9fff]) +([A-Za-z0-9])|([A-Za-z0-9]) +([\u4e00-\u9fff])"
)
ASCII_PUNCT_IN_CN_RE = re.compile(r"[\u4e00-\u9fff][,.:;!?](?:[^A-Za-z0-9]|$)")

CN_RATIO_THRESHOLD = 0.3

DEFAULTS = {
    "no_ascii_punct": True,
    "no_cn_en_space": False,
}


def is_chinese_dominant(s: str) -> bool:
    if not s:
        return False
    cn = sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")
    visible = sum(1 for ch in s if not ch.isspace())
    if visible == 0:
        return False
    return cn / visible >= CN_RATIO_THRESHOLD


def check_text(s: str, path: str, rules: dict) -> list[str]:
    issues = []
    if not isinstance(s, str) or not s.strip():
        return issues
    if not is_chinese_dominant(s):
        return issues

    if rules.get("no_cn_en_space"):
        m = SPACE_BETWEEN_CN_EN_RE.search(s)
        if m:
            snippet = s[max(0, m.start() - 6): m.end() + 6]
            issues.append(f"{path}: 中英/数字间多空格 → ...{snippet}...")

    if rules.get("no_ascii_punct"):
        m2 = ASCII_PUNCT_IN_CN_RE.search(s)
        if m2:
            snippet = s[max(0, m2.start() - 6): m2.end() + 6]
            issues.append(f"{path}: 中文段用了英文标点 → ...{snippet}...（应改用 ，。：；！？）")

    return issues


def walk(node, path: str, rules: dict) -> list[str]:
    issues = []
    if isinstance(node, dict):
        for k, v in node.items():
            issues.extend(walk(v, f"{path}.{k}" if path else k, rules))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            issues.extend(walk(v, f"{path}[{i}]", rules))
    elif isinstance(node, str):
        issues.extend(check_text(node, path, rules))
    return issues


def lint_layout(layout: dict) -> list[str]:
    """对整个 layout.json 做检查。返回所有违规（空 = 通过）。

    规则可在 layout.json 顶层覆盖：
      { "lint": { "no_cn_en_space": true, "no_ascii_punct": false } }
    """
    rules = dict(DEFAULTS)
    rules.update(layout.get("lint", {}) or {})

    issues = []
    for page in layout.get("pages", []):
        page_no = page.get("page", "?")
        for ci, card in enumerate(page.get("cards", [])):
            slot = card.get("slot", "?")
            issues.extend(walk(card.get("data", {}), f"page {page_no} card[{ci}] ({slot}).data", rules))
    return issues


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: lint_cn.py <layout.json>")
        sys.exit(2)
    layout = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    issues = lint_layout(layout)
    if not issues:
        print("[lint] 通过")
        sys.exit(0)
    print(f"[lint] {len(issues)} 处违规：")
    for it in issues:
        print(f"  - {it}")
    sys.exit(1)
