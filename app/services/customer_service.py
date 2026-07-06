from typing import Any

from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException
from app.schemas.customer import CustomerCreate, CustomerLogin
from app.models.customer import Customer


def create_customer(db: Session, customer: CustomerCreate) -> Customer:
    existing_customer = (
        db.query(Customer).filter(Customer.email == customer.email).first()
    )
    if existing_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_customer = Customer(
        email=customer.email,
        password_hash=hash_password(customer.password),
        name=customer.name,
        phone_number=customer.phone_number,
        preferred_currency=customer.preferred_currency,
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


def authenticate_customer(db: Session, customer: CustomerLogin) -> dict[str, str | Any]:
    existing_customer = (
        db.query(Customer).filter(Customer.email == customer.email).first()
    )
    if not existing_customer:
        raise HTTPException(status_code=404, detail="Customer doesn't exists")
    password_verification = verify_password(
        plain_password=customer.password,
        hashed_password=existing_customer.password_hash,
    )
    if not password_verification:
        raise HTTPException(status_code=401, detail="Invalid password")
    bearer_token = create_access_token(
        {"sub": str(existing_customer.id), "role": existing_customer.role.value}
    )
    return {"access_token": bearer_token, "token_type": "bearer"}


def get_customer(db: Session, user_id: str) -> Customer | None:
    customer_details = db.query(Customer).filter(Customer.id == user_id).first()
    if not customer_details:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer_details
