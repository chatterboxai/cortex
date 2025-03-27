from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy import DateTime


class Base(MappedAsDataclass, DeclarativeBase):
    """Base class for all models"""
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        primary_key=True,
        init=False,
        default=lambda: str(uuid.uuid4())
    )
    cognito_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    handle: Mapped[str] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc)
    )
