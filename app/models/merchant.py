from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from datetime import datetime, timezone
import uuid

from app.models.enums import UserRole


class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name = Column(String)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String)
    webhook_url = Column(String)
    business_registration_id = Column(String)
    street = Column(String)
    city = Column(String)
    province = Column(String)
    country = Column(String, nullable=False)
    postal_code = Column(String)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.MERCHANT)
    settlement_currency = Column(String)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )
