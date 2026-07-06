from typing import Optional

from pydantic import BaseModel
from uuid import UUID


class MerchantCreate(BaseModel):
    email: str
    password: str
    name: str
    business_registration_id: str
    settlement_currency: str
    street: str
    city: str
    province: str
    country: str
    postal_code: str
    phone_number: str


class MerchantLogin(BaseModel):
    email: str
    password: str


class MerchantResponse(BaseModel):
    id: UUID
    email: str
    name: str
    business_registration_id: str
    settlement_currency: str
    street: str
    city: str
    province: str
    country: str
    postal_code: str
    webhook_url: Optional[str] = None
    phone_number: str
