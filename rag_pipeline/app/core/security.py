
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class BasicAuth(HTTPBearer):
    """
    Implements HTTP Bearer authentication for FastAPI applications.
    """

    async def __call__(self, request: Request) -> str:
        """
        Extract and validate bearer credentials from the incoming request.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            str: The bearer token if valid.

        Raises:
            HTTPException: If credentials are missing or invalid.
        """
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials and credentials.credentials:
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or missing authorization credentials."
            )