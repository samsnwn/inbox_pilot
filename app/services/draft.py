from app.core.config import settings
from app.services.draft_gemini import generate_draft_gemini

def generate_draft(*, subject: str, body: str, category: str, priority: str, entities: dict) -> str:
    if settings.ai_provider == "gemini":
        return generate_draft_gemini(subject=subject, body=body, category=category, priority=priority, entities=entities)
    raise RuntimeError("AI_PROVIDER not configured for draft generation")