import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.cache import get_redis
from app.models.customer import Customer
from app.models.customer_account import CustomerAccount
from app.models.enums import PaymentStatus
from app.models.merchant import Merchant
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentResponse

TERMINAL_STATES = [
    PaymentStatus.SUCCESS,
    PaymentStatus.ROLLED_BACK,
    PaymentStatus.REJECTED,
]


def create_payment(db: Session, payment: PaymentCreate, customer_id: str) -> Payment:
    existing_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not existing_customer:
        raise HTTPException(status_code=404, detail="Customer doesn't exists")

    existing_merchant = (
        db.query(Merchant).filter(Merchant.id == payment.merchant_id).first()
    )

    if not existing_merchant:
        raise HTTPException(status_code=404, detail="Merchant doesn't exists")

    existing_payment = (
        db.query(Payment)
        .filter(Payment.idempotency_key == payment.idempotency_key)
        .first()
    )
    if existing_payment:
        raise HTTPException(
            status_code=400, detail="Bad Request: Payment Already In Progress"
        )

    existing_balance = (
        db.query(CustomerAccount)
        .filter(CustomerAccount.customer_id == customer_id)
        .with_for_update()  # <- locks this row until transaction commits
        .first()
    )

    if existing_balance:
        if existing_balance.current_balance >= payment.amount:
            existing_balance.current_balance -= payment.amount
            existing_balance.locked_balance += payment.amount
            db.commit()
        else:
            raise HTTPException(status_code=400, detail="Insufficient balance")
    else:
        raise HTTPException(status_code=400, detail="Bad Request:  Account Not found")

    new_payment = Payment(
        customer_id=customer_id,
        merchant_id=payment.merchant_id,
        amount=payment.amount,
        currency=payment.currency,
        idempotency_key=payment.idempotency_key,
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return new_payment


def get_payment_status(db: Session, payment_id: str, user_id: str) -> Payment:
    redis_client = get_redis()
    cache_key = f"payment:{payment_id}"

    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    existing_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not existing_payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if (
        str(existing_payment.customer_id) != user_id
        and str(existing_payment.merchant_id) != user_id
    ):
        raise HTTPException(
            status_code=403, detail="Not authorized to view this payment"
        )

    if existing_payment.status in TERMINAL_STATES:
        payment_dict = PaymentResponse.model_validate(existing_payment).model_dump(
            mode="json"
        )
        redis_client.setex(cache_key, 3600, json.dumps(payment_dict))

    return existing_payment


def get_all_payments(
    db: Session, user_id: str, role: str, cursor: Optional[str] = None, limit: int = 1
):
    query = db.query(Payment)
    if role == "CUSTOMER":
        query = query.filter(Payment.customer_id == user_id)
    else:
        query = query.filter(Payment.merchant_id == user_id)
    if cursor:
        query = query.filter(Payment.created_at < cursor)

    payments = query.order_by(Payment.created_at.desc()).limit(1).all()
    next_cursor = payments[-1].created_at if len(payments) == limit else None
    return {"data": payments, "next_cursor": next_cursor}


def mock_payment_processor(amount) -> tuple[bool, str | None]:
    import random

    success = random.random() > 0.1
    if success:
        return True, None
    else:
        failure_reasons = [
            "Bank connection timeout",
            "Card declined by issuer",
            "Fraud detection triggered",
            "Daily limit exceeded",
        ]
        return False, random.choice(failure_reasons)


def process_payment_completion(
    db: Session, payment_id: str, success: bool, failure_reason: Optional[str] = None
):
    existing_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not existing_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    customer_account = (
        db.query(CustomerAccount)
        .filter(CustomerAccount.customer_id == existing_payment.customer_id)
        .with_for_update()
        .first()
    )
    if not customer_account:
        raise HTTPException(status_code=404, detail="Account not found")

    if success:
        customer_account.locked_balance -= existing_payment.amount
        existing_payment.status = PaymentStatus.SUCCESS
        existing_payment.completed_at = datetime.now(timezone.utc)
    else:
        customer_account.locked_balance -= existing_payment.amount
        customer_account.current_balance += existing_payment.amount
        existing_payment.status = PaymentStatus.ROLLED_BACK
        existing_payment.failure_reason = failure_reason
    db.commit()
    return existing_payment
