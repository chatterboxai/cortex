from typing import Annotated
from fastapi import APIRouter
from fastapi import Depends
import logging
from app.auth.dependencies import get_authenticated_user
from app.auth.dependencies import get_cognito_claims
from app.auth.dependencies import security
from app.schemas.users import UserResponse
from app.models.users import User

from app.schemas.cognito import CognitoClaims
from app.services.users import create_user

logger = logging.getLogger(__name__)


# Define router
router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    dependencies=[Depends(security)],
)


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get or create user profile",
    description=(
        "Retrieves the current user's profile using their Cognito token. "
        "If the user does not exist, it will be created."
        "Requires a valid AWS Cognito JWT token in the Authorization header."
    ),
)
async def get_or_create_user_profile(
    user: Annotated[User | None, Depends(get_authenticated_user)],
    cognito_claims: Annotated[CognitoClaims, Depends(get_cognito_claims)],
):
    if not user:
        user = await create_user(
            cognito_id=cognito_claims.sub,
            handle=cognito_claims.username,
        )
    
    return user
