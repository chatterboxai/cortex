from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict


class CognitoClaims(BaseModel):
    """Claims from a verified Cognito JWT token."""
    
    # Make the model immutable/frozen
    model_config = ConfigDict(frozen=True)
    
    sub: Annotated[str, Field(description="Subject identifier (user ID)")]
    iss: Annotated[str, Field(description="Token issuer")]
    client_id: Annotated[str, Field(description="Client application ID")]
    origin_jti: Annotated[str, Field(description="Original JWT ID")]
    event_id: Annotated[str, Field(description="Event identifier")]
    token_use: Annotated[str, Field(description="Token usage type")]
    scope: Annotated[str, Field(description="Token scope")]
    auth_time: Annotated[int, Field(description="Authentication timestamp")]
    exp: Annotated[int, Field(description="Expiration timestamp")]
    iat: Annotated[int, Field(description="Issued at timestamp")]
    jti: Annotated[str, Field(description="JWT ID")]
    username: Annotated[str, Field(description="User's username")]
