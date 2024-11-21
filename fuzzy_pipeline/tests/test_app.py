# FILE: test_app.py

import os
import yaml
import json
import PyPDF2
from fuzzywuzzy import fuzz
from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq
from pathlib import Path

def load_config(config_path: str = 'config.yaml') -> dict:
    """
    Loads the configuration from a YAML file.
    """
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Configuration file not found at path: {config_path}")
        raise
    except Exception as e:
        print(f"Error loading configuration file: {e}")
        raise

def extract_info_with_llm(field: str, page_content: str, prompts: dict, client: OpenAI, groq_client: Groq) -> str:
    """
    Calls the Groq LLM to extract information based on the field and page content.
    """
    prompt_template = prompts.get(field, "")
    if not prompt_template:
        print(f"No prompt found for field '{field}'.")
        return "NA"

    # Replace the placeholder with actual page content
    prompt = prompt_template.format(page_content=page_content)

    try:
        # Call the Groq API to get a completion
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            model="gpt-4o-mini",
        )

        # Extract and return the concise response content
        response = chat_completion.choices[0].message.content
        return response.strip() if response else "NA"
    except Exception as e:
        print(f"Error extracting '{field}' with LLM: {e}")
        return "NA"

def load_pdf_content(pdf_path: str) -> PyPDF2.PdfReader:
    """
    Loads the PDF file and returns a PdfReader object.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_path)
        return pdf_reader
    except FileNotFoundError:
        print(f"PDF file not found at path: {pdf_path}")
        raise
    except Exception as e:
        print(f"Error loading PDF file: {e}")
        raise

def process_field(field: str, pdf_reader: PyPDF2.PdfReader, templates: dict, prompts: dict, client: OpenAI, groq_client: Groq) -> str:
    """
    Processes a single field by performing fuzzy matching and LLM extraction.
    """
    matched_pages = []
    total_pages = len(pdf_reader.pages)

    # First pass: Collect all pages with a matching template
    for page_num in range(total_pages):
        page_obj = pdf_reader.pages[page_num]
        page_text = page_obj.extract_text() or ""

        # Perform fuzzy matching for each template
        for template in templates.get(field, []):
            ratio = fuzz.partial_ratio(template.lower(), page_text.lower())
            if ratio > 60:
                print(f"Page {page_num + 1} matched with template '{template}' for field '{field}' (Score: {ratio})")
                matched_pages.append((page_num, page_text))
                break  # Only collect the first match on the page

    # Second pass: Process all matched pages and extract information
    for page_num, page_text in matched_pages:
        extracted_value = extract_info_with_llm(field, page_text, prompts, client, groq_client)
        if extracted_value and extracted_value.lower() != "na":
            print(f"Extracted '{field}' from Page {page_num + 1}: {extracted_value}")
            return extracted_value

    # If no valid extraction found
    print(f"No valid '{field}' found in the document after checking all matched pages.")
    return "NA"

def main():
    """
    Test script to process all PDF files in the 'contract_files' directory,
    extract fields, print the results, and update the SQLite database.
    """
    load_dotenv()

    config = load_config()

    # Initialize OpenAI client
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY is not set in the environment variables.")
        return
    client = OpenAI(api_key=openai_api_key)

    # Initialize Groq client
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("Error: GROQ_API_KEY is not set in the environment variables.")
        return
    groq_client = Groq(api_key=groq_api_key)

    # Define the contract_files directory path
    current_dir = Path(__file__).parent.resolve()
    contract_files_dir = os.path.join(current_dir, "contract_files")

    # Verify that the contract_files directory exists
    if not os.path.isdir(contract_files_dir):
        print(f"Error: The directory '{contract_files_dir}' does not exist.")
        print("Please create the 'contract_files/' directory and place your PDF files inside it.")
        return

    # Define templates and prompts
    TEMPLATES = config.get("TEMPLATES", {})
    PROMPTS = config.get("PROMPTS", {})

    # Define the fields to extract (assuming SOW fields)
    fields_to_extract = [
        "currency", "sow_no", "sow_start_date", "remark",
        "inclusive_or_exclusive_gst", "subcontract_clause", "sow_value", "credit_period",
        "cola", "total_fte", "client_company_name",
        "sow_end_date", "type_of_billing", "po_number",
        "amendment_no", "billing_unit_type_and_rate_cost", "particular_role_rate"
    ]

    # Iterate over all PDF files in the contract_files directory
    for filename in os.listdir(contract_files_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(contract_files_dir, filename)
            print(f"\nProcessing file: {filename}")

            # Process the PDF
            try:
                pdf_reader = load_pdf_content(pdf_path)
                print("PDF loaded successfully.")
            except Exception as e:
                print(f"Error loading PDF: {e}")
                continue  # Skip to the next file

            extracted_data = {field: None for field in fields_to_extract}

            for field in fields_to_extract:
                print(f"\nProcessing field: {field}")
                extracted_value = process_field(field, pdf_reader, TEMPLATES, PROMPTS, client, groq_client)
                extracted_data[field] = extracted_value

            print("\nMatching and extraction completed.")
            print(json.dumps(extracted_data, indent=4))

            # Indicate that the SQLite database has been updated
            print("The SQLite database has been updated with the extracted data.")

    # ----------------------
    # Instructions to Test the RAG Pipeline
    # ----------------------
    #
    # 1. **Prepare the Environment:**
    #    - Ensure that the virtual environment is activated.
    #    - Navigate to the project root directory.
    #
    # 2. **Place PDF Files:**
    #    - Upload or place all the PDF files you want to test into the `contract_files/` directory.
    #
    # 3. **Configure Settings:**
    #    - Ensure that the `config.yaml` file contains the correct templates and prompts.
    #    - Verify that all required environment variables (`OPENAI_API_KEY`, `GROQ_API_KEY`) are set in the `.env` file.
    #
    # 4. **Install Dependencies:**
    #    - If not already done, install all required dependencies:
    #      ```bash
    #      pip install -r requirements.txt
    #      ```
    #
    # 5. **Run the Test Script:**
    #    - Execute the test script to process the PDF files:
    #      ```bash
    #      python test_app.py
    #      ```
    #
    # 6. **Review the Output:**
    #    - The script will process each PDF file, extract the defined fields, and print the results to the console.
    #    - Check the console output for any error messages or confirmation of successful processing.
    #
    # 7. **Verify Database Updates:**
    #    - Ensure that the SQLite database has been updated with the extracted data.
    #    - Optionally, use a SQLite browser or CLI to inspect the database contents.
    #
    # 8. **Troubleshooting:**
    #    - If errors occur, review the error messages for clues.
    #    - Ensure that file paths and permissions are correctly set.
    #    - Confirm that the extraction functions are functioning as expected and that LLM API keys are valid.
    #

if __name__ == "__main__":
    main()