from datetime import datetime
from datetime import timezone
from enum import Enum
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.chatbot import Chatbot


class SyncStatus(str, Enum):
    NA = 'NA'
    IN_PROGRESS = 'IN_PROGRESS'
    SYNCED = 'SYNCED'
    FAILED = 'FAILED'


class Document(Base):
    __tablename__ = 'documents'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid.uuid4,
        init=False
    )
    chatbot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('chatbots.id'),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(nullable=False)
    sync_msg: Mapped[str] = mapped_column(nullable=True)
    mime_type: Mapped[str] = mapped_column(String(255), default='application/octet-stream', nullable=False)
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
    sync_status: Mapped[SyncStatus] = mapped_column(
        SQLAlchemyEnum(SyncStatus),
        default=SyncStatus.NA,
        nullable=False
    )

    chatbot: Mapped['Chatbot'] = relationship(back_populates='documents', init=False)