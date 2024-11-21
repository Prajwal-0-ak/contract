from fastapi import APIRouter

# Create a new APIRouter instance
router = APIRouter()

@router.get("/status")
def get_status():
    """
    Endpoint to get the application's status.

    Returns:
        dict: A dictionary containing the status of the application.
    """
    # Return a JSON response indicating the server status
    return {"status": "Server is running!"}