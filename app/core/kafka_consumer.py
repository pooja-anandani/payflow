from kafka import KafkaConsumer
import json
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.payment_service import (
    mock_payment_processor,
    process_payment_completion,
)

consumer = KafkaConsumer(
    settings.kafka_payment_topic,
    bootstrap_servers=settings.kafka_bootstrap_servers,
    value_deserializer=lambda v: json.loads(
        v.decode("utf-8")
    ),  # bytes -> JSON STRING -> PYTHON DICT
    group_id="payment-processor",
)


def start_consumer():
    for message in consumer:
        data = message.value
        payment_id = data["payment_id"]
        amount = data["amount"]
        db = SessionLocal()
        try:
            success, failure_reason = mock_payment_processor(amount)
            process_payment_completion(db, payment_id, success, failure_reason)
        finally:
            db.close()
