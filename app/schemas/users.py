from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict


class UserResponse(BaseModel):
    """Response model for user data with sensitive fields excluded."""
    id: Annotated[str, Field(description="Unique identifier for the user")]
    handle: Annotated[str, Field(description="User's unique handle/username")]

    # Use ConfigDict for model configuration
    model_config = ConfigDict(from_attributes=True)
