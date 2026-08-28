from fastapi import (
    APIRouter,
    Depends,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "AIOS Backend",
    }


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {
        "status": "alive",
        "service": "AIOS Backend",
    }


@router.get("/health/ready")
def readiness(
    db: Session = Depends(get_db),
):
    try:
        db.execute(
            text("SELECT 1")
        )

    except SQLAlchemyError:
        return JSONResponse(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            content={
                "status": "not_ready",
                "service": "AIOS Backend",
                "database": "unavailable",
            },
        )

    return {
        "status": "ready",
        "service": "AIOS Backend",
        "database": "available",
    }
