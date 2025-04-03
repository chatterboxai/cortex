from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from sqlalchemy import UUID, DateTime
from app.models.base import Base
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.chatbot import Chatbot


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        init=False,
        default_factory=uuid.uuid4
    )
    cognito_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    handle: Mapped[str] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default_factory=lambda: datetime.now(timezone.utc),
        init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        init=False
    )
    
    # Add relationship to chatbots with init=False
    chatbots: Mapped[List["Chatbot"]] = relationship(
        back_populates="owner", 
        init=False
    )
