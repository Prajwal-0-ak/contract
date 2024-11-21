
import torch
from transformers import AutoTokenizer, AutoModel
from pymilvus import MilvusClient
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DatabaseManager:
    """
        Manages interactions with the Milvus vector database, including collection setup, text chunking, data insertion with embeddings,
        and retrieval of similar content based on queries. Utilizes a specified ML model for encoding text into embeddings.
        Attributes:
            model_name (str): Pre-trained model for text encoding.
            milvus_uri (str): URI for Milvus database connection.
            collection_name (str): Name of the Milvus collection.
            dimension (int): Dimensionality of vector embeddings.
            chunk_size (int): Size of each text chunk.
            chunk_overlap (int, optional): Overlap between chunks. Defaults to 25.
            inference_batch_size (int): Batch size for inference.
        Methods:
            setup_milvus():
                Sets up the Milvus collection.
            chunk_and_insert(pages: list):
                Splits and inserts text chunks into Milvus.(Chuking)
            process_chunked_texts(chunked_texts: list, page_number: int) -> list:
                Encodes chunked texts and prepares data for insertion.
            insert_data(data_list: list):
                Inserts data into Milvus.
            retrieve_similar_content(query: str, k: int = 3) -> list:
                Retrieves top k similar content based on query.(Retrieval)
            delete_collection():
                Deletes the Milvus collection.
            encode_text(texts: Union[str, list]) -> torch.Tensor:
                Encodes text into normalized sentence embeddings.(Embedding)
    """
    def __init__(
        self,
        model_name: str,
        milvus_uri: str,
        collection_name: str,
        dimension: int,
        chunk_size: int,
        chunk_overlap: int = 25
    ):
        self.model_name = model_name
        self.milvus_uri = milvus_uri
        self.collection_name = collection_name
        self.dimension = dimension
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.inference_batch_size = 64

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(self.model_name, trust_remote_code=True)
        self.milvus_client = MilvusClient(self.milvus_uri)
    
    def setup_milvus(self):
        print(f"Setting up Milvus collection '{self.collection_name}'...")
        if self.milvus_client.has_collection(collection_name=self.collection_name):
            self.milvus_client.drop_collection(collection_name=self.collection_name)

        self.milvus_client.create_collection(
            collection_name=self.collection_name,
            dimension=self.dimension,
            auto_id=True,
            enable_dynamic_field=True,
            vector_field_name="text_embedding",
            consistency_level="Strong"
        )
    
    def chunk_and_insert(self, pages: list):
        print("Chunking and inserting text content into Milvus collection")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

        data_list = []
        for page in pages:
            page_number = page["page_number"]
            chunked_texts = text_splitter.split_text(page["text"])
            data_list.extend(self.process_chunked_texts(chunked_texts, page_number))

        self.insert_data(data_list)
    
    def process_chunked_texts(self, chunked_texts, page_number):
        data_list = []
        for i in range(0, len(chunked_texts), self.inference_batch_size):
            batch = chunked_texts[i:i + self.inference_batch_size]
            embeddings = self.encode_text(batch)
            for text, embedding in zip(batch, embeddings):
                data_list.append({
                    "text": text,
                    "text_embedding": embedding.tolist(),
                    "page_number": page_number  # Add the page number as metadata
                })
        return data_list

    def insert_data(self, data_list):
        print("Inserting data into Milvus collection")
        self.milvus_client.insert(collection_name=self.collection_name, data=data_list)
    
    def retrieve_similar_content(self, query, k=3):
        query_embedding = self.encode_text(query).tolist()[0]  # Extract the first (and only) embedding
        search_results = self.milvus_client.search(
            collection_name=self.collection_name,
            data=[query_embedding],  # Pass as a list of a single embedding
            limit=k,
            output_fields=["text", "page_number"]  # Include page number in the output fields
        )
        return [
            {"text": r["entity"]["text"], "page_number": r["entity"]["page_number"]}
            for r in search_results[0]
        ]  # Return both text and page number

    def delete_collection(self):
        if self.milvus_client.has_collection(collection_name=self.collection_name):
            self.milvus_client.drop_collection(collection_name=self.collection_name)
            print(f"Collection '{self.collection_name}' has been deleted.")
        else:
            print(f"Collection '{self.collection_name}' does not exist.")

    def encode_text(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        encoded_input = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )

        with torch.no_grad():
            model_output = self.model(**encoded_input)

        token_embeddings = model_output[0]  # First element contains token embeddings
        attention_mask = encoded_input["attention_mask"]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sentence_embeddings = torch.sum(
            token_embeddings * input_mask_expanded, 1
        ) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

        return torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)