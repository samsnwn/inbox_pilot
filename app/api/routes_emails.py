from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.db import get_db
from app.models.email import Email
from app.schemas.email import EmailIngest, EmailOut

router = APIRouter(prefix="/emails", tags=["emails"])  # <-- THIS MUST BE TOP LEVEL


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
        return {"email_id": email.id, "idempotent": False}
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
        return {"email_id": existing.id, "idempotent": True}

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

@router.get("/{email_id}", response_model=EmailOut)
def get_email(email_id: str, db: Session = Depends(get_db)):
    e = db.query(Email).filter(Email.id == email_id).one()
    return EmailOut(
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