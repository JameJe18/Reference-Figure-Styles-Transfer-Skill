# Reference figure styles transfer skill

一个用于提取科学图表中可迁移的视觉语法，并将其应用于现有绘图项目的 Codex 技能。

该工作流程在迁移以下内容时会保持科学内容不变：

- 构图与面板层级；
- 调色板角色，以及填充与描边的表现方式；
- 字体特征与尺度；
- 间距、面板间隙与面板几何结构；
- 标记、线条、箭头、图例与注释策略。

它面向两项相互关联的任务：

1. 从论文 PDF 或图表集合中学习一种风格，并保存可复用的
   `figure_style_profile.json`。
2. 通过编辑原始源文件，重新设定现有 Matplotlib/R/绘图输出的样式；
   保留先前的输出，并审计科学内容不变量。

## 安装

仓库根目录即技能目录。请将其克隆到 Codex 技能目录：

```text
<CODEX_HOME>/skills/reference-figure-styles-transfer/
```

在 Windows PowerShell 中：

```powershell
git clone <REPOSITORY_URL> "$env:USERPROFILE\.codex\skills\reference-figure-styles-transfer"
```

如果改为从本地压缩包安装，复制技能文件夹时应排除 `.git` 目录。

显式调用该技能：

```text
Use $reference-figure-styles-transfer to learn the style from paper.pdf and save a validated profile.
```

```text
Use $reference-figure-styles-transfer to apply the saved profile to my existing plotting code without changing any data or statistical wording.
```

## 包含的资源

```text
reference-figure-styles-transfer/
|-- SKILL.md
|-- agents/openai.yaml
|-- references/
|   |-- audit.md
|   |-- case-study.md
|   |-- code-transfer.md
|   |-- style-extraction.md
|   `-- style-profile.schema.json
|-- scripts/
|   |-- audit_rendered_figures.py
|   |-- build_contact_sheet.py
|   |-- extract_pdf_figures.py
|   `-- validate_style_profile.py
|-- examples/example_style_profile.json
|-- tests/
|-- requirements.txt
`-- .github/workflows/ci.yml
```

本仓库不包含论文 PDF、第三方图表图像、用户项目图表或机密数据。

## 快速开始

### 1. 提取候选图

```bash
python scripts/extract_pdf_figures.py paper.pdf -o style_work
```

如果 Poppler 不可用，请安装 Poppler，或改用 PyMuPDF 备用方案：

```bash
python -m pip install -r requirements.txt
```

### 2. 构建并验证风格配置

请参阅 [SKILL.md](SKILL.md) 和
[references/style-extraction.md](references/style-extraction.md)。示例配置位于：

```text
examples/example_style_profile.json
```

按如下方式验证：

```bash
python scripts/validate_style_profile.py \
  examples/example_style_profile.json
```

该模板有意不包含本地参考图像，因此验证时请不要使用 `--check-assets`。
对于包含已提取资源的实际配置：

```bash
python scripts/validate_style_profile.py \
  figure_style_profile.json --check-assets
```

### 3. 检查图表

```bash
python scripts/build_contact_sheet.py extracted-figures \
  -o figure_contact_sheet.jpg
```

### 4. 应用风格

请遵循 [references/code-transfer.md](references/code-transfer.md)。该技能的默认策略是
编辑现有绘图源文件，保持科学内容不变，并在替换已验收输出之前先渲染一个变体。

### 5. 审计

```bash
python scripts/audit_rendered_figures.py \
  output/variant_style1 --profile figure_style_profile.json
```

随后完成 [references/audit.md](references/audit.md) 中的视觉检查与科学检查。

## 设计原则

- 风格按图表家族分别学习，不会在互不相关的图表之间取平均。
- 在仅调整样式的处理中，科学数值、标签、坐标轴范围、拓扑结构和面板含义
  保持不变。
- 仅凭栅格图像证据时，不会断言准确字体或矢量线宽。
- 醒目颜色集中在视觉焦点标记上；大面积区域使用克制的浅色调。
- 颜色会与形状、位置、直接标注或线型配合使用。
- 默认会修改现有绘图文件，不会额外增加一层装饰性的后处理。
- 保留已验收的输出，以供前后对比检查。

## 依赖项

- Python 3.10+
- Pillow
- 用于内嵌图像备用方案的 PyMuPDF
- 可选的 Poppler 可执行文件：`pdfinfo`、`pdfimages`、`pdftoppm`、`pdftotext`

只有目标项目会使用 Matplotlib；验证配置文件不需要它。

## 开发

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/validate_style_profile.py examples/example_style_profile.json
```

## 仓库状态

此文件夹既可视为独立的 GitHub 仓库，也可作为可直接安装的 Codex 技能。
若计划公开发布，可根据需要添加许可证；许可证类型有意留由仓库所有者选择。
