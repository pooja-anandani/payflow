from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.limiter import limiter
from app.schemas.merchant import MerchantCreate, MerchantResponse, MerchantLogin
from app.services.merchant_service import (
    create_merchant,
    authenticate_merchant,
    get_merchant,
)

router = APIRouter()


@router.post("/register", status_code=201, response_model=MerchantResponse)
def register_merchant(merchant: MerchantCreate, db: Session = Depends(get_db)):
    return create_merchant(db, merchant)


@router.post("/login", status_code=200)
@limiter.limit("5/minute")
def login_merchant(
    request: Request, merchant: MerchantLogin, db: Session = Depends(get_db)
):
    return authenticate_merchant(db, merchant)


@router.get("/me", status_code=200, response_model=MerchantResponse)
def fetch_customer(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    return get_merchant(db, current_user["user_id"])
