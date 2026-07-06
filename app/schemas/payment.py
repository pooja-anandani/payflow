from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID


class PaymentCreate(BaseModel):
    merchant_id: UUID
    amount: Decimal
    currency: str
    idempotency_key: str

    @field_validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must not be 0 or negative")
        if v > 500:
            raise ValueError("Amount should be less than 500")
        return v

    @field_validator("currency")
    def validate_currency(cls, v):
        allowed = ["CAD", "USD", "EUR", "GBP"]
        if v.upper() not in allowed:
            raise ValueError(f"Currency must be one of {allowed}")
        return v.upper()


class PaymentResponse(BaseModel):
    id: UUID
    customer_id: UUID
    merchant_id: UUID
    amount: Decimal
    currency: str
    status: str
    description: Optional[str] = None
    failure_reason: Optional[str] = None
    completed_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PaymentStatusUpdate(BaseModel):
    id: UUID
    status: str
    description: str
    failure_reason: Optional[str] = None
    completed_at: Optional[datetime] = None


class PaymentHistoryResponse(BaseModel):
    data: list[PaymentResponse]
    next_cursor: Optional[datetime] = None
