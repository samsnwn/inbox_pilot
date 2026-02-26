from app.core.config import settings
from app.services.ai_gemini import analyze_email_gemini, AnalysisOut

def analyze_email(subject: str, body: str) -> AnalysisOut:
    if settings.ai_provider == "gemini":
        return analyze_email_gemini(subject, body)

    # fallback: keep your current stub implementation (call it here)
    raise RuntimeError("AI_PROVIDER not configured (set AI_PROVIDER=gemini)")