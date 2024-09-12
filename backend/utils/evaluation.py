from pypdf import PdfReader
from fuzzywuzzy import fuzz
import os
import csv


def find_page_number(chunk, file_name, query):
    # Path to the file in contract_files
    file_path = os.path.join("contract_files", file_name)

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File {file_name} not found.")
        return None

    # Open the PDF and iterate through each page using pypdf
    pdf_reader = PdfReader(file_path)
    highest_score = 0
    best_page_no = -1

    for page_no, page in enumerate(pdf_reader.pages):
        # Extract the text content from each page
        page_text = page.extract_text()

        # Calculate the fuzzy matching ratio between the chunk and the page content
        ratio = fuzz.partial_ratio(chunk.lower(), page_text.lower())

        # Track the highest score and the corresponding page number
        if ratio > highest_score:
            highest_score = ratio
            best_page_no = page_no + 1  # PDF pages are 1-indexed

    # After finding the best match, write to CSV
    write_to_csv(file_name, query, best_page_no)


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
