from typing import cast
from fastapi import HTTPException, status
from starlette.requests import Request

from app.schemas.cognito import CognitoClaims


def get_cognito_user_claims(request: Request) -> CognitoClaims:
    """
    Get the current authenticated user from request state.
    This dependency should be used for endpoints that require authentication.
    
    Args:
        request: The request object with user data in state
        
    Returns:
        The user claims from the JWT token
        
    Raises:
        HTTPException: If no authenticated user is found
    """
    if not hasattr(request.state, "claims") or not request.state.claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )
    claims = cast(CognitoClaims, request.state.claims)
    
    return claims
