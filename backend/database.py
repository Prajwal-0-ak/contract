import os
from psycopg2 import pool
from dotenv import load_dotenv
import json
from utils.evaluation import find_page_number


class DatabaseManager:
    def __init__(self):
        load_dotenv()
        connection_string = os.getenv("DATABASE_URL")
        self.connection_pool = pool.SimpleConnectionPool(
            1,
            10,
            connection_string,
        )
        if self.connection_pool:
            print("Connection pool created successfully")
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        conn = self.connection_pool.getconn()
        try:
            curr = conn.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS VecIndex (
                id BIGSERIAL PRIMARY KEY,
                file_name TEXT,
                chunk TEXT,
                chunk_embedding VECTOR(1024)
            );
            """
            curr.execute(create_table_query)
            conn.commit()
            print("Table 'VecIndex' is ready.")
        finally:
            self.connection_pool.putconn(conn)

    def insert_sample_data(self, file_name, chunk, chunk_embedding):
        conn = self.connection_pool.getconn()
        try:
            curr = conn.cursor()
            chunk_embedding_str = json.dumps(
                chunk_embedding
            )  # Convert to JSON array string
            insert_query = """
            INSERT INTO VecIndex (file_name, chunk, chunk_embedding)
            VALUES (%s, %s, %s);
            """
            curr.execute(insert_query, (file_name, chunk, chunk_embedding_str))
            conn.commit()
            print("Sample data inserted successfully.")
        except Exception as e:
            print(f"An error occurred while inserting data: {e}")
        finally:
            self.connection_pool.putconn(conn)

    def retrieve_similar_content(self, query, embedding, top_k=5):
        conn = self.connection_pool.getconn()
        try:
            curr = conn.cursor()
            # Convert the embedding list to a PostgreSQL array format
            embedding_str = f"ARRAY[{', '.join(map(str, embedding))}]::vector"

            # Use the <=> operator for similarity search with pgvector
            db_query = f"""
                SELECT file_name, chunk, 1 - (chunk_embedding <=> {embedding_str}) AS cosine_similarity
                FROM VecIndex
                ORDER BY cosine_similarity DESC
                LIMIT %s;
            """
            curr.execute(db_query, (top_k,))
            results = curr.fetchall()
            find_page_number(results[0][1], results[0][0], query)
            return results
        finally:
            self.connection_pool.putconn(conn)

    def delete_chunks_by_file_name(self, file_name):
        conn = self.connection_pool.getconn()
        try:
            curr = conn.cursor()
            delete_query = """
            DELETE FROM VecIndex WHERE file_name = %s;
            """
            curr.execute(delete_query, (file_name,))
            conn.commit()
            print(f"Chunks for file '{file_name}' deleted successfully.")
        finally:
            self.connection_pool.putconn(conn)

    def __del__(self):
        self.connection_pool.closeall()
