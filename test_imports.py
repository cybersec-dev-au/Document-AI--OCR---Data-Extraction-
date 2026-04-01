import sys
print(f"Python version: {sys.version}")

try:
    print("Testing paddle import...")
    import paddle
    print("Paddle imported successfully.")
except Exception as e:
    print(f"Failed to import paddle: {e}")

try:
    print("Testing paddleocr import...")
    from paddleocr import PaddleOCR
    print("PaddleOCR imported successfully.")
except Exception as e:
    print(f"Failed to import paddleocr: {e}")

try:
    print("Testing torch import (to see if it exists)...")
    import torch
    print("Torch imported successfully.")
except Exception as e:
    print(f"Failed to import torch (optional): {e}")

try:
    print("Testing fastapi import...")
    import fastapi
    print("FastAPI imported successfully.")
except Exception as e:
    print(f"Failed to import fastapi: {e}")
