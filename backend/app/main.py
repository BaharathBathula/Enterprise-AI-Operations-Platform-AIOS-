from fastapi import FastAPI

app = FastAPI(
    title="Enterprise AI Operations Platform",
    description="Enterprise AI platform for document intelligence and workflow automation.",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {
        "application": "Enterprise AI Operations Platform",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }
