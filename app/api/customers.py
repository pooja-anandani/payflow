from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.limiter import limiter
from app.core.dependencies import get_current_user
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerLogin
from app.services.customer_service import (
    create_customer,
    get_customer,
    authenticate_customer,
)

router = APIRouter()


# FastAPI intercepts the returned SQLAlchemy object (new_customer)
# and serializes it using CustomerResponse schema.
# Only fields defined in CustomerResponse are included in the response —
# sensitive fields like password_hash are automatically excluded.
# This works because FastAPI calls CustomerResponse.model_validate(new_customer)
# under the hood, mapping SQLAlchemy model fields to Pydantic schema fields.


@router.post("/register", status_code=201, response_model=CustomerResponse)
def register_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    return create_customer(db, customer)


@router.post("/login", status_code=200)
@limiter.limit("5/minute")
def login_customer(
    request: Request, customer: CustomerLogin, db: Session = Depends(get_db)
):
    return authenticate_customer(db, customer)


@router.get("/me", status_code=200, response_model=CustomerResponse)
def fetch_customer(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    return get_customer(db, current_user["user_id"])
