import os
import logging

import cognitojwt

from app.schemas.cognito import CognitoClaims

# Get environment variables
REGION = os.environ.get("AWS_REGION")
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

    _claims = await cognitojwt.decode_async(
        token=token,
        region=REGION,
        userpool_id=COGNITO_USER_POOL_ID,
        app_client_id=COGNITO_CLIENT_ID,
    )
    claims = CognitoClaims.model_validate(_claims)
    return claims


