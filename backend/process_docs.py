import os
from typing import Optional
from pypdf import PdfReader
import yaml


class ProcessDocuments:
    def __init__(self) -> None:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)

        self.embedding_model_name = config["embedding_model_name"]

    def load_documents(self, file_path: str) -> Optional[str]:
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

    def read_pdf(self, file_name: str) -> str:
        reader = PdfReader(file_name)

        content = ""

        for page in reader.pages:
            content += page.extract_text()

        return content
