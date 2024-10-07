import os
import yaml
from fastapi import HTTPException
import csv

# Import your custom classes for document processing and field extraction
from process_docs import ProcessDocuments
from database import DatabaseManager
from extract_fields import ExtractField

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

UPLOAD_DIR = "contract_files"
OUTPUT_CSV = "extracted_data.csv"

# Initialize classes
process_docs = ProcessDocuments()
db_manager = DatabaseManager(
    model_name="BAAI/bge-large-en-v1.5",
    milvus_uri="./huggingface_milvus_test.db",
    collection_name="huggingface_test",
    dimension=1024
)
extractor = ExtractField()

def process_files_in_directory(directory: str) -> None:
    extracted_data = []

    # Process all PDF files in the directory
    for file_name in os.listdir(directory):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(directory, file_name)
            print(f"Processing {file_name}...")

            pages = process_docs.load_documents(pdf_path)
            db_manager.chunk_and_insert(pages)

            for field in config["sow_fields_to_extract"]:
                field_value_found = False
                query_for_similarity_search = config["query_for_each_field"].get(field, "")
                query_for_llm = config["query_for_each_field"].get(field, "")

                for query in config["sow_queries"][field]:
                    if not field_value_found:
                        try:
                            similar_content = db_manager.retrieve_similar_content(query_for_similarity_search, k=2)
                            response = extractor.extract_field_value(field, similar_content, query=query_for_llm)
                            print(f"Extracted field '{field}': {response}")
                        except Exception as e:
                            print(f"Error extracting field '{field}': {str(e)}")
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

            db_manager.delete_collection()

    # Write output to CSV
    with open(OUTPUT_CSV, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["field", "value", "page_num"])
        writer.writeheader()
        writer.writerows(extracted_data)

    print(f"Data extraction completed. Output saved to {OUTPUT_CSV}")
    print(f"Final extracted data: {extracted_data}")

if __name__ == "__main__":
    process_files_in_directory(UPLOAD_DIR)