from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Dict, List
import yaml

# Import your custom classes for document processing and field extraction
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
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize classes
process_docs = ProcessDocuments()
db_manager = DatabaseManager()
extractor = ExtractField()


@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Hello World"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> JSONResponse:
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        # Save the uploaded PDF file to the contract_files directory
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Load and process the document
        try:
            docs = process_docs.load_documents(file_path)
            print(f"Documents loaded successfully: {docs}")  # Debugging line
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error loading documents: {str(e)}",
            )

        try:
            process_docs.chunk_and_insert(db_manager, docs)
            print("Documents chunked and inserted successfully")  # Debugging line
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error chunking and inserting documents: {str(e)}",
            )

        # Extract fields from the document
        fields_to_extract = config["fields_to_extract"]
        queries_json = config["queries_json"]

        # Initialize an empty dictionary to store extracted field values
        extracted_data = {}

        # Extract values for each field
        for field in fields_to_extract:
            field_value_found = False
            for query in queries_json[field]:
                if not field_value_found:
                    try:
                        query_embedding = process_docs.embedding.embed_query(query)
                        similar_content = db_manager.retrieve_similar_content(
                            query_embedding, top_k=5
                        )
                        response = extractor.extract_field_value(field, similar_content)
                        print(
                            f"Extracted field '{field}': {response}"
                        )  # Debugging line
                    except Exception as e:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Error extracting field '{field}': {str(e)}",
                        )

                    if response["field_value_found"]:
                        extracted_data[field] = response["value"]
                        field_value_found = True
                        break

            if not field_value_found:
                extracted_data[field] = "null"

        # After processing, delete the file's chunks from the vector database
        try:
            db_manager.delete_chunks_by_file_name(file.filename)
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

        # Return the extracted data to the client
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
