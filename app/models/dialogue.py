from datetime import datetime, timezone
from sqlalchemy import ARRAY, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.chatbot import Chatbot


class Dialogue(Base):
    __tablename__ = 'dialogues'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        init=False,
        default_factory=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    questions: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    answer: Mapped[str] = mapped_column(String(255), nullable=False)
    chatbot_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('chatbots.id'),
                                                  nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 nullable=False,
                                                 default_factory=datetime.now(timezone.utc), init=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 nullable=False, default_factory=datetime.now(timezone.utc), init=False)

    # Set init=False for the relationship so it doesn't need to be in __init__
    chatbot: Mapped['Chatbot'] = relationship(back_populates='dialogues', init=False)