from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    unhandled_exception_handler,
)
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.request_logging import (
    RequestLoggingMiddleware,
)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Enterprise AI platform for secure document intelligence, "
        "knowledge retrieval, and workflow automation."
    ),
)

app.add_exception_handler(
    Exception,
    unhandled_exception_handler,
)

app.add_middleware(
    RequestLoggingMiddleware,
)

app.add_middleware(
    RequestIDMiddleware,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
