"""Unsplash image search provider.

启用步骤:
  1. 在 https://unsplash.com/developers 注册应用获得 Access Key
  2. 设置 UNSPLASH_ACCESS_KEY=<your-key>

未启用时 is_available() 返回 False，fetch 阶段自动跳过。
"""

from __future__ import annotations

import hashlib
import os
import urllib.parse
import urllib.request
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
        query = source.get("query", "")
        if not query:
            return None
        slug = hashlib.md5(query.encode()).hexdigest()[:12]
        access_key = os.environ.get("UNSPLASH_ACCESS_KEY", "")

        try:
            import json as _json

            search_url = f"https://api.unsplash.com/search/photos?query={urllib.parse.quote(query)}&per_page=1"
            req = urllib.request.Request(search_url, headers={"Authorization": f"Client-ID {access_key}"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = _json.loads(resp.read())

            results = data.get("results") or []
            if not results:
                print(f"  [unsplash] no results for: {query[:60]}...")
                return None

            img_url = results[0]["urls"]["regular"]
            img_req = urllib.request.Request(img_url, headers={"User-Agent": "bento-ppt-skill/1.0"})
            with urllib.request.urlopen(img_req, timeout=30) as img_resp:
                raw = img_resp.read()

            ext = ".jpg"
            content_type = img_resp.headers.get("Content-Type", "")
            if "png" in content_type:
                ext = ".png"

            out = out_dir / f"{slug}{ext}"
            out.write_bytes(raw)
            print(f"  [unsplash] downloaded → {out.name}")
            return out

        except Exception as e:
            print(f"  [unsplash] search failed: {e}")
            return None


register(UnsplashProvider())
