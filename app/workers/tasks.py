import time
from app.core.db import SessionLocal
from app.models.email import Email

def process_email_task(email_id: str) -> None:
    db = SessionLocal()
    try:
        email = db.query(Email).filter(Email.id == email_id).one()
        email.status = "processing"
        db.commit()

        # Simulate work (later: AI + RAG)
        time.sleep(1)

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