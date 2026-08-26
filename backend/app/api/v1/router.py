from fastapi import APIRouter

from app.api.v1.audit import router as audit_router
from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.conversations import (
    router as conversations_router,
)
from app.api.v1.documents import router as documents_router
from app.api.v1.health import router as health_router
from app.api.v1.organization_members import (
    router as organization_members_router,
)
from app.api.v1.organizations import (
    router as organizations_router,
)
from app.api.v1.tool_approvals import (
    router as tool_approvals_router,
)
from app.api.v1.users import router as users_router
from app.api.v1.agent import router as agent_router
from app.api.v1.incidents import (
    router as incidents_router,
)

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(organizations_router)
api_router.include_router(
    organization_members_router
)
api_router.include_router(
    tool_approvals_router
)
api_router.include_router(documents_router)
api_router.include_router(conversations_router)
api_router.include_router(chat_router)
api_router.include_router(audit_router)
api_router.include_router(agent_router)
api_router.include_router(
    incidents_router
)
