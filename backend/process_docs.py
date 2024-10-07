import os
from typing import Optional
from pypdf import PdfReader
import yaml
import re

class ProcessDocuments:
    def __init__(self) -> None:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)

        self.embedding_model_name = config["embedding_model_name"]

    def load_documents(self, file_path: str) -> Optional[list]:
        print(f"------------------------------Loading document from '{file_path}'------------------------------")

        if not os.path.exists(file_path):
            print(f"------------------------------Error: The file '{file_path}' does not exist.------------------------------")
            return None

        if not file_path.endswith(".pdf"):
            print(f"------------------------------Error: The file '{file_path}' is not a PDF.------------------------------")
            return None

        try:
            return self.read_pdf(file_path)
        except Exception as e:
            print(f"------------------------------Error loading '{file_path}': {str(e)}------------------------------")
            return None

    def read_pdf(self, file_name: str) -> list:
        reader = PdfReader(file_name)
        page_contents = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text:
                cleaned_text = self.clean_text(text)  # Clean the text before adding it to the list
                page_contents.append({"page_number": page_number, "text": cleaned_text})

        return page_contents

    def clean_text(self, text: str) -> str:
        # Remove unnecessary newlines, tabs, and excessive spaces
        cleaned_text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with a single space
        cleaned_text = re.sub(r'\\n', ' ', cleaned_text)  # Remove newline characters
        cleaned_text = re.sub(r'\\u[a-zA-Z0-9]{4}', '', cleaned_text)  # Remove unicode escape sequences
        cleaned_text = re.sub(r'\\uf0b7', '', cleaned_text)  # Remove specific unicode escape sequence
        cleaned_text = re.sub(r'\\', '', cleaned_text)  # Remove any backslashes

        return cleaned_text.strip()  # Remove leading/trailing spaces
