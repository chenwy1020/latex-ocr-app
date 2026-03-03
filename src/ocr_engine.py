import os
import ssl
import numpy as np
from PIL import Image as PILImage


class OcrEngine:
    def __init__(self):
        self.model = None
        self.processor = None

    def _ensure_model(self):
        if self.model is None:
            # Handle SSL certificate issues (common in corporate/education networks)
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
            except Exception:
                pass
            os.environ.setdefault('HF_HUB_DISABLE_SYMLINKS_WARNING', '1')

            from texify.model.model import load_model
            from texify.model.processor import load_processor
            self.model = load_model()
            self.processor = load_processor()

    def _to_rgb(self, image):
        """Convert any image mode to RGB with white background."""
        if image.mode == 'RGBA':
            bg = PILImage.new('RGB', image.size, (255, 255, 255))
            bg.paste(image, mask=image.split()[3])
            return bg
        if image.mode != 'RGB':
            return image.convert('RGB')
        return image

    def _preprocess(self, image):
        """Enhanced preprocessing for better recognition."""
        image = self._to_rgb(image)

        # Convert to grayscale for analysis
        gray = np.array(image.convert('L'))

        # Auto-invert if background is dark
        if np.mean(gray) < 128:
            gray = 255 - gray

        # Crop to content area (remove excess whitespace)
        coords = np.argwhere(gray < 200)
        if coords.size > 0:
            y0, x0 = coords.min(axis=0)
            y1, x1 = coords.max(axis=0)
            pad = 20
            y0 = max(0, y0 - pad)
            x0 = max(0, x0 - pad)
            y1 = min(gray.shape[0], y1 + pad)
            x1 = min(gray.shape[1], x1 + pad)
            image = image.crop((x0, y0, x1, y1))

        return image

    def _find_content_lines(self, gray_arr, min_gap=5):
        """Detect horizontal content lines in a grayscale image array."""
        row_means = gray_arr.mean(axis=1)
        content_rows = np.where(row_means < 240)[0]
        if len(content_rows) == 0:
            return []

        gaps = np.diff(content_rows)
        line_breaks = np.where(gaps > min_gap)[0]

        starts = [content_rows[0]]
        ends = []
        for b in line_breaks:
            ends.append(content_rows[b])
            starts.append(content_rows[b + 1])
        ends.append(content_rows[-1])
        return list(zip(starts, ends))

    def _crop_line(self, image, top, bottom, pad_v=20, pad_h=10):
        """Crop a single line from the image with padding."""
        gray = np.array(image.convert('L'))
        row_slice = gray[top:bottom + 1, :]
        col_mask = row_slice.min(axis=0) < 200
        cols = np.where(col_mask)[0]
        left = max(0, cols[0] - pad_h) if len(cols) > 0 else 0
        right = min(image.width, cols[-1] + pad_h) if len(cols) > 0 else image.width

        crop_top = max(0, top - pad_v)
        crop_bottom = min(image.height, bottom + pad_v)
        line_img = image.crop((left, crop_top, right, crop_bottom))

        # Scale up small lines for better recognition
        if line_img.height < 40:
            scale = max(2, 50 // line_img.height)
            line_img = line_img.resize(
                (line_img.width * scale, line_img.height * scale),
                PILImage.LANCZOS
            )
        return line_img

    def _infer(self, image):
        """Run Texify inference on a single image."""
        from texify.inference import batch_inference
        results = batch_inference([image], self.model, self.processor, temperature=0.0)
        if results and results[0]:
            text = results[0].strip()
            # Remove all common LaTeX delimiters
            for prefix, suffix in [('$$', '$$'), ('$', '$'), ('\\[', '\\]'), ('\\(', '\\)')]:
                if text.startswith(prefix) and text.endswith(suffix) and len(text) > len(prefix) + len(suffix):
                    text = text[len(prefix):-len(suffix)].strip()
            return text
        return ""

    def _looks_valid(self, latex):
        """Heuristic: check if OCR output looks like valid LaTeX formula."""
        if not latex or latex.startswith('Error'):
            return False
        if len(latex) < 2:
            return False
        # Reject very long outputs (likely garbage)
        if len(latex) > 500:
            return False
        # Reject known garbage patterns
        garbage_patterns = ['\\includegraphics', '\\mbox{\\rm', 
                           '\\otimes\\phi' * 3, '\\mbox' * 5]
        for gp in garbage_patterns:
            if gp in latex:
                return False
        # Reject mixed/broken delimiters (e.g. "$\frac{..}$\(\frac{..}")
        if '\\(' in latex or '\\)' in latex:
            return False
        # Reject if still wrapped in $ delimiters (means _infer didn't clean it)
        if latex.startswith('$') or latex.endswith('$'):
            return False
        # Reject high repetition (e.g. \phi\otimes repeated many times)
        if len(latex) > 100:
            for token in ['\\otimes', '\\mbox', '\\phi', '\\rm']:
                if latex.count(token) > 10:
                    return False
        # Should contain typical math tokens
        math_indicators = ['\\int', '\\frac', '\\sum', '\\prod', '\\lim',
                           '\\nabla', '\\partial', '\\sqrt', '\\leq', '\\geq',
                           '\\alpha', '\\beta', '\\gamma', '\\delta', '\\theta',
                           '\\infty', '\\cdot', '\\times', '\\pm', '\\mp',
                           '^', '_', '=', '+', '-', '(', ')']
        return any(ind in latex for ind in math_indicators)

    def predict(self, image):
        """Run OCR on an image. Handles multi-line screenshots automatically."""
        try:
            self._ensure_model()
            image = self._preprocess(image)

            # Check for multiple content lines first
            gray = np.array(image.convert('L'))
            lines = self._find_content_lines(gray)

            if len(lines) > 1:
                # Multi-line image: process each line separately
                valid_results = []
                for top, bottom in lines:
                    line_img = self._crop_line(image, top, bottom)
                    line_result = self._infer(line_img)
                    if self._looks_valid(line_result):
                        valid_results.append(line_result)
                if valid_results:
                    return '\n'.join(valid_results)

            # Single line or no valid line results: try whole image
            result = self._infer(image)
            if result and result.strip():
                return result.strip()

            return "识别失败，请尝试更清晰的图片"
        except Exception as e:
            return f"Error: {str(e)}"
