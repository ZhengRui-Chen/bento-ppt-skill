# SVG → PPTX 内部细节（svgBlip 注入）

排查"为什么 PowerPoint 打开后是 PNG 不是矢量""为什么 SVG 显示不全"等问题时来读这里。

## 工作原理

`scripts/export.py` 的 `to_pptx` 用 python-pptx 创建空 deck，每页：

1. 用 `slide.shapes.add_picture(png_path, ...)` 全屏铺一张 PNG（来自 `shots/`）
2. 找到 `<a:blip>` 元素（位于 `<p:pic><p:blipFill><a:blip r:embed="rIdN"/>`）
3. 把对应 SVG 文件作为新的 `ImagePart` 加入 slide rels，得到 `rIdM`
4. 在 `<a:blip>` 下注入：

```xml
<a:blip r:embed="rIdN_to_PNG">
  <a:extLst>
    <a:ext uri="{96DAC541-7B7A-43D3-8B79-37D633B846F1}">
      <asvg:svgBlip
        xmlns:asvg="http://schemas.microsoft.com/office/drawing/2016/SVG/main"
        r:embed="rIdM_to_SVG"/>
    </a:ext>
  </a:extLst>
</a:blip>
```

## PowerPoint 行为

| 版本 | 行为 |
|---|---|
| **PowerPoint 365 / 2019+ Win/Mac** | 优先渲染 SVG 矢量。文字可点选 / 编辑 |
| **PowerPoint 2016** | 不识别 svgBlip，回落 PNG（清晰度受 PNG 分辨率限制）|
| **WPS** | 视版本，部分支持 SVG，多数回落 PNG |
| **Keynote** | 部分支持 SVG，有时把 SVG 当成图片渲染（不可编辑文字）|
| **Google Slides** | 不支持 svgBlip，回落 PNG |
| **LibreOffice Impress** | 支持 SVG（直接当图片插入）|

## 怎么验证生成的 pptx 是否注入成功

```bash
unzip -o deck.pptx -d /tmp/deck-check/
ls /tmp/deck-check/ppt/media/         # 应该有 image*.png + svg-deck-*.svg
grep -c svgBlip /tmp/deck-check/ppt/slides/slide*.xml   # 每个 slide 应有 1 个
```

每页应有：
- 1 个 `image*.png`（PNG fallback）
- 1 个 `svg-deck-*.svg`（矢量本体）
- slide xml 里 1 个 `<asvg:svgBlip>` 引用

## 关键 OOXML 命名空间

```
a    http://schemas.openxmlformats.org/drawingml/2006/main
r    http://schemas.openxmlformats.org/officeDocument/2006/relationships
asvg http://schemas.microsoft.com/office/drawing/2016/SVG/main
```

`asvg:svgBlip` 的扩展 URI（必须严格写）：
```
{96DAC541-7B7A-43D3-8B79-37D633B846F1}
```

## 常见问题

### 1. PowerPoint 打开看到的是 PNG，不能编辑文字
- 检查 PowerPoint 版本：必须 2019+ 或 365
- 用 unzip 验证 svgBlip 是否真的注入

### 2. SVG 显示但缺字 / 字体被替换
- SVG 里用了系统没有的字体（如 'PingFang SC' 在 Windows 端）
- 解决：themes/<name>/slide-base.svg.j2 里用 system font stack（已默认含 PingFang/Microsoft YaHei/SF Pro/Inter）

### 3. SVG 显示但元素位置错乱
- 多半是 viewBox 不一致。检查 `<svg viewBox="0 0 1280 720">` 必须存在
- 我们的模板默认带，自定义模板时别遗漏

### 4. python-pptx 报 `cannot identify image file`
- python-pptx 用 PIL 探测 image content type，不识别 SVG
- 我们的方案是手动构造 `ImagePart(partname, "image/svg+xml", package, blob)` 绕过 PIL 探测

### 5. 想加更多压缩？
- PNG fallback 来自 chrome headless 截图（默认 1280×720 24bpp，约 200-400 KB/页）
- 如要瘦身：用 `pngquant` 压一遍 `shots/*.png`，或在 `shoot.py` 里加 `--window-size=960,540` 出小一点的 PNG（矢量 SVG 仍然是高清显示，PNG 只是 fallback）

## 替代方案（暂未实现，留作参考）

- **cairosvg → EMF**：把 SVG 转 EMF 矢量格式，PowerPoint 全版本可编辑（但 EMF 在 Mac 端兼容性差，且中文字体问题严重）
- **直接生成 OOXML 形状**：跳过 SVG，把 layout 直接渲染成 pptx 原生 `<a:sp>` shapes（终极方案，但模板要重写一份 jinja2 → OOXML，工作量极大）
- **Aspose.Slides / Aspose Words**：商业库，质量好但收费

## 参考实现

- python-pptx 源码：`pptx.parts.image`
- Anthropic 官方 pptx skill（含 svgBlip 注入）：见 `Gabberflast/academic-pptx-skill`
