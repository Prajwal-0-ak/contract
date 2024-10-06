
import torch
from transformers import AutoTokenizer, AutoModel
from pymilvus import MilvusClient
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DatabaseManager:
    def __init__(self, model_name: str, milvus_uri: str, collection_name: str, dimension: int):
        self.model_name = model_name
        self.milvus_uri = milvus_uri
        self.collection_name = collection_name
        self.dimension = dimension
        self.inference_batch_size = 64

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.milvus_client = MilvusClient(self.milvus_uri)
        self.setup_milvus()
    
    def setup_milvus(self):

        print(f"------------------------------Setting up Milvus collection '{self.collection_name}'...------------------------------")
        if self.milvus_client.has_collection(collection_name=self.collection_name):
            self.milvus_client.drop_collection(collection_name=self.collection_name)

        self.milvus_client.create_collection(
            collection_name=self.collection_name,
            dimension=self.dimension,
            auto_id=True,
            enable_dynamic_field=True,
            vector_field_name="text_embedding",
            consistency_level="Strong",
        )

    def chunk_and_insert(self, text_content: str):

        print("------------------------------Chunking and inserting text content into Milvus collection------------------------------")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512, chunk_overlap=50, separators=["\n\n", "\n", " ", ""]
        )
        chunked_texts = text_splitter.split_text(text_content)

        print(f"------------------------------Number of chunks: {len(chunked_texts)}------------------------------")

        data_list = self.process_chunked_texts(chunked_texts)
        self.insert_data(data_list)

    def process_chunked_texts(self, chunked_texts):

        print("------------------------------Processing chunked texts------------------------------")
        data_list = []
        for i in range(0, len(chunked_texts), self.inference_batch_size):
            batch = chunked_texts[i:i+self.inference_batch_size]
            embeddings = self.encode_text(batch)
            for text, embedding in zip(batch, embeddings):
                data_list.append({
                    "text": text,
                    "text_embedding": embedding.tolist()
                })
        return data_list
    
    def insert_data(self, data_list):

        print("------------------------------Inserting data into Milvus collection------------------------------")
        self.milvus_client.insert(collection_name=self.collection_name, data=data_list)

    def retrieve_similar_content(self, query, k=3):

        print("------------------------------Retrieving similar content from Milvus collection------------------------------")
        query_embedding = self.encode_text(query).tolist()[0]  # Extract the first (and only) embedding
        search_results = self.milvus_client.search(
            collection_name=self.collection_name,
            data=[query_embedding],  # Pass as a list of a single embedding
            limit=k,
            output_fields=["text"],
        )
        print(f"------------------------------Query: {query}------------------------------")
        print(f"------------------------------Search results: \n {search_results}------------------------------")
        return [r["entity"]["text"] for r in search_results[0]]  # Return only the text of top K documents

    def delete_collection(self):
        if self.milvus_client.has_collection(collection_name=self.collection_name):
            self.milvus_client.drop_collection(collection_name=self.collection_name)
            print(f"------------------------------Collection '{self.collection_name}' has been deleted.------------------------------")
        else:
            print(f"------------------------------Collection '{self.collection_name}' does not exist.------------------------------")

    # Utility function to encode text into embeddings
    def encode_text(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        encoded_input = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")

        with torch.no_grad():
            model_output = self.model(**encoded_input)

        token_embeddings = model_output[0]
        attention_mask = encoded_input["attention_mask"]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sentence_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

        return torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
 