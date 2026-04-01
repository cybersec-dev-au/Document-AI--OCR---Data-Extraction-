import os
import sys

# Move to backend to import
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from ocr_engine import OCREngine

def test_ocr():
    try:
        print("🔍 Initializing OCR Engine...")
        engine = OCREngine()
        
        # Look for the uploaded file
        uploads_dir = 'uploads'
        files = os.listdir(uploads_dir)
        if not files:
            print("❌ No files found in uploads directory.")
            return

        test_file = os.path.join(uploads_dir, files[0])
        print(f"📄 Testing on file: {test_file}")
        
        results = engine.extract_text_with_boxes(test_file)
        print(f"✅ OCR results returned. Result type: {type(results)}")
        if results:
             print(f"Sample data: {results[0]}")

    except Exception as e:
        print(f"❌ OCR FAILED with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ocr()
