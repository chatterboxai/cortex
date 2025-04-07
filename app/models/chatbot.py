from datetime import datetime, timezone
from sqlalchemy import JSON, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import UUID
import uuid
from app.models.base import Base
from typing import TYPE_CHECKING, Any
from app.config.settings import load_default_chatbot_settings_dict

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.document import Document
    from app.models.dialogue import Dialogue


class Chatbot(Base):
    __tablename__ = 'chatbots'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True, 
        init=False,
        default_factory=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id'),
        nullable=False
    )
    is_public: Mapped[bool] = mapped_column(nullable=False, default=False)
    settings: Mapped[JSON] = mapped_column(
        JSONB, 
        nullable=False, 
        default_factory=load_default_chatbot_settings_dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default_factory=lambda: datetime.now(timezone.utc),
        init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default_factory=lambda: datetime.now(timezone.utc),
        init=False
    )

    # Set init=False for the relationship so it doesn't need to be in __init__
    owner: Mapped['User'] = relationship(back_populates='chatbots', init=False)
    documents: Mapped[list['Document']] = relationship(
        back_populates='chatbot', 
        init=False
    )
    dialogues: Mapped[list['Dialogue']] = relationship(
        back_populates='chatbot', 
        init=False
    )