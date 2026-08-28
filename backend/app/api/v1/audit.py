import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.organization_dependencies import (
    require_organization_admin,
)
from app.db.database import get_db
from app.models.organization_member import OrganizationMember
from app.schemas.audit import AuditLogResponse
from app.services.audit_service import (
    list_organization_audit_logs,
)

router = APIRouter(
    prefix="/organizations/{organization_id}/audit",
    tags=["Audit Logs"],
)


@router.get(
    "",
    response_model=list[AuditLogResponse],
)
def get_audit_logs(
    organization_id: uuid.UUID,
    event_type: str | None = Query(
        default=None,
        min_length=1,
        max_length=120,
    ),
    outcome: str | None = Query(
        default=None,
        min_length=1,
        max_length=32,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    _: OrganizationMember = Depends(
        require_organization_admin,
    ),
    db: Session = Depends(get_db),
) -> list[AuditLogResponse]:
    return list_organization_audit_logs(
        db=db,
        organization_id=organization_id,
        event_type=event_type,
        outcome=outcome,
        limit=limit,
    )
