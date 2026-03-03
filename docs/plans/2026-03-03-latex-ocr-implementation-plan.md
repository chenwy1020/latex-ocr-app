# LaTeX OCR App Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Build a desktop app that converts images to LaTeX using `pywebview` and `pix2tex`.

**Architecture:** Python backend with `pix2tex` for OCR, exposed via `pywebview` to a vanilla JS/HTML frontend.

**Tech Stack:** Python 3.12, pywebview, pix2tex, Pillow, pyperclip, HTML/CSS/JS.

---

### Task 1: Project Setup and Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `README.md`

**Step 1: Create requirements.txt**
```text
pywebview
pix2tex[gui]
Pillow
pyperclip
torch
torchvision
```

**Step 2: Install dependencies**
Run: `pip install -r requirements.txt`

**Step 3: Create README**
Write basic usage instructions.

**Step 4: Commit**
```bash
git add requirements.txt README.md
git commit -m "setup: project dependencies"
```

### Task 2: Backend - OCR Engine

**Files:**
- Create: `src/ocr_engine.py`

**Step 1: Implement OcrEngine class**
Create a class that loads `LatexOCR` from `pix2tex.cli` on demand (lazy loading).
Implement `predict(image_path_or_pil)` method.

**Step 2: Test OCR Engine (Manual)**
Create a small script `test_ocr.py` to run `OcrEngine` on a sample image.

**Step 3: Commit**
```bash
git add src/ocr_engine.py
git commit -m "feat: implement OCR engine wrapper"
```

### Task 3: Backend - API and Main Window

**Files:**
- Create: `src/api.py`
- Create: `src/main.py`

**Step 1: Implement API class in `src/api.py`**
Methods:
- `process_image_data(base64_str)`: Decodes base64 -> PIL -> OcrEngine -> LaTeX.
- `get_clipboard_image()`: Uses `pyperclip` (or `PIL.ImageGrab`) to get clipboard image, converts to base64 for frontend.

**Step 2: Implement Main in `src/main.py`**
- Initialize `Api` object.
- Create `pywebview.create_window`.
- `pywebview.start`.

**Step 3: Commit**
```bash
git add src/api.py src/main.py
git commit -m "feat: backend api and main window"
```

### Task 4: Frontend - UI Structure

**Files:**
- Create: `src/templates/index.html`
- Create: `src/static/styles.css`

**Step 1: Create HTML structure**
Two panels: Input (Drag/Drop, Paste button) and Output (Textarea, MathJax view).
Import `styles.css` and `app.js`.
Import MathJax CDN.

**Step 2: Create CSS**
Basic styling for a clean look.

**Step 3: Commit**
```bash
git add src/templates/index.html src/static/styles.css
git commit -m "feat: frontend ui structure"
```

### Task 5: Frontend - Logic and Integration

**Files:**
- Create: `src/static/app.js`

**Step 1: Implement Paste/Drop Logic**
Handle `paste` events and drag-and-drop.
Convert files/blobs to base64.

**Step 2: Implement API Calls**
Call `window.pywebview.api.process_image_data`.
Handle `window.pywebview.api.get_clipboard_image`.

**Step 3: Update UI**
Display loading state.
Update textarea with result.
Call `MathJax.typeset()` to render preview.

**Step 4: Commit**
```bash
git add src/static/app.js
git commit -m "feat: frontend logic and integration"
```
