import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
)
from app.api.organization_dependencies import (
    require_organization_admin,
    require_organization_member,
    require_organization_write_access,
)
from app.db.database import get_db
from app.models.incident import (
    Incident,
    IncidentSeverity,
    IncidentStatus,
)
from app.models.organization_member import (
    OrganizationMember,
)
from app.models.user import User
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
)

router = APIRouter(
    prefix=(
        "/organizations/"
        "{organization_id}/incidents"
    ),
    tags=["Incidents"],
)


@router.get(
    "",
    response_model=list[IncidentResponse],
)
def list_incidents(
    organization_id: uuid.UUID,
    incident_status: IncidentStatus | None = Query(
        default=None,
        alias="status",
    ),
    severity: IncidentSeverity | None = None,
    _: OrganizationMember = Depends(
        require_organization_member,
    ),
    db: Session = Depends(get_db),
) -> list[Incident]:
    statement = (
        select(Incident)
        .where(
            Incident.organization_id
            == organization_id
        )
        .order_by(
            Incident.created_at.desc()
        )
    )

    if incident_status is not None:
        statement = statement.where(
            Incident.status
            == incident_status
        )

    if severity is not None:
        statement = statement.where(
            Incident.severity
            == severity
        )

    return list(
        db.scalars(statement).all()
    )


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_incident(
    organization_id: uuid.UUID,
    payload: IncidentCreate,
    _: OrganizationMember = Depends(
        require_organization_write_access,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
) -> Incident:
    incident = Incident(
        organization_id=organization_id,
        created_by_user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        severity=payload.severity,
        status=IncidentStatus.open,
        source=payload.source,
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident(
    organization_id: uuid.UUID,
    incident_id: uuid.UUID,
    _: OrganizationMember = Depends(
        require_organization_member,
    ),
    db: Session = Depends(get_db),
) -> Incident:
    incident = db.scalar(
        select(Incident).where(
            Incident.id == incident_id,
            Incident.organization_id
            == organization_id,
        )
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return incident


@router.patch(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def update_incident(
    organization_id: uuid.UUID,
    incident_id: uuid.UUID,
    payload: IncidentUpdate,
    _: OrganizationMember = Depends(
        require_organization_admin,
    ),
    db: Session = Depends(get_db),
) -> Incident:
    incident = db.scalar(
        select(Incident).where(
            Incident.id == incident_id,
            Incident.organization_id
            == organization_id,
        )
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    changes = payload.model_dump(
        exclude_unset=True,
    )

    for field, value in changes.items():
        setattr(
            incident,
            field,
            value,
        )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident


@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_incident(
    organization_id: uuid.UUID,
    incident_id: uuid.UUID,
    _: OrganizationMember = Depends(
        require_organization_admin,
    ),
    db: Session = Depends(get_db),
) -> None:
    incident = db.scalar(
        select(Incident).where(
            Incident.id == incident_id,
            Incident.organization_id
            == organization_id,
        )
    )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    db.delete(incident)
    db.commit()
