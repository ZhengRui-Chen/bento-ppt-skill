"""ppt fetch：扫 layout.json 里所有 card-image，按 src/source 拉资源到工作区。

四种处理路径：
  1. src 已是本地路径且文件存在 → 跳过
  2. src 是 http(s):// URL → 调 url_download provider 下载
  3. src 缺失但有 source 字段 → 按 source.prefer 找可用 provider
  4. 都没有 → 留空 src（渲染时占位框，主流程不阻塞）

下载到 <ws>/assets/<hash>.<ext>，回填 layout.json 的 src 为本地绝对路径。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from providers import find_provider, get_providers  # noqa: E402


def fetch_all(ws: Path) -> dict:
    layout_path = ws / "layout.json"
    if not layout_path.exists():
        raise SystemExit(
            f"[fetch] {layout_path} 不存在；先把 layout.json 写好再 fetch"
        )
    layout = json.loads(layout_path.read_text(encoding="utf-8"))

    assets_dir = ws / "assets"
    assets_dir.mkdir(exist_ok=True)

    all_providers = get_providers()
    available = [p for p in all_providers if p.is_available()]
    print(
        f"[fetch] 已注册 {len(all_providers)} 个 provider, "
        f"{len(available)} 个就绪: {[p.name for p in available]}"
    )
    if len(available) < len(all_providers):
        unavail = [p.name for p in all_providers if not p.is_available()]
        print(f"        未启用: {unavail}（缺 API key 或依赖；详见 providers/README.md）")

    fetched = 0
    skipped_local = 0
    no_provider = 0
    failed = 0

    for page in layout.get("pages", []):
        page_no = page.get("page", "?")
        for ci, card in enumerate(page.get("cards", [])):
            if card.get("component") != "card-image":
                continue
            data = card.setdefault("data", {})
            src = data.get("src", "") or ""
            tag = f"page {page_no} card[{ci}] ({card.get('slot', '?')})"

            # 1) src 已是本地路径且存在
            if src and not src.startswith(("http://", "https://")):
                if Path(src).expanduser().exists():
                    skipped_local += 1
                    continue
                print(f"  [warn] {tag}: src={src} 不存在，重置为占位")
                data["src"] = ""
                src = ""

            # 2) src 是 URL → 走 url_download
            if src.startswith(("http://", "https://")):
                provider = find_provider({"url": src})
                if not provider:
                    print(f"  [skip] {tag}: 没有可用的 url_download provider（不应发生）")
                    no_provider += 1
                    continue
                out = provider.fetch({"url": src}, assets_dir)
                if out:
                    data["src"] = str(out.resolve())
                    print(f"  [ok]   {tag}: {provider.name} → {out.name}")
                    fetched += 1
                else:
                    data["src"] = ""  # 下载失败 → 走占位
                    failed += 1
                continue

            # 3) 没 src，看 source 规格
            source = data.get("source") or {}
            if not source:
                continue

            provider = find_provider(source)
            if not provider:
                kind = source.get("kind", "?")
                print(
                    f"  [skip] {tag}: 没有可用 provider 处理 kind={kind}; "
                    f"prefer={source.get('prefer') or []}"
                )
                no_provider += 1
                continue

            out = provider.fetch(source, assets_dir)
            if out:
                data["src"] = str(out.resolve())
                print(f"  [ok]   {tag}: {provider.name} ({source.get('kind')}) → {out.name}")
                fetched += 1
            else:
                failed += 1

    layout_path.write_text(
        json.dumps(layout, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "fetched": fetched,
        "skipped_local": skipped_local,
        "no_provider": no_provider,
        "failed": failed,
        "assets_dir": str(assets_dir),
    }
