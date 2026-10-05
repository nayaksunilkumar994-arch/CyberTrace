from fastapi import FastAPI

from app.db.database import Base, engine
from app.models import User, Event
from app.api.routes.events import router as events_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="CyberTrace API",
    description="AI-Powered Digital Forensics & Incident Investigation Platform",
    version="0.1.0",
)


app.include_router(events_router)


@app.get("/")
def root():
    return {
        "name": "CyberTrace",
        "version": "0.1.0",
        "status": "operational",
        "description": "Digital Forensics & Incident Investigation Platform",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CyberTrace API",
    }