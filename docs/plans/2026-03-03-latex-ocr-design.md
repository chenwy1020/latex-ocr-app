# LaTeX OCR App Design Document

## 1. Overview
A desktop application that converts images containing mathematical formulas into LaTeX code. The application uses a modern hybrid architecture with a Python backend for heavy lifting (OCR) and a web-based frontend for a clean, responsive user interface.

## 2. Architecture
The application is built using `pywebview`, which allows running a web-based UI inside a native window, powered by a Python backend.

### Tech Stack
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla).
- **Backend**: Python 3.12+.
- **OCR Engine**: `pix2tex` (LaTeX-OCR), a local transformer-based model.
- **Window Management**: `pywebview` (wraps Edge WebView2 on Windows).
- **Clipboard Management**: `pyperclip`.
- **Image Processing**: `Pillow` (PIL).

## 3. Components

### 3.1 Backend (`src/`)
- **`main.py`**:
  - Initializes the `pywebview` window.
  - Configures the API bridge.
  - Handles application lifecycle.
- **`ocr_engine.py`**:
  - Encapsulates the `pix2tex` model loading (lazy loading to speed up startup).
  - Provides a `predict(image)` method that accepts a PIL Image and returns a LaTeX string.
  - Handles model download on first run.
- **`api.py`**:
  - Defines the `Api` class exposed to JavaScript.
  - Methods:
    - `process_image_data(base64_string)`: Decodes image, runs OCR, returns result.
    - `get_clipboard_image()`: Grabs image from system clipboard.
    - `copy_text(text)`: Copies text to clipboard.

### 3.2 Frontend (`src/templates/`, `src/static/`)
- **`index.html`**:
  - Layout with two main columns/rows:
    1. **Input**: Drag & drop zone, "Paste from Clipboard" button, file input.
    2. **Output**: Text area for LaTeX code, "Copy" button, and a MathJax rendering area for preview.
- **`styles.css`**:
  - Modern, clean styling (likely using a CSS variable system for easy theming).
- **`app.js`**:
  - Handles user interactions (paste, drag & drop).
  - Calls Python API via `window.pywebview.api`.
  - Updates the DOM with results.
  - Configures MathJax for typesetting.

## 4. Data Flow
1. **Input**: User pastes an image (Ctrl+V) or selects a file.
2. **Frontend**: Converts image to Base64 (if file) or requests clipboard content from Backend.
3. **Frontend**: Sends Base64 image data to Backend via `api.process_image_data`.
4. **Backend**:
   - Decodes Base64 to PIL Image.
   - Passes Image to `ocr_engine`.
   - `ocr_engine` runs inference (Pix2Tex model).
   - Returns LaTeX string.
5. **Frontend**:
   - Receives LaTeX string.
   - Displays it in the text area.
   - Renders the formula using MathJax.

## 5. Deployment & Constraints
- **Model Size**: The `pix2tex` model is ~150MB. It will be downloaded on the first run.
- **Performance**: CPU inference is acceptable for single images (~1-3s). CUDA is supported if available but not required.
- **Internet**: Required only for the first run to download model weights.
