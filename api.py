from fastapi import FastAPI

app = FastAPI(
    title="IncidentFlow API",
    description="Enterprise Incident Management REST API",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "application": "IncidentFlow",
        "message": "IncidentFlow API is running",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }
