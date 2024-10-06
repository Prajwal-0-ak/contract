import os
import yaml

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
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]


    for pdf_file in pdf_files:
        file_path = os.path.join(directory, pdf_file)

        print(f"------------------------------Processing file {pdf_file}------------------------------")

        try:
            pdf_content = process_docs.load_documents(file_path)
            print("------------------------------Documents loaded successfully------------------------------")
        except Exception as e:
            print(f"------------------------------Error loading documents for {pdf_file}: {str(e)}------------------------------")
            continue

        try:
            db_manager.chunk_and_insert(pdf_content)
            print("------------------------------Documents chunked and inserted successfully------------------------------")
        except Exception as e:
            print(f"------------------------------Error chunking and inserting documents for {pdf_file}: {str(e)}------------------------------")
            continue

        fields_to_extract = config["sow_fields_to_extract"]
        queries_json = config["sow_queries"]

        extracted_data = {}

        # Extract values for each field
        for field in fields_to_extract:
            field_value_found = False
            for query in queries_json[field]:
                if not field_value_found:
                    try:
                        similar_content = db_manager.retrieve_similar_content(
                            query, k=2
                        )
                        response = extractor.extract_field_value(field, similar_content)
                        print(f"------------------------------Extracted field '{field}': {response['value']}------------------------------")
                    except Exception as e:
                        print(f"------------------------------Error extracting field '{field}': {str(e)}------------------------------")
                        continue

                    if response["field_value_found"]:
                        extracted_data[field] = response["value"]
                        field_value_found = True
                        break

            if not field_value_found:
                extracted_data[field] = "null"


        try:
            db_manager.delete_collection()
            print(f"------------------------------Collection deleted for {pdf_file}------------------------------")
        except Exception as e:
            print(f"------------------------------Error deleting collection for {pdf_file}: {str(e)}------------------------------")
            continue


if __name__ == "__main__":
    process_files_in_directory(UPLOAD_DIR)
