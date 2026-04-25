# 添加新主题

`themes/` 目录下每个子目录就是一个主题包。复制 `themes/bento-tech/` 改名即可起步。

## 必须实现的文件

```
themes/<your-theme>/
├── manifest.json          # 设计 token + layout 槽位元数据
├── slide-base.svg.j2      # 1280×720 容器（背景、defs、字体、页脚）
├── layouts/_base.svg.j2   # 通用 layout 模板（数据驱动，按 manifest.layouts.*.slots 渲染）
└── components/<name>.svg.j2  # 各 component 的渲染模板
```

可选：每种 layout 写专属模板覆盖通用模板。

## manifest.json 必须字段

```json
{
  "name": "<theme-name>",
  "version": "1.0.0",
  "description": "...",

  "viewBox": { "width": 1280, "height": 720 },

  "fonts": {
    "sans": "...",
    "mono": "...",
    "display": "..."
  },

  "type_scale": {
    "eyebrow": 16,
    "h1": 60, "h2": 44, "h3": 30, "h4": 22,
    "body": 18, "small": 14,
    "stat_huge": 110, "stat_unit": 28
  },

  "colors": {
    "bg_start": "#...", "bg_end": "#...",
    "card_fill": "#...", "card_fill_opacity": 0.06,
    "card_stroke": "#...", "card_stroke_opacity": 0.12,
    "text_primary": "#...", "text_secondary": "#...", "text_muted": "#...",
    "accent_primary": "#...", "accent_secondary": "#...",
    "accent_success": "#...", "accent_warning": "#..."
  },

  "spacing": {
    "page_padding": 56,
    "footer_height": 30,
    "card_padding": 40,
    "card_gap": 20,
    "card_radius": 20,
    "card_stroke_width": 1
  },

  "layouts": {
    "<layout-name>": {
      "card_count": N,
      "description": "...",
      "slots": {
        "<slot-name>": { "x": 56, "y": 56, "w": 1168, "h": 578 }
      }
    }
  }
}
```

## 关键约定

1. **viewBox 固定 1280×720**——所有 slot 坐标都基于这个画布
2. **slots 坐标含义**：x/y 是卡片**外框左上角**在画布的位置；w/h 是卡片**外框尺寸**（含 card_padding，组件可用尺寸 = w - card_padding * 2）
3. **slot 名字**只能从这套基础集合里选（让 layout.json 跨主题可用）：
   - 1 槽：`main`
   - 2 槽：`left, right` 或 `main, side`
   - 3 槽：`left, middle, right`
   - 4-5 槽：`main + top/bottom/right_top/right_bottom` 或 `hero/col1/col2/col3` 或 `tl/tr/bl/br`

## components 的字号自适应（推荐做法）

每个 component 模板拿到 `slot_w` / `slot_h` 变量。相对小的 slot 应该缩小字号：

```jinja
{%- set H = slot_h or 560 -%}
{%- set W = slot_w or 600 -%}
{# 小卡片用更小的 stat-huge #}
{%- set huge_size = theme.type_scale.stat_huge if W > 400 else (W * 0.22) | int -%}
<text font-size="{{ huge_size }}" ...>{{ d.value }}</text>
```

## 测试新主题

```bash
# 准备一个最小 layout.json，theme 字段指向你的新主题
echo '{"theme":"<your-theme>","meta":{"title":"Test"},"pages":[{"page":1,"name":"test","layout":"single-focus","cards":[{"slot":"main","component":"card-hero","data":{"title":"Hello"}}]}]}' > /tmp/test-layout/layout.json

# 在 /tmp/test-layout/ 加 .layout 标识
touch /tmp/test-layout/.layout

# 渲染 + 截图看效果
PPT_DECKS_DIR=/tmp ppt scaffold /tmp/test-layout
PPT_DECKS_DIR=/tmp ppt shoot /tmp/test-layout
open /tmp/test-layout/deck.html
```

## 注意

- 不要往 SKILL.md 里硬编码"主题列表"——`ppt scaffold` 会自动扫描 `themes/` 目录
- 如果你的主题用了非系统字体，请在 `slide-base.svg.j2` 的 defs 里用 `@font-face` 引入并 base64 嵌入字体文件，否则 PowerPoint 端会回落到默认字体
- 主题包不要互相 import（每个主题自包含），便于复制分享
