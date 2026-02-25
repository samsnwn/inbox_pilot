import uuid
from sqlalchemy import String, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class EmailAnalysis(Base):
    __tablename__ = "email_analysis"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email_id: Mapped[str] = mapped_column(String(36), ForeignKey("emails.id", ondelete="CASCADE"), unique=True)

    category: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    entities: Mapped[dict] = mapped_column(JSONB, default=dict)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    model_version: Mapped[str] = mapped_column(String(100), default="stub-v1")

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())