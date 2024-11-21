
import os
from typing import List
from datetime import datetime
from fastapi import UploadFile
from app.utils.document_processor import DocumentProcessor
from app.database.connection import SOWSessionLocal, MSASessionLocal
from app.models.models import SOWContract, MSAContract

class DocumentService:
    """
    Service class for document processing and database operations.
    """
    def __init__(self):
        # Initialize the document processor and ensure the storage directory exists
        self.document_processor = DocumentProcessor()
        os.makedirs("contract_files", exist_ok=True)

    def process_files(self, files: List[UploadFile], pdfType: str):
        """
        Processes uploaded files based on the specified PDF type.

        Args:
            files (List[UploadFile]): List of uploaded files to process.
            pdfType (str): Type of PDF ('SOW' or 'MSA').

        Returns:
            List[dict]: Results of the processing for each file.
        """
        results = []

        for file in files:
            # Read the content of the uploaded file
            content = file.file.read()
            file_location = f"contract_files/{file.filename}"
            
            # Save the uploaded file to the designated directory
            with open(file_location, "wb") as f:
                f.write(content)
            
            # Process the file content to extract necessary data
            extracted_data = self.document_processor.process(content, pdfType)
            
            # Determine the appropriate database session and contract model
            if pdfType.upper() == "SOW":
                db_session = SOWSessionLocal()
                contract = SOWContract(
                    file_name=file.filename,
                    upload_date=datetime.utcnow(),
                    processed=True,
                    **extracted_data  # Populate contract fields with extracted data
                )
            elif pdfType.upper() == "MSA":
                db_session = MSASessionLocal()
                contract = MSAContract(
                    file_name=file.filename,
                    upload_date=datetime.utcnow(),
                    processed=True,
                    **extracted_data  # Populate contract fields with extracted data
                )
            else:
                # Raise an error for unsupported PDF types
                raise ValueError(f"Invalid pdfType: {pdfType}")
            
            # Add and commit the contract to the database
            db_session.add(contract)
            db_session.commit()
            db_session.refresh(contract)
            db_session.close()
            
            # Remove the uploaded file after processing
            os.remove(file_location)
            
            # Prepare the extracted data for the response
            final_extracted_data = [
                {
                    "field": field_name,
                    "value": field_info.get("value", ""),
                    "page_num": field_info.get("page_number", "0")
                }
                for field_name, field_info in extracted_data.items()
            ]
            
            # Append the processing result for the current file
            results.append({
                "file": file.filename,
                "status": "processed",
                "extracted_data": final_extracted_data
            })
        
        return results