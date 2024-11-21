import re
import os
from typing import Optional, List, Dict
from pypdf import PdfReader

def clean_text(text: str) -> str:
    """
    Cleans and preprocesses the input text by removing unnecessary whitespace,
    newline characters, and specific unicode escape sequences.
    
    Args:
        text (str): The raw text to be cleaned.
    
    Returns:
        str: The cleaned and stripped text.
    """
    # Replace multiple whitespace characters (spaces, tabs, newlines) with a single space
    cleaned_text = re.sub(r'\s+', ' ', text)
    
    # Remove newline characters
    cleaned_text = re.sub(r'\\n', ' ', cleaned_text)
    
    # Remove unicode escape sequences
    cleaned_text = re.sub(r'\\u[a-zA-Z0-9]{4}', '', cleaned_text)
    cleaned_text = re.sub(r'\\uf0b7', '', cleaned_text)
    
    # Remove any remaining backslashes
    cleaned_text = re.sub(r'\\', '', cleaned_text)
    
    return cleaned_text.strip()

def load_documents(file_path: str) -> Optional[List[Dict]]:
    """
    Loads and processes a PDF document from the specified file path.
    
    Args:
        file_path (str): The path to the PDF file.
    
    Returns:
        Optional[List[Dict]]: A list of dictionaries containing page numbers and cleaned text,
                              or None if an error occurs.
    """
    print(f"------------------------------Loading document from '{file_path}'------------------------------")

    if not os.path.exists(file_path):
        print(f"------------------------------Error: The file '{file_path}' does not exist.------------------------------")
        return None

    if not file_path.lower().endswith(".pdf"):
        print(f"------------------------------Error: The file '{file_path}' is not a PDF.------------------------------")
        return None

    try:
        return read_pdf(file_path)
    except Exception as e:
        print(f"------------------------------Error loading '{file_path}': {str(e)}------------------------------")
        return None

def read_pdf(file_name: str) -> List[Dict]:
    """
    Reads and extracts text from each page of a PDF file, cleaning the text before storage.
    
    Args:
        file_name (str): The name of the PDF file to read.
    
    Returns:
        List[Dict]: A list of dictionaries with page numbers and their corresponding cleaned text.
    """
    reader = PdfReader(file_name)
    page_contents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text:
            cleaned_text = clean_text(text)  # Clean the text before adding it to the list
            page_contents.append({"page_number": page_number, "text": cleaned_text})

    return page_contents