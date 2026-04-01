import paddle
paddle.set_flags({'FLAGS_use_mkldnn': False})
print("Importing PaddleOCR...")
from paddleocr import PaddleOCR
print("Initializing PaddleOCR...")
ocr = PaddleOCR(use_angle_cls=True, lang='en', device='cpu')
print("PaddleOCR initialized.")
