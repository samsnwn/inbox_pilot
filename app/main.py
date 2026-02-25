from fastapi import FastAPI
from app.api.routes_emails import router as emails_router

app = FastAPI(title="Inbox Pilot", version="0.1.0")

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(emails_router)