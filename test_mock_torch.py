import sys
from types import ModuleType

# Mock torch to prevent broken DLL load
mock_torch = ModuleType("torch")
sys.modules["torch"] = mock_torch
print("Torch mocked.")

print("Importing PaddleOCR...")
from paddleocr import PaddleOCR
print("PaddleOCR imported.")
ocr = PaddleOCR(use_angle_cls=True, lang='en', device='cpu')
print("PaddleOCR initialized.")
