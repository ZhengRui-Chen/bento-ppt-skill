# Image Provider 开发指南

`ppt fetch` 阶段调 provider 把 `card-image` 的需求规格转成本地文件。
provider 之间解耦：加一个新的就是新一个 .py 文件，无需改其他代码。

## 文件结构

```
scripts/providers/
├── __init__.py        # auto-discovery，自动 import 同目录下所有 .py
├── base.py            # ImageProvider 抽象 + register / find_provider
├── url_download.py    # 内置：处理 src=URL（不需 API key）
├── nanobanana.py      # stub：Gemini 3 Image 生图
├── unsplash.py        # stub：Unsplash 搜图
└── README.md          # 本文档
```

## 接口契约

```python
class ImageProvider(ABC):
    name: str                              # 唯一名字
    kinds: list[str]                       # 'url' / 'search' / 'generate'

    def is_available(self) -> bool:        # 依赖 / API key 是否就绪
        return True
    def can_handle(self, source) -> bool:  # 能否处理这个 source 规格
        ...
    def fetch(self, source, out_dir) -> Path | None:
        # 下载/生成图片，返回本地路径；失败返回 None（不抛异常）
        ...
```

文件末尾必须调 `register(<provider实例>())`。

## 增加新 provider 的步骤

以接入 Pexels 为例：

1. 在 `providers/pexels.py` 写：

```python
import os, urllib.request, json, hashlib
from pathlib import Path
from .base import ImageProvider, register

class PexelsProvider(ImageProvider):
    name = "pexels"
    kinds = ["search"]

    def is_available(self):
        return bool(os.environ.get("PEXELS_API_KEY"))

    def can_handle(self, source):
        return source.get("kind") == "search"

    def fetch(self, source, out_dir):
        query = source.get("query")
        if not query:
            return None
        req = urllib.request.Request(
            f"https://api.pexels.com/v1/search?query={query}&per_page=1",
            headers={"Authorization": os.environ["PEXELS_API_KEY"]},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
            url = data["photos"][0]["src"]["large"]
            # 复用 url_download 风格下载即可
            ...
            return out_path
        except Exception as e:
            print(f"  [warn] pexels: {e}")
            return None

register(PexelsProvider())
```

2. 设环境变量 `PEXELS_API_KEY=xxx`
3. `ppt fetch` 自动找到（`__init__.py` 的 auto-discovery）

## source 规格的 schema

`layout.json` 里 `card-image` 的 data 字段：

```json
{
  "alt": "图片描述（必填，占位时显示 + 传给 svg image 的 alt）",
  "caption": "图下方说明（可选）",
  "src": "/abs/local/path.png  或  https://...  或  留空",
  "source": {
    "kind": "search" | "generate",
    "query": "AI workflow editor screenshot",
    "style": "screenshot | illustration | photo | abstract | diagram",
    "aspect": "16:9 | 4:3 | 1:1",
    "prefer": ["unsplash", "pexels"]
  }
}
```

`fetch` 阶段的优先级：

1. **src 已是本地路径且存在** → 跳过
2. **src 是 http(s) URL** → 用 `url_download` provider 下载
3. **src 缺失但有 source** → 按 `source.prefer` 顺序找能处理的可用 provider
4. **都没有** → 留空，渲染时显示占位框（不阻塞流程）

## prefer 顺序

`source.prefer` 是 provider 名字列表，按顺序尝试。例：
```json
"prefer": ["unsplash", "pexels"]
```
表示"先试 Unsplash，没装/失败再试 Pexels"。没列出的 provider 排在 999，最后才用。

## 失败处理

- provider.fetch() 返回 None → 当前 card-image 留空 src，渲染时占位框
- provider 抛异常会被 fetch.py 捕获并记录，不影响其他 card-image 的处理
- 整个 fetch 命令永远不会因为下载失败而中断主流程
