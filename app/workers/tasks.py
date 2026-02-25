import re
from app.core.db import SessionLocal
from app.models.email import Email
from app.models.analysis import EmailAnalysis


def classify_email(subject: str, body: str):
    text = (subject + " " + body).lower()

    if "refund" in text or "invoice" in text:
        category = "billing"
    elif "login" in text or "password" in text:
        category = "support"
    elif "buy" in text or "pricing" in text:
        category = "sales"
    elif "win money" in text or "lottery" in text:
        category = "spam"
    else:
        category = "other"

    if "urgent" in text or "asap" in text:
        priority = "urgent"
    elif "immediately" in text:
        priority = "high"
    else:
        priority = "medium"

    return category, priority


def extract_entities(text: str):
    order_match = re.search(r"[A-Z]\d{4}", text)
    email_match = re.search(r"\S+@\S+", text)

    return {
        "order_id": order_match.group(0) if order_match else None,
        "customer_email": email_match.group(0) if email_match else None,
    }


def process_email_task(email_id: str) -> None:
    db = SessionLocal()
    try:
        email = db.query(Email).filter(Email.id == email_id).one()

        email.status = "processing"
        db.commit()

        # classification
        category, priority = classify_email(email.subject, email.body_text)
        entities = extract_entities(email.body_text)

        analysis = EmailAnalysis(
            email_id=email.id,
            category=category,
            priority=priority,
            entities=entities,
        )

        db.add(analysis)

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