
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core.config import settings

# Initialize FastAPI application with project settings
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# CORS Configuration
# Define the list of allowed origins for CORS
origins = [
    "http://localhost:3000",
    # Add other origins if needed
]

# Add CORS middleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,             # Allowed origins
    allow_credentials=True,            # Allow credentials
    allow_methods=["*"],               # Allowed HTTP methods
    allow_headers=["*"],               # Allowed headers
)

# Include the API router
app.include_router(api_router)