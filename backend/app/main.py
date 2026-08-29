from fastapi import FastAPI

app = FastAPI(
    title="CyberTrace API",
    description="AI-Powered Digital Forensics & Incident Investigation Platform",
    version="0.1.0",
)


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