# PayFlow — Scalable Payment Processing API

A production-grade payment processing backend built with FastAPI, PostgreSQL, Redis, and Kafka. Designed to demonstrate real-world distributed systems concepts including async processing, pessimistic locking, event-driven architecture, and caching strategies.

---

## Architecture

```
Client
  │
  ▼
FastAPI (REST API)
  │
  ├── PostgreSQL (primary data store)
  ├── Redis (caching terminal payment states)
  └── Kafka (async payment processing)
         │
         ▼
    Payment Consumer (background worker)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Framework | FastAPI |
| Database | PostgreSQL 15 |
| ORM | SQLAlchemy + Alembic |
| Caching | Redis 7 |
| Message Queue | Apache Kafka |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Validation | Pydantic V2 |
| Containerization | Docker + docker-compose |

---

## Features

- **JWT Authentication** — secure login for customers and merchants with role-based access control
- **Payment State Machine** — full lifecycle management: `INITIATED → VALIDATING → PROCESSING → SUCCESS / REJECTED / FAILED → ROLLED_BACK`
- **Idempotency** — prevents double charging via client-generated idempotency keys
- **Pessimistic Locking** — `SELECT FOR UPDATE` prevents race conditions on balance updates
- **Async Payment Processing** — Kafka decouples payment creation from processing; API returns immediately
- **Redis Caching** — terminal payment states cached for 1 hour; non-terminal states always hit DB
- **Rate Limiting** — login endpoints limited to 5 requests/minute per IP
- **Cursor Pagination** — stable payment history pagination unaffected by new inserts
- **Input Validation** — Pydantic validators on email, password strength, amount range, currency

---

## Project Structure

```
payflow/
├── app/
│   ├── api/                  # FastAPI routers (endpoints)
│   │   ├── customers.py
│   │   ├── merchants.py
│   │   └── payments.py
│   ├── core/                 # Shared infrastructure
│   │   ├── config.py         # Environment config (Pydantic Settings)
│   │   ├── database.py       # SQLAlchemy engine + session
│   │   ├── security.py       # JWT + bcrypt
│   │   ├── dependencies.py   # get_current_user (FastAPI Depends)
│   │   ├── cache.py          # Redis client
│   │   ├── kafka_producer.py # Kafka message publisher
│   │   ├── kafka_consumer.py # Kafka message consumer
│   │   └── limiter.py        # Rate limiter
│   ├── models/               # SQLAlchemy DB models
│   │   ├── customer.py
│   │   ├── merchant.py
│   │   ├── customer_account.py
│   │   ├── payment.py
│   │   └── enums.py
│   ├── schemas/              # Pydantic request/response schemas
│   │   ├── customer.py
│   │   ├── merchant.py
│   │   └── payment.py
│   ├── services/             # Business logic layer
│   │   ├── customer_service.py
│   │   ├── merchant_service.py
│   │   └── payment_service.py
│   ├── main.py               # FastAPI app entrypoint
│   └── worker.py             # Kafka consumer entrypoint
├── alembic/                  # DB migrations
├── docker-compose.yml
├── Dockerfile
├── .env
└── requirements.txt
```

---

## Data Model

```
Customer
  id, name, email, password_hash, phone_number, preferred_currency,
  role, created_at, updated_at

Merchant
  id, name, email, password_hash, phone_number, webhook_url,
  business_registration_id, street, city, province, country,
  postal_code, settlement_currency, role, created_at, updated_at

CustomerAccount
  id, customer_id (FK), account_number, current_balance,
  locked_balance, currency, created_at, updated_at

Payment
  id, customer_id (FK), merchant_id (FK), amount, currency,
  status, idempotency_key, description, failure_reason,
  created_at, updated_at, completed_at
```

---

## Payment Flow

```
1. Customer hits POST /api/v1/payments/
2. API validates JWT → extracts customer_id
3. Checks idempotency key — rejects duplicates
4. Validates merchant exists
5. Checks customer balance (SELECT FOR UPDATE — pessimistic lock)
6. Locks balance: current_balance -= amount, locked_balance += amount
7. Creates Payment record (status: INITIATED)
8. Publishes message to Kafka topic "payment.process"
9. Returns INITIATED response immediately

[Background Worker]
10. Kafka consumer picks up message
11. Calls mock payment processor (90% success rate)
12. On SUCCESS: locked_balance -= amount, status → SUCCESS
13. On FAILURE: locked_balance -= amount, current_balance += amount, status → ROLLED_BACK
14. Updates DB with completed_at timestamp
```

---

## API Endpoints

### Auth
```
POST /api/v1/customers/register    — register customer
POST /api/v1/customers/login       — login, returns JWT
GET  /api/v1/customers/me          — customer profile (protected)

POST /api/v1/merchants/register    — register merchant
POST /api/v1/merchants/login       — login, returns JWT
GET  /api/v1/merchants/me          — merchant profile (protected)
```

### Payments
```
POST /api/v1/payments/             — initiate payment (protected)
GET  /api/v1/payments/{id}         — payment status (protected)
GET  /api/v1/payments/             — payment history with cursor pagination (protected)
```

### Health
```
GET  /health                       — service health check
```

---

## Getting Started

### Prerequisites
- Docker + Docker Compose

### Run with Docker

```bash
git clone <repo>
cd payflow
cp .env.example .env   # update values as needed
docker compose up --build
```

App runs at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### Run locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start infrastructure
docker compose up -d db redis kafka zookeeper

# Run migrations
alembic upgrade head

# Start API
uvicorn app.main:app --reload

# Start Kafka consumer (separate terminal)
python -m app.worker
```

---

## Key Design Decisions

**Why Kafka for payment processing?**
Decouples payment creation from processing. API returns immediately, consumer processes asynchronously. Enables horizontal scaling of consumers independently of the API layer.

**Why pessimistic locking on CustomerAccount?**
Payments are high-contention — multiple payments can hit the same account simultaneously. Pessimistic locking (`SELECT FOR UPDATE`) prevents race conditions and overdrafts. Optimistic locking would risk failed retries mid-transaction.

**Why cursor pagination over offset?**
Offset pagination suffers from page drift when new records are inserted mid-browse. Cursor pagination anchors position to a specific `created_at` timestamp, ensuring no records are missed or duplicated.

**Why cache only terminal states?**
`INITIATED` and `PROCESSING` states change frequently — caching them risks stale data. `SUCCESS`, `ROLLED_BACK`, and `REJECTED` are immutable — safe to cache indefinitely (1 hour TTL).

**Why snapshot currency on Payment?**
Customer and merchant currencies may differ and may change over time. Snapshotting currency at transaction time ensures historical accuracy for audits and disputes.

---

## Environment Variables

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/payflow
REDIS_URL=redis://localhost:6379
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_PAYMENT_TOPIC=payment.process
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=PayFlow
APP_VERSION=v1
DEBUG=True
```