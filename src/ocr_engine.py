import numpy as np
from PIL import Image as PILImage


class OcrEngine:
    def __init__(self):
        self.model = None

    def _ensure_model(self):
        if self.model is None:
            from pix2tex.cli import LatexOCR
            self.model = LatexOCR()

    def _to_rgb(self, image):
        """Convert any image mode to RGB with white background."""
        if image.mode == 'RGBA':
            bg = PILImage.new('RGB', image.size, (255, 255, 255))
            bg.paste(image, mask=image.split()[3])
            return bg
        if image.mode != 'RGB':
            return image.convert('RGB')
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

    def _looks_valid(self, latex):
        """Heuristic: check if OCR output looks like valid LaTeX formula."""
        if not latex or latex.startswith('Error'):
            return False
        # Reject if too many repeated characters (sign of garbage output)
        if '\\!\\!' * 5 in latex:
            return False
        if '\\Psi' * 3 in latex:
            return False
        # Should contain typical math commands or symbols
        math_indicators = ['\\int', '\\frac', '\\sum', '\\prod', '\\lim',
                           '\\nabla', '\\partial', '\\sqrt', '\\leq', '\\geq',
                           '\\alpha', '\\beta', '\\gamma', '\\delta', '\\theta',
                           '\\infty', '\\cdot', '\\times', '\\pm', '\\mp',
                           '^', '_', '=', '+', '-']
        has_math = any(ind in latex for ind in math_indicators)
        # Reject very long outputs with high repetition density
        if len(latex) > 300:
            return False
        return has_math

    def predict(self, image):
        """Run OCR on an image. Handles multi-line screenshots automatically."""
        try:
            self._ensure_model()
            image = self._to_rgb(image)

            # First try the whole image
            result = self.model(image)
            if self._looks_valid(result):
                return result

            # If whole-image result looks bad, try line splitting
            gray = np.array(image.convert('L'))
            lines = self._find_content_lines(gray)

            if len(lines) <= 1:
                # Single line or no lines detected, return whatever we got
                return result

            # Process each line, collect valid results
            valid_results = []
            for top, bottom in lines:
                line_img = self._crop_line(image, top, bottom)
                line_result = self.model(line_img)
                if self._looks_valid(line_result):
                    valid_results.append(line_result)

            if valid_results:
                return '\n'.join(valid_results)

            # Fallback: return the whole-image result
            return result
        except Exception as e:
            return f"Error: {str(e)}"
