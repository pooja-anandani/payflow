import enum


class PaymentStatus(enum.Enum):
    INITIATED = "INITIATED"
    VALIDATING = "VALIDATING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class UserRole(enum.Enum):
    CUSTOMER = "CUSTOMER"
    MERCHANT = "MERCHANT"
