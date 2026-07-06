from kafka import KafkaProducer
import json
from app.core.config import settings

producer = KafkaProducer(
    bootstrap_servers=settings.kafka_bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def publish_payments(payment_id: str, amount: float):
    producer.send(
        settings.kafka_payment_topic,
        {"payment_id": payment_id, "amount": float(amount)},
    )
    producer.flush()
