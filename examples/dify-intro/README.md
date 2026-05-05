# dify-intro 端到端样本

这是一份完整跑通的示范 deck，覆盖 6 种 Bento 布局 + 6 种 component 中的大部分。

## 文件

- `layout.json` — 8 页内容定义（输入）
- `slides/` — 渲染产物（每页一个 SVG）
- `shots/` — 每页截图 PNG（chrome headless）
- `deck.html` — 浏览器翻页预览（左右键 / 空格 / 缩略图栏）
- `deck.pptx` — PowerPoint 2019+ 可编辑矢量演示文稿

## 怎么从这个 example 自己复现一份

```bash
# 1. 起新工作区（会复制一份 layout.json 模板）
ppt new "Dify 企业介绍 Demo"
# → ~/ppt-decks/<date>-dify-企业介绍-demo/

# 2. 把本目录的 layout.json 拷过去（替代 outline 阶段的产出）
cp ~/.claude/skills/ppt-agent/examples/dify-intro/layout.json ~/ppt-decks/<date>-dify-企业介绍-demo/

# 3. 渲染 / 截图 / 导出
ppt scaffold ~/ppt-decks/<date>-dify-企业介绍-demo/
ppt shoot    ~/ppt-decks/<date>-dify-企业介绍-demo/
ppt export   ~/ppt-decks/<date>-dify-企业介绍-demo/ --format pptx
```

## 8 页 layout 速查

| # | name | layout | 内容 |
|---|---|---|---|
| 1 | cover | single-focus | 封面 hero |
| 2 | two-col-symmetric-demo | two-col-symmetric | 两个统计数字对比 |
| 3 | two-col-asymmetric-demo | two-col-asymmetric | 主文 + 侧边要点列表 |
| 4 | three-col-demo | three-col | 三个并列指标 |
| 5 | major-minor-demo | major-minor | 中央引言 + 4 个支撑数据 |
| 6 | hero-top-demo | hero-top | 顶部论点 + 三个分层论据 |
| 7 | mixed-grid-demo | mixed-grid | 柱状图 + 数字 + 图占位 + 文字 |
| 8 | end | single-focus | 末页 thank you |

## V1 → V2 已修复

- ✅ 第 5 页 stat 截断：窄卡 `word_wrap=True` + unit 换行 y 偏移
- ✅ 第 5 页 quote 断行：每行容量 ×1.1 余量防 CJK 词组拆分
- ✅ 第 7 页 card-text 溢出：文本区 64px 保底高度
- ✅ 渐变背景 + 字体嵌入 + 3 主题
