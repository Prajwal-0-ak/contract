import os
import csv
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
db_manager = DatabaseManager()
extractor = ExtractField()

def process_files_in_directory(directory: str) -> None:
    # List all PDF files in the directory
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]

    # Initialize a list to store extracted data for all files
    all_extracted_data = []

    for pdf_file in pdf_files:
        file_path = os.path.join(directory, pdf_file)

        print(f"Processing file: {file_path}")  # Debugging line

        # Load and process the document
        try:
            docs = process_docs.load_documents(file_path)
            print(f"Documents loaded successfully: {docs}")  # Debugging line
        except Exception as e:
            print(f"Error loading documents for {pdf_file}: {str(e)}")
            continue

        try:
            process_docs.chunk_and_insert(db_manager, docs)
            print("Documents chunked and inserted successfully")  # Debugging line
        except Exception as e:
            print(f"Error chunking and inserting documents for {pdf_file}: {str(e)}")
            continue

        # Extract fields from the document
        fields_to_extract = config["fields_to_extract"]
        queries_json = config["queries_json"]

        # Initialize an empty dictionary to store extracted field values
        extracted_data = {"file_name": pdf_file}

        # Extract values for each field
        for field in fields_to_extract:
            field_value_found = False
            for query in queries_json[field]:
                if not field_value_found:
                    try:
                        query_embedding = process_docs.embedding.embed_query(query)
                        similar_content = db_manager.retrieve_similar_content(
                            query, query_embedding, top_k=5
                        )
                        response = extractor.extract_field_value(field, similar_content)
                        print(f"Extracted field '{field}': {response}")  # Debugging line
                    except Exception as e:
                        print(f"Error extracting field '{field}' for {pdf_file}: {str(e)}")
                        continue

                    if response["field_value_found"]:
                        extracted_data[field] = response["value"]
                        field_value_found = True
                        break

            if not field_value_found:
                extracted_data[field] = "null"

        # Append the extracted data for this file
        all_extracted_data.append(extracted_data)

        # After processing, delete the file's chunks from the vector database
        try:
            db_manager.delete_chunks_by_file_name(pdf_file)
            print(f"Chunks for {pdf_file} deleted successfully")  # Debugging line
        except Exception as e:
            print(f"Error deleting chunks for {pdf_file}: {str(e)}")
            continue

    # Write the extracted data to a CSV file
    if all_extracted_data:
        save_to_csv(all_extracted_data, OUTPUT_CSV)

def save_to_csv(data: list, output_file: str) -> None:
    # Get the header from the first dictionary keys
    header = data[0].keys()

    with open(output_file, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()
        writer.writerows(data)

    print(f"Extracted data saved to {output_file}")

if __name__ == "__main__":
    process_files_in_directory(UPLOAD_DIR)
