# Inbox Pilot

Inbox Pilot is a backend-focused system that simulates an AI-powered email triage pipeline.

It ingests emails, guarantees idempotent storage, processes them asynchronously, and is designed to later integrate AI-based classification and reply generation.

The goal of this project is to demonstrate real-world backend engineering patterns such as idempotency, asynchronous processing, database-driven integrity, and clean service separation.

---

## Architecture Overview

The system follows a pipeline model:

1. **Ingestion API**  
   Emails are received via `POST /emails/ingest`.

2. **Idempotent Storage**  
   A unique constraint on `(provider, provider_message_id)` ensures duplicate messages cannot be stored.

3. **Async Processing (Worker)**  
   After ingestion, a background worker processes the email:
   - Updates status (`new → processing → done`)
   - (Future step) performs AI classification and reply drafting

4. **Read APIs**  
   - `GET /emails`
   - `GET /emails/{id}`  
   Used to inspect stored emails and track processing state.

---

## Tech Stack

- FastAPI – REST API framework  
- PostgreSQL – Primary database  
- SQLAlchemy 2.0 – ORM  
- Alembic – Database migrations  
- Redis + RQ – Background job queue  
- Docker Compose – Local orchestration  

---


Running the Project
1. Create environment file
cp .env.example .env
2. Start services
docker compose up --build

This starts:

PostgreSQL

Redis

API server

Worker process

Database Setup

Generate and apply migrations:

docker compose run --rm api alembic revision --autogenerate -m "init schema"
docker compose run --rm api alembic upgrade head
API Usage
Health Check
GET /health
Ingest Email
POST /emails/ingest

Behavior:

First request → creates record (idempotent: false)

Same request again → returns same ID (idempotent: true)

List Emails
GET /emails

Returns emails ordered newest-first.

Get Single Email
GET /emails/{email_id}

Returns full email details and current processing status.

Email Lifecycle
new → processing → done
                   ↘ failed

This models real-world asynchronous backend pipelines.

Key Concepts Demonstrated
Idempotency

Duplicate deliveries are handled safely using a database-level unique constraint instead of relying on application-level checks.

Async Processing

The API responds immediately while background workers handle longer-running tasks.

State Management

Emails move through controlled lifecycle states to ensure reliability and observability.

Separation of Concerns

emails → raw source of truth

email_analysis → derived AI output (future step)

draft_replies → generated responses (future step)

Future Extensions

AI-based classification and entity extraction

RAG-based reply generation

Retry policies and dead-letter queues

Authentication and rate limiting

Metrics and observability

Purpose

Inbox Pilot is intentionally backend-heavy and infrastructure-focused.

It is designed to be:

Architecture-driven

Production-pattern oriented

Easily extensible