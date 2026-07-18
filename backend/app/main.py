from fastapi import FastAPI

app = FastAPI(
    title="Enterprise AI Operations Platform",
    version="0.1.0",
    description="Enterprise AI platform for document intelligence.",
)


@app.get("/")
async def root():
    return {
        "application": "AIOS",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }
