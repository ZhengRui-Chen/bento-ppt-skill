"""URL 直接下载 provider。

用途：处理 card-image 里 src 字段是 http(s) URL 的情况——AI 用 WebSearch
找到好图后把 URL 直接写到 layout.json 的 src，fetch 时下载到本地。

不依赖任何 API key，纯 stdlib。
"""

from __future__ import annotations

import hashlib
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .base import ImageProvider, register


_VALID_EXTS = {"png", "jpg", "jpeg", "gif", "webp", "svg", "bmp"}


def _ext_from_url(url: str) -> str:
    tail = url.rsplit(".", 1)[-1].split("?")[0].split("#")[0].lower()
    return tail if tail in _VALID_EXTS else "png"


class UrlDownloadProvider(ImageProvider):
    name = "url_download"
    kinds = ["url"]

    def can_handle(self, source: dict[str, Any]) -> bool:
        url = source.get("url") or source.get("src")
        return isinstance(url, str) and url.startswith(("http://", "https://"))

    def fetch(self, source: dict[str, Any], out_dir: Path) -> Path | None:
        url = source.get("url") or source.get("src")
        if not url:
            return None
        out_dir.mkdir(parents=True, exist_ok=True)
        h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
        ext = _ext_from_url(url)
        out_path = out_dir / f"{h}.{ext}"
        if out_path.exists() and out_path.stat().st_size > 0:
            return out_path

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; ppt-agent/1.0)"},
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            if len(data) < 200:
                print(f"  [warn] 下载 {url} 内容过小 ({len(data)} bytes)，可能是占位/错误页")
                return None
            out_path.write_bytes(data)
            return out_path
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            print(f"  [warn] 下载失败 {url[:60]}...: {e}")
            return None


register(UrlDownloadProvider())
