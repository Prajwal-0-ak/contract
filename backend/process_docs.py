import os
from typing import List
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from database import DatabaseManager
import yaml


class ProcessDocuments:
    def __init__(self) -> None:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512, chunk_overlap=50, separators=["\n\n", "\n", " ", ""]
        )
        self.embedding = HuggingFaceEmbeddings(
            model_name=config["embedding_model_name"],
            model_kwargs={"device": "cpu", "trust_remote_code": True},
            encode_kwargs={"normalize_embeddings": True},
        )

    def load_documents(self, file_path: str) -> List[Document]:
        print(f"Loading document from '{file_path}'...")
        docs = []

        if not os.path.exists(file_path):
            print(f"Error: The file '{file_path}' does not exist.")
            return docs

        if not file_path.endswith(".pdf"):
            print(f"Error: The file '{file_path}' is not a PDF.")
            return docs

        try:
            with open(file_path, "rb") as file:
                pdf_reader = PdfReader(file)
                page_content = ""
                for page in pdf_reader.pages:
                    page_content += page.extract_text()

                # Create Document object
                docs.append(
                    Document(
                        page_content=page_content,
                        metadata={"file_name": os.path.basename(file_path)},
                    )
                )
                print(f"Successfully loaded: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"Error loading '{file_path}': {str(e)}")

        print(f"Total documents loaded: {len(docs)}")
        return docs

    def chunk_and_insert(self, db_manager: DatabaseManager, docs: List[Document]):
        print("Chunking documents and inserting into the database...")
        chunked_docs = self.text_splitter.split_documents(docs)
        print(f"Total documents chunked: {len(chunked_docs)}")

        for i, doc in enumerate(chunked_docs):
            chunk_text = doc.page_content
            chunk_embedding = self.embedding.embed_query(chunk_text)

            print(f"Document {i}: {chunk_text[:100]}...")  # Print first 100 chars
            print(f"Embedding shape: {len(chunk_embedding)}")

            db_manager.insert_sample_data(
                doc.metadata["file_name"], chunk_text, chunk_embedding
            )
