# Use a slim Python base image
FROM python:3.9-slim

# Install necessary system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-venv \
        git \
        npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# ----------------------
# RAG Pipeline Setup
# ----------------------

# Copy requirements.txt to the root directory for better caching
COPY requirements.txt ./

# Remove 'torch' and 'sentence-transformers' from requirements to install them separately
RUN sed -i '/^torch$/d' requirements.txt && \
    sed -i '/^sentence-transformers$/d' requirements.txt

# Create and activate virtual environment
RUN python3 -m venv /env-rag

# Upgrade pip and install RAG pipeline dependencies
RUN /env-rag/bin/pip install --upgrade pip && \
    /env-rag/bin/pip install --no-cache-dir -r requirements.txt

# Install CPU-only PyTorch and sentence-transformers separately
RUN /env-rag/bin/pip install --no-cache-dir torch==2.0.1+cpu \
    -f https://download.pytorch.org/whl/cpu/torch_stable.html && \
    /env-rag/bin/pip install --no-cache-dir sentence-transformers

# Copy the RAG pipeline source code
COPY rag_pipeline/ ./rag_pipeline/

# ----------------------
# Fuzzy Pipeline Setup
# ----------------------

# Copy the fuzzy pipeline source code
COPY fuzzy_pipeline/ ./fuzzy_pipeline/

# ----------------------
# Frontend Setup
# ----------------------

# Copy frontend package files first for better caching
COPY frontend/package*.json ./frontend/

# Install frontend dependencies
RUN cd frontend && npm install

# Copy the frontend source code
COPY frontend/ ./frontend/

# Build the frontend
RUN cd frontend && npm run build

# ----------------------
# Expose Ports
# ----------------------

EXPOSE 3000 8000 8080

# ----------------------
# Start Services
# ----------------------

CMD ["sh", "-c", "cd rag_pipeline && /env-rag/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 & \
                 cd ../fuzzy_pipeline && /env-rag/bin/uvicorn main:app --host 0.0.0.0 --port 8080 & \
                 cd ../frontend && npm start"]