# LaTeX OCR Desktop App

一款基于深度学习的桌面应用，能够将数学公式图片自动识别并转换为 LaTeX 代码。使用copilot CLI+ superpowers搭建的，其实本身的算法还是pix2tex，基本没有改进，还有很多不足（UI垃圾），不过算是一键部署了，开心。

## 功能特性

- **图片识别** — 支持拖拽、文件选择、剪贴板粘贴（Ctrl+V）三种方式导入图片
- **多行智能分割** — 自动检测截图中的多行内容，逐行识别数学公式
- **实时预览** — 识别结果通过 MathJax 实时渲染为数学公式
- **一键复制** — 快速复制 LaTeX 代码到剪贴板
- **RGBA 支持** — 自动处理 PNG 透明背景等多种图片格式

## 技术栈

| 组件 | 技术 |
|------|------|
| OCR 引擎 | [pix2tex (LaTeX-OCR)](https://github.com/lukas-blecher/LaTeX-OCR) |
| 桌面窗口 | [pywebview](https://pywebview.flowrl.com/) |
| Web 后端 | [Flask](https://flask.palletsprojects.com/) |
| 公式渲染 | [MathJax](https://www.mathjax.org/) |
| 图像处理 | Pillow + NumPy |

## 项目结构

```
latex-ocr-app/
├── src/
│   ├── main.py            # 应用入口，Flask + pywebview 启动
│   ├── api.py             # JS ↔ Python 桥接 API
│   ├── ocr_engine.py      # OCR 引擎（行分割 + pix2tex 推理）
│   ├── templates/
│   │   └── index.html     # 前端页面
│   └── static/
│       ├── styles.css      # 样式
│       └── app.js          # 前端交互逻辑
├── test_ocr.py             # 单元测试
├── requirements.txt        # Python 依赖
└── README.md
```

## 安装

### 环境要求

- Python 3.10+
- pip

### 安装步骤

```bash
# 克隆项目
git clone https://github.com/chenwy1020/latex-ocr-app.git
cd latex-ocr-app

# 安装依赖
pip install -r requirements.txt
```

> **注意**：首次运行时会自动下载 pix2tex 模型权重（约 100MB），请确保网络畅通。

## 使用方法

```bash
python src/main.py
```

启动后会弹出桌面窗口，支持以下操作：

1. **拖拽图片** — 将公式截图直接拖入窗口
2. **选择文件** — 点击文件选择按钮，选取本地图片
3. **粘贴图片** — 复制图片后按 Ctrl+V，或点击 "Paste from Clipboard" 按钮
4. **复制结果** — 识别完成后点击 "Copy LaTeX" 复制代码

## 示例

输入公式截图后，输出：

```latex
\int_{B_{R}}\eta^{2}|\nabla u^{p/2}|^{2}dx\leqslant C\int_{B_{R}}u^{p}|\nabla\eta|^{2}dx
```

## 依赖

```
pywebview
pix2tex[gui]
Pillow
pyperclip
torch
torchvision
flask
```

## License

MIT
