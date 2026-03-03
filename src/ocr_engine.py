class OcrEngine:
    def __init__(self):
        self.model = None

    def predict(self, image):
        try:
            if self.model is None:
                # Lazy load to avoid heavy import at startup or if unused
                from pix2tex.cli import LatexOCR
                self.model = LatexOCR()
            
            # The model is callable, returns the latex string
            return self.model(image)
        except Exception as e:
            # Handle exceptions gracefully as requested
            # Returning an error string is a common pattern for UI apps 
            # so the user sees what went wrong instead of crashing.
            return f"Error: {str(e)}"
