import os
import logging

import cognitojwt

from app.schemas.cognito import CognitoClaims

# Get environment variables
REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")

logger = logging.getLogger(__name__)


async def verify_cognito_token(token: str) -> CognitoClaims:
    """
    Verify and decode an AWS Cognito JWT token.

    Args:
        token: The JWT token to verify

    Returns:
        CognitoClaims object containing the claims from the token

    Raises:
        CognitoJWTException: If token validation fails
    """

    # Use cognitojwt library to verify and decode the token
    _claims = await cognitojwt.decode_async(
        token=token,
        region=REGION,
        userpool_id=COGNITO_USER_POOL_ID,
        app_client_id=COGNITO_CLIENT_ID,
    )
    claims = CognitoClaims.model_validate(_claims)
    return claims


def extract_token_from_header(authorization_header: str | None) -> str | None:
    """
    Extract the JWT token from the Authorization header.

    Args:
        authorization_header: The Authorization header value

    Returns:
        The JWT token if found, None otherwise
    """
    if not authorization_header:
        return None

    parts = authorization_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]
