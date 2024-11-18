# Use a slim Python base image
FROM python:3.9-slim

# Install necessary system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-venv \
        supervisor \
        git \
        npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# ----------------------
# Backend Setup
# ----------------------

# Copy backend requirements first for better caching
COPY backend/requirements.txt ./backend/

# Remove 'torch' and 'sentence-transformers' from requirements to install them separately
RUN sed -i '/^torch$/d' ./backend/requirements.txt && \
    sed -i '/^sentence-transformers$/d' ./backend/requirements.txt

# Create and activate virtual environment
RUN python3 -m venv /env-backend

# Upgrade pip and install backend dependencies
RUN /env-backend/bin/pip install --upgrade pip && \
    /env-backend/bin/pip install --no-cache-dir -r ./backend/requirements.txt

# Install CPU-only PyTorch and sentence-transformers separately
RUN /env-backend/bin/pip install --no-cache-dir torch==2.0.1+cpu \
    -f https://download.pytorch.org/whl/cpu/torch_stable.html && \
    /env-backend/bin/pip install --no-cache-dir sentence-transformers

# Copy the backend source code
COPY backend/ ./backend/

# ----------------------
# Fuzzy Pipeline Setup
# ----------------------

# Copy the fuzzy source code
COPY fuzzy/ ./fuzzy/

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
# Supervisor Configuration
# ----------------------

# Copy supervisor configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose necessary ports
EXPOSE 3000 8000 8080

# Start Supervisor to run all services
CMD ["/usr/bin/supervisord"]