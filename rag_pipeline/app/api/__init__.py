from fastapi import APIRouter
from app.api.endpoints import upload, intial  # Import endpoint routers

# Initialize the main API router
api_router = APIRouter()

# Include the upload endpoint router with a specific prefix and tag
api_router.include_router(
    upload.router,
    prefix="/upload",
    tags=["upload"]
)

# Include the initial endpoint router with a specific prefix and tag
api_router.include_router(
    intial.router,
    prefix="/other",
    tags=["other"]
)