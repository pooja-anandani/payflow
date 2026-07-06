from numbers import Number

from pydantic import BaseModel, field_validator, EmailStr
from uuid import UUID


class CustomerCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone_number: str
    preferred_currency: str

    @field_validator("name")
    def validate_name(cls, v):
        if not v.replace(" ", "").isalpha():
            raise ValueError("Name must contain only letters")
        if len(v) < 2 or len(v) > 50:
            raise ValueError("Name must be between 2-50 characters")
        return v

    @field_validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("preferred_currency")
    def currency_valid(cls, v):
        allowed = ["CAD", "USD", "EUR", "GBP"]
        if v.upper() not in allowed:
            raise ValueError(f"Currency must be one of {allowed}")
        return v.upper()


class CustomerLogin(BaseModel):
    email: str
    password: str


class CustomerResponse(BaseModel):
    id: UUID
    name: str
    email: str
    phone_number: str
    preferred_currency: str

    # By default, Pydantic only reads from dicts.
    # from_attributes=True tells Pydantic to also read from object attributes,
    # allowing it to serialize SQLAlchemy models directly.
    # FastAPI calls CustomerResponse.model_validate(new_customer) under the hood,
    # mapping SQLAlchemy model fields to Pydantic schema fields.
    model_config = {"from_attributes": True}
