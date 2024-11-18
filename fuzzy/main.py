from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import yaml
import json
from typing import Dict, List
from dotenv import load_dotenv

import PyPDF2
from fuzzywuzzy import fuzz
from groq import Groq

app = FastAPI()

load_dotenv()

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

config = load_config()

# Initialize Groq client (reads API key from environment variable)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Directory to save uploaded files
UPLOAD_DIR = "contract_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Define templates and prompts
TEMPLATES = config.get("TEMPLATES", {})
PROMPTS = config.get("PROMPTS", {})

# -----------------------------
# CORS Configuration
# -----------------------------

origins = [
    "http://localhost:3000",
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Extraction Functions
# -----------------------------

def extract_info_with_llm(field: str, page_content: str) -> str:
    """
    Calls the Groq LLM to extract information based on the field and page content.
    """
    prompt_template = PROMPTS.get(field, "")
    if not prompt_template:
        print(f"No prompt found for field '{field}'.")
        return "NA"

    # Replace the placeholder with actual page content
    prompt = prompt_template.format(page_content=page_content)

    try:
        # Call the Groq API to get a completion
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-70b-8192",
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

def process_field(field: str, pdf_reader: PyPDF2.PdfReader, templates: dict) -> str:
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
        extracted_value = extract_info_with_llm(field, page_text)
        if extracted_value and extracted_value.lower() != "na":
            print(f"Extracted '{field}' from Page {page_num + 1}: {extracted_value}")
            return extracted_value

    # If no valid extraction found
    print(f"No valid '{field}' found in the document after checking all matched pages.")
    return "NA"

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    pdfType: str = Form(...)
):
    """
    Endpoint to upload and process a SOW PDF document.
    """
    # Key Assumption: Only SOW type documents are processed
    if pdfType.upper() != "SOW":
        raise HTTPException(status_code=400, detail="Invalid pdfType. Only 'SOW' is supported.")

    # Save the uploaded file
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_location, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    print(f"File saved to {file_location}")

    # Set the PDF_PATH to the saved file
    pdf_path = file_location

    try:
        pdf_reader = load_pdf_content(pdf_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Define the fields to extract (assuming SOW fields)
    fields_to_extract = [
        "currency", "sow_no", "sow_start_date", "remark",
        "inclusive_or_exclusive_gst", "subcontract_clause", "sow_value", "credit_period",
        "cola", "total_fte", "client_company_name",
        "sow_end_date", "type_of_billing", "po_number",
        "amendment_no", "billing_unit_type_and_rate_cost", "particular_role_rate"
    ]

    extracted_data = {field: None for field in fields_to_extract}

    for field in fields_to_extract:
        print(f"\nProcessing field: {field}")
        extracted_value = process_field(field, pdf_reader, TEMPLATES)
        extracted_data[field] = extracted_value

    print("\nMatching and extraction completed.")
    print(json.dumps(extracted_data, indent=4))

    # Format the extracted data for the response
    final_extracted_data = []
    for field_name, field_value in extracted_data.items():
        final_extracted_data.append({
            "field": field_name,
            "value": field_value if field_value else "NA",
            "page_num": "0"  # Since `process_field` doesn't return page_num, setting as "0"
        })

    return JSONResponse({"extracted_data": final_extracted_data})

@app.get("/")
def read_root():
    return {"message": "SOW Document Processing API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)