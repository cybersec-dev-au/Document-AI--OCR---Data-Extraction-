import paddle
# Ensure oneDNN is disabled before ANY other imports in the backend process
paddle.set_flags({'FLAGS_use_mkldnn': False})

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import shutil
import os
import uuid
import pandas as pd
from typing import List, Dict

# Local imports
from ocr_engine import OCREngine
from data_extractor import DataExtractor

# Initialize App
app = FastAPI(title="Document AI API", description="AI-powered document processing")

# Enable CORS (for cross-origin requests from frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Mount frontend files (optional if using separate dev server)
# app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

# Initialize models (might be slow to load)
ocr_model = None
extractor = None
try:
    ocr_model = OCREngine()
    extractor = DataExtractor()
except Exception as e:
    print(f"Error initializing models: {e}")
    # Fallback/Error state might occur if paddleocr is not installed or 
    # environment is not ready.

@app.post("/process_document")
async def process_document(file: UploadFile = File(...)):
    """
    Receives an uploaded image/PDF, performs OCR, and extracts fields.
    """
    if ocr_model is None or extractor is None:
        raise HTTPException(status_code=503, detail="AI models not loaded. Please check the backend connection.")

    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image or PDF.")
    
    # Save file temporarily
    file_id = str(uuid.uuid4())
    ext = file.filename.split('.')[-1]
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # 1. OCR Step
        ocr_result = ocr_model.extract_text_with_boxes(file_path)
        text_lines = [item["text"] for item in ocr_result]
        
        # 2. Field Extraction Step
        extracted_data = extractor.extract_all(text_lines)
        
        # 3. Clean up (optional: keep for reference/logs, but for this demo delete)
        # os.remove(file_path) 
        
        return JSONResponse(content={
            "id": file_id,
            "filename": file.filename,
            "data": extracted_data,
            "ocr_raw": ocr_result
        })
        
    except Exception as e:
        import traceback
        error_msg = f"Error processing document: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": "Processing failed", "details": str(e)})

@app.get("/export/{format}")
async def export_data(data: str, format: str):
    """
    Query parameter 'data' should be a JSON-encoded string of extracted values.
    Returns a CSV or Excel file.
    """
    import json
    try:
        data_list = json.loads(data)
        df = pd.DataFrame(data_list)
        
        export_file = f"export_{uuid.uuid4()}.{format}"
        if format == "csv":
            df.to_csv(export_file, index=False)
        elif format == "xlsx":
            df.to_excel(export_file, index=False)
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
        # Cleanup should happen after download 
        # (This is a simplified approach)
        return FileResponse(export_file, filename=f"extracted_data.{format}")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Export failed", "details": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
