import os
import csv
import yaml
from PyPDF2 import PdfReader
from fuzzywuzzy import fuzz
from groq import Groq

# Load config.yaml
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Set up Groq API client
client = Groq(api_key="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")

# Create CSV file
csv_filename = "contract_field_extraction.csv"
csv_columns = [
    "Document Name",
    "Contract Field",
    "Page No That is Sent to LLM",
    "field_value",
    "value_found",
]

# Initialize the CSV file with headers
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=csv_columns)
    writer.writeheader()


def generate_prompt(field, page_content):
    prompt_template = """
        You are an AI assistant specializing in extracting specific fields from business contracts.
        Your task is to retrieve the requested field value from the provided contract content.

        Context:
        - The documents you are analyzing are legally binding contracts between businesses or entities.
        - Fields you are tasked with extracting include key contract details such as dates, company names, terms, parties involved, and other important business information.
        - Your role is to accurately extract these values without any assumptions or additional commentary.

        Instructions:
        1. Based on the provided field name and the relevant contract content, extract the value for the specified field in the following format:
        {{ "value": "[Extracted value]", "field_value_found": true }} if the value is found.
        2. If the value is not present in the provided content or cannot be determined, return:
        {{ "value": "null", "field_value_found": false }}.
        3. Return the output in plain text, not as a code cell or in markdown.
        4. Do not hallucinate or invent any information. If the content does not contain the answer, return "null" as the value.
        5. Ensure your response is based only on the provided contract content and related field.
        6. Return the output only in the JSON format described above, with no additional text or explanations.

        Required Field: {field}
        Relevant Contract Content: {page_content}

        Return only the value in the strict JSON format.
    """
    return prompt_template.format(field=field, page_content=page_content)


def extract_info_with_llm(field, page_content):
    prompt = generate_prompt(field, page_content)
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
    )
    response = chat_completion.choices[0].message.content
    return response.strip() if response else None


def process_field(field, pages, doc_name):
    best_match_page = None
    top_page_matches = []

    for page_num, page_text in pages.items():
        for template in config["templates"][field]:
            ratio = fuzz.partial_ratio(template.lower(), page_text.lower())
            if ratio > 60:
                top_page_matches.append((page_num, page_text, ratio))

    # Sort by match score and take the top 3 matches
    top_page_matches = sorted(top_page_matches, key=lambda x: x[2], reverse=True)[:3]

    for match in top_page_matches:
        page_num, page_text, score = match
        print(f"Page {page_num + 1} matched for {field} with score {score}")
        result = extract_info_with_llm(field, page_text)
        if result and '"field_value_found": true' in result:
            print(f"Extracted {field}: {result}")
            return doc_name, field, page_num + 1, result, "true"

    # If no valid result is found, return null
    return doc_name, field, "N/A", "null", "false"


def process_pdf(pdf_path):
    # Read the PDF file
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        pages = {
            i: pdf_reader.pages[i].extract_text() for i in range(len(pdf_reader.pages))
        }
        return pages


def main():
    directory_path = "contract_files"
    output_data = []

    # Process all PDF files in the directory
    for file_name in os.listdir(directory_path):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(directory_path, file_name)
            print(f"Processing {file_name}...")

            pages = process_pdf(pdf_path)
            for field in config["templates"]:
                field_data = process_field(field, pages, file_name)
                output_data.append(field_data)

    # Write output to CSV
    with open(csv_filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        for data_row in output_data:
            writer.writerow(data_row)

    print(f"Data extraction completed. Output saved to {csv_filename}")


if __name__ == "__main__":
    main()
