import json
import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.middleware.request_id import REQUEST_ID_HEADER


logger = logging.getLogger("app.errors")


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    log_data = {
        "event": "unhandled_exception",
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "exception_type": type(exc).__name__,
    }

    logger.error(
        json.dumps(
            log_data,
            separators=(",", ":"),
        ),
        exc_info=(
            type(exc),
            exc,
            exc.__traceback__,
        ),
    )

    headers = {}

    if request_id is not None:
        headers[REQUEST_ID_HEADER] = request_id

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
        headers=headers,
    )
