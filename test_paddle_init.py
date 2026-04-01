print("Importing PaddleOCR...")
from paddleocr import PaddleOCR
print("Initializing PaddleOCR...")
# Note: paddleocr 3.4.0 might have different flags
ocr = PaddleOCR(use_angle_cls=True, lang='en', device='cpu')
print("PaddleOCR initialized successfully.")
