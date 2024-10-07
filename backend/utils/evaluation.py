from pypdf import PdfReader
from fuzzywuzzy import fuzz
import os
import csv

def find_page_number(chunk, query):
    
    # Ensure 'chunk' is a string
    if isinstance(chunk, list):
        chunk = ' '.join(chunk)  # Convert list of strings to a single string

    contract_dir = "contract_files"
    pdf_files = [f for f in os.listdir(contract_dir) if f.endswith('.pdf')]

    if not pdf_files:
        print("No PDF file found in the contract_files directory.")
        return None

    file_path = os.path.join(contract_dir, pdf_files[0])
    pdf_reader = PdfReader(file_path)
    highest_score = 0
    best_page_no = -1

    for page_no, page in enumerate(pdf_reader.pages):
        page_text = page.extract_text()

        # Fuzzy matching between chunk and page content
        ratio = fuzz.partial_ratio(chunk.lower(), page_text.lower())  # Ensure 'chunk' is a string

        if ratio > highest_score:
            highest_score = ratio
            best_page_no = page_no + 1

    return int(best_page_no)


def write_to_csv(file_name, query, page_no):
    csv_file = "final_content.csv"
    file_exists = os.path.exists(csv_file)

    # Define the headers for the CSV
    headers = ["file_name", "query", "page_no"]

    # Write to CSV: create if it doesn't exist, otherwise append
    with open(csv_file, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        # Write the header only if the file doesn't already exist
        if not file_exists:
            writer.writeheader()

        # Write the new row with file name, query, and page number
        writer.writerow({"file_name": file_name, "query": query, "page_no": page_no})

    print(f"Data written to {csv_file}: {file_name}, {query}, {page_no}")
