from fastapi import APIRouter, Depends

from app.auth.dependencies import get_cognito_user_claims
from app.schemas.cognito import CognitoClaims
from app.schemas.users import UserResponse
from app.services.users import find_or_create_user

# Define router
router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/profile", response_model=UserResponse)
async def get_user_profile_endpoint(
    user_claims: CognitoClaims = Depends(get_cognito_user_claims)
):
    """Get the current authenticated user's profile."""
    user = await find_or_create_user(
        cognito_id=user_claims.sub,
        handle=user_claims.username
    )
    
    return user

