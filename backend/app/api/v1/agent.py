import uuid

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.agents.orchestrator import AgentOrchestrator
from app.api.dependencies import get_current_user
from app.api.organization_dependencies import (
    require_organization_member,
)
from app.db.database import get_db
from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.schemas.agent import (
    AgentRequest,
    AgentResponse,
)
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
        require_organization_member,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
) -> AgentResponse:
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
