from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.db import get_db
from app.models.email import Email
from app.schemas.email import EmailIngest, EmailOut, EmailDetailOut, EmailAnalysisOut
from app.models.analysis import EmailAnalysis

import redis
from rq import Queue
from app.core.config import settings
from app.workers.tasks import process_email_task

from app.models.draft import DraftReply
from app.schemas.email import DraftOut

router = APIRouter(prefix="/emails", tags=["emails"])

def enqueue_processing(email_id: str) -> str:
    redis_conn = redis.from_url(settings.redis_url)
    q = Queue("default", connection=redis_conn)
    job = q.enqueue(process_email_task, email_id, job_timeout=120)
    return job.id

@router.post("/ingest")
def ingest_email(payload: EmailIngest, db: Session = Depends(get_db)):
    email = Email(
        provider=payload.provider,
        provider_message_id=payload.provider_message_id,
        thread_id=payload.thread_id,
        from_addr=payload.from_addr,
        to_addr=payload.to_addr,
        subject=payload.subject,
        body_text=payload.body_text,
        received_at=payload.received_at,
        status="new",
    )

    db.add(email)

    try:
        db.commit()
        db.refresh(email)
        job_id = enqueue_processing(email.id)
        return {"email_id": email.id, "idempotent": False, "job_id": job_id}
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(Email)
            .filter(
                Email.provider == payload.provider,
                Email.provider_message_id == payload.provider_message_id,
            )
            .one()
        )
        job_id = enqueue_processing(existing.id)
        return {"email_id": existing.id, "idempotent": True, "job_id": job_id}

@router.get("", response_model=list[EmailOut])
def list_emails(db: Session = Depends(get_db)):
    emails = db.query(Email).order_by(Email.received_at.desc()).all()
    return [
        EmailOut(
            id=e.id,
            provider=e.provider,
            provider_message_id=e.provider_message_id,
            thread_id=e.thread_id,
            from_addr=e.from_addr,
            to_addr=e.to_addr,
            subject=e.subject,
            body_text=e.body_text,
            received_at=e.received_at,
            status=e.status,
        )
        for e in emails
    ]

@router.get("/{email_id}", response_model=EmailDetailOut)
def get_email(email_id: str, db: Session = Depends(get_db)):
    e = db.query(Email).filter(Email.id == email_id).one()

    a = (
        db.query(EmailAnalysis)
        .filter(EmailAnalysis.email_id == e.id)
        .one_or_none()
    )

    analysis_out = None
    if a is not None:
        analysis_out = EmailAnalysisOut(
            category=a.category,
            priority=a.priority,
            entities=a.entities,
            confidence=a.confidence,
            model_version=a.model_version,
        )

    d = (
    db.query(DraftReply)
    .filter(DraftReply.email_id == e.id)
    .one_or_none()
    )

    draft_out = None
    if d is not None:
        draft_out = DraftOut(
            body_text=d.draft_text,
            model_version=getattr(d, "model_version", None),
        )
        
    return EmailDetailOut(
        id=e.id,
        provider=e.provider,
        provider_message_id=e.provider_message_id,
        thread_id=e.thread_id,
        from_addr=e.from_addr,
        to_addr=e.to_addr,
        subject=e.subject,
        body_text=e.body_text,
        received_at=e.received_at,
        status=e.status,
        processing_error=e.processing_error,
        analysis=analysis_out,
        draft=draft_out,
    )

@router.post("/{email_id}/reprocess")
def reprocess_email(email_id: str, db: Session = Depends(get_db)):
    e = db.query(Email).filter(Email.id == email_id).one()
    job_id = enqueue_processing(e.id)
    return {"email_id": e.id, "job_id": job_id}