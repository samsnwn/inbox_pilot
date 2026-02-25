# 📬 Inbox Pilot

Inbox Pilot is an asynchronous email-processing system that ingests emails, processes them using AI, retrieves relevant company policies (RAG), and generates draft replies.

It is designed using a **production-grade architecture pattern**:

> Ingestion → Storage → Queue → Worker → AI Processing → Results API

This mirrors how real SaaS and enterprise systems are built.

---

# 🏗 Architecture Overview

```
Incoming Email
      ↓
Ingestion API
      ↓
Database (idempotent storage)
      ↓
Queue (async processing)
      ↓
Worker
   ├─ Classification
   ├─ Field Extraction
   ├─ KB Retrieval (RAG)
   └─ Draft Generation
      ↓
Database (store results)
      ↓
Results API
```

---

# 🔑 Core Concepts

## 1️⃣ Ingestion
- Receives emails (simulator for now, Gmail webhook later)
- Stores them safely in the database
- Prevents duplicates using DB constraints (idempotency)
- Pushes jobs to the queue

## 2️⃣ Idempotency
- Enforced via a `UNIQUE` constraint on `provider_message_id`
- Safe under concurrency
- Retries do not create duplicate records

## 3️⃣ Async Processing
- Heavy AI tasks run in background workers
- API remains fast and responsive
- System is horizontally scalable

## 4️⃣ RAG (Retrieval-Augmented Generation)
- Retrieves relevant Knowledge Base (KB) documents
- Injects them into AI prompts
- Ensures accurate, policy-based replies

---

# 🧱 Tech Stack

- **FastAPI** – REST API
- **PostgreSQL** – Primary database
- **SQLAlchemy** – ORM
- **Alembic** – Database migrations
- **Docker Compose** – Local orchestration
- **OpenAI (or similar)** – AI classification & drafting
- **Vector Search (future)** – KB retrieval

---

# 📂 Project Structure

```
app/
  api/
    routes_emails.py
  models/
    email.py
  services/
    ingestion.py
    worker.py
    rag.py
  db/
    session.py
    base.py
alembic/
docker-compose.yml
```

---

# 🚀 Getting Started

## 1️⃣ Start services

```bash
docker compose up -d
```

## 2️⃣ Run database migrations

```bash
docker compose exec api alembic upgrade head
```

## 3️⃣ Access API

### List emails
```
GET /emails
```

### Ingest email
```
POST /emails
```

---

# 🗄 Database Design (Simplified)

## `emails` table

| Column | Description |
|--------|-------------|
| id | Internal UUID |
| provider | Email provider (simulator, gmail) |
| provider_message_id | External ID (UNIQUE) |
| thread_id | Conversation thread |
| from_addr | Sender |
| to_addr | Recipient |
| subject | Email subject |
| body_text | Email content |
| received_at | Timestamp |
| status | RECEIVED / PROCESSING / COMPLETED / FAILED |
| classification | AI classification |
| draft_reply | Generated response |

---

# 🔄 Email Lifecycle

1. Email received
2. Stored with status `RECEIVED`
3. Worker picks it up → sets `PROCESSING`
4. AI classification + RAG retrieval
5. Draft generated
6. Status updated to `COMPLETED`

If worker fails → job can be retried safely.

---

# 🧪 Development Notes

## Reset database (dev only)

```bash
docker compose down -v
docker compose up -d
docker compose exec api alembic upgrade head
```

## Check migration state

```bash
alembic current
alembic heads
```

---

# 🎯 Design Principles

- Idempotent ingestion
- Database as source of truth
- Async-first processing
- Clear separation of concerns
- Scalable architecture
- Production-ready patterns

---

# 📌 Future Improvements

- Gmail webhook integration
- Real queue system (Redis / RabbitMQ)
- Vector database for KB embeddings
- Admin dashboard
- Multi-tenant support
- Observability (metrics + tracing)

---

# 🧠 Why This Project Matters

Inbox Pilot is not just an AI demo.

It demonstrates:
- Real-world backend architecture
- Async job processing
- Database migration discipline
- AI integration with RAG
- Idempotent system design

This is the foundation of modern AI-powered SaaS systems.