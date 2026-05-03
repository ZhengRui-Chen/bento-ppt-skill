"""SVG → 截图 + 多页翻页 HTML 预览。

策略：用 chrome / chromium headless 二进制（不引入 playwright，减少依赖）：
- 自动探测可用 chrome：env CHROME_BIN > /Applications/Google Chrome.app > /Applications/Chromium.app > which chrome/chromium
- 给每个 SVG 出一张同名 PNG → shots/
- 把 SVG 列表生成 deck.html：左右键 / 空格 / 点击翻页 + 底部缩略图栏 + Esc 退全屏

为什么不用 playwright：
- chrome headless 命令足够（生成静态截图，不需要交互/等待网络等高级能力）
- 少一个 pip 依赖（playwright 装包 + browser 下载约 200MB）
- 用户机器上多半已经有 Chrome
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def find_chrome() -> str:
    """探测可用的 chrome/chromium 二进制路径。"""
    env = os.environ.get("CHROME_BIN")
    if env and Path(env).exists():
        return env
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
        path = shutil.which(name)
        if path:
            return path
    raise SystemExit(
        "[shoot] 找不到 Chrome/Chromium。\n"
        "  请安装 Google Chrome（推荐）或 Chromium，或设环境变量 CHROME_BIN=<binary path>"
    )


def shoot_svg(chrome: str, svg_path: Path, out_path: Path, viewport=(1280, 720)) -> None:
    """用 chrome headless 把 svg 渲染成 png。

    chrome --headless --screenshot 会生成截图但**不主动退出**（坑），
    所以我们 Popen 启动后轮询截图文件是否生成，到了就 kill 进程。
    每次给独立 user-data-dir 避免多次串行调用相互锁住。
    """
    import tempfile
    import time
    if out_path.exists():
        out_path.unlink()
    with tempfile.TemporaryDirectory(prefix="ppt-shoot-") as tmpdir:
        cmd = [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={tmpdir}",
            f"--window-size={viewport[0]},{viewport[1]}",
            f"--screenshot={out_path}",
            f"file://{svg_path.resolve()}",
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # 轮询 + kill：截图出现且大小稳定（两次相同）就 kill
        deadline = time.time() + 15
        last_size = -1
        stable_count = 0
        while time.time() < deadline:
            time.sleep(0.3)
            if proc.poll() is not None:
                break  # chrome 自己退出了
            if out_path.exists():
                sz = out_path.stat().st_size
                if sz > 1024 and sz == last_size:
                    stable_count += 1
                    if stable_count >= 2:
                        proc.terminate()
                        try:
                            proc.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                        break
                last_size = sz
        else:
            proc.kill()
    if not out_path.exists() or out_path.stat().st_size < 1024:
        raise SystemExit(f"[shoot] chrome 截图失败: {svg_path.name}")


_DECK_HTML_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · ppt-agent preview</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: #07091a; color: #e6edf3;
               font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif; }
  body { display: flex; flex-direction: column; height: 100vh; overflow: hidden; }

  .stage { flex: 1; display: flex; align-items: center; justify-content: center; padding: 24px; min-height: 0; }
  .frame {
    aspect-ratio: 16 / 9;
    width: 100%;
    max-width: calc((100vh - 200px) * 16 / 9);
    max-height: calc(100vh - 200px);
    background: #000;
    box-shadow: 0 20px 60px rgba(0,0,0,.5);
    border-radius: 4px;
    overflow: hidden;
    position: relative;
  }
  .frame > svg, .frame > object { width: 100%; height: 100%; display: block; }

  .topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 20px; background: rgba(255,255,255,.03); border-bottom: 1px solid rgba(255,255,255,.06);
    font-size: 13px; color: #8d96a0;
  }
  .topbar .title { color: #fff; font-weight: 600; font-size: 14px; }
  .topbar .meta { font-family: ui-monospace, Menlo, monospace; }
  .topbar button {
    background: rgba(255,255,255,.06); color: #fff; border: 1px solid rgba(255,255,255,.12);
    padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; margin-left: 8px;
  }
  .topbar button:hover { background: rgba(255,255,255,.12); }

  .strip {
    flex-shrink: 0;
    height: 110px;
    display: flex; gap: 8px; padding: 12px 16px;
    overflow-x: auto; overflow-y: hidden;
    background: rgba(255,255,255,.02); border-top: 1px solid rgba(255,255,255,.06);
  }
  .thumb {
    flex-shrink: 0; height: 86px; aspect-ratio: 16/9; cursor: pointer;
    border: 2px solid transparent; border-radius: 4px; overflow: hidden;
    background: #000; position: relative;
  }
  .thumb img { width: 100%; height: 100%; display: block; object-fit: cover; }
  .thumb.active { border-color: #7c5cff; box-shadow: 0 0 0 2px rgba(124,92,255,.3); }
  .thumb-num {
    position: absolute; bottom: 2px; right: 4px;
    font-size: 10px; color: #fff; background: rgba(0,0,0,.6); padding: 1px 4px; border-radius: 2px;
    font-family: ui-monospace, Menlo, monospace;
  }

  .nav {
    position: absolute; top: 50%; transform: translateY(-50%);
    width: 48px; height: 48px; border-radius: 50%; background: rgba(0,0,0,.4);
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-size: 24px; cursor: pointer; user-select: none;
    opacity: 0; transition: opacity .2s;
  }
  .stage:hover .nav { opacity: 1; }
  .nav.prev { left: 32px; } .nav.next { right: 32px; }
  .nav:hover { background: rgba(0,0,0,.7); }
</style>
</head>
<body>
  <div class="topbar">
    <div class="title">{title}</div>
    <div>
      <span class="meta" id="counter">01 / __TOTAL__</span>
      <button onclick="document.documentElement.requestFullscreen()">全屏</button>
    </div>
  </div>
  <div class="stage">
    <div class="nav prev" onclick="go(-1)">‹</div>
    <div class="frame" id="frame"></div>
    <div class="nav next" onclick="go(1)">›</div>
  </div>
  <div class="strip" id="strip"></div>

<script>
const SLIDES = __SLIDES_JSON__;
let cur = 0;
const frame = document.getElementById('frame');
const strip = document.getElementById('strip');
const counter = document.getElementById('counter');

function pad2(n) { return n < 10 ? '0' + n : '' + n; }

function render() {
  frame.innerHTML = '<object type="image/svg+xml" data="' + SLIDES[cur].svg + '"></object>';
  counter.textContent = pad2(cur + 1) + ' / ' + pad2(SLIDES.length);
  document.querySelectorAll('.thumb').forEach((t, i) => {
    t.classList.toggle('active', i === cur);
    if (i === cur) t.scrollIntoView({behavior:'smooth', block:'nearest', inline:'center'});
  });
}

function go(delta) {
  cur = Math.max(0, Math.min(SLIDES.length - 1, cur + delta));
  render();
}

SLIDES.forEach((s, i) => {
  const t = document.createElement('div');
  t.className = 'thumb';
  t.innerHTML = '<img src="' + s.thumb + '"><span class="thumb-num">' + pad2(i+1) + '</span>';
  t.onclick = () => { cur = i; render(); };
  strip.appendChild(t);
});

render();

document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { go(1); e.preventDefault(); }
  else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { go(-1); e.preventDefault(); }
  else if (e.key === 'Home') { cur = 0; render(); }
  else if (e.key === 'End') { cur = SLIDES.length - 1; render(); }
});
</script>
</body>
</html>
"""


def shoot_all(ws: Path) -> dict:
    slides_dir = ws / "slides"
    if not slides_dir.is_dir():
        raise SystemExit(f"[shoot] {slides_dir} 不存在；先跑 ppt scaffold")
    svgs = sorted(slides_dir.glob("*.svg"))
    if not svgs:
        raise SystemExit(f"[shoot] {slides_dir} 没有 .svg 文件")

    chrome = find_chrome()
    shots_dir = ws / "shots"
    shots_dir.mkdir(exist_ok=True)
    # 清理旧截图
    for old in shots_dir.glob("*.png"):
        old.unlink()

    print(f"[shoot] 用 chrome 截图 {len(svgs)} 张...", flush=True)
    slides_meta = []
    for svg in svgs:
        png = shots_dir / (svg.stem + ".png")
        shoot_svg(chrome, svg, png)
        slides_meta.append({
            "svg": f"slides/{svg.name}",
            "thumb": f"shots/{png.name}",
            "name": svg.stem,
        })
        print(f"  ✓ {svg.name}", flush=True)

    # 写 deck.html（用相对路径引用 slides/ 和 shots/）
    deck_html = (
        _DECK_HTML_TEMPLATE
        .replace("{title}", _read_title(ws))
        .replace("__TOTAL__", f"{len(svgs):02d}")
        .replace("__SLIDES_JSON__", json.dumps(slides_meta, ensure_ascii=False))
    )
    deck_path = ws / "deck.html"
    deck_path.write_text(deck_html, encoding="utf-8")

    # macOS 自动打开
    if sys.platform == "darwin":
        subprocess.Popen(["open", str(deck_path)])

    return {"shots": len(svgs), "deck_html": str(deck_path)}


def _read_title(ws: Path) -> str:
    layout = ws / "layout.json"
    if layout.exists():
        try:
            data = json.loads(layout.read_text(encoding="utf-8"))
            return data.get("meta", {}).get("title") or ws.name
        except Exception:
            pass
    return ws.name
