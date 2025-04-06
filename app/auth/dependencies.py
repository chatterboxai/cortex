from typing import Annotated, cast
from fastapi import Depends, HTTPException, status

from fastapi.security import HTTPBearer
from starlette.requests import Request

from app.schemas.cognito import CognitoClaims
from app.models.users import User
from app.services.users import find_user_by_cognito_id

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
    claims: Annotated[CognitoClaims | None, Depends(get_cognito_claims)]
) -> User | None:
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User not authenticated"
        )

    cognito_id = claims.sub
    return await find_user_by_cognito_id(cognito_id)
