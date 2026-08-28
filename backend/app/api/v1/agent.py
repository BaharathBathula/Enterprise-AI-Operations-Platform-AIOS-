import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.agents.orchestrator import AgentOrchestrator
from app.api.dependencies import get_current_user
from app.api.organization_dependencies import (
    require_organization_write_access,
)
from app.db.database import get_db
from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.schemas.agent import (
    AgentRequest,
    AgentResponse,
)
from app.services.rate_limit_service import rate_limiter
from app.tools.base import ToolExecutionContext
from app.tools.default_registry import (
    create_default_tool_registry,
)
from app.tools.executor import ToolExecutor


router = APIRouter(
    prefix="/organizations/{organization_id}/agent",
    tags=["Agent"],
)


@router.post(
    "",
    response_model=AgentResponse,
)
def run_agent(
    organization_id: uuid.UUID,
    request: AgentRequest,
    _: OrganizationMember = Depends(
        require_organization_write_access,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
) -> AgentResponse:
    rate_limit_result = rate_limiter.check(
        key=(
            f"agent:"
            f"{organization_id}:"
            f"{current_user.id}"
        )
    )

    if not rate_limit_result.allowed:
        headers = {}

        if (
            rate_limit_result.retry_after_seconds
            is not None
        ):
            headers["Retry-After"] = str(
                rate_limit_result.retry_after_seconds
            )

        headers["X-RateLimit-Limit"] = str(
            rate_limit_result.limit
        )

        headers["X-RateLimit-Remaining"] = str(
            rate_limit_result.remaining
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers=headers,
        )

    registry = create_default_tool_registry()

    executor = ToolExecutor(
        registry
    )

    orchestrator = AgentOrchestrator(
        executor
    )

    context = ToolExecutionContext(
        organization_id=organization_id,
        user_id=current_user.id,
        db=db,
    )

    result = orchestrator.handle(
        user_input=request.message,
        context=context,
    )

    return AgentResponse(
        success=result.success,
        message=result.message,
        error=result.error,
        data=result.data,
    )
