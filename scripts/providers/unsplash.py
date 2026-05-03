"""Unsplash 网络搜图 provider — STUB

启用步骤：
  1. 在 https://unsplash.com/developers 注册应用，拿 Access Key
  2. 设置环境变量 UNSPLASH_ACCESS_KEY=<your-key>
  3. 实现 fetch() 里的 TODO（GET /search/photos → 取首张 → 下载）

当前是 stub。

参考：
  - https://unsplash.com/documentation#search-photos
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .base import ImageProvider, register


class UnsplashProvider(ImageProvider):
    name = "unsplash"
    kinds = ["search"]

    def is_available(self) -> bool:
        return bool(os.environ.get("UNSPLASH_ACCESS_KEY"))

    def can_handle(self, source: dict[str, Any]) -> bool:
        return source.get("kind") == "search"

    def fetch(self, source: dict[str, Any], out_dir: Path) -> Path | None:
        # TODO: 调 Unsplash API
        #   query = source.get("query")
        #   resp = GET https://api.unsplash.com/search/photos?query={query}&per_page=1
        #     headers Authorization: Client-ID <key>
        #   first = resp.json()['results'][0]
        #   url = first['urls']['regular']
        #   下载 url → out_dir/<hash>.jpg → return path
        print("  [unsplash] stub 未实现，请按 unsplash.py 顶部说明接 API")
        return None


register(UnsplashProvider())
