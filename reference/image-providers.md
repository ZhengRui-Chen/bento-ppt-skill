# 阶段 4.5：图片来源（fetch）

写完 `layout.json` 之后、`scaffold` 之前的可选阶段。把 `card-image` 的需求规格转成本地文件。

## 三种填法（AI 自己选）

### A. 直接给本地路径（最稳）

```json
{ "component": "card-image", "data": {
  "src": "/Users/me/Desktop/screenshot.png",
  "alt": "产品截图"
}}
```

- fetch 会跳过这种
- 适合：用户已经有图、自己截的图、工作目录里有素材

### B. 直接给 URL（最常用，AI 主导）

```json
{ "component": "card-image", "data": {
  "src": "https://example.com/some-photo.jpg",
  "alt": "产品截图"
}}
```

- AI 用自带的 WebSearch 找好图（或读用户给的链接），把 URL 写进 `src`
- fetch 会用 `url_download` provider 下到 `<ws>/assets/<hash>.jpg`，回填本地路径
- 不依赖任何 API key
- **适合：截图、产品图、品牌素材、有明确出处的图**

### C. 给 source 规格让 provider 处理

```json
{ "component": "card-image", "data": {
  "alt": "AI 思考的人脑示意图",
  "source": {
    "kind": "generate",
    "query": "minimalist human brain made of neural network nodes, dark background, glowing purple accent",
    "style": "illustration",
    "aspect": "16:9",
    "prefer": ["nanobanana"]
  }
}}
```

- fetch 按 `prefer` 顺序找能处理 `kind` 且就绪的 provider
- **适合：抽象意象图、概念示意、找不到现成的场景**
- 可选 `kind`：`search`（关键词搜图）/ `generate`（AI 生图）

## 选哪种？AI 决策框架

| 图的性质 | 推荐 |
|---|---|
| 用户提供的素材、确定的产品截图 | A. 本地路径 |
| 真实场景照片（办公室、会议、设备）| B. URL（搜真图）|
| 公司 logo、产品 UI、品牌资产 | B. URL（找官方）|
| 抽象概念（"AI 大脑"、"全球协作"）| C. generate（生成）|
| 装饰性背景图、风格化插画 | C. generate（生成）|
| 数据图表 | 不用 card-image，用 chart-bar 或在 layout 里插占位 |

## fetch 失败怎么办

`ppt fetch` **永远不会因为下载失败阻塞主流程**：

- URL 下载失败 / provider 没就绪 / 抛异常 → 该图 src 留空 → 渲染时显示**虚线占位框 + alt 文本**
- 整个 deck 还是能 scaffold / shoot / export 出来
- 用户可以事后手动给 `data.src` 填本地路径再重渲单页

## 当前可用的 provider

| name | kinds | 启用条件 |
|---|---|---|
| `url_download` | url | 默认启用，无需配置 |
| `nanobanana` | generate | env `GEMINI_API_KEY`（需 `pip install google-generativeai`）|
| `unsplash` | search | env `UNSPLASH_ACCESS_KEY`（stdlib `urllib`，无额外依赖）|

加新 provider 见 [scripts/providers/README.md](../scripts/providers/README.md)。

## 工作流位置

```
1. needs       → brief.md
2. research    → research/
3. outline     → outline.json
4. planning    → layout.json
4.5. fetch     → assets/  (← 在这里)
5. design      → slides/*.svg
6. review      → shots/, deck.html
7. export      → deck.pptx
```

fetch 是**可选**的：
- 如果 layout.json 里 card-image 都用本地路径或 URL，**必须**先跑 fetch
- 如果只用占位图（demo / 未确定素材），**可以**跳过
