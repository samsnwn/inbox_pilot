from __future__ import annotations

import json
from google import genai
from google.genai import types
from app.core.config import settings

def generate_draft_gemini(*, subject: str, body: str, category: str, priority: str, entities: dict) -> str:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=settings.gemini_api_key)

    system = (
        "You write professional, concise customer support email drafts.\n"
        "Rules:\n"
        "- Be helpful and polite\n"
        "- Ask for missing info if needed\n"
        "- Do not invent policies\n"
        "- Keep it under 120 words\n"
        "- Output plain text only"
    )

    prompt = f"""Draft a reply.

Category: {category}
Priority: {priority}
Entities (JSON): {json.dumps(entities)}

Original email:
Subject: {subject}

Body:
{body}
"""

    resp = client.models.generate_content(
        model=settings.ai_model,
        contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.3,
        ),
    )

    text = (resp.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned empty draft")
    return text