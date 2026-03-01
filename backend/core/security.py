from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from backend.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Validates that the incoming request has the correct APP_SECRET_PIN in the X-API-Key header.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header. Please log in to the frontend first.",
        )
    
    if api_key != settings.APP_SECRET_PIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid PIN provided.",
        )
    
    return api_key
