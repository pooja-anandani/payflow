from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.kafka_producer import publish_payments
from app.core.limiter import limiter
from app.schemas.payment import PaymentResponse, PaymentCreate, PaymentHistoryResponse
from app.services.payment_service import (
    create_payment,
    get_payment_status,
    get_all_payments,
)

router = APIRouter()

@router.post("/", status_code=201, response_model=PaymentResponse)
@limiter.limit("5/minute")
def register_payment(
    request: Request,
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    new_payment = create_payment(db, payment, current_user["user_id"])
    publish_payments(str(new_payment.id), new_payment.amount)
    return new_payment


@router.get("/{payment_id}", status_code=200, response_model=PaymentResponse)
def status_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return get_payment_status(db, payment_id, current_user["user_id"])


@router.get("/", status_code=200, response_model=PaymentHistoryResponse)
def payment_history(
    cursor: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return get_all_payments(
        db, current_user["user_id"], current_user["role"], cursor, limit
    )