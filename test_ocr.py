import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from PIL import Image

# Add src to path so we can import ocr_engine
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from ocr_engine import OcrEngine

class TestOcrEngine(unittest.TestCase):
    def setUp(self):
        # Mock pix2tex module to avoid import errors due to environment issues
        self.mock_pix2tex = MagicMock()
        self.mock_latex_ocr = MagicMock()
        self.mock_pix2tex.cli.LatexOCR = self.mock_latex_ocr
        
        self.modules_patcher = patch.dict('sys.modules', {
            'pix2tex': self.mock_pix2tex,
            'pix2tex.cli': self.mock_pix2tex.cli
        })
        self.modules_patcher.start()
        
        # Now we can safely import or patch without triggering real import
        # Patch where we expect it to be used
        self.patcher = patch('pix2tex.cli.LatexOCR', new=self.mock_latex_ocr)
        self.MockLatexOCR = self.patcher.start()
        self.mock_model_instance = self.MockLatexOCR.return_value
        # Setup mock behavior
        self.mock_model_instance.return_value = "e=mc^2" 
        
    def tearDown(self):
        self.patcher.stop()
        self.modules_patcher.stop()

    def test_lazy_loading(self):
        """Test that LatexOCR is not initialized until needed or at least handled correctly."""
        # Note: The requirement says "lazy-load ... inside __init__ OR on first predict call".
        # If it's lazy loaded in __init__, it means it's loaded when instance is created.
        # If it's lazy loaded on predict, it's loaded when predict is called.
        # We'll check that initializing OcrEngine works without error.
        engine = OcrEngine()
        self.assertIsInstance(engine, OcrEngine)

    def test_predict_returns_latex(self):
        """Test that predict method returns expected LaTeX string."""
        engine = OcrEngine()
        
        # Create a dummy image
        dummy_image = Image.new('RGB', (100, 30), color='white')
        
        # Configure mock to return specific string when called
        # The LatexOCR model is usually called as model(img)
        self.mock_model_instance.side_effect = ["e=mc^2"]
        
        result = engine.predict(dummy_image)
        
        self.assertEqual(result, "e=mc^2")
        self.mock_model_instance.assert_called_with(dummy_image)

    def test_predict_handles_exception(self):
        """Test that predict method handles exceptions gracefully."""
        engine = OcrEngine()
        dummy_image = Image.new('RGB', (100, 30), color='white')
        
        # Make the model raise an exception
        # We need to ensure self.mock_model_instance is set correctly
        # In setUp, we set it via self.MockLatexOCR.return_value
        # Since OcrEngine calls LatexOCR(), it gets the return_value which is mock_model_instance
        # Then it calls that instance. So we set side_effect on the instance.
        
        # However, we need to make sure side_effect is set correctly.
        # self.mock_model_instance is the mock OBJECT that is returned by LatexOCR() constructor.
        # So when we call self.model(image), we are calling this object.
        self.mock_model_instance.side_effect = Exception("Model error")
        
        # We expect NO exception raised, but an error string returned
        result = engine.predict(dummy_image)
        
        self.assertTrue(isinstance(result, str))
        self.assertTrue("error" in result.lower(), f"Expected error message, got: {result}")


if __name__ == '__main__':
    unittest.main()
