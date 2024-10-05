import sqlite3
import sqlite_vec
import json
import struct
import numpy as np
from dotenv import load_dotenv
from utils.evaluation import find_page_number

class DatabaseManager:
    def _init_(self):
        load_dotenv()
        # Connect to the SQLite database and load sqlite_vec extension
        self.conn = sqlite3.connect('vecindex.sqlite')
        self.conn.enable_load_extension(True)
        print("AAAAA")
        sqlite_vec.load(self.conn)  # Load the sqlite_vec extension for vector operations
        print("BBBBB")
        self.cursor = self.conn.cursor()
        print("CCCCC")
        self.create_table_if_not_exists()


    @staticmethod
    def serialize(vector: list[float]) -> bytes:
        """
        Serializes a list of floats into a compact "raw bytes" format. Taken from:
        https://github.com/asg017/sqlite-vec/blob/496560cf9ac4b358ea43793e591f376c02c16b90/examples/python-recipes/openai-sample.py#L10
        """
        return struct.pack("%sf" % len(vector), *vector)


    def create_table_if_not_exists(self):
        create_chunks_table_query = """
        CREATE TABLE IF NOT EXISTS text_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            chunk TEXT NOT NULL,
        );
        """

        create_vector_index_table_query = """
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_idx USING vec0 (
            id INTEGER PRIMARY KEY,
            embedding FLOAT[1024]
        );
        """

        self.cursor.execute(create_chunks_table_query)
        self.cursor.execute(create_vector_index_table_query)
        self.conn.commit()
        print("Table 'text_chunks' and 'vec_idx' is ready.")


    def insert_sample_data(self, file_name, chunk, chunk_embedding):
        try:
            # Convert embedding to bytes and insert
            # chunk_embedding_bytes = json.dumps(chunk_embedding).encode('utf-8')
            insert_chunk_query = """
            INSERT INTO text_chunks (file_name, chunk)
            VALUES (?, ?)
            """

            insert_emb_query = """
            INSERT INTO vec_idx (embedding)
            VALUES (?)
            """
            self.cursor.execute(insert_chunk_query, (file_name, chunk))
            self.cursor.execute(insert_emb_query, (DatabaseManager.serialize(chunk_embedding), ))
            self.conn.commit()
            print("Sample data inserted successfully.")
        except Exception as e:
            print(f"An error occurred while inserting data: {e}")

    def retrieve_similar_content(self, query, embedding, top_k=5):
        try:
            # Convert the embedding list to a NumPy array
            query_embedding = np.array(embedding)

            # Retrieve all chunks from the database
            db_query = """
                SELECT
                    vec_idx.id,
                    distance,
                    file_name,
                    chunk,
                    chunk_embedding
                FROM vec_idx
                LEFT JOIN text_chunks ON text_chunks.id = vec_idx.id
                WHERE embedding MATCH ?
                    AND k = ?
                ORDER BY distance
            """
            self.cursor.execute(db_query, (DatabaseManager.serialize(query_embedding), top_k))
            results = self.cursor.fetchall()

            similar_content = []
            for result in results:
                # Append (file_name, chunk, cosine_similarity)
                similar_content.append((result[2], result[3], result[1]))

            # Call the external function with the best match (assuming it is the top result)
            # find_page_number(similar_content[0][1], similar_content[0][0], query)

            return similar_content
        except Exception as e:
            print(f"An error occurred while retrieving similar content: {e}")
            return None

    def delete_chunks_by_file_name(self, file_name):
        # TODO: remove redundant file_name argument
        try:
            delete_query = """
            TRUNCATE TABLE text_chunks;
            """
            self.cursor.execute(delete_query)
            delete_query = """
            TRUNCATE TABLE vec_idx;
            """
            self.cursor.execute(delete_query)
            self.conn.commit()
            print(f"Chunks deleted successfully.")
        except Exception as e:
            print(f"An error occurred while deleting chunks: {e}")

    def _del_(self):
        # Close the connection when the instance is destroyed
        self.conn.close()