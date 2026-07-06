from typing import Any

from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException

from app.models.merchant import Merchant
from app.schemas.merchant import MerchantCreate, MerchantLogin


def create_merchant(db: Session, merchant: MerchantCreate) -> Merchant:
    existing_merchant = (
        db.query(Merchant).filter(Merchant.email == merchant.email).first()
    )
    if existing_merchant:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_merchant = Merchant(
        email=merchant.email,
        password_hash=hash_password(merchant.password),
        name=merchant.name,
        business_registration_id=merchant.business_registration_id,
        phone_number=merchant.phone_number,
        settlement_currency=merchant.settlement_currency,
        street=merchant.street,
        city=merchant.city,
        province=merchant.province,
        country=merchant.country,
        postal_code=merchant.postal_code,
    )
    db.add(new_merchant)
    db.commit()
    db.refresh(new_merchant)
    return new_merchant


def authenticate_merchant(db: Session, merchant: MerchantLogin) -> dict[str, str | Any]:
    existing_merchant = (
        db.query(Merchant).filter(Merchant.email == merchant.email).first()
    )
    if not existing_merchant:
        raise HTTPException(status_code=404, detail="Account not found")
    password_verification = verify_password(
        plain_password=merchant.password,
        hashed_password=existing_merchant.password_hash,
    )
    if not password_verification:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    bearer_token = create_access_token(
        {"sub": str(existing_merchant.id), "role": existing_merchant.role.value}
    )
    return {"access_token": bearer_token, "token_type": "bearer"}


def get_merchant(db: Session, user_id: str) -> Merchant | None:
    merchant_details = db.query(Merchant).filter(Merchant.id == user_id).first()
    if not Merchant:
        raise HTTPException(status_code=404, detail="Account not found")
    return merchant_details
