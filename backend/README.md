# Contract Analysis Backend

This is the backend for the Contract Analysis System, built with FastAPI.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   Create a `.env` file in the backend directory with the following content:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

3. Run the server:
   ```
   uvicorn api:app --reload
   ```

## API Endpoints

- `GET /`: Health check endpoint
- `POST /upload`: Upload and process a contract file

## Configuration

The `config.yaml` file contains important configuration settings, including:

- Embedding model name
- Fields to extract
- Query templates for field extraction
- Prompt template for the AI model

## Components

- `api.py`: Main FastAPI application
- `process_docs.py`: Handles document loading and processing
- `extract_fields.py`: Manages field extraction using AI
- `database.py`: Handles database operations (not provided in the snippets)

## Docker

To run the backend in a Docker container, use the Dockerfile in the root directory.