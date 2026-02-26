from app.core.db import SessionLocal
from app.models.email import Email
from app.models.analysis import EmailAnalysis
from app.models.draft import DraftReply
from app.services.ai import analyze_email
from app.services.draft import generate_draft
from app.core.config import settings

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
        email.processing_error = None
        db.commit()

        draft_text = generate_draft(
            subject=email.subject,
            body=email.body_text,
            category=analysis.category,
            priority=analysis.priority,
            entities=analysis.entities,
        )

        draft = db.query(DraftReply).filter(DraftReply.email_id == email.id).one_or_none()
        if draft is None:
            draft = DraftReply(
                email_id=email.id,
                draft_text=draft_text,
            )
            db.add(draft)
            db.commit()
        else:
            draft.draft_text = draft_text
        if hasattr(draft, "model_version"):
            draft.model_version = settings.ai_model
        

    except Exception as e:
        email = db.query(Email).filter(Email.id == email_id).one_or_none()
        if email:
            email.status = "failed"
            email.processing_error = str(e)[:2000]
            db.commit()
        raise
    finally:
        db.close()