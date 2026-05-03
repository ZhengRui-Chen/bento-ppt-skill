"""nanobanana (Gemini 3 Image / Nano Banana Pro) provider — STUB

启用步骤：
  1. 设置环境变量 GEMINI_API_KEY=<your-key>
  2. pip install google-generativeai
  3. 实现 fetch() 里的 TODO（调 Gemini Image API → 写文件）

当前是 stub：is_available() 在 GEMINI_API_KEY 缺失时返回 False，
fetch 阶段会跳过此 provider 并尝试下一个，主流程不受影响。

参考：
  - https://ai.google.dev/gemini-api/docs/image-generation
  - sandun 原文用的是 Gemini 3 Flash 出图
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .base import ImageProvider, register


class NanoBananaProvider(ImageProvider):
    name = "nanobanana"
    kinds = ["generate"]

    def is_available(self) -> bool:
        return bool(os.environ.get("GEMINI_API_KEY"))

    def can_handle(self, source: dict[str, Any]) -> bool:
        return source.get("kind") == "generate"

    def fetch(self, source: dict[str, Any], out_dir: Path) -> Path | None:
        # TODO: 接入 Gemini 3 Image API
        #   query = source.get("query")
        #   style = source.get("style")  # screenshot / illustration / photo / abstract
        #   aspect = source.get("aspect", "16:9")
        #   ... 调 API ... 写到 out_dir/<hash>.png ... return path
        print("  [nanobanana] stub 未实现，请按 nanobanana.py 顶部说明接 API")
        return None


register(NanoBananaProvider())
