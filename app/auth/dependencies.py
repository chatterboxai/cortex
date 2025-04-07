from typing import Annotated, cast
from fastapi import Depends, HTTPException, status
from uuid import UUID
from fastapi.security import HTTPBearer
from starlette.requests import Request
import logging
from app.schemas.cognito import CognitoClaims
from app.models.users import User
from app.services.users import create_user, find_user_by_cognito_id
from app.services.chatbot import ChatbotService

security = HTTPBearer(
    scheme_name="AWS Cognito JWT",
    description="AWS Cognito JWT Bearer token",
    auto_error=True
)


async def get_cognito_claims(
    request: Request,
) -> CognitoClaims:
    if not hasattr(request.state, "claims") or not request.state.claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User not authenticated"
        )
    return cast(CognitoClaims, request.state.claims)


async def get_authenticated_user(
    request: Request,
    claims: Annotated[CognitoClaims, Depends(get_cognito_claims)]
) -> User:
    """Get the authenticated user from the request, based on the Cognito claims.
    
    Returns: `User` object if the user is authenticated and found in the database.
    Creates a new user if the user is authenticated but not found in the database.
    
    Raises HTTPException if the request is not authenticated
    """
    cognito_id = claims.sub
    user = await find_user_by_cognito_id(cognito_id)
    if not user:
        user = await create_user(cognito_id, claims.username)
    return user


async def get_chatbot_owner(
    chatbot_id: UUID,
    user: Annotated[User, Depends(get_authenticated_user)]
) -> User:
    chatbot = await ChatbotService.afind_by_id(chatbot_id)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    if chatbot.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to access this chatbot"
        )
    return user
