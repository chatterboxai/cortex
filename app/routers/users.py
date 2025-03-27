from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from app.auth.dependencies import get_cognito_user_claims
from app.schemas.cognito import CognitoClaims
from app.schemas.users import UserResponse
from app.services.users import find_or_create_user

logger = logging.getLogger(__name__)

# Define router
router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# Define the security scheme
security = HTTPBearer(
    scheme_name="AWS Cognito JWT",
    description="AWS Cognito JWT Bearer token",
    auto_error=False
)

@router.get(
    "/profile", 
    response_model=UserResponse,
    summary="Get user profile",
    description="Retrieves the current user's profile using their Cognito token. Requires a valid AWS Cognito JWT token in the Authorization header."
)
async def get_user_profile_endpoint(
    user_claims: CognitoClaims = Depends(get_cognito_user_claims),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """
    Get the current authenticated user's profile.
    
    - **Authorization**: Requires a valid AWS Cognito JWT Bearer token
    - Format: `Authorization: Bearer your-token-here`
    """
    logger.info(credentials)
    user = await find_or_create_user(
        cognito_id=user_claims.sub,
        handle=user_claims.username
    )
    
    return user