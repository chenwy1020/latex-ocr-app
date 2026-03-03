import base64
import io
from PIL import Image, ImageGrab
from src.ocr_engine import OcrEngine

class Api:
    def __init__(self):
        self.engine = OcrEngine()

    def process_image_data(self, base64_str):
        try:
            if ',' in base64_str:
                base64_str = base64_str.split(',')[1]
            
            image_data = base64.b64decode(base64_str)
            image = Image.open(io.BytesIO(image_data))
            return self.engine.predict(image)
        except Exception as e:
            return f"Error processing image: {str(e)}"

    def get_clipboard_image(self):
        try:
            image = ImageGrab.grabclipboard()
            if isinstance(image, Image.Image):
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                return img_str
            else:
                return "Error: No image found in clipboard"
        except Exception as e:
            return f"Error getting clipboard image: {str(e)}"
