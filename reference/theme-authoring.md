# 添加新主题

> 完整的延展规范（含 Layout / Component / Theme）见 **[extension-guide.md](extension-guide.md)**。  
> 本文是快速版摘要。

## 主题继承机制

`themes/bento-tech/` 是**模板基础库**。所有派生主题只需提供 `manifest.json`，jinja2 模板（slide-base、layouts、components）自动 fallback 到 bento-tech。

```
themes/
├── bento-tech/        ← 基础库（不要删模板文件）
│   ├── manifest.json
│   ├── slide-base.svg.j2
│   ├── layouts/
│   └── components/
└── bento-light/       ← 派生主题，只需 manifest.json
    └── manifest.json
```

如需覆盖某个模板（例如给新主题加特殊背景效果），在派生主题目录放同名 `.svg.j2` 即可——render.py 优先用派生主题目录里的文件。

## 新建一个主题（三步）

```bash
# 1. 建目录
mkdir themes/<your-style>

# 2. 复制底板（深色用 bento-tech，浅色用 bento-light）
cp themes/bento-light/manifest.json themes/<your-style>/manifest.json

# 3. 改 name / description / colors / effects
```

## manifest.json 必填字段

见 [extension-guide.md § 四、新增 Theme](extension-guide.md)。

关键字段速查：

| 字段 | 说明 |
|---|---|
| `colors.bg_start / bg_end` | 背景渐变颜色 |
| `colors.card_fill / card_fill_opacity` | 卡片填充色和透明度 |
| `colors.text_primary / secondary / muted` | 文字三级颜色 |
| `colors.accent_primary / secondary` | 主题强调色（eyebrow / badge / 高亮） |
| `effects.bg_texture_color` | 网格/点状纹理色（深色主题 `#ffffff`，浅色主题 `#1a1a2e`） |
| `effects.bg_spot_opacity` | 装饰光斑强度（深色 0.35-0.50，浅色 0.08-0.15） |

## 测试新主题

```bash
python3 -c "
from scripts.render import render_all
from pathlib import Path
render_all(Path('examples/dify-intro'), theme='<your-style>')
print('SVG OK')
"

python3 -c "
from scripts.native_render import render_pptx
from pathlib import Path
render_pptx(Path('examples/dify-intro'), theme_name='<your-style>', out_path=Path('/tmp/test.pptx'))
print('PPTX OK')
"

# 截图看效果
python3 scripts/ppt.py shoot examples/dify-intro
open examples/dify-intro/deck.html
```

## 注意

- 不要删除 `bento-tech/` 里的模板文件——所有派生主题都依赖它
- 如果你的主题需要自定义字体，在派生主题目录放一个 `slide-base.svg.j2`，`@font-face` 里 base64 嵌入字体文件
- layout.json 里 `"theme": "<your-style>"` 即可切换
