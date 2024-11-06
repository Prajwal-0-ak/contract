import os
import yaml

from process_docs import ProcessDocuments
from database import DatabaseManager
from extract_fields import ExtractField
from utils.util import convert_list_to_xml, rerank_chunks
import json

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

UPLOAD_DIR = "contract_files"

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

def process_files_in_directory(directory: str) -> None:
    final_extracted_data = {}

    # Process all PDF files in the directory
    for file_name in os.listdir(directory):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(directory, file_name)
            print(f"Processing {file_name}...")

            pages = process_docs.load_documents(pdf_path)
            db_manager.setup_milvus()
            db_manager.chunk_and_insert(pages)

            extracted_data = {}

            for field in config["sow_fields_to_extract"]:

                field_value_found = False
                query_for_llm = config["sow_query_for_each_field"].get(field, "")
                sow_points_to_remember = config["sow_points_to_remember"].get(field, "")

                k_value = 5
                if field == 'insurance_required':
                    k_value = 10

                for query in config["sow_queries"][field]:

                    if not field_value_found:
                        try:
                            similar_content = db_manager.retrieve_similar_content(query, k=k_value)
                            xml_content = convert_list_to_xml(similar_content)
                            print(f"XML content App.py: \n{xml_content}\n\n")

                            response = extractor.extract_field_value(
                                field,
                                xml_content,
                                query=query_for_llm,
                                points_to_remember=sow_points_to_remember
                            )

                            if field == 'insurance_required':

                                # print(f"\nExtracted Insurance Fields: {response}")
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
                                        extracted_data[insurance_field] = response[insurance_field]
                                field_value_found = True
                                print(f"\nExtracted Insurance Fields: {extracted_data}")
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

            # print(f"\n\nExtracted Data: {file_name} \n{extracted_data}")
            final_extracted_data[file_name] = extracted_data

    print("\n\nFinal Extracted Data: ")
    print(json.dumps(final_extracted_data, indent=4))

    db_manager.delete_collection()


if __name__ == "__main__":
    process_files_in_directory(UPLOAD_DIR)
