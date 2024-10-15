from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Dict
import yaml
import csv

from process_docs import ProcessDocuments
from database import DatabaseManager
from extract_fields import ExtractField

app = FastAPI()

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "contract_files"
OUTPUT_CSV = "extracted_data.csv"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize classes
process_docs = ProcessDocuments()
db_manager = DatabaseManager(
    model_name="BAAI/bge-large-en-v1.5",
    milvus_uri="./huggingface_milvus_test.db",
    collection_name="huggingface_test",
    dimension=1024
)
extractor = ExtractField()


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Hello World"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), pdfType: str = Form(...)) -> JSONResponse:
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        # Save the uploaded PDF file to the contract_files directory
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Load and process the document
        try:
            pdf_content = process_docs.load_documents(file_path)
            print("Documents Content loaded successfully")  # Debugging line
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error loading documents: {str(e)}",
            )
        
        db_manager.setup_milvus()

        try:
            db_manager.chunk_and_insert(pdf_content)
            print("Documents chunked and inserted successfully")  # Debugging line
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error chunking and inserting documents: {str(e)}",
            )

        # Handle dynamic document type (NDA, SOW, MSA)
        if pdfType == "NDA":
            fields_to_extract = config["nda_fields_to_extract"]
            queries_json = config["nda_queries"]
        elif pdfType == "SOW":
            fields_to_extract = config["sow_fields_to_extract"]
            queries_json = config["sow_queries"]
        elif pdfType == "MSA":
            fields_to_extract = config["msa_fields_to_extract"]
            queries_json = config["msa_queries"]
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF type. Please specify 'NDA', 'SOW', or 'MSA'.",
            )

        extracted_data = []

        # Extract fields
        for field in fields_to_extract:
            field_value_found = False
            query_for_llm = config["query_for_each_field"].get(field, "")

            for query in queries_json[field]:
                if not field_value_found:
                    try:
                        similar_content = db_manager.retrieve_similar_content(query, k=2)
                        response = extractor.extract_field_value(field, similar_content, query=query_for_llm)
                        print(f"Extracted field '{field}': {response}")
                    except Exception as e:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Error extracting field '{field}': {str(e)}",
                        )
                    if response["field_value_found"]:
                        extracted_data.append({
                            "field": field,
                            "value": response["value"],
                            "page_num": response["page_number"]
                        })
                        field_value_found = True
                        break

            if not field_value_found:
                extracted_data.append({
                    "field": field,
                    "value": "null",
                    "page_num": 0
                })

        # After processing, delete the file's chunks from the vector database
        try:
            db_manager.delete_collection()
            print("Chunks deleted successfully")  # Debugging line
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting chunks by file name: {str(e)}",
            )

        # Delete the uploaded PDF file after processing
        try:
            os.remove(file_path)
            print("Uploaded file deleted successfully")  # Debugging line
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting uploaded file: {str(e)}",
            )

        # Write output to CSV
        try:
            with open(OUTPUT_CSV, mode="w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=["field", "value", "page_num"])
                writer.writeheader()
                writer.writerows(extracted_data)
            print(f"Data extraction completed. Output saved to {OUTPUT_CSV}")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error writing to CSV: {str(e)}",
            )

        print(f"Final extracted data: {extracted_data}")  # Debugging line
        return JSONResponse(content={"extracted_data": extracted_data})

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
