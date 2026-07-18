from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Enterprise AI platform for secure document intelligence, "
        "knowledge retrieval, and workflow automation."
    ),
)

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get(
    "/",
    tags=["Root"],
)
def root() -> dict[str, str]:
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "documentation": "/docs",
    }
