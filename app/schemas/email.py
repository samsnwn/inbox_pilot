from pydantic import BaseModel
from datetime import datetime
from typing import Any

class EmailIngest(BaseModel):
    provider: str = "simulator"
    provider_message_id: str
    thread_id: str | None = None
    from_addr: str
    to_addr: str
    subject: str
    body_text: str
    received_at: datetime | None = None

class EmailOut(BaseModel):
    id: str
    provider: str
    provider_message_id: str
    thread_id: str | None
    from_addr: str
    to_addr: str
    subject: str
    body_text: str
    received_at: datetime | None
    status: str

class EmailAnalysisOut(BaseModel):
    category: str
    priority: str
    entities: dict[str, Any]
    confidence: float
    model_version: str

class EmailDetailOut(EmailOut):
    analysis: EmailAnalysisOut | None = None