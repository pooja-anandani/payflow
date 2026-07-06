from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.sqltypes import Numeric

from app.core.database import Base
from datetime import datetime, timezone
import uuid


class CustomerAccount(Base):
    __tablename__ = "customer_accounts"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    customer_id = Column(ForeignKey("customers.id"))
    account_number = Column(String, nullable=False, unique=True)
    current_balance = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    locked_balance = Column(Numeric(precision=18, scale=2), nullable=False, default=0)
    currency = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )
