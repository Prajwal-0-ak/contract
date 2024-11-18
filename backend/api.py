from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import yaml
import json
from typing import Dict, List

from process_docs import ProcessDocuments
from database import DatabaseManager
from extract_fields import ExtractField
from utils.util import convert_list_to_xml

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
db_manager = DatabaseManager(
    model_name=config["embedding_model_name"],
    milvus_uri="./huggingface_milvus_test.db",
    collection_name="huggingface_test",
    dimension=config["dimension"],
    chunk_size=config["chunk_size"],
    chunk_overlap=config["chunk_overlap"]
)
extractor = ExtractField()

@app.get("/")
async def root():
    return {"message": "Server Running"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    pdfType: str = Form(...)
):
    # Save the uploaded file
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Determine fields to extract based on pdfType
    if pdfType == "SOW":
        fields_to_extract = config["sow_fields_to_extract"]
        query_for_each_field = config["sow_query_for_each_field"]
        points_to_remember = config["sow_points_to_remember"]
        queries = config["sow_queries"]
    elif pdfType == "MSA":
        fields_to_extract = config["msa_fields_to_extract"]
        query_for_each_field = config["msa_query_for_each_field"]
        points_to_remember = config["msa_points_to_remember"]
        queries = config["msa_queries"]
    else:
        return JSONResponse({"error": "Invalid pdfType"}, status_code=400)

    # Process the document
    pages = process_docs.load_documents(file_location)
    db_manager.setup_milvus()
    db_manager.chunk_and_insert(pages)

    extracted_data = {}

    for field in fields_to_extract:
        field_value_found = False
        query_for_llm = query_for_each_field.get(field, "")
        field_points_to_remember = points_to_remember.get(field, "")

        k_value = 5
        if field == 'insurance_required':
            k_value = 10

        for query in queries[field]:
            if not field_value_found:
                try:
                    similar_content = db_manager.retrieve_similar_content(query, k=k_value)
                    xml_content = convert_list_to_xml(similar_content)

                    response = extractor.extract_field_value(
                        field,
                        xml_content,
                        query=query_for_llm,
                        points_to_remember=field_points_to_remember
                    )

                    if field == 'insurance_required':
                        insurance_fields = [
                            "insurance_required",
                            "type_of_insurance_required",
                            "is_cyber_insurance_required",
                            "cyber_insurance_amount",
                            "is_workman_compensation_insurance_required",
                            "workman_compensation_insurance_amount",
                            "other_insurance_required",
                            "other_insurance_amount"
                        ]
                        for insurance_field in insurance_fields:
                            if insurance_field in response:
                                extracted_data[insurance_field] = {
                                    "value": response[insurance_field]["value"],
                                    "page_number": response[insurance_field]["page_number"]
                                }
                        field_value_found = True
                        break
                    else:
                        if response["field_value_found"]:
                            extracted_data[field] = {
                                "value": response["value"],
                                "page_number": response["page_number"]
                            }
                            field_value_found = True
                            break
                except Exception as e:
                    print(f"An error occurred while extracting field '{field}': {e}")

            if not field_value_found:
                extracted_data[field] = {
                    "value": "null",
                    "page_number": 0
                }
    
    # Format the extracted data for the response

    db_manager.delete_collection()

    final_extracted_data = []
    for field_name, field_info in extracted_data.items():
        final_extracted_data.append({
            "field": field_name,
            "value": field_info.get("value", ""),
            "page_num": field_info.get("page_number", "0")
        })

    return JSONResponse({"extracted_data": final_extracted_data})

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    