import paddle
# Set global flags BEFORE other imports to ensure they take effect
paddle.set_flags({'FLAGS_use_mkldnn': False})

from paddleocr import PaddleOCR
import cv2
import numpy as np
import os

class OCREngine:
    def __init__(self, lang='en'):
        # Initialize PaddleOCR with correct 2025+ argument names
        self.ocr = PaddleOCR(
            use_angle_cls=True, 
            lang=lang, 
            device='cpu', 
            enable_mkldnn=False
        )

    def extract_text_with_boxes(self, image_path):
        """
        Extracts text from an image and returns a list of dictionaries with text and coordinates.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")

        result = self.ocr.ocr(image_path)

        extracted_data = []
        if result:
            for res in result:
                # PaddleX v5 / PaddleOCR 2025 result format
                if isinstance(res, dict) and 'rec_texts' in res:
                    texts = res['rec_texts']
                    scores = res.get('rec_scores', [1.0] * len(texts))
                    boxes = res.get('dt_polys', [])
                    
                    for i, (text, score) in enumerate(zip(texts, scores)):
                        box = boxes[i].tolist() if i < len(boxes) and hasattr(boxes[i], 'tolist') else [[0,0],[0,0],[0,0],[0,0]]
                        extracted_data.append({
                            "text": text,
                            "box": box,
                            "confidence": float(score)
                        })
                # Legacy / List-based format
                elif isinstance(res, list):
                    for line in res:
                        try:
                            if isinstance(line, (list, tuple)) and len(line) >= 2:
                                box = line[0].tolist() if hasattr(line[0], 'tolist') else line[0]
                                text_info = line[1]
                                if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                    text, score = text_info[0], text_info[1]
                                else:
                                    text, score = str(text_info), 1.0
                            else:
                                box = [[0,0],[0,0],[0,0],[0,0]]
                                text, score = str(line), 1.0
                                
                            extracted_data.append({
                                "text": text,
                                "box": box,
                                "confidence": float(score)
                            })
                        except Exception as e:
                            print(f"⚠️ Warning: Parsing line {line} failed: {e}")
                else:
                    print(f"⚠️ Warning: Unknown result format: {type(res)}")
        
        return extracted_data

    def get_full_text(self, image_path):
        """
        Returns all extracted text as a single string.
        """
        data = self.extract_text_with_boxes(image_path)
        return "\n".join([item["text"] for item in data])
