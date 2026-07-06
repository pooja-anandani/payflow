from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from datetime import datetime, timezone
import uuid

from app.models.enums import UserRole


class Customer(Base):
    __tablename__ = "customers"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name = Column(String)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String)
    preferred_currency = Column(String)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )
