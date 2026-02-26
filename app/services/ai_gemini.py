from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field, ConfigDict, ValidationError
from google import genai
from google.genai import types

from app.core.config import settings


class AnalysisOut(BaseModel):
    # Avoid the "model_" protected namespace warning
    model_config = ConfigDict(protected_namespaces=())

    category: str = Field(pattern="^(billing|support|sales|spam|other)$")
    priority: str = Field(pattern="^(low|medium|high|urgent)$")

    # We'll validate entities ourselves as a dict with known keys
    entities: dict[str, Any] = Field(default_factory=dict)

    confidence: float = Field(ge=0.0, le=1.0)
    model_version: str


def analyze_email_gemini(subject: str, body: str) -> AnalysisOut:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=settings.gemini_api_key)

    # IMPORTANT: use types.Schema, and DO NOT use additionalProperties
    response_schema = types.Schema(
        type=types.Type.OBJECT,
        required=["category", "priority", "entities", "confidence", "model_version"],
        properties={
            "category": types.Schema(
                type=types.Type.STRING,
                enum=["billing", "support", "sales", "spam", "other"],
            ),
            "priority": types.Schema(
                type=types.Type.STRING,
                enum=["low", "medium", "high", "urgent"],
            ),
            "confidence": types.Schema(type=types.Type.NUMBER),
            "model_version": types.Schema(type=types.Type.STRING),
            "entities": types.Schema(
                type=types.Type.OBJECT,
                required=["order_id", "customer_email", "deadline"],
                properties={
                    "order_id": types.Schema(type=types.Type.STRING, nullable=True),
                    "customer_email": types.Schema(type=types.Type.STRING, nullable=True),
                    "deadline": types.Schema(type=types.Type.STRING, nullable=True),  # YYYY-MM-DD or null
                },
            ),
        },
    )

    system = (
        "You are an email triage assistant. "
        "Return ONLY JSON that matches the provided schema. "
        "deadline must be YYYY-MM-DD or null."
    )

    prompt = f"""Subject: {subject}

Body:
{body}
"""

    resp = client.models.generate_content(
        model=settings.ai_model,
        contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
        config=types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.2,
        ),
    )

    raw = (resp.text or "").strip()
    if not raw:
        raise RuntimeError("Gemini returned empty response")

    try:
        data = json.loads(raw)
        # Ensure model_version is always set
        data.setdefault("model_version", settings.ai_model)
        return AnalysisOut(**data)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Gemini returned non-JSON: {raw[:200]}") from e
    except ValidationError as e:
        raise RuntimeError(f"Gemini JSON failed validation: {e}") from e