import sqlite3
import sqlite_vec
import json
import struct
import numpy as np
from dotenv import load_dotenv
from utils.evaluation import find_page_number

class DatabaseManager:
    def __init__(self):
        load_dotenv()
        # Connect to the SQLite database and load sqlite_vec extension
        self.conn = sqlite3.connect('vecindex.sqlite')
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)  # Load the sqlite_vec extension for vector operations
        self.cursor = self.conn.cursor()
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS VecIndex (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            chunk TEXT NOT NULL,
            chunk_embedding BLOB NOT NULL  -- Store as binary (blob)
        );
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()
        print("Table 'VecIndex' is ready.")

    def insert_sample_data(self, file_name, chunk, chunk_embedding):
        try:
            # Convert embedding to bytes and insert
            chunk_embedding_bytes = json.dumps(chunk_embedding).encode('utf-8')
            insert_query = """
            INSERT INTO VecIndex (file_name, chunk, chunk_embedding)
            VALUES (?, ?, ?);
            """
            self.cursor.execute(insert_query, (file_name, chunk, chunk_embedding_bytes))
            self.conn.commit()
            print("Sample data inserted successfully.")
        except Exception as e:
            print(f"An error occurred while inserting data: {e}")

    def retrieve_similar_content(self, query, embedding, top_k=5):
        # util functions
        def serialize(vector: list[float]) -> bytes:
            """
            Serializes a list of floats into a compact "raw bytes" format. Taken from:
            https://github.com/asg017/sqlite-vec/blob/496560cf9ac4b358ea43793e591f376c02c16b90/examples/python-recipes/openai-sample.py#L10
            """
            return struct.pack("%sf" % len(vector), *vector)

        try:
            # Convert the embedding list to a NumPy array
            query_embedding = np.array(embedding)

            # Retrieve all chunks from the database
            db_query = """
                SELECT file_name, chunk, chunk_embedding
                FROM VecIndex
                LIMIT ?;
            """
            self.cursor.execute(db_query, (top_k,))
            results = self.cursor.fetchall()

            # Calculate cosine similarity manually
            similar_content = []
            for result in results:
                # Convert stored embedding from JSON string (binary blob) back to NumPy array
                stored_embedding = json.loads(result[2].decode('utf-8'))
                stored_embedding = np.array(stored_embedding)
                
                # Calculate cosine similarity
                cosine_similarity = np.dot(query_embedding, stored_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                )
                
                # Append (file_name, chunk, cosine_similarity)
                similar_content.append((result[0], result[1], cosine_similarity))

            # Sort the results based on cosine similarity in descending order
            similar_content.sort(key=lambda x: x[2], reverse=True)
            # Call the external function with the best match (assuming it is the top result)
            find_page_number(similar_content[0][1], similar_content[0][0], query)

            return similar_content[:top_k]
        except Exception as e:
            print(f"An error occurred while retrieving similar content: {e}")
            return None

    def delete_chunks_by_file_name(self, file_name):
        try:
            delete_query = """
            DELETE FROM VecIndex WHERE file_name = ?;
            """
            self.cursor.execute(delete_query, (file_name,))
            self.conn.commit()
            print(f"Chunks for file '{file_name}' deleted successfully.")
        except Exception as e:
            print(f"An error occurred while deleting chunks: {e}")

    def __del__(self):
        # Close the connection when the instance is destroyed
        self.conn.close()
