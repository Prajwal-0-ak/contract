from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from app.utils.document_processor import DocumentProcessor
from fastapi.responses import JSONResponse

import os

router = APIRouter()
document_processor = DocumentProcessor()

@router.post("/")
async def upload_files(
    file: UploadFile = File(...),
    pdfType: str = Form(...)
):
    """
    This endpoint accepts a file and a PDF type, saves the file to the server, processes it,
    and returns the extracted data.
    Parameters:
        file (UploadFile): The file to be uploaded.
        pdfType (str): The type of PDF to process.
    Returns:
        JSONResponse: A response containing the extracted data from the file.
    Raises:
        HTTPException: If an error occurs during file upload or processing.
    """
    """
    Endpoint to upload one or multiple files.
    """
    try:
        results = []
        content = await file.read()
        file_location = f"contract_files/{file.filename}"

        # Save the uploaded file
        with open(file_location, "wb") as f:
            f.write(content)

        # Process the file content
        results = document_processor.process(pdfType, file_location)

        # Remove the uploaded file
        os.remove(file_location)
        
        return JSONResponse({"extracted_data": results})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))