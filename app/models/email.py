import uuid
from sqlalchemy import String, Text, DateTime, Enum, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

EMAIL_STATUS = ("new", "processing", "done", "failed")

class Email(Base):
    __tablename__ = "emails"
    __table_args__ = (
        UniqueConstraint("provider", "provider_message_id", name="uq_email_provider_msgid"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider: Mapped[str] = mapped_column(String(50), default="simulator")
    provider_message_id: Mapped[str] = mapped_column(String(255), nullable=False)

    thread_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    from_addr: Mapped[str] = mapped_column(String(255), nullable=False)
    to_addr: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)

    received_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(Enum(*EMAIL_STATUS, name="email_status"), default="new")