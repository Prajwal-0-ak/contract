import os
from typing import List
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from database import DatabaseManager


class ProcessDocuments:
    def __init__(self) -> None:
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024, chunk_overlap=25, separators=["\n\n", "\n", " ", ""]
        )
        self.embedding = HuggingFaceEmbeddings(
            model_name="BAAI/bge-large-en-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    def load_documents(self, folder_name: str = "contract_files") -> List[Document]:
        print(f"Loading documents from '{folder_name}' folder...")
        docs = []
        folder_path = os.path.join(os.getcwd(), folder_name)

        if not os.path.exists(folder_path):
            print(f"Error: The folder '{folder_path}' does not exist.")
            return docs

        for file_name in os.listdir(folder_path):
            if file_name.endswith(".pdf"):
                file_path = os.path.join(folder_path, file_name)

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
                                metadata={"file_name": file_name},
                            )
                        )
                        print(f"Successfully loaded: {file_name}")
                except Exception as e:
                    print(f"Error loading '{file_name}': {str(e)}")

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
