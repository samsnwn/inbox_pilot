import uuid
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class DraftReply(Base):
    __tablename__ = "draft_replies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email_id: Mapped[str] = mapped_column(String(36), ForeignKey("emails.id", ondelete="CASCADE"), unique=True)

    draft_text: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[list] = mapped_column(JSONB, default=list)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())