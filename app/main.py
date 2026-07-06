from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.limiter import limiter
from app.core.config import settings
from app.api.customers import router as customers_router
from app.api.merchants import router as merchants_router
from app.api.payments import router as payments_router

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(customers_router, prefix="/api/v1/customers", tags=["customers"])
app.include_router(merchants_router, prefix="/api/v1/merchants", tags=["merchants"])
app.include_router(payments_router, prefix="/api/v1/payments", tags=["payments"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}
