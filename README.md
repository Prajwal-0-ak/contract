# Contract Analysis System

## Table of Contents

- [Contract Analysis System](#contract-analysis-system)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Architecture](#architecture)
    - [Frontend](#frontend)
      - [Key Components](#key-components)
      - [Workflow](#workflow)
    - [Backend](#backend)
      - [Key Modules](#key-modules)
      - [Workflow](#workflow-1)
    - [Processing Pipelines](#processing-pipelines)
      - [Retrieval-Augmented Generation (RAG) Pipeline](#retrieval-augmented-generation-rag-pipeline)
      - [Fuzzy Keyword Matching Pipeline](#fuzzy-keyword-matching-pipeline)
  - [Technology Stack](#technology-stack)
    - [Frontend](#frontend-1)
    - [Backend](#backend-1)
    - [Database and Storage](#database-and-storage)
    - [Deployment and DevOps](#deployment-and-devops)
    - [Miscellaneous](#miscellaneous)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Environment Setup](#environment-setup)
      - [Clone the Repository](#clone-the-repository)
      - [Set Up Environment Variables](#set-up-environment-variables)
      - [Backend Dependencies](#backend-dependencies)
      - [Frontend Dependencies](#frontend-dependencies)
    - [Development Setup](#development-setup)
      - [Starting the Backend Service for RAG Pipeline:](#starting-the-backend-service-for-rag-pipeline)
      - [For the fuzzy pipeline:](#for-the-fuzzy-pipeline)
      - [Starting the Frontend Application](#starting-the-frontend-application)
    - [Docker Setup (Optional)](#docker-setup-optional)
    - [Processing Flow](#processing-flow)
      - [File Upload](#file-upload)
      - [File Reception and Storage](#file-reception-and-storage)
      - [Pipeline Selection](#pipeline-selection)
      - [Document Processing](#document-processing)
      - [Response to Frontend](#response-to-frontend)
      - [Data Visualization and Export](#data-visualization-and-export)
  - [Directory Structure](#directory-structure)
    - [Root Directory](#root-directory)
    - [Backend Directory (`backend/`)](#backend-directory-backend)
    - [Frontend Directory (`frontend/`)](#frontend-directory-frontend)
    - [Fuzzy Matching Pipeline Directory (`fuzzy/`)](#fuzzy-matching-pipeline-directory-fuzzy)

## Overview

The Contract Analysis System is a professional tool designed for financial analysts and accountants to efficiently manage and analyze contract documents. Users can upload contract files, and the application will automatically extract essential fields, display them in a comprehensive table, and provide an option to download the data in Excel format. Leveraging advanced AI-driven pipelines, the system ensures accurate data extraction and seamless integration between the frontend and backend components.

## Features

- **Contract Upload:** Easily upload contract PDFs through an intuitive frontend interface.
- **Dual Processing Pipelines:** 
    - **RAG Pipeline:** Advanced data extraction using Retrieval-Augmented Generation.
    - **Fuzzy Matching Pipeline:** Quick extraction using fuzzy keyword matching.
- **Automated Data Extraction:** Extracts essential fields such as company name, currency, SOW dates, COLA, FTE counts, and more.
- **Data Visualization:** Displays extracted information in a searchable table.
- **Excel Export:** Download extracted data as an Excel (`.csv`) file.
- **Integrated PDF Viewer:** Review documents with navigation, zoom, and search functionalities.
- **Responsive Frontend:** Built with Next.js for a user-friendly experience across devices.
- **Backend API with FastAPI:** High-performance API for rapid data processing.
- **Database Integration:** Utilizes Milvus Vector Database for efficient data storage and retrieval.
- **Dockerized Deployment:** Consistent environments through Docker configurations.
- **Configuration Management:** Centralized settings in `backend/config.yaml` and `fuzzy/config.yaml`.
- **Version Control and Environment Management:** Secure management with `.gitignore` and `.env` files.

## Architecture

### Frontend

Located in the [`frontend/`](frontend/) directory, built with Next.js and TypeScript, providing an interactive interface for uploading contracts and viewing extracted data.

#### Key Components

- **Main Page:** Handles file uploads and manages state.
- **FileUpload Component:** Renders the file input field with drag-and-drop functionality.
- **PDFViewer Component:** Displays uploaded PDFs using `pdfjs`.
- **ContractDataTable Component:** Shows extracted data in a table with search and sort features.

#### Workflow

1. **File Upload:** Users upload PDFs via the `FileUpload` component.
2. **Contract Form:** Users enter's the some of the manually entered field values about the contract and contract type.
3. **File Preview:** PDFs are displayed using the `PDFViewer` component.
4. **Processing Request:** Users select the desired pipeline for processing.
5. **Loading Indicator:** `LoadingSpinner` displays processing status.
6. **Data Display:** Extracted data is shown in `ContractDataTable`.
7. **Data Export:** Users can download data as an Excel file.

### Backend

Resides in the [`backend/`](backend/) directory, built with FastAPI, handling file uploads, processing documents, extracting fields, and interacting with the database.

#### Key Modules

- **API Entry Point:** Defines API endpoints and integrates CORS middleware.
- **Document Processing:** Loads and cleans documents from PDF files.
- **Field Extraction:** Uses AI models to extract specified fields using OpenAI API.
- **Database Management:** Interacts with Milvus for embedding storage.
- **Utilities:** Provides text processing and data conversion functions.

#### Workflow

1. **File Upload Handling:** Receives and saves uploaded files.
2. **Document Loading:** Reads and cleans PDF content.
3. **Content Chunking:** Splits text based on `chunk_size` and `chunk_overlap`.
4. **Embedding and Storage:** Generates embeddings and stores them in Milvus.
5. **Field Extraction:** Retrieves relevant content and extracts field values using OpenAI API.
6. **Result Compilation:** Aggregates extracted data into JSON.
7. **Response to Frontend:** Sends JSON with extracted fields to the frontend.

### Processing Pipelines

Supports two pipelines for contract analysis:

#### Retrieval-Augmented Generation (RAG) Pipeline

- **Purpose:** Advanced AI-driven extraction using language models.
- **Components:** Embedding model, Milvus vector database.
- **Flow:** Chunking → Embedding → Similarity Search → Language Model Processing.
- **Advantages:** Handles complex queries with context-aware extraction.
- **Execution:** Runs via [`backend/api.py`](backend/api.py) on port `8000`.

#### Fuzzy Keyword Matching Pipeline

- **Purpose:** Quick extraction using fuzzy string matching.
- **Components:** FuzzyWuzzy library.
- **Flow:** Text Extraction → Keyword Matching → Data Extraction.
- **Advantages:** Faster processing for straightforward tasks.
- **Execution:** Runs via [`fuzzy/main.py`](fuzzy/main.py) on port `8080`.

## Technology Stack

### Frontend

- **Next.js, React, TypeScript**
- **Tailwind CSS, Shadcn UI Components**
- **PDFjs, Axios**

### Backend

- **Python 3, FastAPI, Uvicorn**
- **LangChain, OpenAI API**
- **Sentence Transformers, Milvus**
- **PyPDF, FuzzyWuzzy**
- **Pandas, NumPy, Levenshtein**
- **Dotenv**

### Database and Storage

- **Milvus Vector Database**

### Deployment and DevOps

- **Docker, Docker Compose**
- **Git, GitHub**

### Miscellaneous

- **OpenAI GPT Models, Torch (PyTorch)**
- **Python-Multipart, PSYCOPG2-Binary**
- **YAML**

## Installation

### Prerequisites

- **Python 3.10+**
- **Node.js v18+**
- **npm**
- **Docker & Docker Compose** (optional)
- **Git**
- **Virtual Environment Tools (`venv`, `conda`)**
- **OpenAI API Key**
- **Minimum System Requirements:**
    - 8GB RAM (16GB recommended)
    - 4 CPU cores
    - 2GB free disk space for embedding models
    - CUDA-compatible GPU recommended but not required

### Environment Setup

#### Clone the Repository

```bash
git clone https://github.com/Prajwal-0-ak/contract.git
cd contract
```

#### Set Up Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your-openai-api-key
```

#### Backend Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend Dependencies

```bash
cd frontend
npm install
```

### Development Setup

#### Starting the Backend Service for RAG Pipeline:

```bash
cd backend
uvicorn api:app --reload --port 8000
```

#### For the fuzzy pipeline:

```bash
cd fuzzy
python main.py
```

#### Starting the Frontend Application

```bash
cd frontend
npm run dev
```

### Docker Setup (Optional)

```bash
docker-compose up --build
docker-compose down
```

### Processing Flow

#### File Upload

- Upload PDFs via frontend and the user select the contract type, enter the contract details, and select the pipeline.
- Backend receives and saves files.

#### File Reception and Storage

- Files saved to `contract_files/` for processing.

#### Pipeline Selection

Choose between **RAG Pipeline** and **Fuzzy Matching Pipeline**.

#### Document Processing

**RAG Pipeline:**

1. **Loading:** Read and extract text from PDF.
2. **Chunking:** Split text into chunks.
3. **Embedding:** Generate embeddings.
4. **Storage:** Save embeddings in Milvus.
5. **Extraction:** Retrieve content and extract fields using OpenAI API.
6. **Compilation:** Aggregate data into JSON.

**Fuzzy Matching Pipeline:**

1. **Extraction:** Extract raw text from PDF.
2. **Matching:** Perform fuzzy keyword matching.
3. **Data Collection:** Gather extracted values.

#### Response to Frontend

- Backend sends extracted data as JSON.
- Frontend displays data in a table and offers Excel export.

#### Data Visualization and Export

- Interactive table with extracted fields.
- Option to download data as `.csv`.

## Directory Structure

### Root Directory

- **.env**
- **.gitignore**
- **backend/** 
- **frontend/** 
- **fuzzy/** 
- **compose.yaml**

### Backend Directory (`backend/`)

- **api.py**
- **app.py**
- **config.yaml**
- **contract_files/**
- **extract_fields.py**
- **process_docs.py**
- **database.py**
- **utils/**
- **requirements.txt**

### Frontend Directory (`frontend/`)

- **app/**
- **components/**
- **public/**
- **package.json**

### Fuzzy Matching Pipeline Directory (`fuzzy/`)

- **main.py**
