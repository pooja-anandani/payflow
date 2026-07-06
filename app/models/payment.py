from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Numeric

from app.core.database import Base
from datetime import datetime, timezone
import uuid

from app.models.enums import PaymentStatus


class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"))
    amount = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    currency = Column(String)
    idempotency_key = Column(String, unique=True, nullable=False)
    description = Column(String)
    status = Column(
        Enum(PaymentStatus), default=PaymentStatus.INITIATED, nullable=False
    )
    failure_reason = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = Column(DateTime, nullable=True)
