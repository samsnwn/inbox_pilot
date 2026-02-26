from app.core.db import SessionLocal
from app.models.email import Email
from app.models.analysis import EmailAnalysis
from app.services.ai import analyze_email

def process_email_task(email_id: str) -> None:
    db = SessionLocal()
    try:
        email = db.query(Email).filter(Email.id == email_id).one()

        email.status = "processing"
        db.commit()

        # classification
        result = analyze_email(email.subject, email.body_text)

        analysis = db.query(EmailAnalysis).filter_by(email_id=email.id).first()

        if analysis is None:
            analysis = EmailAnalysis(
                email_id=email.id,
                category=result.category,
                priority=result.priority,
                entities=result.entities,
                confidence=result.confidence,
                model_version=result.model_version,
            )
            db.add(analysis)
        else:
            analysis.category = result.category
            analysis.priority = result.priority
            analysis.entities = result.entities
            analysis.confidence = result.confidence
            analysis.model_version = result.model_version

        email.status = "done"
        db.commit()

    except Exception:
        email = db.query(Email).filter(Email.id == email_id).one_or_none()
        if email:
            email.status = "failed"
            db.commit()
        raise
    finally:
        db.close()